from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, NoReturn, Optional, Type, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .types import (
    Book,
    BookStyle,
    BookType,
    Configuration,
    CreateBookParams,
    Model,
    ModelVersion,
    OutputFormat,
    Usage,
)
from .webhooks import Webhook

if TYPE_CHECKING:
    from requests import Response, Session

# Version is defined here to avoid circular import from __init__.py
__version__: str = "0.1.0"


class NellieError(Exception):
    """Base exception for all Nellie API errors."""

    pass


class APIError(NellieError):
    """Raised when the API returns an error response."""

    status_code: int
    body: Any

    def __init__(self, message: str, status_code: int, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthenticationError(NellieError):
    """Raised when API key is invalid."""

    status_code: int
    body: Any

    def __init__(self, message: str, status_code: int = 401, body: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, message: str, status_code: int = 429, body: Any = None) -> None:
        super().__init__(message, status_code, body)


class Books:
    """Handles operations related to books."""

    _client: "Nellie"

    def __init__(self, client: "Nellie") -> None:
        self._client = client

    def create(
        self,
        prompt: str = "",
        style: BookStyle = "automatic",
        type: BookType = "automatic",
        images: bool = False,
        author: str = "Nellie",
        custom_tone: str = "",
        model: ModelVersion = "2.0",
        output_format: OutputFormat = "txt",
        webhook_url: Optional[str] = None,
    ) -> Book:
        """
        Start a new book generation job.
        
        Args:
            prompt: The core idea or instructions for the book.
            style: Genre or narrative style.
            type: Format of the output (novel, comic, etc.).
            images: Whether to generate illustrations.
            author: Author name to credit.
            custom_tone: Extra tone guidance.
            model: Nellie model version (2.0 or 3.0).
            output_format: Format of the final file (txt, epub, etc.).
            webhook_url: URL to notify upon completion.
            
        Returns:
            Book: Object containing the request ID and initial status.
        """
        params = CreateBookParams(
            prompt=prompt,
            style=style,
            type=type,
            images=images,
            author=author,
            custom_tone=custom_tone,
            model=model,
            output_format=output_format,
            webhook_url=webhook_url
        )
        
        response = self._client._post("/v1/book", params.to_dict())
        return Book.from_api_response(response)

    def retrieve(self, request_id: str) -> Book:
        """
        Get the status and results of a book generation job.
        
        Args:
            request_id: The ID returned by create().
            
        Returns:
            Book: Object containing current progress and results.
        """
        response = self._client._get(f"/v1/status/{request_id}")
        return Book.from_api_response(response)

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: int = 120,
        timeout: int = 7200,
        on_progress: Optional[Callable[[Book], None]] = None,
    ) -> Book:
        """
        Poll for book completion, blocking until the job finishes or times out.

        Args:
            request_id: The ID returned by create().
            poll_interval: Seconds between status checks (default: 120, minimum: 60).
            timeout: Maximum seconds to wait before raising TimeoutError (default: 7200 = 2 hours).
            on_progress: Optional callback invoked after each status check with the current Book.

        Returns:
            Book: The final book object with status 'completed' or 'failed'.

        Raises:
            TimeoutError: If the job doesn't complete within the timeout period.
            APIError: If there's an error fetching status.

        Example:
            >>> book = client.books.create(prompt="A mystery novel")
            >>> result = client.books.wait_for_completion(
            ...     book.request_id,
            ...     poll_interval=120,
            ...     on_progress=lambda s: print(f"Progress: {s.progress}%")
            ... )
            >>> print(result.result_url)
        """
        # Enforce minimum poll interval to respect rate limits
        poll_interval = max(poll_interval, 60)

        start_time = time.time()
        while True:
            book = self.retrieve(request_id)

            if on_progress:
                on_progress(book)

            if book.is_complete():
                return book

            elapsed = time.time() - start_time
            if elapsed + poll_interval > timeout:
                raise TimeoutError(
                    f"Book generation timed out after {int(elapsed)}s. "
                    f"Last status: {book.status} ({book.progress}%)"
                )

            time.sleep(poll_interval)

    def download(
        self,
        request_id: str,
        output_path: str,
        chunk_size: int = 8192,
    ) -> str:
        """
        Download the generated content for a completed book.

        Args:
            request_id: The ID of a completed book generation job.
            output_path: Local file path to save the downloaded content.
            chunk_size: Size of chunks for streaming download (default: 8192 bytes).

        Returns:
            str: The path to the downloaded file.

        Raises:
            APIError: If the book is not completed or download fails.

        Example:
            >>> book = client.books.create(prompt="A mystery novel")
            >>> result = client.books.wait_for_completion(book.request_id)
            >>> if result.is_successful():
            ...     path = client.books.download(result.request_id, "my_book.pdf")
            ...     print(f"Downloaded to: {path}")
        """
        # Construct the download URL using the custom domain endpoint
        download_url = f"{self._client.base_url.rstrip('/')}/v1/download/{request_id}"

        try:
            # Stream the download, following redirects automatically
            response = self._client._session.get(
                download_url,
                stream=True,
                timeout=self._client.timeout * 10,  # Allow more time for downloads
                allow_redirects=True,
            )

            if response.status_code == 404:
                raise APIError("Request not found or not completed", status_code=404)
            elif response.status_code == 400:
                raise APIError("Book generation not yet completed", status_code=400)
            elif not 200 <= response.status_code < 300:
                raise APIError(
                    f"Download failed with status {response.status_code}",
                    status_code=response.status_code,
                )

            # Write content to file
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)

            return output_path

        except requests.exceptions.RequestException as e:
            raise APIError(f"Download failed: {str(e)}", status_code=0)

