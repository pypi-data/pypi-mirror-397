import requests
from typing import List
from .__base__ import FetchBase


class FetchModelScope(FetchBase):
    @property
    def provider(self) -> str:
        return "modelscope"

    def fetch_models(self) -> List[str]:
        url = "https://api-inference.modelscope.cn/v1/models"
        try:
            response = self._http_get(url)
            response.raise_for_status()
            data = response.json()
            # Assume API directly returns list of model IDs or in 'data' field
            # Adjust according to actual API response structure
            if isinstance(data, list):
                return data
            elif (
                isinstance(data, dict)
                and "data" in data
                and isinstance(data["data"], list)
            ):
                return [model["id"] for model in data["data"]]
            else:
                return self._handle_unexpected_format(data)
        except requests.exceptions.RequestException as e:
            return self._handle_http_error(e)
