"""
HTTP Client for WATS API.

This module provides a clean HTTP client with Basic authentication
for communicating with the WATS server.

Note: The HttpClient does NOT raise exceptions for HTTP error status codes.
It always returns a Response object. Error handling is delegated to the
ErrorHandler class in the repository layer.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
import httpx
import json

from .exceptions import (
    ConnectionError,
    TimeoutError,
    PyWATSError
)


@dataclass
class Response:
    """HTTP Response wrapper."""
    status_code: int
    data: Any
    headers: Dict[str, str]
    raw: bytes

    @property
    def is_success(self) -> bool:
        """True if status code is 2xx."""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """True if status code is 4xx or 5xx."""
        return self.status_code >= 400
    
    @property
    def is_not_found(self) -> bool:
        """True if status code is 404."""
        return self.status_code == 404
    
    @property
    def is_server_error(self) -> bool:
        """True if status code is 5xx."""
        return 500 <= self.status_code < 600
    
    @property
    def is_client_error(self) -> bool:
        """True if status code is 4xx."""
        return 400 <= self.status_code < 500
    
    @property
    def error_message(self) -> Optional[str]:
        """Extract error message from response data if available."""
        if self.is_success:
            return None
        
        if isinstance(self.data, dict):
            return (
                self.data.get("message") or 
                self.data.get("Message") or
                self.data.get("error") or 
                self.data.get("detail") or
                self.data.get("title")
            )
        elif isinstance(self.data, str):
            return self.data
        
        return f"HTTP {self.status_code}"


class HttpClient:
    """
    HTTP client with Basic authentication for WATS API.

    This client handles all HTTP communication with the WATS server,
    including authentication, request/response handling, and error management.
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
        verify_ssl: bool = True
    ):
        """
        Initialize the HTTP client.

        Args:
            base_url: Base URL of the WATS server
            token: Base64 encoded authentication token for Basic auth
            timeout: Request timeout in seconds (default: 30)
            verify_ssl: Whether to verify SSL certificates (default: True)
        """
        # Clean up base URL - remove trailing slashes and /api suffixes
        self.base_url = base_url.rstrip("/")
        if self.base_url.endswith("/api"):
            self.base_url = self.base_url[:-4]

        self.token = token
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        # Default headers
        self._headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Create httpx client
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create the httpx client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers=self._headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                follow_redirects=True
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> None:
        self.close()

    def _handle_response(self, response: httpx.Response) -> Response:
        """
        Handle HTTP response and convert to Response object.

        Args:
            response: The httpx response

        Returns:
            Response object with parsed data
            
        Note:
            This method does NOT raise exceptions for HTTP error status codes.
            Error handling is delegated to the ErrorHandler in the repository layer.
        """
        # Try to parse JSON response
        data = None
        try:
            if response.content:
                data = response.json()
        except (json.JSONDecodeError, ValueError):
            data = response.text if response.text else None

        # Create and return response object (no exceptions raised here)
        return Response(
            status_code=response.status_code,
            data=data,
            headers=dict(response.headers),
            raw=response.content
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Response:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/api/Product/ABC123")
            params: Query parameters
            data: Request body data (will be JSON encoded)
            headers: Additional headers to merge with defaults

        Returns:
            Response object
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        # Merge headers
        request_headers = self._headers.copy()
        if headers:
            request_headers.update(headers)

        # Prepare request kwargs
        kwargs: Dict[str, Any] = {
            "method": method,
            "url": endpoint,
            "headers": request_headers
        }

        if params:
            # Filter out None values
            kwargs["params"] = {
                k: v for k, v in params.items() if v is not None
            }

        if data is not None:
            if isinstance(data, (dict, list)):
                kwargs["json"] = data
            else:
                kwargs["content"] = data

        try:
            response = self.client.request(**kwargs)
            return self._handle_response(response)
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}: {e}")
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}")
        except Exception as e:
            raise PyWATSError(f"HTTP request failed: {e}")

    # Convenience methods
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Response:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Response:
        """Make a POST request."""
        return self._make_request(
            "POST", endpoint, data=data, params=params, **kwargs
        )

    def put(
        self,
        endpoint: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Response:
        """Make a PUT request."""
        return self._make_request(
            "PUT", endpoint, data=data, params=params, **kwargs
        )

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Response:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, params=params, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Any = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Response:
        """Make a PATCH request."""
        return self._make_request(
            "PATCH", endpoint, data=data, params=params, **kwargs
        )
