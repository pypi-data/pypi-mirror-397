"""
Model list fetching base class
"""

import logging
import threading
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, List, Optional

import requests

from .__log_config__ import LOGGER_NAMESPACE


class FetchBase(ABC):
    """Model list fetching base class with integrated logging and error handling."""

    # Shared Session instance for connection reuse across all Fetcher subclasses
    _session: ClassVar[Optional[requests.Session]] = None
    _session_lock: ClassVar[threading.Lock] = threading.Lock()
    _default_timeout: ClassVar[int] = 30
    _default_headers: ClassVar[Dict[str, str]] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    @classmethod
    def _get_session(cls) -> requests.Session:
        """
        Get or create shared Session instance (thread-safe).

        Returns:
            Shared requests.Session instance configured with default headers.
        """
        if cls._session is None:
            with cls._session_lock:
                # Double-check locking pattern
                if cls._session is None:
                    session = requests.Session()
                    session.headers.update(cls._default_headers)
                    cls._session = session
        return cls._session

    @classmethod
    def close_session(cls) -> None:
        """
        Close shared Session and release resources.

        Thread-safe method to close the shared Session if it exists.
        """
        with cls._session_lock:
            if cls._session is not None:
                cls._session.close()
                cls._session = None

    def _http_get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make GET request using shared Session.

        Args:
            url: The URL to request.
            headers: Optional custom headers to merge with Session defaults.
            timeout: Optional timeout in seconds (default: 30s).

        Returns:
            requests.Response object.

        Raises:
            requests.RequestException: On HTTP errors.
        """
        session = self._get_session()
        effective_timeout = timeout if timeout is not None else self._default_timeout

        # Merge custom headers with session defaults (custom takes precedence)
        merged_headers = dict(session.headers)
        if headers:
            merged_headers.update(headers)

        return session.get(url, headers=merged_headers, timeout=effective_timeout)

    def _http_post(
        self,
        url: str,
        json: Any = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        """
        Make POST request using shared Session.

        Args:
            url: The URL to request.
            json: Optional JSON payload to send.
            headers: Optional custom headers to merge with Session defaults.
            timeout: Optional timeout in seconds (default: 30s).

        Returns:
            requests.Response object.

        Raises:
            requests.RequestException: On HTTP errors.
        """
        session = self._get_session()
        effective_timeout = timeout if timeout is not None else self._default_timeout

        # Merge custom headers with session defaults (custom takes precedence)
        merged_headers = dict(session.headers)
        if headers:
            merged_headers.update(headers)

        return session.post(
            url, json=json, headers=merged_headers, timeout=effective_timeout
        )

    @property
    @abstractmethod
    def provider(self) -> str:
        """Provider identifier, such as 'zhipu', 'openrouter'"""
        pass

    @abstractmethod
    def fetch_models(self) -> List[str]:
        """Fetch model list from remote"""
        pass

    @property
    def _logger(self) -> logging.Logger:
        """
        Get a logger instance with the provider name as identifier.

        Returns:
            Logger instance namespaced under oiiai.fetchModelList.{provider}
        """
        return logging.getLogger(f"{LOGGER_NAMESPACE}.{self.provider}")

    def _log_error(self, message: str, exc_info: bool = False) -> None:
        """
        Log an ERROR level message.

        Args:
            message: The error message to log.
            exc_info: Whether to include exception info (default: False).
        """
        self._logger.error(message, exc_info=exc_info)

    def _log_warning(self, message: str) -> None:
        """
        Log a WARNING level message.

        Args:
            message: The warning message to log.
        """
        self._logger.warning(message)

    def _log_info(self, message: str) -> None:
        """
        Log an INFO level message.

        Args:
            message: The info message to log.
        """
        self._logger.info(message)

    def _log_debug(self, message: str) -> None:
        """
        Log a DEBUG level message.

        Args:
            message: The debug message to log.
        """
        self._logger.debug(message)

    def _handle_http_error(self, error: Exception) -> List[str]:
        """
        Handle HTTP request errors by logging and returning empty list.

        Args:
            error: The exception that occurred during HTTP request.

        Returns:
            Empty list to indicate no models were fetched.
        """
        self._log_error(
            f"[{self.provider}] HTTP request failed: {error}", exc_info=True
        )
        return []

    def _handle_unexpected_format(self, data: Any) -> List[str]:
        """
        Handle unexpected API response format by logging and returning empty list.

        Args:
            data: The unexpected data received from the API.

        Returns:
            Empty list to indicate no models were fetched.
        """
        self._log_warning(
            f"[{self.provider}] Unexpected API response format: {type(data).__name__}"
        )
        return []

    def _handle_missing_env_var(self, var_name: str) -> List[str]:
        """
        Handle missing environment variable by logging and returning empty list.

        Args:
            var_name: The name of the missing environment variable.

        Returns:
            Empty list to indicate no models were fetched.
        """
        self._log_warning(f"[{self.provider}] Missing environment variable: {var_name}")
        return []
