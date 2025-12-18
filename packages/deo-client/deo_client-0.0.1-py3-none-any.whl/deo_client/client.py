"""Main client implementation for the deo document database."""

import json
from typing import Any, Dict, List, Optional, TypeVar
from urllib.parse import urlencode

import requests

from .types import (
    CreateCollectionRequest,
    CreateDatabaseRequest,
    DeoResponse,
    Document,
    ListDocumentsOptions,
)

T = TypeVar("T")


class DeoError(Exception):
    """Exception raised for deo API errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class Collection:
    """Collection class for document operations."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def _fetch(self, url: str, method: str = "GET", **kwargs: Any) -> DeoResponse[Any]:
        """Internal fetch method with error handling."""
        try:
            response = requests.request(method, url, **kwargs)

            data = response.json()
            if not isinstance(data, dict) or "success" not in data:
                raise DeoError(
                    f"Invalid JSON structure received from {url}: "
                    f"{response.status_code} {response.reason}. "
                    f"Raw response: {response.text}"
                )

            deo_response = DeoResponse(**data)
            if not deo_response.success:
                raise DeoError(deo_response.message or "An unknown error occurred.")

            return deo_response

        except requests.RequestException as e:
            raise DeoError(f"Request failed: {str(e)}") from None
        except json.JSONDecodeError as e:
            raise DeoError(f"Failed to parse JSON response from {url}: {str(e)}") from None

    def create_document(self, document: Dict[str, Any]) -> DeoResponse[Document]:
        """Create a new document in the collection."""
        response = self._fetch(
            f"{self.base_url}/documents",
            method="POST",
            headers={"Content-Type": "application/json"},
            json=document,
        )
        return response

    def list_documents(
        self, options: Optional[ListDocumentsOptions] = None
    ) -> DeoResponse[List[Document]]:
        """List documents in the collection with optional filtering and sorting."""
        params = {}

        if options:
            if options.filters:
                for key, value in options.filters.items():
                    params[f"filter[{key}]"] = value

            if options.sort_by:
                params["sort_by"] = options.sort_by
                if options.order:
                    params["order"] = options.order

            if options.limit is not None:
                params["limit"] = str(options.limit)

            if options.offset is not None:
                params["offset"] = str(options.offset)

        query_string = urlencode(params) if params else ""
        url = f"{self.base_url}/documents"
        if query_string:
            url += f"?{query_string}"

        response = self._fetch(url)
        return response

    def read_document(self, document_id: str) -> DeoResponse[Document]:
        """Read a document by ID."""
        response = self._fetch(f"{self.base_url}/documents/{document_id}")
        return response

    def update_document(
        self, document_id: str, document: Dict[str, Any]
    ) -> DeoResponse[Document]:
        """Update a document by ID."""
        response = self._fetch(
            f"{self.base_url}/documents/{document_id}",
            method="PUT",
            headers={"Content-Type": "application/json"},
            json=document,
        )
        return response

    def delete_document(self, document_id: str) -> DeoResponse[None]:
        """Delete a document by ID."""
        response = self._fetch(
            f"{self.base_url}/documents/{document_id}",
            method="DELETE",
        )
        return response


