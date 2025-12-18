"""Collection resource for interacting with the Mielto Collections API."""

import base64
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

from mielto.client.base import AsyncBaseClient, BaseClient
from mielto.types.collection import (
    Collection,
    CollectionCreate,
    CollectionUpdate,
    SearchRequest,
    SearchResponse,
)
from mielto.types.upload import FileUpload, UploadRequest, UploadResponse


class Collections:
    """Synchronous Collections resource."""

    def __init__(self, client: BaseClient):
        """Initialize the Collections resource.

        Args:
            client: Base HTTP client instance
        """
        self._client = client

    def create(self, collection_data: Union[CollectionCreate, dict]) -> Collection:
        """Create a new collection.

        Args:
            collection_data: Collection data to create

        Returns:
            Created collection

        Example:
            ```python
            collection = client.collections.create(
                CollectionCreate(
                    name="My Documents",
                    description="Personal document collection",
                    store_type="pgvector",
                    tags=["personal", "documents"]
                )
            )
            ```
        """
        if isinstance(collection_data, CollectionCreate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = self._client.post("/collections", json_data=payload)
        return Collection(**response)

    def get(self, collection_id: str) -> Collection:
        """Get a specific collection by ID.

        Args:
            collection_id: Collection ID

        Returns:
            Collection object

        Example:
            ```python
            collection = client.collections.get("col_123")
            print(collection.name)
            ```
        """
        response = self._client.get(f"/collections/{collection_id}")
        return Collection(**response)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        visibility: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List collections with filtering and pagination.

        Args:
            skip: Number of collections to skip
            limit: Number of collections to return (1-1000)
            status: Filter by collection status
            visibility: Filter by visibility ('public' or 'private')
            search: Search term for name or description
            tags: Comma-separated list of tags to filter by

        Returns:
            Dict with collections data and total count

        Example:
            ```python
            result = client.collections.list(
                limit=20,
                status="active",
                tags="personal,work"
            )
            for collection in result["data"]:
                print(collection.name)
            ```
        """
        params = {
            "skip": skip,
            "limit": limit,
        }
        if status:
            params["status"] = status
        if visibility:
            params["visibility"] = visibility
        if search:
            params["search"] = search
        if tags:
            params["tags"] = tags

        return self._client.get("/collections", params=params)

    def update(self, collection_id: str, collection_data: Union[CollectionUpdate, dict]) -> Collection:
        """Update an existing collection.

        Args:
            collection_id: Collection ID
            collection_data: Updated collection data

        Returns:
            Updated collection

        Example:
            ```python
            updated = client.collections.update(
                "col_123",
                CollectionUpdate(
                    name="Updated Name",
                    tags=["updated", "documents"]
                )
            )
            ```
        """
        if isinstance(collection_data, CollectionUpdate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = self._client.put(f"/collections/{collection_id}", json_data=payload)
        return Collection(**response)

    def delete(self, collection_id: str) -> dict:
        """Delete a collection (async operation).

        This initiates an asynchronous deletion process.

        Args:
            collection_id: Collection ID

        Returns:
            Deletion status with job_id

        Example:
            ```python
            result = client.collections.delete("col_123")
            print(f"Deletion job: {result['job_id']}")
            ```
        """
        return self._client.delete(f"/collections/{collection_id}")

    def search(self, search_request: Union[SearchRequest, dict]) -> SearchResponse:
        """Search within a collection.

        Args:
            search_request: Search parameters

        Returns:
            SearchResponse with results

        Example:
            ```python
            results = client.collections.search(
                SearchRequest(
                    query="artificial intelligence",
                    collection_id="col_123",
                    search_type="hybrid",
                    max_results=10
                )
            )
            for result in results.results:
                print(f"{result.content[:100]}... (score: {result.score})")
            ```
        """
        if isinstance(search_request, SearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = self._client.post("/collections/search", json_data=payload)
        return SearchResponse(**response)

    def insert(
        self,
        collection_id: str,
        content: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        file_obj: Optional[BinaryIO] = None,
        urls: Optional[List[str]] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
    ) -> UploadResponse:
        """Insert content into a collection.

        This method supports multiple input types:
        - Raw text content
        - File path
        - File object (opened file)
        - URLs

        Args:
            collection_id: Collection ID
            content: Raw text content to insert
            file_path: Path to file to upload
            file_obj: File object to upload
            urls: List of URLs to download and insert
            label: Custom label for the content
            description: Description of the content
            metadata: Additional metadata
            ingest: Whether to ingest content into vector database
            reader: Reader configuration for file processing

        Returns:
            UploadResponse with upload results

        Examples:
            ```python
            # Insert raw text
            result = client.collections.insert(
                collection_id="col_123",
                content="This is my text content",
                label="Quick Note"
            )

            # Insert from file path
            result = client.collections.insert(
                collection_id="col_123",
                file_path="document.pdf",
                reader="native"
            )

            # Insert from file object
            with open("document.pdf", "rb") as f:
                result = client.collections.insert(
                    collection_id="col_123",
                    file_obj=f,
                    label="document.pdf"
                )

            # Insert from URLs
            result = client.collections.insert(
                collection_id="col_123",
                urls=["https://example.com/doc.pdf"],
                reader="native"
            )
            ```
        """
        # Prepare the request data
        files_list = []

        # Handle file path
        if file_path:
            file_path = Path(file_path)
            with open(file_path, "rb") as f:
                file_content = f.read()
                encoded = base64.b64encode(file_content).decode("utf-8")
                files_list.append(
                    FileUpload(
                        file=encoded,
                        label=label or file_path.name,
                    )
                )

        # Handle file object
        elif file_obj:
            file_content = file_obj.read()
            encoded = base64.b64encode(file_content).decode("utf-8")
            files_list.append(
                FileUpload(
                    file=encoded,
                    label=label or getattr(file_obj, "name", "file"),
                )
            )

        # Prepare upload request
        upload_req = UploadRequest(
            collection_id=collection_id,
            content_type="text" if content else "url" if urls else "file",
            files=files_list if files_list else None,
            content=content,
            urls=urls,
            label=label,
            description=description,
            metadata=metadata,
            ingest=ingest,
            reader=reader,
        )

        payload = upload_req.model_dump(exclude_none=True)
        response = self._client.post("/upload", json_data=payload)
        return UploadResponse(**response)


class AsyncCollections:
    """Asynchronous Collections resource."""

    def __init__(self, client: AsyncBaseClient):
        """Initialize the async Collections resource.

        Args:
            client: Async base HTTP client instance
        """
        self._client = client

    async def create(self, collection_data: Union[CollectionCreate, dict]) -> Collection:
        """Create a new collection asynchronously."""
        if isinstance(collection_data, CollectionCreate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = await self._client.post("/collections", json_data=payload)
        return Collection(**response)

    async def get(self, collection_id: str) -> Collection:
        """Get a specific collection by ID asynchronously."""
        response = await self._client.get(f"/collections/{collection_id}")
        return Collection(**response)

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        visibility: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List collections with filtering and pagination asynchronously."""
        params = {
            "skip": skip,
            "limit": limit,
        }
        if status:
            params["status"] = status
        if visibility:
            params["visibility"] = visibility
        if search:
            params["search"] = search
        if tags:
            params["tags"] = tags

        return await self._client.get("/collections", params=params)

    async def update(self, collection_id: str, collection_data: Union[CollectionUpdate, dict]) -> Collection:
        """Update an existing collection asynchronously."""
        if isinstance(collection_data, CollectionUpdate):
            payload = collection_data.model_dump(exclude_none=True)
        else:
            payload = collection_data

        response = await self._client.put(f"/collections/{collection_id}", json_data=payload)
        return Collection(**response)

    async def delete(self, collection_id: str) -> dict:
        """Delete a collection asynchronously."""
        return await self._client.delete(f"/collections/{collection_id}")

    async def search(self, search_request: Union[SearchRequest, dict]) -> SearchResponse:
        """Search within a collection asynchronously."""
        if isinstance(search_request, SearchRequest):
            payload = search_request.model_dump(exclude_none=True)
        else:
            payload = search_request

        response = await self._client.post("/collections/search", json_data=payload)
        return SearchResponse(**response)

    async def insert(
        self,
        collection_id: str,
        content: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        file_obj: Optional[BinaryIO] = None,
        urls: Optional[List[str]] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
    ) -> UploadResponse:
        """Insert content into a collection asynchronously."""
        files_list = []

        if file_path:
            file_path = Path(file_path)
            with open(file_path, "rb") as f:
                file_content = f.read()
                encoded = base64.b64encode(file_content).decode("utf-8")
                files_list.append(
                    FileUpload(
                        file=encoded,
                        label=label or file_path.name,
                    )
                )

        elif file_obj:
            file_content = file_obj.read()
            encoded = base64.b64encode(file_content).decode("utf-8")
            files_list.append(
                FileUpload(
                    file=encoded,
                    label=label or getattr(file_obj, "name", "file"),
                )
            )

        upload_req = UploadRequest(
            collection_id=collection_id,
            content_type="text" if content else "url" if urls else "file",
            files=files_list if files_list else None,
            content=content,
            urls=urls,
            label=label,
            description=description,
            metadata=metadata,
            ingest=ingest,
            reader=reader,
        )

        payload = upload_req.model_dump(exclude_none=True)
        response = await self._client.post("/upload", json_data=payload)
        return UploadResponse(**response)
