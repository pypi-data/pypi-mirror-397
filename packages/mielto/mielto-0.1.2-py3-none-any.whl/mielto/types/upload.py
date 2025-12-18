"""Upload type definitions."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class FileUpload(BaseModel):
    """Schema for file upload."""

    file: str = Field(..., description="Base64 encoded file content")
    label: str = Field(..., description="Filename/label for the file")
    mimetype: Optional[str] = Field(None, description="File MIME type")


class UploadRequest(BaseModel):
    """Request schema for uploading content."""

    collection_id: str = Field(..., description="ID of the collection to upload to")
    content_type: str = Field(default="file", description="Type of content - 'file', 'url', or 'text'")
    files: Optional[List[FileUpload]] = Field(None, description="List of files to upload (base64 encoded)")
    content: Optional[str] = Field(None, description="Direct text content to upload")
    urls: Optional[List[str]] = Field(None, description="List of URLs to download and upload")
    label: Optional[str] = Field(None, description="Custom label for the content")
    description: Optional[str] = Field(None, description="Description of the content")
    user_id: Optional[str] = Field(None, description="User ID for the upload")
    crawl: Optional[bool] = Field(False, description="Whether to crawl linked content from URLs")
    ingest: Optional[bool] = Field(True, description="Whether to ingest content into vector database")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata to attach")
    reader: Optional[Union[str, Dict[str, str]]] = Field(None, description="Reader configuration")


class UploadResult(BaseModel):
    """Individual upload result."""

    content_id: str = Field(..., description="ID of the uploaded content")
    label: Optional[str] = Field(None, description="Label of the content")
    status: str = Field(..., description="Status of the upload")
    message: Optional[str] = Field(None, description="Optional message")


class UploadResponse(BaseModel):
    """Response schema for upload."""

    collection_id: str = Field(..., description="ID of the collection")
    content_type: str = Field(..., description="Type of content uploaded")
    uploads: List[UploadResult] = Field(..., description="List of successfully uploaded content")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of failed uploads with error details")
    total_uploads: int = Field(..., description="Total number attempted")
    successful_uploads: int = Field(..., description="Number successful")
    failed_uploads: int = Field(..., description="Number failed")
