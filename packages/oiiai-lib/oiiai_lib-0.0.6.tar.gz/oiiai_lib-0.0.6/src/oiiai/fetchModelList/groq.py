"""
Groq model list fetching
"""

import os
import requests
from typing import Any, Dict, List

from .__base__ import FetchBase

GROQ_API_URL = "https://api.groq.com/openai/v1/models"


class FetchGroq(FetchBase):
    """Groq model list fetcher"""

    def __init__(self, api_key: str = None):
        """
        Initialize Groq model fetcher.

        Args:
            api_key: Groq API key. If not provided, reads from GROQ_API_KEY env var.
        """
        self._api_key = api_key or os.getenv("GROQ_API_KEY", "")

    @property
    def provider(self) -> str:
        return "groq"

    def fetch_models(self) -> List[str]:
        """
        Fetch model list in unified format.

        Returns:
            List of model ID strings extracted from the API response.
        """
        if not self._api_key:
            return self._handle_missing_env_var("GROQ_API_KEY")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._http_get(GROQ_API_URL, headers=headers)
            response.raise_for_status()

            data = response.json()
            models = data.get("data", [])

            if not isinstance(models, list):
                return self._handle_unexpected_format(data)

            return [m.get("id") for m in models if m.get("id")]
        except requests.exceptions.RequestException as e:
            return self._handle_http_error(e)

    def fetch_models_raw(self) -> Dict[str, Any]:
        """
        Fetch raw API response.

        Returns:
            Complete JSON response from Groq API as dictionary.
        """
        if not self._api_key:
            self._log_warning(
                f"[{self.provider}] Missing environment variable: GROQ_API_KEY"
            )
            return {}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._http_get(GROQ_API_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._log_error(
                f"[{self.provider}] HTTP request failed: {e}", exc_info=True
            )
            return {}
