"""
OpenRouter model list fetching
"""

import os
import requests
from typing import List

from .__base__ import FetchBase

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/models"


class FetchOpenRouter(FetchBase):
    """OpenRouter model list fetcher"""

    def __init__(self, api_key: str = None):
        """
        Initialize OpenRouter model fetcher.

        Args:
            api_key: OpenRouter API key, if not provided, get from environment variable OPENROUTER_API_KEY
        """
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")

    @property
    def provider(self) -> str:
        return "openrouter"

    def fetch_models(self) -> List[str]:
        """Fetch available model list from OpenRouter API"""
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        try:
            response = self._http_get(OPENROUTER_API_URL, headers=headers)
            response.raise_for_status()

            data = response.json()
            models = data.get("data", [])

            if not isinstance(models, list):
                return self._handle_unexpected_format(data)

            return [m.get("id") for m in models if m.get("id")]
        except requests.exceptions.RequestException as e:
            return self._handle_http_error(e)
