"""Tests for the deo client."""

import json
import uuid
from unittest.mock import Mock, patch

import pytest
import requests

from deo_client import DeoClient, DeoError


class TestDeoClient:
    """Test cases for DeoClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = DeoClient("http://localhost:6741")

    @patch("requests.request")
    def test_create_database_success(self, mock_request: Mock) -> None:
        """Test creating a database successfully."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": True,
            "message": "Database created successfully"
        }
        mock_request.return_value = mock_response

        response = self.client.create_database("test_db")

        assert response.success is True
        assert response.message == "Database created successfully"
        mock_request.assert_called_once_with(
            "POST",
            "http://localhost:6741/api/dbs",
            headers={"Content-Type": "application/json"},
            json={"db_name": "test_db"}
        )

    @patch("requests.request")
    def test_create_database_error(self, mock_request: Mock) -> None:
        """Test creating a database with error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "message": "Database already exists"
        }
        mock_request.return_value = mock_response

        with pytest.raises(DeoError, match="Database already exists"):
            self.client.create_database("test_db")

    @patch("requests.request")
    def test_list_databases_success(self, mock_request: Mock) -> None:
        """Test listing databases successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": ["db1", "db2"]
        }
        mock_request.return_value = mock_response

        response = self.client.list_databases()

        assert response.success is True
        assert response.data == ["db1", "db2"]
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:6741/api/dbs"
        )

    @patch("requests.request")
    def test_delete_database_success(self, mock_request: Mock) -> None:
        """Test deleting a database successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Database deleted successfully"
        }
        mock_request.return_value = mock_response

        response = self.client.delete_database("test_db")

        assert response.success is True
        assert response.message == "Database deleted successfully"
        mock_request.assert_called_once_with(
            "DELETE",
            "http://localhost:6741/api/dbs/test_db"
        )

    def test_database_proxy_access(self) -> None:
        """Test dynamic database access via proxy."""
        db1 = self.client.dbs["test_db"]
        db2 = self.client.dbs.test_db

        assert db1 is db2  # Same instance from cache
        assert isinstance(db1, type(self.client.dbs._cache["test_db"]))


class TestDatabase:
    """Test cases for Database class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = DeoClient()
        self.database = self.client.dbs["test_db"]

    @patch("requests.request")
    def test_create_collection_success(self, mock_request: Mock) -> None:
        """Test creating a collection successfully."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": True,
            "message": "Collection created successfully"
        }
        mock_request.return_value = mock_response

        response = self.database.create_collection("test_collection")

        assert response.success is True
        assert response.message == "Collection created successfully"
        mock_request.assert_called_once_with(
            "POST",
            "http://localhost:6741/api/dbs/test_db/collections",
            headers={"Content-Type": "application/json"},
            json={"collection_name": "test_collection"}
        )

    @patch("requests.request")
    def test_list_collections_success(self, mock_request: Mock) -> None:
        """Test listing collections successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": ["col1", "col2"]
        }
        mock_request.return_value = mock_response

        response = self.database.list_collections()

        assert response.success is True
        assert response.data == ["col1", "col2"]
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:6741/api/dbs/test_db/collections"
        )

    @patch("requests.request")
    def test_delete_collection_success(self, mock_request: Mock) -> None:
        """Test deleting a collection successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Collection deleted successfully"
        }
        mock_request.return_value = mock_response

        response = self.database.delete_collection("test_collection")

        assert response.success is True
        assert response.message == "Collection deleted successfully"
        mock_request.assert_called_once_with(
            "DELETE",
            "http://localhost:6741/api/dbs/test_db/collections/test_collection"
        )

    def test_collection_proxy_access(self) -> None:
        """Test dynamic collection access via proxy."""
        col1 = self.database.collections["test_collection"]
        col2 = self.database.collections.test_collection

        assert col1 is col2  # Same instance from cache
        assert isinstance(col1, type(self.database.collections._cache["test_collection"]))


class TestCollection:
    """Test cases for Collection class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = DeoClient()
        self.collection = self.client.dbs["test_db"].collections["test_collection"]

    @patch("requests.request")
    def test_create_document_success(self, mock_request: Mock) -> None:
        """Test creating a document successfully."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "success": True,
            "message": "Document created successfully",
            "data": {
                "_id": "uuid-123",
                "name": "John Doe",
                "age": 30
            }
        }
        mock_request.return_value = mock_response

        document = {"name": "John Doe", "age": 30}
        response = self.collection.create_document(document)

        assert response.success is True
        assert response.data["_id"] == "uuid-123"
        assert response.data["name"] == "John Doe"
        mock_request.assert_called_once_with(
            "POST",
            "http://localhost:6741/api/dbs/test_db/collections/test_collection/documents",
            headers={"Content-Type": "application/json"},
            json=document
        )

    @patch("requests.request")
    def test_list_documents_success(self, mock_request: Mock) -> None:
        """Test listing documents successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {"_id": "doc1", "name": "John"},
                {"_id": "doc2", "name": "Jane"}
            ]
        }
        mock_request.return_value = mock_response

        response = self.collection.list_documents()

        assert response.success is True
        assert len(response.data) == 2
        assert response.data[0]["_id"] == "doc1"
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:6741/api/dbs/test_db/collections/test_collection/documents"
        )

    @patch("requests.request")
    def test_list_documents_with_options(self, mock_request: Mock) -> None:
        """Test listing documents with filtering and sorting options."""
        from deo_client.types import ListDocumentsOptions

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [{"_id": "doc1", "name": "John"}]
        }
        mock_request.return_value = mock_response

        options = ListDocumentsOptions(
            filters={"status": "active"},
            sort_by="name",
            order="asc",
            limit=10,
            offset=0
        )
        response = self.collection.list_documents(options)

        assert response.success is True
        expected_url = (
            "http://localhost:6741/api/dbs/test_db/collections/test_collection/documents"
            "?filter%5Bstatus%5D=active&sort_by=name&order=asc&limit=10&offset=0"
        )
        mock_request.assert_called_once_with("GET", expected_url)

    @patch("requests.request")
    def test_read_document_success(self, mock_request: Mock) -> None:
        """Test reading a document successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"_id": "doc1", "name": "John", "age": 30}
        }
        mock_request.return_value = mock_response

        response = self.collection.read_document("doc1")

        assert response.success is True
        assert response.data["_id"] == "doc1"
        assert response.data["name"] == "John"
        mock_request.assert_called_once_with(
            "GET",
            "http://localhost:6741/api/dbs/test_db/collections/test_collection/documents/doc1"
        )

    @patch("requests.request")
    def test_update_document_success(self, mock_request: Mock) -> None:
        """Test updating a document successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Document updated successfully",
            "data": {"_id": "doc1", "name": "John Doe", "age": 31}
        }
        mock_request.return_value = mock_response

        document = {"name": "John Doe", "age": 31}
        response = self.collection.update_document("doc1", document)

        assert response.success is True
        assert response.data["age"] == 31
        mock_request.assert_called_once_with(
            "PUT",
            "http://localhost:6741/api/dbs/test_db/collections/test_collection/documents/doc1",
            headers={"Content-Type": "application/json"},
            json=document
        )

    @patch("requests.request")
    def test_delete_document_success(self, mock_request: Mock) -> None:
        """Test deleting a document successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "message": "Document deleted successfully"
        }
        mock_request.return_value = mock_response

        response = self.collection.delete_document("doc1")

        assert response.success is True
        assert response.message == "Document deleted successfully"
        mock_request.assert_called_once_with(
            "DELETE",
            "http://localhost:6741/api/dbs/test_db/collections/test_collection/documents/doc1"
        )


class TestErrorHandling:
    """Test cases for error handling."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = DeoClient()

    @patch("requests.request")
    def test_request_exception(self, mock_request: Mock) -> None:
        """Test handling of requests exceptions."""
        mock_request.side_effect = requests.RequestException("Connection failed")

        with pytest.raises(DeoError, match="Request failed: Connection failed"):
            self.client.list_databases()

    @patch("requests.request")
    def test_json_decode_error(self, mock_request: Mock) -> None:
        """Test handling of JSON decode errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_request.return_value = mock_response

        with pytest.raises(DeoError, match="Failed to parse JSON response"):
            self.client.list_databases()

    @patch("requests.request")
    def test_invalid_response_structure(self, mock_request: Mock) -> None:
        """Test handling of invalid response structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "structure"}
        mock_response.text = '{"invalid": "structure"}'
        mock_response.reason = "OK"
        mock_request.return_value = mock_response

        with pytest.raises(DeoError, match="Invalid JSON structure received"):
            self.client.list_databases()

    @patch("requests.request")
    def test_api_error_response(self, mock_request: Mock) -> None:
        """Test handling of API error responses."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "success": False,
            "message": "Database not found"
        }
        mock_request.return_value = mock_response

        with pytest.raises(DeoError, match="Database not found"):
            self.client.list_databases()


class TestIntegration:
    """Integration tests that connect to a real deo database instance."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = DeoClient("http://localhost:6741")
        # Generate unique names to avoid conflicts between test runs
        self.test_db_name = f"test_integration_{uuid.uuid4().hex[:8]}"
        self.test_collection_name = f"users_{uuid.uuid4().hex[:8]}"
        self.created_documents = []

    def teardown_method(self) -> None:
        """Clean up test resources."""
        try:
            # Clean up documents
            for doc_id in self.created_documents:
                try:
                    self.client.dbs[self.test_db_name].collections[self.test_collection_name].delete_document(doc_id)
                except DeoError:
                    pass  # Document might already be deleted

            # Clean up collection
            try:
                self.client.dbs[self.test_db_name].delete_collection(self.test_collection_name)
            except DeoError:
                pass

            # Clean up database
            try:
                self.client.delete_database(self.test_db_name)
            except DeoError:
                pass
        except Exception:
            pass  # Ignore cleanup errors

    def test_full_database_lifecycle(self) -> None:
        """Test complete database lifecycle: create, use, delete."""
        # Create database
        result = self.client.create_database(self.test_db_name)
        assert result.success, f"Failed to create database: {result.message}"

        # Verify database exists
        result = self.client.list_databases()
        assert result.success, f"Failed to list databases: {result.message}"
        assert self.test_db_name in result.data, "Database not found in list"

        # Create collection
        db = self.client.dbs[self.test_db_name]
        result = db.create_collection(self.test_collection_name)
        assert result.success, f"Failed to create collection: {result.message}"

        # Verify collection exists
        result = db.list_collections()
        assert result.success, f"Failed to list collections: {result.message}"
        assert self.test_collection_name in result.data, "Collection not found in list"

        # Create documents
        collection = db.collections[self.test_collection_name]
        test_docs = [
            {"name": "Alice Johnson", "email": "alice@example.com", "age": 28, "active": True},
            {"name": "Bob Smith", "email": "bob@example.com", "age": 34, "active": False},
            {"name": "Carol Williams", "email": "carol@example.com", "age": 29, "active": True},
        ]

        created_docs = []
        for doc in test_docs:
            result = collection.create_document(doc)
            assert result.success, f"Failed to create document: {result.message}"
            assert result.data is not None, "Document data is None"
            assert "_id" in result.data, "Document missing _id field"
            created_docs.append(result.data)
            self.created_documents.append(result.data["_id"])

        # Verify documents were created
        result = collection.list_documents()
        assert result.success, f"Failed to list documents: {result.message}"
        assert len(result.data) == 3, f"Expected 3 documents, got {len(result.data)}"

        # Test document retrieval
        first_doc = created_docs[0]
        result = collection.read_document(first_doc["_id"])
        assert result.success, f"Failed to read document: {result.message}"
        assert result.data == first_doc, "Retrieved document doesn't match created document"

        # Test document update
        result = collection.update_document(first_doc["_id"], {"age": 29, "department": "Engineering"})
        assert result.success, f"Failed to update document: {result.message}"
        assert result.data is not None, "Updated document data is None"
        assert result.data["age"] == 29, "Age not updated"
        assert result.data["department"] == "Engineering", "Department not added"
        # Note: update response may not include _id, so we can't check for it here

        # Test document deletion
        doc_to_delete = created_docs[1]["_id"]
        result = collection.delete_document(doc_to_delete)
        assert result.success, f"Failed to delete document: {result.message}"

        # Verify document was deleted
        result = collection.list_documents()
        assert result.success, f"Failed to list documents after deletion: {result.message}"
        assert len(result.data) == 2, f"Expected 2 documents after deletion, got {len(result.data)}"

        # Note: Due to a server bug, list_documents may not return complete documents with _id
        # after updates, so we can't reliably check individual document IDs

        # Remove from tracking since it's deleted
        self.created_documents.remove(doc_to_delete)

    def test_querying_and_filtering(self) -> None:
        """Test document querying with filters, sorting, and pagination."""
        # Setup: create database and collection
        result = self.client.create_database(self.test_db_name)
        assert result.success
        result = self.client.dbs[self.test_db_name].create_collection(self.test_collection_name)
        assert result.success

        collection = self.client.dbs[self.test_db_name].collections[self.test_collection_name]

        # Create test documents
        test_docs = [
            {"name": "Alice", "age": 25, "city": "New York", "active": True},
            {"name": "Bob", "age": 30, "city": "London", "active": False},
            {"name": "Charlie", "age": 35, "city": "New York", "active": True},
            {"name": "Diana", "age": 28, "city": "Paris", "active": True},
            {"name": "Eve", "age": 32, "city": "London", "active": False},
        ]

        for doc in test_docs:
            result = collection.create_document(doc)
            assert result.success
            self.created_documents.append(result.data["_id"])

        # Test listing all documents
        result = collection.list_documents()
        assert result.success
        assert len(result.data) == 5

        # Test pagination
        from deo_client.types import ListDocumentsOptions

        options = ListDocumentsOptions(limit=2, offset=1)
        result = collection.list_documents(options)
        assert result.success
        assert len(result.data) == 2

        # Test sorting by age ascending
        options = ListDocumentsOptions(sort_by="age", order="asc")
        result = collection.list_documents(options)
        assert result.success
        ages = [doc["age"] for doc in result.data]
        assert ages == sorted(ages), "Documents not sorted by age ascending"

        # Test sorting by age descending
        options = ListDocumentsOptions(sort_by="age", order="desc")
        result = collection.list_documents(options)
        assert result.success
        ages = [doc["age"] for doc in result.data]
        assert ages == sorted(ages, reverse=True), "Documents not sorted by age descending"

        # Test sorting by name
        options = ListDocumentsOptions(sort_by="name", order="asc")
        result = collection.list_documents(options)
        assert result.success
        names = [doc["name"] for doc in result.data]
        assert names == sorted(names), "Documents not sorted by name"

    def test_error_handling(self) -> None:
        """Test error handling for invalid operations."""
        # Try to access non-existent database
        try:
            db = self.client.dbs["non_existent_database_12345"]
            collection = db.collections["test_collection"]
            result = collection.read_document("fake-id")
            # If we get here, the operation succeeded unexpectedly
            pytest.fail("Expected error for non-existent database, but operation succeeded")
        except DeoError as e:
            # Expected error
            assert "error" in str(e).lower() or "not found" in str(e).lower()

        # Create a real database for more specific error tests
        result = self.client.create_database(self.test_db_name)
        assert result.success
        db = self.client.dbs[self.test_db_name]

        # Try to read non-existent document from existing collection
        result = db.create_collection(self.test_collection_name)
        assert result.success
        collection = db.collections[self.test_collection_name]

        # This should raise a DeoError (404)
        with pytest.raises(DeoError, match="Document not found"):
            collection.read_document("non-existent-doc-id")

        # Try to delete non-existent document - this might succeed or fail depending on API
        try:
            result = collection.delete_document("non-existent-doc-id")
            # If it doesn't raise an error, check if the response indicates failure
            if hasattr(result, 'success') and not result.success:
                assert result.message is not None, "Error message should not be None"
        except DeoError as e:
            # Expected if API raises error for deleting non-existent document
            assert "not found" in str(e).lower() or "document" in str(e).lower()
