import json
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Union

from bson import ObjectId, json_util
from deepdiff import DeepDiff
from motor.motor_asyncio import AsyncIOMotorClientSession, AsyncIOMotorDatabase
from pymongo.errors import CollectionInvalid

from .models import AuditLogModel

logger = logging.getLogger(__name__)


async def init_timeseries_collection(
    db: AsyncIOMotorDatabase,
    collection_name: str,
    time_field: str,
    meta_field: Optional[str] = None,
    granularity: str = "seconds",
):
    """
    Initialize a MongoDB Time Series collection.

    Args:
        db: MongoDB database instance
        collection_name: Name of the collection to create
        time_field: Name of the timestamp field
        meta_field: Optional metadata field for grouping documents
        granularity: Time granularity ("seconds", "minutes", or "hours")
    """
    try:
        timeseries_config = {
            "timeField": time_field,
            "granularity": granularity,
        }

        if meta_field:
            timeseries_config["metaField"] = meta_field

        await db.create_collection(
            collection_name,
            timeseries=timeseries_config,
        )
        logger.info(
            f"Time Series collection '{collection_name}' created/verified"
        )
    except CollectionInvalid:
        # Collection already exists - this is normal
        logger.debug(
            f"Time Series collection '{collection_name}' already exists"
        )
    except Exception as e:
        logger.warning(
            f"Warning during Time Series initialization for "
            f"'{collection_name}': {e}",
            exc_info=True,
        )


async def init_audit_timeseries(db: AsyncIOMotorDatabase):
    """
    Initialize MongoDB Time Series collection for efficient audit log storage.

    This is a convenience wrapper for audit logs specifically.
    """
    await init_timeseries_collection(
        db=db,
        collection_name="audit_logs",
        time_field="date",
        meta_field="collection",
        granularity="seconds",
    )


def json_serializer(obj):
    """
    Custom JSON serializer for MongoDB types and Python sets.

    Handles special cases that standard JSON encoder can't process:
    - Python sets (convert to lists)
    - Type objects (convert to strings)
    - MongoDB-specific types via json_util
    """
    if isinstance(obj, (set, frozenset)) or type(obj).__name__ == "SetOrdered":
        return list(obj)
    if isinstance(obj, type):
        return str(obj)
    return json_util.default(obj)


async def log_audit(
    db: AsyncIOMotorDatabase,
    collection: str,
    doc_id: Union[str, ObjectId],
    user: str,
    action: str,
    old_doc: Optional[Dict] = None,
    new_doc: Optional[Dict] = None,
    session: Optional[AsyncIOMotorClientSession] = None,
) -> None:
    """
    Log CRUD operations to audit collection with detailed change tracking.

    For UPDATE operations, only logs if actual changes are detected (excluding
    audit metadata fields). This prevents noise from unchanged updates.

    Args:
        db: MongoDB database instance
        collection: Name of the collection being modified
        doc_id: ID of the document being modified
        user: User ID performing the action
        action: Operation type (CREATE, UPDATE, DELETE, RESTORE, HARD_DELETE)
        old_doc: Document state before change (for UPDATE/DELETE/RESTORE)
        new_doc: Document state after change (for UPDATE/RESTORE)
        session: Optional database session for transactions

    Raises:
        ValueError: If required parameters are invalid
        ValidationError: If audit log entry is invalid
    """
    # Input validation
    if not collection or not isinstance(collection, str):
        raise ValueError("collection must be a non-empty string")
    if not user or not isinstance(user, str):
        raise ValueError("user must be a non-empty string")
    if not action or not isinstance(action, str):
        raise ValueError("action must be a non-empty string")

    changes = None

    if action == "UPDATE" and old_doc and new_doc:
        # Calculate semantic diff
        # Ignore audit metadata fields to reduce noise
        try:
            diff = DeepDiff(
                old_doc,
                new_doc,
                ignore_order=True,  # Order changes in arrays aren't meaningful
                exclude_paths=[
                    "root['_id']",
                    "root['created_at']",
                    "root['created_by']",
                    "root['updated_at']",
                    "root['updated_by']",
                ],
            )

            if diff:
                # Serialize diff with custom handler for special types
                diff_dict = diff.to_dict()
                changes_json_str = json.dumps(
                    diff_dict, default=json_serializer
                )
                changes = json.loads(changes_json_str)
            else:
                # No actual changes detected - skip logging to reduce noise
                logger.debug(
                    f"No changes detected for UPDATE on "
                    f"{collection}/{doc_id}, skipping audit log"
                )
                return
        except Exception as e:
            logger.warning(
                f"Error calculating diff for audit log "
                f"({collection}/{doc_id}): {e}",
                exc_info=True,
            )
            # Continue with logging but without changes

    if action == "DELETE" and old_doc and new_doc is None:
        # Store complete snapshot of deleted document for potential recovery
        try:
            old_doc_json_str = json.dumps(old_doc, default=json_serializer)
            changes = {"old_document": json.loads(old_doc_json_str)}
        except Exception as e:
            logger.warning(
                f"Error serializing deleted document for audit log "
                f"({collection}/{doc_id}): {e}",
                exc_info=True,
            )
            # Continue with logging but without changes

    # Create audit log entry
    try:
        log_entry = AuditLogModel(
            date=datetime.now(timezone.utc),
            user=user,
            action=action,
            collection=collection,
            doc_id=str(doc_id),
            changes=changes,
        )

        doc_to_insert = log_entry.model_dump(by_alias=True, exclude={"id"})

        await db.audit_logs.insert_one(doc_to_insert, session=session)

        logger.debug(
            f"Audit log created: {action} on {collection}/{doc_id} "
            f"by {user}"
        )
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        logger.error(
            f"Error creating audit log entry "
            f"({collection}/{doc_id}/{action}): {e}",
            exc_info=True,
        )
        # Re-raise to ensure caller knows audit logging failed
        raise
