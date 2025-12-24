"""
Fuzentry Python SDK - Core Client

HTTP client with retries, rate limiting, and error handling.
"""

import requests
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class FuzentryConfig:
    """SDK Configuration"""
    api_key: Optional[str] = None
    session_token: Optional[str] = None
    base_url: str = "https://api.tailoredtechworks.net"
    timeout: int = 30
    max_retries: int = 3
    
    
class FuzentryError(Exception):
    """Base exception for Fuzentry SDK"""
    def __init__(self, status_code: int, message: str, details: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{status_code}] {message}")


class FuzentryClient:
    """
    Core HTTP client for Fuzentry API
    
    Example:
        client = FuzentryClient(api_key="fuz_abc123...")
        response = client.get("/agents/status")
    """
    
    def __init__(self, config: Optional[FuzentryConfig] = None, **kwargs):
        """
        Initialize client
        
        Args:
            config: FuzentryConfig object
            **kwargs: Config parameters (api_key, session_token, base_url, etc.)
        """
        if config:
            self.config = config
        else:
            self.config = FuzentryConfig(**kwargs)
        
        if not self.config.api_key and not self.config.session_token:
            raise ValueError("Either api_key or session_token is required")
        
        self.session = requests.Session()
        
        # Set default headers
        if self.config.api_key:
            self.session.headers['x-api-key'] = self.config.api_key
        elif self.config.session_token:
            self.session.headers['Authorization'] = f'Bearer {self.config.session_token}'
        
        self.session.headers['Content-Type'] = 'application/json'
        self.session.headers['User-Agent'] = 'fuzentry-python-sdk/0.1.0'
    
    def request(
        self,
        method: str,
        path: str,
        body: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retries
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (e.g., "/agents/invoke")
            body: Request body (will be JSON encoded)
            headers: Additional headers
            timeout: Request timeout in seconds
            retries: Max retry attempts for 5xx errors
            
        Returns:
            Response data with status, headers, and body
        """
        url = f"{self.config.base_url}{path}"
        timeout = timeout or self.config.timeout
        max_retries = retries if retries is not None else self.config.max_retries
        
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=body,
                    headers=request_headers,
                    timeout=timeout
                )
                
                # Handle errors
                if not response.ok:
                    error_body = response.json() if response.content else {}
                    
                    # Don't retry client errors (4xx)
                    if 400 <= response.status_code < 500:
                        raise FuzentryError(
                            response.status_code,
                            error_body.get('message', f'HTTP {response.status_code}'),
                            error_body
                        )
                    
                    # Retry server errors (5xx)
                    if response.status_code >= 500 and attempt < max_retries:
                        last_error = Exception(f"HTTP {response.status_code}: {error_body.get('message', 'Server error')}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                    raise FuzentryError(
                        response.status_code,
                        error_body.get('message', f'HTTP {response.status_code}'),
                        error_body
                    )
                
                # Success
                return {
                    'data': response.json() if response.content else {},
                    'status': response.status_code,
                    'headers': {
                        'budgetRemaining': response.headers.get('X-Budget-Remaining'),
                        'rateLimit': response.headers.get('X-RateLimit-Remaining')
                    }
                }
                
            except requests.exceptions.Timeout:
                if attempt >= max_retries:
                    raise FuzentryError(408, "Request timeout")
                time.sleep(2 ** attempt)
                
            except requests.exceptions.RequestException as e:
                if attempt >= max_retries:
                    raise FuzentryError(500, str(e))
                time.sleep(2 ** attempt)
        
        # Should not reach here, but just in case
        raise FuzentryError(500, str(last_error) if last_error else "Unknown error")
    
    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        return self.request('GET', path, **kwargs)
    
    def post(self, path: str, body: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """POST request"""
        return self.request('POST', path, body=body, **kwargs)
    
    def put(self, path: str, body: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        return self.request('PUT', path, body=body, **kwargs)
    
    def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        return self.request('DELETE', path, **kwargs)
