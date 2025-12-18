"""Collection resource for interacting with the Mielto Collections API."""

import base64
import mimetypes
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

from tqdm import tqdm

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
        file_base64: Optional[str] = None,
        urls: Optional[List[str]] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mimetype: Optional[str] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
    ) -> UploadResponse:
        """Insert content into a collection.

        This method supports multiple input types:
        - Raw text content
        - File path (with automatic mimetype detection)
        - File object (opened file)
        - Base64 encoded file content
        - URLs

        Args:
            collection_id: Collection ID
            content: Raw text content to insert
            file_path: Path to file to upload
            file_obj: File object to upload
            file_base64: Base64 encoded file content (alternative to file_path/file_obj)
            urls: List of URLs to download and insert
            label: Custom label for the content
            description: Description of the content
            metadata: Additional metadata
            mimetype: MIME type of the file (auto-detected if not provided)
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

            # Insert from file path (mimetype auto-detected)
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
                    label="document.pdf",
                    mimetype="application/pdf"
                )

            # Insert from base64
            result = client.collections.insert(
                collection_id="col_123",
                file_base64="base64_encoded_content...",
                label="document.pdf",
                mimetype="application/pdf"
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

                # Auto-detect mimetype if not provided
                detected_mimetype = mimetype
                if not detected_mimetype:
                    detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                files_list.append(
                    FileUpload(
                        file=encoded,
                        label=label or file_path.name,
                        mimetype=detected_mimetype,
                    )
                )

        # Handle file object
        elif file_obj:
            file_content = file_obj.read()
            encoded = base64.b64encode(file_content).decode("utf-8")

            # Try to detect mimetype from file object name
            detected_mimetype = mimetype
            if not detected_mimetype and hasattr(file_obj, "name"):
                detected_mimetype, _ = mimetypes.guess_type(file_obj.name)

            files_list.append(
                FileUpload(
                    file=encoded,
                    label=label or getattr(file_obj, "name", "file"),
                    mimetype=detected_mimetype,
                )
            )

        # Handle base64 directly
        elif file_base64:
            files_list.append(
                FileUpload(
                    file=file_base64,
                    label=label or "file",
                    mimetype=mimetype,
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

    def insert_directory(
        self,
        collection_id: str,
        directory_path: Union[str, Path],
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
        batch_size: int = 10,
        show_progress: bool = True,
    ) -> List[UploadResponse]:
        """Insert all files from a directory into a collection.

        Args:
            collection_id: Collection ID
            directory_path: Path to directory containing files
            recursive: Whether to recursively traverse subdirectories
            file_extensions: List of file extensions to include (e.g., ['.pdf', '.txt'])
            exclude_patterns: List of filename patterns to exclude (e.g., ['*.tmp', '.DS_Store'])
            metadata: Additional metadata to attach to all files
            ingest: Whether to ingest content into vector database
            reader: Reader configuration for file processing
            batch_size: Number of files to upload per batch
            show_progress: Whether to show progress bar (default: True)

        Returns:
            List of UploadResponse objects, one per batch

        Examples:
            ```python
            # Upload all files from a directory
            results = client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents"
            )

            # Upload only PDFs, non-recursively
            results = client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents",
                recursive=False,
                file_extensions=['.pdf']
            )

            # Upload with exclusions
            results = client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents",
                exclude_patterns=['*.tmp', '.DS_Store', '__pycache__']
            )
            ```
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        # Collect all files
        files_to_upload = self._collect_files(
            directory=directory,
            recursive=recursive,
            file_extensions=file_extensions,
            exclude_patterns=exclude_patterns,
        )

        if not files_to_upload:
            return []

        # Upload in batches with progress bar
        responses = []
        total_batches = (len(files_to_upload) + batch_size - 1) // batch_size

        # Create progress bars
        batch_pbar = tqdm(
            total=total_batches,
            desc="Uploading batches",
            unit="batch",
            disable=not show_progress,
        )
        file_pbar = tqdm(
            total=len(files_to_upload),
            desc="Processing files",
            unit="file",
            disable=not show_progress,
        )

        try:
            for i in range(0, len(files_to_upload), batch_size):
                batch = files_to_upload[i : i + batch_size]

                # Prepare files for this batch
                files_list = []
                for file_path in batch:
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                        encoded = base64.b64encode(file_content).decode("utf-8")

                        # Auto-detect mimetype
                        detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                        # Get relative path for label
                        try:
                            relative_path = file_path.relative_to(directory)
                            label = str(relative_path)
                        except ValueError:
                            label = file_path.name

                        files_list.append(
                            FileUpload(
                                file=encoded,
                                label=label,
                                mimetype=detected_mimetype,
                            )
                        )

                    file_pbar.update(1)

                # Upload batch
                upload_req = UploadRequest(
                    collection_id=collection_id,
                    content_type="file",
                    files=files_list,
                    metadata=metadata,
                    ingest=ingest,
                    reader=reader,
                )

                payload = upload_req.model_dump(exclude_none=True)
                response_data = self._client.post("/upload", json_data=payload)
                responses.append(UploadResponse(**response_data))

                batch_pbar.update(1)

        finally:
            batch_pbar.close()
            file_pbar.close()

        return responses

    def _collect_files(
        self,
        directory: Path,
        recursive: bool,
        file_extensions: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
    ) -> List[Path]:
        """Collect files from directory based on filters.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            file_extensions: File extensions to include
            exclude_patterns: Patterns to exclude

        Returns:
            List of file paths
        """
        files = []

        # Get all files
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for item in directory.glob(pattern):
            if not item.is_file():
                continue

            # Check if file should be excluded
            if exclude_patterns:
                excluded = False
                for pattern in exclude_patterns:
                    if item.match(pattern) or item.name == pattern:
                        excluded = True
                        break
                if excluded:
                    continue

            # Check file extension
            if file_extensions:
                if item.suffix.lower() not in [ext.lower() for ext in file_extensions]:
                    continue

            files.append(item)

        return files


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
        file_base64: Optional[str] = None,
        urls: Optional[List[str]] = None,
        label: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        mimetype: Optional[str] = None,
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

                # Auto-detect mimetype if not provided
                detected_mimetype = mimetype
                if not detected_mimetype:
                    detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                files_list.append(
                    FileUpload(
                        file=encoded,
                        label=label or file_path.name,
                        mimetype=detected_mimetype,
                    )
                )

        elif file_obj:
            file_content = file_obj.read()
            encoded = base64.b64encode(file_content).decode("utf-8")

            # Try to detect mimetype from file object name
            detected_mimetype = mimetype
            if not detected_mimetype and hasattr(file_obj, "name"):
                detected_mimetype, _ = mimetypes.guess_type(file_obj.name)

            files_list.append(
                FileUpload(
                    file=encoded,
                    label=label or getattr(file_obj, "name", "file"),
                    mimetype=detected_mimetype,
                )
            )

        elif file_base64:
            files_list.append(
                FileUpload(
                    file=file_base64,
                    label=label or "file",
                    mimetype=mimetype,
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

    async def insert_directory(
        self,
        collection_id: str,
        directory_path: Union[str, Path],
        recursive: bool = True,
        file_extensions: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ingest: bool = True,
        reader: Optional[Union[str, Dict[str, str]]] = None,
        batch_size: int = 10,
        show_progress: bool = True,
    ) -> List[UploadResponse]:
        """Insert all files from a directory into a collection asynchronously.

        Args:
            collection_id: Collection ID
            directory_path: Path to directory containing files
            recursive: Whether to recursively traverse subdirectories
            file_extensions: List of file extensions to include (e.g., ['.pdf', '.txt'])
            exclude_patterns: List of filename patterns to exclude (e.g., ['*.tmp', '.DS_Store'])
            metadata: Additional metadata to attach to all files
            ingest: Whether to ingest content into vector database
            reader: Reader configuration for file processing
            batch_size: Number of files to upload per batch
            show_progress: Whether to show progress bar (default: True)

        Returns:
            List of UploadResponse objects, one per batch

        Example:
            ```python
            # Upload all files from a directory
            results = await client.collections.insert_directory(
                collection_id="col_123",
                directory_path="./documents",
                file_extensions=['.pdf', '.docx']
            )
            ```
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory_path}")

        # Collect all files
        files_to_upload = self._collect_files(
            directory=directory,
            recursive=recursive,
            file_extensions=file_extensions,
            exclude_patterns=exclude_patterns,
        )

        if not files_to_upload:
            return []

        # Upload in batches with progress bar
        responses = []
        total_batches = (len(files_to_upload) + batch_size - 1) // batch_size

        # Create progress bars
        batch_pbar = tqdm(
            total=total_batches,
            desc="Uploading batches",
            unit="batch",
            disable=not show_progress,
        )
        file_pbar = tqdm(
            total=len(files_to_upload),
            desc="Processing files",
            unit="file",
            disable=not show_progress,
        )

        try:
            for i in range(0, len(files_to_upload), batch_size):
                batch = files_to_upload[i : i + batch_size]

                # Prepare files for this batch
                files_list = []
                for file_path in batch:
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                        encoded = base64.b64encode(file_content).decode("utf-8")

                        # Auto-detect mimetype
                        detected_mimetype, _ = mimetypes.guess_type(str(file_path))

                        # Get relative path for label
                        try:
                            relative_path = file_path.relative_to(directory)
                            label = str(relative_path)
                        except ValueError:
                            label = file_path.name

                        files_list.append(
                            FileUpload(
                                file=encoded,
                                label=label,
                                mimetype=detected_mimetype,
                            )
                        )

                    file_pbar.update(1)

                # Upload batch
                upload_req = UploadRequest(
                    collection_id=collection_id,
                    content_type="file",
                    files=files_list,
                    metadata=metadata,
                    ingest=ingest,
                    reader=reader,
                )

                payload = upload_req.model_dump(exclude_none=True)
                response_data = await self._client.post("/upload", json_data=payload)
                responses.append(UploadResponse(**response_data))

                batch_pbar.update(1)

        finally:
            batch_pbar.close()
            file_pbar.close()

        return responses

    def _collect_files(
        self,
        directory: Path,
        recursive: bool,
        file_extensions: Optional[List[str]],
        exclude_patterns: Optional[List[str]],
    ) -> List[Path]:
        """Collect files from directory based on filters.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            file_extensions: File extensions to include
            exclude_patterns: Patterns to exclude

        Returns:
            List of file paths
        """
        files = []

        # Get all files
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for item in directory.glob(pattern):
            if not item.is_file():
                continue

            # Check if file should be excluded
            if exclude_patterns:
                excluded = False
                for pattern in exclude_patterns:
                    if item.match(pattern) or item.name == pattern:
                        excluded = True
                        break
                if excluded:
                    continue

            # Check file extension
            if file_extensions:
                if item.suffix.lower() not in [ext.lower() for ext in file_extensions]:
                    continue

            files.append(item)

        return files
