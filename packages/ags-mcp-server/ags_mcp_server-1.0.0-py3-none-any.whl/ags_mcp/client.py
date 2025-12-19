"""HTTP client for Anzo API with retry logic and error handling."""

import urllib.parse
from typing import Dict, Any, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import structlog

from .config import AnzoConfig
from .errors import (
    AnzoAPIError,
    AnzoConnectionError,
    AnzoAuthenticationError,
    AnzoNotFoundError,
    AnzoValidationError,
    AnzoTimeoutError
)

logger = structlog.get_logger(__name__)


class AnzoAPIClient:
    """HTTP client for Anzo Graph Studio REST API."""
    
    def __init__(self, config: AnzoConfig):
        """
        Initialize the Anzo API client.
        
        Args:
            config: Anzo configuration object
        """
        self.config = config
        self.session = self._create_session()
        self.base_url = config.http_base
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        session.auth = (self.config.username, self.config.password)
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _build_url(self, path: str) -> str:
        """Build full URL from path with validation."""
        if not path:
            raise ValueError("Path cannot be empty")
        # Remove leading slash if present to avoid double slashes
        path = path.lstrip("/")
        # Basic path traversal protection
        if ".." in path or path.startswith("/"):
            raise ValueError("Invalid path: contains path traversal")
        return f"{self.base_url}/{path}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and convert errors to custom exceptions.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed JSON response or success indicator
            
        Raises:
            AnzoAPIError: On API errors
        """
        try:
            response.raise_for_status()
            
            # Return parsed JSON if response has content
            if response.content:
                try:
                    return response.json()
                except ValueError:
                    # Return text if not JSON
                    return {"content": response.text, "status": "success"}
            
            return {"status": "success"}
            
        except requests.HTTPError as e:
            status_code = e.response.status_code
            
            # Try to extract error details from response
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = {"message": e.response.text}
            
            # Map status codes to specific exceptions
            if status_code == 401:
                raise AnzoAuthenticationError(
                    "Authentication failed",
                    status_code=status_code,
                    details=error_details
                )
            elif status_code == 404:
                raise AnzoNotFoundError(
                    "Resource not found",
                    status_code=status_code,
                    details=error_details
                )
            elif status_code == 400:
                raise AnzoValidationError(
                    "Invalid request",
                    status_code=status_code,
                    details=error_details
                )
            else:
                raise AnzoAPIError(
                    f"API request failed: {str(e)}",
                    status_code=status_code,
                    details=error_details
                )
        
        except requests.Timeout as e:
            raise AnzoTimeoutError(f"Request timed out: {str(e)}")
        
        except requests.ConnectionError as e:
            raise AnzoConnectionError(f"Connection failed: {str(e)}")
        
        except Exception as e:
            raise AnzoAPIError(f"Unexpected error: {str(e)}")
    
    def get(
        self, 
        path: str, 
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make GET request to Anzo API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            **kwargs: Additional arguments for requests
            
        Returns:
            Parsed API response
        """
        url = self._build_url(path)
        logger.debug("get_request", url=url, params=params)
        
        response = self.session.get(
            url,
            params=params,
            timeout=self.config.request_timeout,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make POST request to Anzo API.
        
        Args:
            path: API endpoint path
            json: JSON payload
            data: Form data
            params: Query parameters
            files: Files to upload
            **kwargs: Additional arguments for requests
            
        Returns:
            Parsed API response
        """
        url = self._build_url(path)
        logger.debug("post_request", url=url, has_json=json is not None, has_files=files is not None)
        
        response = self.session.post(
            url,
            json=json,
            data=data,
            params=params,
            files=files,
            timeout=self.config.request_timeout,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def put(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make PUT request to Anzo API.
        
        Args:
            path: API endpoint path
            json: JSON payload
            params: Query parameters
            **kwargs: Additional arguments for requests
            
        Returns:
            Parsed API response
        """
        url = self._build_url(path)
        logger.debug("put_request", url=url)
        
        response = self.session.put(
            url,
            json=json,
            params=params,
            timeout=self.config.request_timeout,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make PATCH request to Anzo API.
        
        Args:
            path: API endpoint path
            json: JSON payload
            params: Query parameters
            **kwargs: Additional arguments for requests
            
        Returns:
            Parsed API response
        """
        url = self._build_url(path)
        logger.debug("patch_request", url=url)
        
        response = self.session.patch(
            url,
            json=json,
            params=params,
            timeout=self.config.request_timeout,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make DELETE request to Anzo API.
        
        Args:
            path: API endpoint path
            params: Query parameters
            **kwargs: Additional arguments for requests
            
        Returns:
            Parsed API response
        """
        url = self._build_url(path)
        logger.debug("delete_request", url=url)
        
        response = self.session.delete(
            url,
            params=params,
            timeout=self.config.request_timeout,
            **kwargs
        )
        
        return self._handle_response(response)
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, *args):
        """Context manager exit - close session."""
        self.close()
