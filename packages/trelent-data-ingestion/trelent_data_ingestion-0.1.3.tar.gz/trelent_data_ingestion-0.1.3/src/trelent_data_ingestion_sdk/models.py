"""Typed request/response models for the Data Ingestion API."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, Set, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class TokenPermission(str, Enum):
    """Permissions that can be granted to a generated token.
    
    Note: token:generate and token:* are not available for token generation
    as they would allow privilege escalation.
    """
    # Full workflow access (includes video and document)
    WORKFLOW_ADMIN = "workflow:*"
    # Process video files
    WORKFLOW_VIDEO = "workflow:video"
    # Process documents
    WORKFLOW_DOCUMENT = "workflow:document"
    # Full file access (includes list and upload)
    FILE_ADMIN = "file:*"
    # List uploaded files
    FILE_LIST = "file:list"
    # Upload files
    FILE_UPLOAD = "file:upload"
    # List tokens
    TOKEN_LIST = "token:list"
    # Revoke tokens
    TOKEN_REVOKE = "token:revoke"


class S3Prefix(BaseModel):
    """A prefix descriptor for listing S3 objects."""
    prefix: str = Field(..., description="The prefix to list the objects from")
    recursive: bool = Field(..., description="Whether to recursively list the objects in the prefix")
# NOTE: These are intentionally duplicated from our internal connectors package
# to avoid a runtime dependency on a generically named third-party package when
# this SDK is installed from PyPI.
class S3CreateInput(BaseModel):
    """Input required to create/connect an S3-based data source."""
    type: Literal["s3"] = "s3"
    bucket_name: str = Field(..., description="The name of the bucket to connect to")
    prefixes: List[Union[str, S3Prefix]] = Field(..., description="The keys of the objects to connect to")

class UrlCreateInput(BaseModel):
    """Input required to create/connect a URL-based data source."""
    type: Literal["url"] = "url"
    urls: list[str] = Field(..., description="The URLs to connect to")


# ---- Connector inputs (mirrors API schema) ----

class ConnectorBase(BaseModel):
    """Base class for all connector inputs (discriminated by 'type')."""
    pass

class S3Connector(ConnectorBase, S3CreateInput):
    """Discriminated union variant for S3 connector inputs."""
    type: Literal["s3"] = "s3"


class UrlConnector(ConnectorBase, UrlCreateInput):
    """Discriminated union variant for URL connector inputs."""
    type: Literal["url"] = "url"


class FileUploadConnector(ConnectorBase):
    """Connector for files uploaded via the /v1/files/ endpoint."""
    type: Literal["file_upload"] = "file_upload"
    file_ids: list[UUID] = Field(..., description="IDs of uploaded files to process")


Connector = Annotated[
    Union[S3Connector, UrlConnector, FileUploadConnector],
    Field(discriminator="type"),
]


# ---- Output definitions (mirrors API schema) ----


class BucketOutput(BaseModel):
    """Output destination describing an object storage bucket and prefix."""
    type: Literal["bucket"] = "bucket"
    bucket_name: str
    prefix: str


class S3SignedUrlOutput(BaseModel):
    """Output destination requesting S3 pre-signed URLs."""
    type: Literal["s3-signed-url"] = "s3-signed-url"
    expires_minutes: int = 1440


Output = Annotated[
    Union[BucketOutput, S3SignedUrlOutput],
    Field(discriminator="type"),
]


class ProcessDocumentsConfig(BaseModel):
    """Configuration controlling document processing behavior."""
    reprocess_documents: bool = Field(description="Whether to reprocess documents.", default=True)
    extract_elements: bool = Field(description="Whether to extract elements from the documents.", default=False)
    extract_page_images: bool = Field(description="Whether to extract page images from the documents.", default=True)


class ProcessVideoConfig(BaseModel):
    """Configuration controlling video processing behavior and sensitivity."""
    screenshot_interval_seconds: float = Field(description="The interval in seconds between screenshots.", default=1.0)
    sensitivity: float = Field(description="The sensitivity for detecting frame changes.", default=0.1)
    openai_model: str = Field(description="The OpenAI model to use for the video processing.", default="gpt-4.1")
    whisper_model: str = Field(description="The Whisper model to use for the audio processing.", default="whisper-1")
    max_completion_tokens: int = Field(description="The maximum number of completion tokens to use for the video processing.", default=64000)
    tile: Optional[int] = Field(description="The tile size for detecting frame changes.", default=None)
    mad_thresh: Optional[float] = Field(description="The MAD threshold for detecting frame changes.", default=None)
    local_ssim_drop: Optional[float] = Field(description="The local SSIM drop for detecting frame changes.", default=None)
    max_bad_frac: Optional[float] = Field(description="The max bad fraction for detecting frame changes.", default=None)


class ProcessConfig(BaseModel):
    """Top-level processing configuration aggregating document and video settings."""
    documents: ProcessDocumentsConfig
    video: ProcessVideoConfig
    def __init__(self, documents: ProcessDocumentsConfig = ProcessDocumentsConfig(), video: ProcessVideoConfig = ProcessVideoConfig()):
        """Construct a default `ProcessConfig` if not provided.

        Args:
            documents: Document processing configuration. Defaults to `ProcessDocumentsConfig()`.
            video: Video processing configuration. Defaults to `ProcessVideoConfig()`.
        """
        super().__init__(documents=documents, video=video)


class JobInput(BaseModel):
    """Input payload to create a processing job."""
    connector: Connector
    output: Output
    config: ProcessConfig = Field(description="The configuration for the job.", default=ProcessConfig())
    force_error: Optional[bool] = False


# ---- Responses (mirrors API schema) ----


class WorkflowSummary(BaseModel):
    """Summary of an Argo workflow submission and identity."""
    type: str
    namespace: str
    uid: str
    name: Optional[str] = None
    generate_name: Optional[str] = None
    submitted: bool


class ProcessResponse(BaseModel):
    """Response containing the identifier of the created job."""
    job_id: UUID


class JobStatus(str, Enum):
    """Enumeration of job lifecycle phases."""
    Queued = "queued"
    Running = "running"
    Completed = "completed"
    Initializing = "initializing"

class JobStatusItem(BaseModel):
    """Status of an individual batch or sub-task within a job."""
    uid: str
    phase: JobStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class BucketDelivery(BaseModel):
    """Pointer to content delivered to an object storage bucket."""
    type: Literal["bucket"] = "bucket"
    bucket_name: str
    object_key: str


class S3PresignedUrlDelivery(BaseModel):
    """Pointer to content available via a pre-signed S3 URL."""
    type: Literal["presigned-url"] = "presigned-url"
    url: HttpUrl
    expiry: int


DeliveryPointer = Annotated[
    Union[BucketDelivery, S3PresignedUrlDelivery],
    Field(discriminator="type"),
]


class DeliveryItem(BaseModel):
    """Delivery details for a processed document including images and markdown."""
    images: Dict[str, DeliveryPointer]
    markdown_delivery: DeliveryPointer
    markdown: Optional[str] = None
    file_metadata: Optional[dict] = None


class JobStatusResponse(BaseModel):
    """Aggregate status response describing a job's progress and outputs."""
    job_id: UUID
    status: JobStatus
    batches: List[JobStatusItem]
    delivery: Optional[Dict[str, DeliveryItem]] = None
    errors: Optional[Dict[str, Dict[str, Any]]] = None

    model_config = ConfigDict(extra="allow")