class Nellie:
    """
    The Nellie API Client.

    Usage:
        from nellie_api import Nellie

        client = Nellie(api_key="nel_...")
        book = client.books.create(prompt="...")
    """

    DEFAULT_BASE_URL: str = "https://api.nelliewriter.com"

    api_key: str
    base_url: str
    max_retries: int
    timeout: int
    books: Books
    webhooks: Type[Webhook]
    _session: "Session"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 30,
    ) -> None:
        """
        Initialize the Nellie API client.

        Args:
            api_key: Your Nellie API key (or set NELLIE_API_KEY env var).
            base_url: Override the API base URL (or set NELLIE_API_BASE_URL env var).
            max_retries: Number of retries for failed requests (default: 3).
            timeout: Request timeout in seconds (default: 30).
        """
        resolved_key = api_key or os.environ.get("NELLIE_API_KEY")
        if not resolved_key:
            raise AuthenticationError(
                "No API key provided. Set NELLIE_API_KEY env var or pass api_key to constructor."
            )
        self.api_key = resolved_key

        # Allow overriding base URL for testing or custom deployments
        self.base_url = (
            base_url or os.environ.get("NELLIE_API_BASE_URL") or self.DEFAULT_BASE_URL
        )
        self.max_retries = max_retries
        self.timeout = timeout

        self._session = requests.Session()
        if max_retries > 0:
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)

        self.books = Books(self)
        # We expose the Webhook utility class as a static-like accessor for convenience
        self.webhooks = Webhook

    def get_configuration(self) -> Configuration:
        """
        Get available configuration options for book generation.

        Returns the valid options for styles, types, and output formats
        that can be used when creating books.

        Returns:
            Configuration: Object containing lists of valid options.
        """
        response = self._get("/v1/configuration")
        data = response.get("data", {})
        return Configuration.from_api_response(data)

    def get_models(self) -> List[Model]:
        """
        Get available generation models and their costs.

        Returns:
            List[Model]: List of available model configurations.
        """
        response = self._get("/v1/models")
        data = response.get("data", [])
        return [Model.from_api_response(m) for m in data]

    def get_usage(self) -> Usage:
        """
        Get usage statistics for the authenticated API key.

        Returns credit consumption and recent request history.
        Requires authentication via API key.

        Returns:
            Usage: Object containing usage statistics.
        """
        response = self._get("/v1/usage")
        return Usage.from_api_response(response)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"nellie-api/Python/{__version__}",
        }

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self.base_url:
            raise ValueError(
                "API Base URL not configured. Pass base_url to Nellie() or set NELLIE_API_BASE_URL."
            )

        url = f"{self.base_url.rstrip('/')}{path}"
        headers = self._get_headers()

        try:
            response = self._session.request(
                method, url, headers=headers, timeout=self.timeout, **kwargs
            )
        except requests.exceptions.Timeout as e:
            raise APIError(f"Request timed out after {self.timeout}s: {str(e)}", status_code=0)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Connection error: {str(e)}", status_code=0)

        if not 200 <= response.status_code < 300:
            self._handle_error(response)

        try:
            return response.json()
        except ValueError:
            return response.content

    def _post(self, path: str, json_data: Dict[str, Any]) -> Any:
        return self._request("POST", path, json=json_data)

    def _get(self, path: str) -> Any:
        return self._request("GET", path)

    def _handle_error(self, response: "Response") -> NoReturn:
        msg = f"API Request Failed: {response.status_code} {response.reason}"
        body: Any
        try:
            body = response.json()
            if "error" in body:
                msg = f"API Error: {body['error']}"
                if "details" in body:
                    msg += f" - {body['details']}"
        except ValueError:
            body = response.text

        if response.status_code == 401:
            raise AuthenticationError(msg, status_code=response.status_code, body=body)
        elif response.status_code == 429:
            raise RateLimitError(msg, status_code=response.status_code, body=body)
        else:
            raise APIError(msg, status_code=response.status_code, body=body)
