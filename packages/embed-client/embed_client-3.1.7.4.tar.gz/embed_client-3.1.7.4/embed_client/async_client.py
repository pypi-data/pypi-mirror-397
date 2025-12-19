"""
Async client for Embedding Service API (OpenAPI 3.0.2)

- 100% type-annotated
- English docstrings and examples
- Ready for PyPi
- Supports new API format with body, embedding, and chunks
- Supports all authentication methods (API Key, JWT, Basic Auth, Certificate)
- Integrates with mcp_security_framework
- Supports all security modes (HTTP, HTTPS, mTLS)

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from typing import Any, Dict, List, Optional, Union
import asyncio
import os
import logging
import time
from pathlib import Path

# Import authentication, configuration, and SSL systems
from .auth import ClientAuthManager
from .config import ClientConfig
from .adapter_config_factory import AdapterConfigFactory
from .adapter_transport import AdapterTransport
from .response_normalizer import ResponseNormalizer
from .response_parsers import (
    extract_embeddings,
    extract_embedding_data,
    extract_texts,
    extract_chunks,
    extract_tokens,
    extract_bm25_tokens,
)


class EmbeddingServiceError(Exception):
    """Base exception for EmbeddingServiceAsyncClient."""


class EmbeddingServiceConnectionError(EmbeddingServiceError):
    """Raised when the service is unavailable or connection fails."""


class EmbeddingServiceHTTPError(EmbeddingServiceError):
    """Raised for HTTP errors (4xx, 5xx)."""

    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


class EmbeddingServiceAPIError(EmbeddingServiceError):
    """Raised for errors returned by the API in the response body."""

    def __init__(self, error: Any):
        super().__init__(f"API error: {error}")
        self.error = error


class EmbeddingServiceConfigError(EmbeddingServiceError):
    """Raised for configuration errors (invalid base_url, port, etc.)."""


class EmbeddingServiceTimeoutError(EmbeddingServiceError):
    """Raised when request times out."""


class EmbeddingServiceJSONError(EmbeddingServiceError):
    """Raised when JSON parsing fails."""


class EmbeddingServiceAsyncClient:
    """
    Asynchronous client for the Embedding Service API.

    Supports both old and new API formats:
    - Old format: {"result": {"success": true, "data": {"embeddings": [...]}}}
    - New format: {"result": {"success": true, "data": {"embeddings": [...], "results": [{"body": "text", "embedding": [...], "tokens": [...], "bm25_tokens": [...]}]}}}

    Supports all authentication methods and security modes:
    - API Key authentication
    - JWT token authentication
    - Basic authentication
    - Certificate authentication (mTLS)
    - HTTP, HTTPS, and mTLS security modes

    Args:
        base_url (str, optional): Base URL of the embedding service (e.g., "http://localhost").
        port (int, optional): Port of the embedding service (e.g., 8001).
        timeout (float): Request timeout in seconds (default: 30).
        config (ClientConfig, optional): Configuration object with authentication and SSL settings.
        config_dict (dict, optional): Configuration dictionary with authentication and SSL settings.
        auth_manager (ClientAuthManager, optional): Authentication manager instance.

    Raises:
        EmbeddingServiceConfigError: If base_url or port is invalid.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        port: Optional[int] = None,
        timeout: float = 30.0,
        config: Optional[ClientConfig] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        auth_manager: Optional[ClientAuthManager] = None,
    ):
        # Initialize configuration
        self.config = config
        self.config_dict = config_dict
        self.auth_manager = auth_manager

        # If config is provided, use it to set base_url and port
        if config:
            self.base_url = config.get(
                "server.host",
                base_url or os.getenv("EMBEDDING_SERVICE_BASE_URL", "http://localhost"),
            )
            self.port = config.get("server.port", port or int(os.getenv("EMBEDDING_SERVICE_PORT", "8001")))
            self.timeout = config.get("client.timeout", timeout)
        elif config_dict:
            server_config = config_dict.get("server", {})
            # ✅ ИСПРАВЛЕНИЕ: Использовать base_url из конфигурации, если он есть
            if "base_url" in server_config:
                self.base_url = server_config["base_url"]
                self.port = None  # Порт уже включен в base_url
            else:
                host = server_config.get(
                    "host",
                    base_url or os.getenv("EMBEDDING_SERVICE_BASE_URL", "http://localhost"),
                )
                port = server_config.get("port", port or int(os.getenv("EMBEDDING_SERVICE_PORT", "8001")))
                # Determine protocol from SSL config
                ssl_config = config_dict.get("ssl", {})
                protocol = "https" if ssl_config.get("enabled", False) else "http"
                # Create base_url from host and port
                if host.startswith("http://") or host.startswith("https://"):
                    self.base_url = host
                    self.port = port
                else:
                    self.base_url = f"{protocol}://{host}"
                    self.port = port
            self.timeout = config_dict.get("client", {}).get("timeout", timeout)
        else:
            # Use provided parameters or environment variables
            try:
                self.base_url = base_url or os.getenv("EMBEDDING_SERVICE_BASE_URL", "http://localhost")
            except (TypeError, AttributeError) as e:
                raise EmbeddingServiceConfigError(f"Invalid base_url configuration: {e}") from e

            try:
                self.port = port or int(os.getenv("EMBEDDING_SERVICE_PORT", "8001"))
            except (ValueError, TypeError) as e:
                raise EmbeddingServiceConfigError(f"Invalid port configuration: {e}") from e
            self.timeout = timeout

        # Validate base_url
        try:
            if not self.base_url:
                raise EmbeddingServiceConfigError("base_url must be provided.")
            if not isinstance(self.base_url, str):
                raise EmbeddingServiceConfigError("base_url must be a string.")

            # Validate URL format
            if not (self.base_url.startswith("http://") or self.base_url.startswith("https://")):
                raise EmbeddingServiceConfigError("base_url must start with http:// or https://")
        except (TypeError, AttributeError) as e:
            raise EmbeddingServiceConfigError(f"Invalid base_url configuration: {e}") from e

        # Validate port
        try:
            # ✅ ИСПРАВЛЕНИЕ: Порт не обязателен, если он уже в base_url
            if self.port is not None:
                if not isinstance(self.port, int) or self.port <= 0 or self.port > 65535:
                    raise EmbeddingServiceConfigError("port must be a valid integer between 1 and 65535.")
        except (ValueError, TypeError) as e:
            raise EmbeddingServiceConfigError(f"Invalid port configuration: {e}") from e

        # Validate timeout
        try:
            self.timeout = float(self.timeout)
            if self.timeout <= 0:
                raise EmbeddingServiceConfigError("timeout must be positive.")
        except (ValueError, TypeError) as e:
            raise EmbeddingServiceConfigError(f"Invalid timeout configuration: {e}") from e

        # Store auth_manager if provided (for diagnostics only)
        # Actual authentication is handled by adapter
        self.auth_manager = auth_manager

        # SSL and auth managers are created lazily only when needed for diagnostics
        # Transport uses only adapter, which handles all SSL/TLS and auth
        self._ssl_manager = None

        # Initialize adapter transport (always used) - this is the only transport
        # Adapter reads config and handles all SSL/TLS, authentication, and queue operations
        config_data = self.config_dict if self.config_dict else (self.config.get_all() if self.config else {})
        adapter_params = AdapterConfigFactory.from_config_dict(config_data)
        self._adapter_transport: Optional[AdapterTransport] = None
        self._adapter_transport = AdapterTransport(adapter_params)

    def _format_error_response(
        self, error: str, lang: Optional[str] = None, text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format error response in a standard way.
        Args:
            error (str): Error message
            lang (str, optional): Language of the text that caused the error
            text (str, optional): Text that caused the error
        Returns:
            dict: Formatted error response
        """
        response = {"error": f"Embedding service error: {error}"}
        if lang is not None:
            response["lang"] = lang
        if text is not None:
            response["text"] = text
        return response

    def extract_embeddings(self, result: Dict[str, Any]) -> List[List[float]]:
        """Extract embeddings from API response. Delegates to response_parsers module."""
        return extract_embeddings(result)

    def extract_embedding_data(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract full embedding data from API response. Delegates to response_parsers module."""
        return extract_embedding_data(result)

    def extract_texts(self, result: Dict[str, Any]) -> List[str]:
        """Extract original texts from API response. Delegates to response_parsers module."""
        return extract_texts(result)

    def extract_chunks(self, result: Dict[str, Any]) -> List[List[str]]:
        """Extract text chunks from API response. Delegates to response_parsers module."""
        return extract_chunks(result)

    def extract_tokens(self, result: Dict[str, Any]) -> List[List[str]]:
        """Extract tokens from API response. Delegates to response_parsers module."""
        return extract_tokens(result)

    def extract_bm25_tokens(self, result: Dict[str, Any]) -> List[List[str]]:
        """Extract BM25 tokens from API response. Delegates to response_parsers module."""
        return extract_bm25_tokens(result)

    async def __aenter__(self):
        try:
            # Use adapter transport (always)
            await self._adapter_transport.__aenter__()
            return self
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to create transport: {e}") from e

    async def __aexit__(self, exc_type, exc, tb):
        if self._adapter_transport:
            try:
                await self._adapter_transport.__aexit__(exc_type, exc, tb)
            except Exception as e:
                raise EmbeddingServiceError(f"Failed to close adapter transport: {e}") from e

    async def health(self, base_url: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
        """
        Check the health of the service.
        Args:
            base_url (str, optional): Override base URL (not used with adapter).
            port (int, optional): Override port (not used with adapter).
        Returns:
            dict: Health status and model info.
        """
        try:
            return await self._adapter_transport.health()
        except Exception as e:
            raise EmbeddingServiceError(f"Health check failed: {e}") from e

    async def get_openapi_schema(self, base_url: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
        """
        Get the OpenAPI schema of the service.
        Args:
            base_url (str, optional): Override base URL (not used with adapter).
            port (int, optional): Override port (not used with adapter).
        Returns:
            dict: OpenAPI schema.
        """
        try:
            return await self._adapter_transport.get_openapi_schema()
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to get OpenAPI schema: {e}") from e

    async def get_commands(self, base_url: Optional[str] = None, port: Optional[int] = None) -> Dict[str, Any]:
        """
        Get the list of available commands.
        Args:
            base_url (str, optional): Override base URL (not used with adapter).
            port (int, optional): Override port (not used with adapter).
        Returns:
            dict: List of commands and their descriptions.
        """
        try:
            return await self._adapter_transport.get_commands_list()
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to get commands: {e}") from e

    def _validate_texts(self, texts: List[str]) -> None:
        """
        Validate input texts before sending to the API.
        Args:
            texts (List[str]): List of texts to validate
        Raises:
            EmbeddingServiceAPIError: If texts are invalid
        """
        if not texts:
            raise EmbeddingServiceAPIError({"code": -32602, "message": "Empty texts list provided"})

        invalid_texts = []
        for i, text in enumerate(texts):
            if not isinstance(text, str):
                invalid_texts.append(f"Text at index {i} is not a string")
                continue
            if not text or not text.strip():
                invalid_texts.append(f"Text at index {i} is empty or contains only whitespace")
            elif len(text.strip()) < 2:  # Минимальная длина текста
                invalid_texts.append(f"Text at index {i} is too short (minimum 2 characters)")

        if invalid_texts:
            raise EmbeddingServiceAPIError(
                {
                    "code": -32602,
                    "message": "Invalid input texts",
                    "details": invalid_texts,
                }
            )

    async def cmd(
        self,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        base_url: Optional[str] = None,
        port: Optional[int] = None,
        validate_texts: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute a command via JSON-RPC protocol.

        Args:
            command: Command to execute (embed, models, health, help, config).
            params: Parameters for the command.
            base_url: Override base URL (not used with adapter).
            port: Override port (not used with adapter).
            validate_texts: When True, perform local validation for ``embed`` texts
                via ``_validate_texts`` before sending the request.

        Returns:
            Normalized command execution result. On success, typically:

            - ``{\"result\": {\"success\": true, \"data\": {...}}}``

            On error, an :class:`EmbeddingServiceAPIError` is raised with details
            extracted from the response.
        """
        if not command:
            raise EmbeddingServiceAPIError({"code": -32602, "message": "Command is required"})

        # Local validation for embed texts (legacy fail-fast behavior).
        # High-level helpers (e.g. embed()) may disable this to rely entirely
        # on server-side error_policy semantics.
        if validate_texts and command == "embed" and params and "texts" in params:
            self._validate_texts(params["texts"])
            # Command name stays "embed" - adapter will handle queue automatically
            # based on command's use_queue=True flag

        logger = logging.getLogger("EmbeddingServiceAsyncClient.cmd")

        # Execute command via adapter transport
        try:
            logger.info(f"Executing command via adapter: {command}, params={params}")
            # Use execute_command_unified to call /api/jsonrpc endpoint (embedding service uses JSON-RPC)
            result = await self._adapter_transport.execute_command_unified(
                command=command,
                params=params,
                use_cmd_endpoint=False,  # Use /api/jsonrpc endpoint (JSON-RPC format)
                auto_poll=True,
            )

            # Handle response from execute_command_unified
            # Adapter now automatically handles queue polling and returns completed result
            if isinstance(result, dict):
                mode = result.get("mode", "immediate")

                # If adapter completed the job (auto_poll=True), result is already available
                if mode == "queued" and result.get("status") == "completed":
                    # Extract the actual result from nested structure
                    nested_result = result.get("result")
                    if nested_result and isinstance(nested_result, dict):
                        # Check if result contains another result (from queue job)
                        if "result" in nested_result:
                            return {"result": nested_result["result"]}
                        # Otherwise return the nested result directly
                        return {"result": nested_result}
                    return {"result": result.get("result", {})}

                # For immediate responses, return as-is
                if mode == "immediate":
                    return {"result": result.get("result", result)}

                # For queued responses without completion (auto_poll=False), extract job_id
                if mode == "queued" and not result.get("status") == "completed":
                    job_id = (
                        result.get("job_id")
                        or result.get("result", {}).get("job_id")
                        or result.get("result", {}).get("data", {}).get("job_id")
                        or result.get("data", {}).get("job_id")
                    )
                    if job_id:
                        # Wait for job completion
                        job_result = await self.wait_for_job(job_id, timeout=60.0)
                        if isinstance(job_result, dict):
                            if "result" in job_result:
                                return {"result": job_result["result"]}
                            elif "data" in job_result:
                                return {
                                    "result": {
                                        "success": True,
                                        "data": job_result["data"],
                                    }
                                }
                            else:
                                return {"result": {"success": True, "data": job_result}}
                        return {"result": {"success": True, "data": job_result}}

            # Normalize adapter response to legacy format
            normalized = ResponseNormalizer.normalize_command_response(result)

            # Check for errors in normalized response
            if "error" in normalized:
                raise EmbeddingServiceAPIError(normalized["error"])

            # Check for error in result
            if "result" in normalized:
                result_data = normalized["result"]
                if isinstance(result_data, dict) and (result_data.get("success") is False or "error" in result_data):
                    raise EmbeddingServiceAPIError(result_data.get("error", result_data))

            return normalized
        except EmbeddingServiceAPIError:
            raise
        except Exception as e:
            logger.error(f"Error in adapter cmd: {e}", exc_info=True)
            # Try to extract structured error
            error_dict = ResponseNormalizer.extract_error_from_adapter(e)
            raise EmbeddingServiceAPIError(error_dict.get("error", {"message": str(e)})) from e

    async def embed(
        self,
        texts: List[str],
        *,
        model: Optional[str] = None,
        dimension: Optional[int] = None,
        error_policy: str = "continue",
        **extra_params: Any,
    ) -> Dict[str, Any]:
        """
        High-level helper for the ``embed`` command.

        This method is the recommended entry point for embedding text batches.
        It:

        - Sends ``error_policy=\"continue\"`` by default (per-item error reporting).
        - Relies on the server to handle validation according to the memo
          (top-level errors vs per-item errors).
        - Returns the service ``data`` section, which typically contains:
          ``embeddings``, ``results``, ``model``, and ``dimension``.

        Args:
            texts: List of input texts to embed.
            model: Optional model name.
            dimension: Optional expected embedding dimension (> 0).
            error_policy: Embedding error policy, ``\"continue\"`` (default)
                or ``\"fail_fast\"``.
            **extra_params: Additional command parameters passed through to the
                underlying ``embed`` command (for future extensions).

        Returns:
            The ``data`` section from the embedding service response. For the
            new contract this includes:

            - ``embeddings``: list of vectors or ``null`` for failed items.
            - ``results``: list of per-item structures with
              ``body``, ``embedding``, ``tokens``, ``bm25_tokens``, ``error``.
            - ``model`` and ``dimension`` where available.

        Raises:
            EmbeddingServiceAPIError: If a top-level JSON-RPC error occurs or
                the service reports ``success: false``.
        """
        # Build params for the embed command following the integration memo.
        params: Dict[str, Any] = {"texts": texts}
        if model is not None:
            params["model"] = model
        if dimension is not None:
            params["dimension"] = dimension
        if error_policy:
            params["error_policy"] = error_policy
        if extra_params:
            params.update(extra_params)

        # Rely on server-side error_policy semantics (per-item errors for "continue").
        raw_result = await self.cmd("embed", params=params, validate_texts=False)

        # Extract the data section according to the documented contract.
        data: Optional[Dict[str, Any]] = None
        if "result" in raw_result and isinstance(raw_result["result"], dict):
            res = raw_result["result"]
            if "data" in res and isinstance(res["data"], dict):
                data = res["data"]
            elif "data" in res and isinstance(res["data"], list):
                # Legacy list-of-items format.
                data = {"results": res["data"]}

        # Fallbacks for older or non-standard formats using response_parsers.
        if data is None:
            try:
                # New format: full per-item structures.
                results = extract_embedding_data(raw_result)
                data = {"results": results}
            except ValueError:
                # Old format: just embeddings.
                embeddings = extract_embeddings(raw_result)
                data = {"embeddings": embeddings}

        return data

    async def wait_for_job(self, job_id: str, timeout: float = 60.0, poll_interval: float = 1.0) -> Dict[str, Any]:
        """
        Wait for job completion and return results.

        Args:
            job_id: Job identifier
            timeout: Maximum time to wait (seconds)
            poll_interval: Time between status checks (seconds)

        Returns:
            Complete job results

        Raises:
            EmbeddingServiceTimeoutError: If job doesn't complete within timeout
            EmbeddingServiceAPIError: If job fails
        """
        try:
            # Get initial status
            status = await self.job_status(job_id)
            logger = logging.getLogger("EmbeddingServiceAsyncClient.wait_for_job")
            logger.debug(f"Initial job status: {status}")

            start_time = time.time()

            while time.time() - start_time < timeout:
                current_status = status.get("status", "unknown")
                logger.debug(f"Job {job_id} status: {current_status}, full status: {status}")

                if current_status in ("completed", "success", "done"):
                    result = status.get("result")
                    if result:
                        # If result is a dict with 'data', extract it
                        if isinstance(result, dict) and "data" in result:
                            return result["data"]
                        return result
                    # If no result in status, return the whole status
                    return status
                elif current_status in ("failed", "error"):
                    error = status.get("error", status.get("message", "Job failed"))
                    raise EmbeddingServiceAPIError({"message": str(error)})

                await asyncio.sleep(poll_interval)
                status = await self.job_status(job_id)

            raise EmbeddingServiceTimeoutError(f"Job {job_id} did not complete within {timeout} seconds")
        except EmbeddingServiceTimeoutError:
            raise
        except EmbeddingServiceAPIError:
            raise
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to wait for job: {e}") from e

    async def job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status.

        Args:
            job_id: Job identifier

        Returns:
            Job status information
        """
        try:
            status = await self._adapter_transport.queue_get_job_status(job_id)
            normalized = ResponseNormalizer.normalize_queue_status(status)
            logger = logging.getLogger("EmbeddingServiceAsyncClient.job_status")
            logger.debug(f"Raw status: {status}, Normalized: {normalized}")
            return normalized
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to get job status: {e}") from e

    async def cancel_command(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a command execution in queue.

        Args:
            job_id: Job identifier

        Returns:
            Cancellation result
        """
        try:
            # Stop and delete job
            await self._adapter_transport.queue_stop_job(job_id)
            return await self._adapter_transport.queue_delete_job(job_id)
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to cancel command: {e}") from e

    async def list_queued_commands(self, status: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        List all commands currently in the queue.

        Args:
            status: Filter by status (pending, running, completed, failed, stopped)
            limit: Maximum number of jobs to return

        Returns:
            Dictionary containing list of queued commands
        """
        try:
            result = await self._adapter_transport.queue_list_jobs(status=status, job_type="command_execution")

            # Apply limit if specified
            if limit and "data" in result:
                jobs = result.get("data", {}).get("jobs", [])
                if len(jobs) > limit:
                    result["data"]["jobs"] = jobs[:limit]
                    result["data"]["total_count"] = limit

            return result
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to list queued commands: {e}") from e

    async def get_job_logs(self, job_id: str) -> Dict[str, Any]:
        """
        Get job logs (stdout and stderr).

        Args:
            job_id: Job identifier

        Returns:
            Dictionary containing job logs
        """
        try:
            return await self._adapter_transport.queue_get_job_logs(job_id)
        except Exception as e:
            raise EmbeddingServiceError(f"Failed to get job logs: {e}") from e

    async def close(self) -> None:
        """
        Close the underlying adapter transport explicitly.

        This method allows the user to manually close the transport used by the client.
        It is safe to call multiple times; if the transport is already closed or was never opened, nothing happens.

        Raises:
            EmbeddingServiceError: If closing the transport fails.
        """
        if self._adapter_transport:
            try:
                await self._adapter_transport.close()
            except Exception as e:
                raise EmbeddingServiceError(f"Failed to close adapter transport: {e}") from e

    # TODO: Add methods for /cmd, /api/commands, etc.

    @classmethod
    def from_config(cls, config: ClientConfig) -> "EmbeddingServiceAsyncClient":
        """
        Create client from ClientConfig object.

        Args:
            config: ClientConfig object with authentication and SSL settings

        Returns:
            EmbeddingServiceAsyncClient instance configured with the provided config
        """
        return cls(config=config)

    @classmethod
    def from_config_dict(cls, config_dict: Dict[str, Any]) -> "EmbeddingServiceAsyncClient":
        """
        Create client from configuration dictionary.

        Args:
            config_dict: Configuration dictionary with authentication and SSL settings

        Returns:
            EmbeddingServiceAsyncClient instance configured with the provided config
        """
        return cls(config_dict=config_dict)

    @classmethod
    def from_config_file(cls, config_path: Union[str, Path]) -> "EmbeddingServiceAsyncClient":
        """
        Create client from configuration file.

        Args:
            config_path: Path to configuration file (JSON or YAML)

        Returns:
            EmbeddingServiceAsyncClient instance configured with the provided config
        """
        # ✅ ИСПРАВЛЕНИЕ: Создать объект ClientConfig и загрузить конфигурацию
        config = ClientConfig(config_path)
        config.load_config()
        return cls(config=config)

    @classmethod
    def with_auth(cls, base_url: str, port: int, auth_method: str, **kwargs) -> "EmbeddingServiceAsyncClient":
        """
        Create client with authentication configuration.

        Args:
            base_url: Base URL of the embedding service
            port: Port of the embedding service
            auth_method: Authentication method ("api_key", "jwt", "basic", "certificate")
            **kwargs: Additional authentication parameters

        Returns:
            EmbeddingServiceAsyncClient instance with authentication configured

        Examples:
            # API Key authentication
            client = EmbeddingServiceAsyncClient.with_auth(
                "http://localhost", 8001, "api_key",
                api_keys={"user": "api_key_123"}
            )

            # JWT authentication
            client = EmbeddingServiceAsyncClient.with_auth(
                "http://localhost", 8001, "jwt",
                secret="secret", username="user", password="pass"
            )

            # Basic authentication
            client = EmbeddingServiceAsyncClient.with_auth(
                "http://localhost", 8001, "basic",
                username="user", password="pass"
            )

            # Certificate authentication
            client = EmbeddingServiceAsyncClient.with_auth(
                "https://localhost", 9443, "certificate",
                cert_file="certs/client.crt", key_file="keys/client.key"
            )
        """
        # Build configuration dictionary
        config_dict = {
            "server": {"host": base_url, "port": port},
            "client": {"timeout": kwargs.get("timeout", 30.0)},
            "auth": {"method": auth_method},
        }

        # Add authentication configuration based on method
        if auth_method == "api_key":
            if "api_keys" in kwargs:
                config_dict["auth"]["api_keys"] = kwargs["api_keys"]
            elif "api_key" in kwargs:
                config_dict["auth"]["api_keys"] = {"user": kwargs["api_key"]}
            else:
                raise ValueError("api_keys or api_key parameter required for api_key authentication")

        elif auth_method == "jwt":
            required_params = ["secret", "username", "password"]
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"{param} parameter required for jwt authentication")

            config_dict["auth"]["jwt"] = {
                "secret": kwargs["secret"],
                "username": kwargs["username"],
                "password": kwargs["password"],
                "expiry_hours": kwargs.get("expiry_hours", 24),
            }

        elif auth_method == "basic":
            required_params = ["username", "password"]
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"{param} parameter required for basic authentication")

            config_dict["auth"]["basic"] = {
                "username": kwargs["username"],
                "password": kwargs["password"],
            }

        elif auth_method == "certificate":
            required_params = ["cert_file", "key_file"]
            for param in required_params:
                if param not in kwargs:
                    raise ValueError(f"{param} parameter required for certificate authentication")

            config_dict["auth"]["certificate"] = {
                "cert_file": kwargs["cert_file"],
                "key_file": kwargs["key_file"],
            }

        else:
            raise ValueError(f"Unsupported authentication method: {auth_method}")

        # Add SSL configuration if provided or if using HTTPS
        ssl_enabled = kwargs.get("ssl_enabled")
        if ssl_enabled is None:
            ssl_enabled = base_url.startswith("https://")

        if ssl_enabled or any(key in kwargs for key in ["ca_cert_file", "cert_file", "key_file", "ssl_enabled"]):
            config_dict["ssl"] = {
                "enabled": ssl_enabled,
                "verify_mode": kwargs.get("verify_mode", "CERT_REQUIRED"),
                "check_hostname": kwargs.get("check_hostname", True),
                "check_expiry": kwargs.get("check_expiry", True),
            }

            if "ca_cert_file" in kwargs:
                config_dict["ssl"]["ca_cert_file"] = kwargs["ca_cert_file"]

            if "cert_file" in kwargs:
                config_dict["ssl"]["cert_file"] = kwargs["cert_file"]

            if "key_file" in kwargs:
                config_dict["ssl"]["key_file"] = kwargs["key_file"]

        return cls(config_dict=config_dict)

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for requests.

        Returns:
            Dictionary of authentication headers
        """
        # Authentication is handled by adapter at transport level
        # This method is kept for compatibility but returns empty dict
        # as adapter handles all auth via token_header and token parameters
        return {}

    def is_authenticated(self) -> bool:
        """
        Check if client is configured for authentication.

        Returns:
            True if authentication is configured, False otherwise
        """
        if self.auth_manager:
            return self.auth_manager.is_auth_enabled()
        # Check config directly
        if self.config_dict:
            return self.config_dict.get("auth", {}).get("method", "none") != "none"
        if self.config:
            return self.config.get("auth.method", "none") != "none"
        return False

    def get_auth_method(self) -> str:
        """
        Get current authentication method.

        Returns:
            Authentication method name or "none" if not configured
        """
        if self.auth_manager:
            return self.auth_manager.get_auth_method()
        # Get from config directly
        if self.config_dict:
            return self.config_dict.get("auth", {}).get("method", "none")
        if self.config:
            return self.config.get("auth.method", "none")
        return "none"

    def is_ssl_enabled(self) -> bool:
        """
        Check if SSL/TLS is enabled.

        Returns:
            True if SSL/TLS is enabled, False otherwise
        """
        # Get from config directly - adapter handles SSL
        if self.config_dict:
            return self.config_dict.get("ssl", {}).get("enabled", False)
        if self.config:
            return self.config.get("ssl.enabled", False)
        return False

    def is_mtls_enabled(self) -> bool:
        """
        Check if mTLS (mutual TLS) is enabled.

        Returns:
            True if mTLS is enabled, False otherwise
        """
        # Get from config directly - adapter handles mTLS
        if self.config_dict:
            ssl_config = self.config_dict.get("ssl", {})
            return (
                ssl_config.get("enabled", False)
                and bool(ssl_config.get("cert_file"))
                and bool(ssl_config.get("key_file"))
            )
        if self.config:
            ssl_config = self.config.get("ssl", {})
            return (
                ssl_config.get("enabled", False)
                and bool(ssl_config.get("cert_file"))
                and bool(ssl_config.get("key_file"))
            )
        return False

    def get_ssl_config(self) -> Dict[str, Any]:
        """
        Get current SSL configuration.

        Returns:
            Dictionary with SSL configuration or empty dict if not configured
        """
        # Get from config directly
        if self.config_dict:
            return self.config_dict.get("ssl", {})
        if self.config:
            return self.config.get("ssl", {})
        return {}

    def validate_ssl_config(self) -> List[str]:
        """
        Validate SSL configuration.

        Returns:
            List of validation errors
        """
        # Validate only structure - adapter handles actual SSL/TLS
        errors = []
        if self.config_dict:
            ssl_config = self.config_dict.get("ssl", {})
        elif self.config:
            ssl_config = self.config.get("ssl", {})
        else:
            return errors

        if ssl_config.get("enabled", False):
            import os

            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            if cert_file and not os.path.exists(cert_file):
                errors.append(f"Certificate file not found: {cert_file}")
            if key_file and not os.path.exists(key_file):
                errors.append(f"Key file not found: {key_file}")
            ca_cert_file = ssl_config.get("ca_cert_file")
            if ca_cert_file and not os.path.exists(ca_cert_file):
                errors.append(f"CA certificate file not found: {ca_cert_file}")

        return errors

    def get_supported_ssl_protocols(self) -> List[str]:
        """
        Get list of supported SSL/TLS protocols.

        Returns:
            List of supported protocol names
        """
        # Protocols are handled by adapter
        return ["TLSv1.2", "TLSv1.3"]
