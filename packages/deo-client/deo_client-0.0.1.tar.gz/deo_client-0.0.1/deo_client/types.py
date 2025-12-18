"""Type definitions for the deo client."""

from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class DeoResponse(Generic[T]):
    """Response wrapper for deo API calls."""

    success: bool
    message: Optional[str]
    data: Optional[T]

    def __init__(
        self,
        success: bool,
        message: Optional[str] = None,
        data: Optional[T] = None,
    ) -> None:
        self.success = success
        self.message = message
        self.data = data


class Document(Dict[str, Any]):
    """Base document type with required _id field."""

    _id: str

    def __init__(self, _id: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self["_id"] = _id
        self._id = _id


class ListDocumentsOptions:
    """Options for listing documents with filtering and sorting."""

    filters: Optional[Dict[str, str]]
    sort_by: Optional[str]
    order: Optional[str]  # "asc" or "desc"
    limit: Optional[int]
    offset: Optional[int]

    def __init__(
        self,
        filters: Optional[Dict[str, str]] = None,
        sort_by: Optional[str] = None,
        order: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> None:
        self.filters = filters
        self.sort_by = sort_by
        self.order = order
        self.limit = limit
        self.offset = offset


class CreateDatabaseRequest:
    """Request payload for creating a database."""

    db_name: str

    def __init__(self, db_name: str) -> None:
        self.db_name = db_name


class CreateCollectionRequest:
    """Request payload for creating a collection."""

    collection_name: str

    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name
