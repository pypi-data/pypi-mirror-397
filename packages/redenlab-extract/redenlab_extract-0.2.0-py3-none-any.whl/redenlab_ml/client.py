"""
Main client for RedenLab ML SDK.

Provides the high-level InferenceClient class for running ML inference.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from . import api
from .auth import mask_api_key, validate_api_key
from .config import get_default_base_url, get_merged_config
from .exceptions import AuthenticationError, ConfigurationError
from .polling import poll_until_complete, poll_with_callback
from .upload import upload_to_presigned_url
from .utils import get_content_type, validate_file_path, validate_model_name, validate_timeout


class InferenceClient:
    """
    Client for RedenLab ML inference service.

    This is the main entry point for running ML inference on audio files.
    Handles authentication, file upload, job submission, and result retrieval.

    Example:
        >>> client = InferenceClient(api_key="sk_live_...")
        >>> result = client.predict(file_path="audio.wav")
        >>> print(result['result'])

    Args:
        api_key: API key for authentication (optional, can use env var or config file)
        base_url: API base URL (optional, defaults to production endpoint)
        model_name: Model to use for inference (default: 'intelligibility')
        timeout: Maximum time to wait for inference in seconds (default: 3600)
        config_path: Path to config file (optional)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: str = "intelligibility",
        timeout: int = 3600,
        config_path: Optional[str] = None,
    ):
        """
        Initialise the inference client.

        Raises:
            AuthenticationError: If no API key is found
            ValidationError: If parameters are invalid
            ConfigurationError: If configuration is invalid
        """
        # Load configuration from all sources
        config_path_obj: Optional[Path] = Path(config_path) if config_path else None
        config = get_merged_config(
            config_path=config_path_obj,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            timeout=timeout,
        )

        # Get and validate API key
        self.api_key: str = config.get("api_key")  # type: ignore
        if not self.api_key:
            raise AuthenticationError(
                "No API key found. Please set via:\n"
                "1. InferenceClient(api_key='...')\n"
                "2. Environment variable: REDENLAB_ML_API_KEY\n"
                "3. Config file: ~/.redenlab-ml/config.yaml"
            )
        validate_api_key(self.api_key)

        # Set base URL (use provided, or from config, or default)
        self.base_url: str = config.get("base_url") or get_default_base_url()  # type: ignore
        if not self.base_url:
            raise ConfigurationError(
                "No API base URL configured. Please set via:\n"
                "1. InferenceClient(base_url='https://...')\n"
                "2. Environment variable: REDENLAB_ML_BASE_URL\n"
                "3. Config file: ~/.redenlab-ml/config.yaml"
            )

        # Validate and set model name
        self.model_name = validate_model_name(
            model_name or config.get("model_name", "intelligibility")
        )

        # Validate and set timeout
        self.timeout = validate_timeout(timeout if timeout != 3600 else config.get("timeout", 3600))

    def submit(self, file_path: str) -> str:
        """
        Upload file and submit inference job. Returns immediately without waiting.

        This method handles phases 1-3 of the inference workflow:
        1. Request presigned URL for upload
        2. Upload file to S3
        3. Submit inference job

        The job will process asynchronously on the server. Use poll() or get_status()
        to check results later.

        Args:
            file_path: Path to the audio file to process

        Returns:
            job_id: Job identifier string that can be used with poll() or get_status()

        Raises:
            ValidationError: If file path is invalid or file type not supported
            AuthenticationError: If API key is invalid
            UploadError: If file upload fails
            APIError: If API communication fails

        Example:
            >>> # Submit job and get job_id immediately
            >>> job_id = client.submit(file_path="audio.wav")
            >>> print(f"Submitted job: {job_id}")
            >>> # ... do other work ...
            >>> # Poll for results when ready
            >>> result = client.poll(job_id)
        """
        # Validate file path
        file_path_obj = validate_file_path(file_path)

        # Get content type from file extension
        content_type = get_content_type(file_path)

        # Get filename
        filename = file_path_obj.name

        # Step 1: Request presigned URL
        job_id, upload_url, file_key, expires_in = api.request_presigned_url(
            base_url=self.base_url,
            api_key=self.api_key,
            filename=filename,
            content_type=content_type,
        )

        # Step 2: Upload file to S3
        upload_to_presigned_url(
            file_path=str(file_path_obj),
            presigned_url=upload_url,
            content_type=content_type,
        )

        # Step 3: Submit inference job
        api.submit_inference_job(
            base_url=self.base_url,
            api_key=self.api_key,
            job_id=job_id,
            file_key=file_key,
            model_name=self.model_name,
        )

        return job_id

    def poll(
        self,
        job_id: str,
        timeout: Optional[int] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Poll for inference job completion. Blocks until job completes, fails, or times out.

        This method handles phase 4 of the inference workflow:
        4. Poll for completion

        Args:
            job_id: Job identifier (returned from submit())
            timeout: Maximum time to wait in seconds (default: use client timeout)
            progress_callback: Optional callback function that receives status updates
                             during polling. Called with status dict after each check.

        Returns:
            Dictionary containing inference results:
            - job_id: Job identifier
            - status: 'completed'
            - result: Inference result data (model-specific)
            - created_at: Job creation timestamp
            - completed_at: Job completion timestamp

        Raises:
            InferenceError: If inference job fails
            TimeoutError: If inference doesn't complete within timeout
            APIError: If API communication fails

        Example:
            >>> # Poll with custom timeout and progress callback
            >>> def on_progress(status):
            ...     print(f"Status: {status['status']}")
            >>> result = client.poll(
            ...     job_id="abc-123",
            ...     timeout=7200,
            ...     progress_callback=on_progress
            ... )
            >>> print(result['result'])
        """
        poll_timeout = timeout if timeout is not None else self.timeout

        if progress_callback:
            result = poll_with_callback(
                get_status_func=lambda: self.get_status(job_id),
                job_id=job_id,
                progress_callback=progress_callback,
                timeout=poll_timeout,
            )
        else:
            result = poll_until_complete(
                get_status_func=lambda: self.get_status(job_id),
                job_id=job_id,
                timeout=poll_timeout,
            )

        return result

    def predict(
        self,
        file_path: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Run inference on an audio file. Convenience method that submits and polls.

        This method handles the complete inference workflow:
        1. Request presigned URL for upload
        2. Upload file to S3
        3. Submit inference job
        4. Poll for completion
        5. Return results

        This is equivalent to: client.poll(client.submit(file_path))

        For batch processing of multiple files, use submit() and poll() separately
        for better efficiency.

        Args:
            file_path: Path to the audio file to process
            progress_callback: Optional callback function that receives status updates
                             during polling. Called with status dict after each check.

        Returns:
            Dictionary containing inference results:
            - job_id: Job identifier
            - status: 'completed'
            - result: Inference result data (model-specific)
            - created_at: Job creation timestamp
            - completed_at: Job completion timestamp

        Raises:
            ValidationError: If file path is invalid or file type not supported
            AuthenticationError: If API key is invalid
            UploadError: If file upload fails
            InferenceError: If inference job fails
            TimeoutError: If inference doesn't complete within timeout
            APIError: If API communication fails

        Example:
            >>> def on_progress(status):
            ...     print(f"Status: {status['status']}")
            >>> result = client.predict(
            ...     file_path="audio.wav",
            ...     progress_callback=on_progress
            ... )
            >>> print(result['result'])
        """
        job_id = self.submit(file_path)
        return self.poll(job_id, progress_callback=progress_callback)

    def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the current status of an inference job.

        Args:
            job_id: Job ID to check

        Returns:
            Dictionary containing job status:
            - job_id: Job identifier
            - status: Current status (upload_pending, processing, completed, failed)
            - result: Inference result (if completed)
            - error: Error message (if failed)
            - created_at: Job creation timestamp
            - completed_at: Job completion timestamp (if completed)

        Raises:
            APIError: If status check fails
            AuthenticationError: If API key is invalid

        Example:
            >>> status = client.get_status(job_id="abc-123")
            >>> print(status['status'])
            'processing'
        """
        return api.get_job_status(
            base_url=self.base_url,
            api_key=self.api_key,
            job_id=job_id,
            model_name=self.model_name,
        )

    def __repr__(self) -> str:
        """Return string representation of the client."""
        return (
            f"InferenceClient("
            f"api_key='{mask_api_key(self.api_key)}', "
            f"base_url='{self.base_url}', "
            f"model_name='{self.model_name}', "
            f"timeout={self.timeout}"
            f")"
        )
