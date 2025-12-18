"""
PromptJudge Python SDK
A client library for the PromptJudge AI Security API.
"""

import requests
from typing import Dict, Any, Optional

__version__ = "1.0.0"
__author__ = "PromptJudge"


class PromptJudgeError(Exception):
    """Base exception for PromptJudge errors."""
    pass


class AuthenticationError(PromptJudgeError):
    """Raised when API key is invalid or missing."""
    pass


class NetworkError(PromptJudgeError):
    """Raised when a network error occurs."""
    pass


class APIError(PromptJudgeError):
    """Raised when the API returns an error response."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class ScanResult:
    """Represents the result of a prompt scan."""
    
    def __init__(self, safe: bool, reason: str):
        self.safe = safe
        self.reason = reason
    
    def __repr__(self) -> str:
        return f"ScanResult(safe={self.safe}, reason='{self.reason}')"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            "safe": self.safe,
            "reason": self.reason
        }


class PromptJudge:
    """
    PromptJudge API client.
    
    Args:
        api_key: Your PromptJudge API key.
        base_url: Optional custom base URL for the API.
        timeout: Request timeout in seconds (default: 30).
    
    Example:
        >>> from promptjudge import PromptJudge
        >>> client = PromptJudge(api_key="your-api-key")
        >>> result = client.scan("Hello, how are you?")
        >>> print(result.safe)
        True
    """
    
    DEFAULT_BASE_URL = "https://api.promptjudge.com"
    DEFAULT_TIMEOUT = 30
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        if not api_key:
            raise AuthenticationError("API key is required")
        
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"promptjudge-python/{__version__}"
        })
    
    def scan(self, prompt_text: str) -> ScanResult:
        """
        Scan a prompt for security issues.
        
        Args:
            prompt_text: The prompt text to analyze.
        
        Returns:
            ScanResult: An object containing 'safe' (bool) and 'reason' (str).
        
        Raises:
            AuthenticationError: If the API key is invalid.
            NetworkError: If a network error occurs.
            APIError: If the API returns an error response.
        
        Example:
            >>> result = client.scan("What is the weather today?")
            >>> if result.safe:
            ...     print("Prompt is safe to process")
            ... else:
            ...     print(f"Warning: {result.reason}")
        """
        if not isinstance(prompt_text, str):
            raise ValueError("prompt_text must be a string")
        
        if not prompt_text.strip():
            raise ValueError("prompt_text cannot be empty")
        
        url = f"{self.base_url}/v1/scan"
        payload = {"prompt": prompt_text}
        
        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self.timeout
            )
        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise NetworkError("Failed to connect to the API. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error occurred: {str(e)}")
        
        # Handle authentication errors
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key. Please check your credentials.")
        
        if response.status_code == 403:
            raise AuthenticationError("Access forbidden. Your API key may not have the required permissions.")
        
        # Handle other error responses
        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get("error", error_data.get("message", "Unknown error"))
            except ValueError:
                error_message = response.text or "Unknown error"
            
            raise APIError(
                f"API error: {error_message}",
                status_code=response.status_code
            )
        
        # Parse successful response
        try:
            data = response.json()
        except ValueError:
            raise APIError("Invalid JSON response from API")
        
        if "safe" not in data or "reason" not in data:
            raise APIError("Invalid response format: missing 'safe' or 'reason' field")
        
        return ScanResult(
            safe=bool(data["safe"]),
            reason=str(data["reason"])
        )
    
    def close(self):
        """Close the HTTP session."""
        self._session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# Convenience function for quick scanning
def scan(api_key: str, prompt_text: str) -> ScanResult:
    """
    Convenience function to scan a prompt without creating a client instance.
    
    Args:
        api_key: Your PromptJudge API key.
        prompt_text: The prompt text to analyze.
    
    Returns:
        ScanResult: An object containing 'safe' (bool) and 'reason' (str).
    
    Example:
        >>> from promptjudge import scan
        >>> result = scan("your-api-key", "Hello world")
        >>> print(result.safe)
    """
    with PromptJudge(api_key=api_key) as client:
        return client.scan(prompt_text)
