import logging
from typing import Optional, Type

import strawberry
from pydantic import BaseModel, ValidationError
from pydantic.alias_generators import to_pascal, to_snake
from strawberry.exceptions import GraphQLError
from strawberry.types import Info

from ..exceptions import (
    DocumentNotFoundException,
    InvalidDocumentIdException,
)
from ..permissions import PermissionDenied, PermissionManager
from ..protocol import TInput, TOutput
from ..service import LazyQL

logger = logging.getLogger(__name__)

# Constants for error messages
DB_CONNECTION_NOT_AVAILABLE = "Database connection not available"
DOCUMENT_ID_REQUIRED = "Document ID is required"


class MutationBuilder:
    """Builds GraphQL Mutation types with CRUD resolvers."""

    def build(
        self,
        name: str,
        collection_name: Optional[str],
        model: Type[BaseModel],
        input_type: Type[TInput],
        output_type: Type[TOutput],
        permission_manager: PermissionManager,
    ):
        """
        Create Mutation type with CRUD operations and permission checks.

        Generated mutations:
        - create: Insert new document with audit logging
        - update: Modify existing document with change tracking
        - delete: Remove document with audit trail
        """
        fields = {}
        if collection_name is None:
            collection_name = model.__name__.lower() + "s"

        # CREATE
        async def resolve_create(info: Info, input: TInput) -> TOutput:
            """Create a new document."""
            try:
                permission_manager.ensure_permission("create", info)

                db = info.context.get("db")
                user = info.context.get("user", "system")

                if not db:
                    raise GraphQLError(DB_CONNECTION_NOT_AVAILABLE)

                service = LazyQL(db, collection_name, model)

                try:
                    data = input.to_pydantic()
                except (AttributeError, ValidationError) as e:
                    logger.error(f"Invalid input data for create: {e}")
                    raise GraphQLError(f"Invalid input data: {e}") from e

                res = await service.create(data, user)
                return output_type.from_pydantic(res)
            except PermissionDenied as e:
                logger.warning(f"Permission denied for create: {e}")
                raise GraphQLError(str(e)) from e
            except Exception as e:
                logger.error(f"Error creating document: {e}", exc_info=True)
                raise GraphQLError(f"Error creating document: {e}") from e

        resolve_create.__annotations__["input"] = input_type
        resolve_create.__annotations__["return"] = output_type

        fields[f"create_{to_snake(name)}"] = strawberry.mutation(
            resolver=resolve_create, name=f"create{to_pascal(name)}"
        )

        # UPDATE
        async def resolve_update(
            info: Info, id: str, input: TInput
        ) -> TOutput:
            """Update an existing document."""
            try:
                permission_manager.ensure_permission("update", info)

                db = info.context.get("db")
                user = info.context.get("user", "system")

                if not db:
                    raise GraphQLError(DB_CONNECTION_NOT_AVAILABLE)

                if not id:
                    raise GraphQLError(DOCUMENT_ID_REQUIRED)

                service = LazyQL(db, collection_name, model)

                try:
                    data = input.to_pydantic()
                except (AttributeError, ValidationError) as e:
                    logger.error(f"Invalid input data for update: {e}")
                    raise GraphQLError(f"Invalid input data: {e}") from e

                try:
                    res = await service.update(id, data, user)
                except InvalidDocumentIdException as e:
                    raise GraphQLError(str(e)) from e
                except DocumentNotFoundException as e:
                    raise GraphQLError(str(e)) from e

                return output_type.from_pydantic(res)
            except PermissionDenied as e:
                logger.warning(f"Permission denied for update: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                logger.error(
                    f"Error updating document {id}: {e}", exc_info=True
                )
                raise GraphQLError(f"Error updating document: {e}") from e

        resolve_update.__annotations__["input"] = input_type
        resolve_update.__annotations__["return"] = output_type

        fields[f"update_{to_snake(name)}"] = strawberry.mutation(
            resolver=resolve_update, name=f"update{to_pascal(name)}"
        )

        # DELETE
        async def resolve_delete(info: Info, id: str) -> bool:
            """Delete document and return success status."""
            try:
                permission_manager.ensure_permission("delete", info)

                db = info.context.get("db")
                user = info.context.get("user", "system")

                if not db:
                    raise GraphQLError(DB_CONNECTION_NOT_AVAILABLE)

                if not id:
                    raise GraphQLError(DOCUMENT_ID_REQUIRED)

                service = LazyQL(db, collection_name, model)

                try:
                    await service.delete(id, user)
                    return True
                except InvalidDocumentIdException as e:
                    raise GraphQLError(str(e)) from e
                except DocumentNotFoundException as e:
                    raise GraphQLError(str(e)) from e
            except PermissionDenied as e:
                logger.warning(f"Permission denied for delete: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                logger.error(
                    f"Error deleting document {id}: {e}", exc_info=True
                )
                raise GraphQLError(f"Error deleting document: {e}") from e

        fields[f"delete_{to_snake(name)}"] = strawberry.mutation(
            resolver=resolve_delete, name=f"delete{to_pascal(name)}"
        )

        # HARD DELETE
        async def resolve_hard_delete(info: Info, id: str) -> bool:
            """Permanently delete document and return success status."""
            try:
                permission_manager.ensure_permission("delete", info)

                db = info.context.get("db")
                user = info.context.get("user", "system")

                if not db:
                    raise GraphQLError(DB_CONNECTION_NOT_AVAILABLE)

                if not id:
                    raise GraphQLError(DOCUMENT_ID_REQUIRED)

                service = LazyQL(db, collection_name, model)

                try:
                    await service.hard_delete(id, user)
                    return True
                except InvalidDocumentIdException as e:
                    raise GraphQLError(str(e)) from e
            except PermissionDenied as e:
                logger.warning(f"Permission denied for hard_delete: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                logger.error(
                    f"Error hard deleting document {id}: {e}", exc_info=True
                )
                raise GraphQLError(f"Error hard deleting document: {e}") from e

        fields[f"hard_delete_{to_snake(name)}"] = strawberry.mutation(
            resolver=resolve_hard_delete,
            name=f"hardDelete{to_pascal(name)}",
        )

        # RESTORE
        async def resolve_restore(info: Info, id: str) -> TOutput:
            """Restore a soft-deleted document."""
            try:
                permission_manager.ensure_permission("update", info)

                db = info.context.get("db")
                user = info.context.get("user", "system")

                if not db:
                    raise GraphQLError(DB_CONNECTION_NOT_AVAILABLE)

                if not id:
                    raise GraphQLError(DOCUMENT_ID_REQUIRED)

                service = LazyQL(db, collection_name, model)

                try:
                    res = await service.restore(id, user)
                except InvalidDocumentIdException as e:
                    raise GraphQLError(str(e)) from e
                except DocumentNotFoundException as e:
                    raise GraphQLError(str(e)) from e

                return output_type.from_pydantic(res)
            except PermissionDenied as e:
                logger.warning(f"Permission denied for restore: {e}")
                raise GraphQLError(str(e)) from e
            except GraphQLError:
                raise
            except Exception as e:
                logger.error(
                    f"Error restoring document {id}: {e}", exc_info=True
                )
                raise GraphQLError(f"Error restoring document: {e}") from e

        resolve_restore.__annotations__["return"] = output_type

        fields[f"restore_{to_snake(name)}"] = strawberry.mutation(
            resolver=resolve_restore, name=f"restore{to_pascal(name)}"
        )

        # Create Mutation class
        _Mutation = type(f"{to_pascal(name)}Mutation", (), fields)
        return strawberry.type(_Mutation)
