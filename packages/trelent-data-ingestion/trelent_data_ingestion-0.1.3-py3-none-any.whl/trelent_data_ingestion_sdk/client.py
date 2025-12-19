"""Client for the Trelent Data Ingestion API.

Provides a thin, typed wrapper around HTTP endpoints with a managed
requests.Session and sensible defaults.
"""
from __future__ import annotations

from typing import Optional, Union
from uuid import UUID

import requests

from .config import SDKConfig
from .models import (
    FileListResponse,
    FileUploadResponse,
    GenerateTokenRequest,
    GenerateTokenResponse,
    HealthzResponse,
    JobInput,
    JobStatusResponse,
    ListTokensParams,
    ListTokensResponse,
    ProcessResponse,
    RevokeTokenRequest,
    RevokeTokenResponse,
)


class DataIngestionClient:
    """High-level Python client for interacting with the Data Ingestion API.

    This client manages an underlying `requests.Session`, applies authentication
    and JSON headers, and exposes convenience methods for key API operations.

    Attributes:
        _config: The validated SDK configuration.
        _client: The underlying requests session used for HTTP calls.
        _timeout: Default timeout (seconds) applied to requests.
    """
    def __init__(
        self,
        config: Optional[SDKConfig] = None,
        *,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[float] = 10.0,
    ):
        """Initialize the client.

        Args:
            config: Optional SDK configuration. If not provided, a new configuration
                is derived from `base_url`/`token` or the environment.
            base_url: Optional API base URL (used when `config` is omitted).
            token: Optional bearer token (used when `config` is omitted).
            timeout: Default request timeout in seconds for all operations.

        Raises:
            ValueError: If the configuration is missing required fields.
        """
        if config and (base_url or token):
            raise ValueError("Pass either `config` or `base_url`/`token`, not both.")

        if config is None:
            if base_url or token:
                if not base_url or not token:
                    raise ValueError("Both `base_url` and `token` must be provided together.")
                config = SDKConfig(base_url=base_url, token=token)
            else:
                config = SDKConfig.from_env()
        # Defensive checks to ensure required fields are present
        if not getattr(config, "base_url", None):
            raise ValueError("SDKConfig.base_url is required")
        if not getattr(config, "token", None):
            raise ValueError("SDKConfig.token is required")
        self._config = config
        self._client = requests.Session()
        self._client.headers.update({"Content-Type": "application/json", **config.auth_header})
        self._timeout = timeout

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._client.close()

    def __enter__(self) -> "DataIngestionClient":
        """Enter the context manager, returning the client instance."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit the context manager and close the session."""
        self.close()

    # ---- API methods ----

    def _url(self, path: str) -> str:
        """Build a full URL from the configured base URL and a relative path.

        Args:
            path: A path that may or may not start with a leading slash.

        Returns:
            The absolute URL string for the request.
        """
        # Join base URL with a path that may or may not start with "/"
        if not path.startswith("/"):
            path = "/" + path
        return f"{self._config.base_url}{path}"

    def healthz(self) -> HealthzResponse:
        """Check API health.

        Returns:
            HealthzResponse: A simple status payload indicating service health.
        """
        resp = self._client.get(self._url("/healthz"), timeout=self._timeout)
        resp.raise_for_status()
        return HealthzResponse.model_validate(resp.json())

    def generate_token(self, request: GenerateTokenRequest) -> GenerateTokenResponse:
        """Generate a signed JWT token.

        Args:
            request: The token generation parameters.

        Returns:
            GenerateTokenResponse: The generated token.
        """
        resp = self._client.post(
            self._url("/v1/token/generate"),
            json=request.model_dump(mode="json", exclude_none=True),
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return GenerateTokenResponse.model_validate(resp.json())

    def list_tokens(self, params: Optional[ListTokensParams] = None) -> ListTokensResponse:
        """List tokens with optional filters.

        Args:
            params: Optional filter parameters for listing tokens.

        Returns:
            ListTokensResponse: A list of tokens.
        """
        query_params = {}
        if params is not None:
            if params.token_id is not None:
                query_params["token_id"] = str(params.token_id)
            if params.issuer is not None:
                query_params["issuer"] = params.issuer
            if params.subject is not None:
                query_params["subject"] = params.subject
            if params.include_invalid:
                query_params["include_invalid"] = "true"

        resp = self._client.get(
            self._url("/v1/token/list"),
            params=query_params if query_params else None,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return ListTokensResponse.model_validate(resp.json())

    def revoke_token(self, request: RevokeTokenRequest) -> RevokeTokenResponse:
        """Revoke a token by its ID.

        Args:
            request: The revoke token request containing the token ID.

        Returns:
            RevokeTokenResponse: Indicates success or failure.
        """
        resp = self._client.post(
            self._url("/v1/token/revoke"),
            json=request.model_dump(mode="json"),
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return RevokeTokenResponse.model_validate(resp.json())

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        expires_in_days: int = 30
    ) -> FileUploadResponse:
        """Upload a file to storage.

        Args:
            file_data: The raw bytes of the file.
            filename: The name of the file.
            content_type: The MIME type of the file.
            expires_in_days: Days until the file expires (default 30).

        Returns:
            FileUploadResponse: The ID of the uploaded file.
        """
        files = {"file": (filename, file_data, content_type)}
        data = {"expires_in_days": str(expires_in_days)}
        
        # Suppress the session's Content-Type header so requests can set the
        # correct multipart/form-data header with the boundary.
        resp = self._client.put(
            self._url("/v1/files/"),
            files=files,
            data=data,
            headers={"Content-Type": None},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return FileUploadResponse.model_validate(resp.json())

    def list_files(self) -> FileListResponse:
        """List all files uploaded by the authenticated user.

        Returns:
            FileListResponse: A list of files.
        """
        resp = self._client.get(self._url("/v1/files/"), timeout=self._timeout)
        resp.raise_for_status()
        return FileListResponse.model_validate(resp.json())

    def submit_job(self, payload: JobInput) -> ProcessResponse:
        """Submit a processing job.

        Args:
            payload: A job definition including connector, output,
                and processing configuration.

        Returns:
            ProcessResponse: Contains the created job identifier.

        Examples:
            Submit with an S3 connector writing to a bucket:

            ```python
            from trelent_data_ingestion_sdk.models import (
                S3Prefix, S3Connector, BucketOutput,
                ProcessConfig, ProcessDocumentsConfig, ProcessVideoConfig,
                JobInput,
            )

            cfg = ProcessConfig(
                documents=ProcessDocumentsConfig(
                    reprocess_documents=True,
                    extract_elements=False,
                ),
                video=ProcessVideoConfig(
                    screenshot_interval_seconds=1.0,
                    sensitivity=0.2,
                    openai_model="gpt-4.1",
                    whisper_model="whisper-1",
                ),
            )

            job = JobInput(
                connector=S3Connector(
                    bucket_name="my-input-bucket",
                    prefixes=[S3Prefix(prefix="reports/2024/", recursive=True)],
                ),
                output=BucketOutput(bucket_name="my-output-bucket", prefix="processed/"),
                config=cfg,
            )

            with DataIngestionClient() as client:
                client.submit_job(job)
            ```

            Submit URLs and request presigned URLs back with a more sensitive video config:

            ```python
            from trelent_data_ingestion_sdk.models import (
                UrlConnector, S3SignedUrlOutput,
                ProcessConfig, ProcessDocumentsConfig, ProcessVideoConfig,
                JobInput,
            )

            cfg = ProcessConfig(
                documents=ProcessDocumentsConfig(reprocess_documents=False, extract_elements=True),
                video=ProcessVideoConfig(
                    screenshot_interval_seconds=0.5,
                    sensitivity=0.05,
                    tile=8,
                    mad_thresh=2.0,
                    local_ssim_drop=0.25,
                    max_bad_frac=0.1,
                ),
            )

            job = JobInput(
                connector=UrlConnector(urls=[
                    "https://example.com/a.pdf",
                    "https://example.com/b.pdf",
                ]),
                output=S3SignedUrlOutput(expires_minutes=60),
                config=cfg,
            )

            DataIngestionClient().submit_job(job)
            ```
        """
        resp = self._client.post(
            self._url("/v1/jobs/"),
            json=payload.model_dump(mode="json", by_alias=True, exclude_none=True),
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return ProcessResponse.model_validate(resp.json())

    def get_job_status(self, job_id: Union[UUID, str], *, include_markdown: bool = False, include_file_metadata: bool = False, timeout: Optional[float] = None) -> JobStatusResponse:
        """Retrieve the current status of a job.

        Args:
            job_id: The job UUID (or string) returned from `submit_job`.
            include_markdown: If True, include rendered markdown content when available.
            timeout: Optional per-call timeout override (seconds).

        Returns:
            JobStatusResponse: The job status, batch phases, and any deliveries/errors.
        """
        jid = str(job_id)
        resp = self._client.get(
            self._url(f"/v1/jobs/{jid}"),
            params={"include_markdown": str(bool(include_markdown)).lower(), "include_file_metadata": str(bool(include_file_metadata)).lower()},
            timeout=self._timeout if timeout is None else timeout,
        )
        resp.raise_for_status()
        return JobStatusResponse.model_validate(resp.json())