class Database:
    """Database class for collection operations."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self._collections_cache: Dict[str, Collection] = {}

    @property
    def collections(self) -> Dict[str, Collection]:
        """Dynamic collection access via dictionary-like interface."""
        return _CollectionProxy(self.base_url, self._collections_cache)

    def _fetch(self, url: str, method: str = "GET", **kwargs: Any) -> DeoResponse[Any]:
        """Internal fetch method with error handling."""
        try:
            response = requests.request(method, url, **kwargs)

            data = response.json()
            if not isinstance(data, dict) or "success" not in data:
                raise DeoError(
                    f"Invalid JSON structure received from {url}: "
                    f"{response.status_code} {response.reason}. "
                    f"Raw response: {response.text}"
                )

            deo_response = DeoResponse(**data)
            if not deo_response.success:
                raise DeoError(deo_response.message or "An unknown error occurred.")

            return deo_response

        except requests.RequestException as e:
            raise DeoError(f"Request failed: {str(e)}") from None
        except json.JSONDecodeError as e:
            raise DeoError(f"Failed to parse JSON response from {url}: {str(e)}") from None

    def create_collection(self, collection_name: str) -> DeoResponse[None]:
        """Create a new collection in the database."""
        request = CreateCollectionRequest(collection_name)
        response = self._fetch(
            f"{self.base_url}/collections",
            method="POST",
            headers={"Content-Type": "application/json"},
            json={"collection_name": request.collection_name},
        )
        return response

    def list_collections(self) -> DeoResponse[List[str]]:
        """List all collections in the database."""
        response = self._fetch(f"{self.base_url}/collections")
        return response

    def delete_collection(self, collection_name: str) -> DeoResponse[None]:
        """Delete a collection from the database."""
        response = self._fetch(
            f"{self.base_url}/collections/{collection_name}",
            method="DELETE",
        )
        return response


class _CollectionProxy(Dict[str, Collection]):
    """Proxy class for dynamic collection access."""

    def __init__(self, base_url: str, cache: Dict[str, Collection]) -> None:
        super().__init__()
        self.base_url = base_url
        self._cache = cache

    def __getitem__(self, name: str) -> Collection:
        if name not in self._cache:
            self._cache[name] = Collection(f"{self.base_url}/collections/{name}")
        return self._cache[name]

    def __getattr__(self, name: str) -> Collection:
        return self[name]


class DeoClient:
    """Main client class for interacting with the deo database."""

    def __init__(self, host: str = "http://localhost:6741") -> None:
        self.base_url = f"{host}/api"
        self._databases_cache: Dict[str, Database] = {}

    @property
    def dbs(self) -> Dict[str, Database]:
        """Dynamic database access via dictionary-like interface."""
        return _DatabaseProxy(self.base_url, self._databases_cache)

    def _fetch(self, url: str, method: str = "GET", **kwargs: Any) -> DeoResponse[Any]:
        """Internal fetch method with error handling."""
        try:
            response = requests.request(method, url, **kwargs)

            data = response.json()
            if not isinstance(data, dict) or "success" not in data:
                raise DeoError(
                    f"Invalid JSON structure received from {url}: "
                    f"{response.status_code} {response.reason}. "
                    f"Raw response: {response.text}"
                )

            deo_response = DeoResponse(**data)
            if not deo_response.success:
                raise DeoError(deo_response.message or "An unknown error occurred.")

            return deo_response

        except requests.RequestException as e:
            raise DeoError(f"Request failed: {str(e)}") from None
        except json.JSONDecodeError as e:
            raise DeoError(f"Failed to parse JSON response from {url}: {str(e)}") from None

    def create_database(self, db_name: str) -> DeoResponse[None]:
        """Create a new database."""
        request = CreateDatabaseRequest(db_name)
        response = self._fetch(
            f"{self.base_url}/dbs",
            method="POST",
            headers={"Content-Type": "application/json"},
            json={"db_name": request.db_name},
        )
        return response

    def list_databases(self) -> DeoResponse[List[str]]:
        """List all databases."""
        response = self._fetch(f"{self.base_url}/dbs")
        return response

    def delete_database(self, db_name: str) -> DeoResponse[None]:
        """Delete a database."""
        response = self._fetch(
            f"{self.base_url}/dbs/{db_name}",
            method="DELETE",
        )
        return response


class _DatabaseProxy(Dict[str, Database]):
    """Proxy class for dynamic database access."""

    def __init__(self, base_url: str, cache: Dict[str, Database]) -> None:
        super().__init__()
        self.base_url = base_url
        self._cache = cache

    def __getitem__(self, name: str) -> Database:
        if name not in self._cache:
            self._cache[name] = Database(f"{self.base_url}/dbs/{name}")
        return self._cache[name]

    def __getattr__(self, name: str) -> Database:
        return self[name]