class HealthzResponse(BaseModel):
    """Simple health probe response."""
    status: str


class GenerateTokenRequest(BaseModel):
    """Request payload to generate a signed JWT."""
    name: Optional[str] = None
    subject: str
    permissions: Set[TokenPermission]
    expires_seconds: int = 3600
    audiences: Optional[List[str]] = None
    not_before_seconds: Optional[int] = None


class GenerateTokenResponse(BaseModel):
    """Response containing the generated token."""
    token: str


class TokenInfo(BaseModel):
    """Information about a token."""
    id: UUID
    issuer: str
    subject: str
    created_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    is_valid: bool


class ListTokensParams(BaseModel):
    """Parameters for listing tokens."""
    token_id: Optional[UUID] = None
    issuer: Optional[str] = None
    subject: Optional[str] = None
    include_invalid: bool = False


class ListTokensResponse(BaseModel):
    """Response containing a list of tokens."""
    tokens: List[TokenInfo]


class RevokeTokenRequest(BaseModel):
    """Request payload to revoke a token."""
    token_id: UUID


class RevokeTokenResponse(BaseModel):
    """Response after revoking a token."""
    success: bool
    message: str


class FileUploadResponse(BaseModel):
    """Response after successfully uploading a file."""
    id: UUID


class FileItem(BaseModel):
    """Metadata for a single user-uploaded file."""
    id: UUID
    filename: str
    created_at: datetime


class FileListResponse(BaseModel):
    """Response containing a list of user files."""
    files: List[FileItem]


