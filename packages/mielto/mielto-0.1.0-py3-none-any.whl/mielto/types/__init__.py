"""Type definitions for Mielto API."""

from mielto.types.collection import (
    Collection,
    CollectionCreate,
    CollectionUpdate,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from mielto.types.compress import CompressRequest, CompressResponse
from mielto.types.memory import (
    Memory,
    MemoryCreate,
    MemoryListResponse,
    MemoryReplace,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryUpdate,
)
from mielto.types.upload import FileUpload, UploadRequest, UploadResponse

__all__ = [
    # Memory types
    "Memory",
    "MemoryCreate",
    "MemoryUpdate",
    "MemoryReplace",
    "MemorySearchRequest",
    "MemorySearchResponse",
    "MemoryListResponse",
    # Collection types
    "Collection",
    "CollectionCreate",
    "CollectionUpdate",
    "SearchRequest",
    "SearchResponse",
    "SearchResult",
    # Compress types
    "CompressRequest",
    "CompressResponse",
    # Upload types
    "UploadRequest",
    "UploadResponse",
    "FileUpload",
]
