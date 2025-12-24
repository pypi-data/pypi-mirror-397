import requests
import os
from typing import List
from .__base__ import FetchBase


class FetchSiliconFlow(FetchBase):
    """SiliconFlow 模型列表获取器"""

    def __init__(self, api_key: str = None):
        """
        初始化 SiliconFlow 模型获取器。

        Args:
            api_key: SiliconFlow API Key，未提供时从环境变量 SILICONFLOW_API_KEY 读取
        """
        self._api_key = api_key or os.getenv("SILICONFLOW_API_KEY", "")

    @property
    def provider(self) -> str:
        return "siliconflow"

    def fetch_models(self) -> List[str]:
        url = "https://api.siliconflow.cn/v1/models"
        if not self._api_key:
            return self._handle_missing_env_var("SILICONFLOW_API_KEY")

        headers = {"Authorization": f"Bearer {self._api_key}"}

        try:
            response = self._http_get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Assume API directly returns list of model IDs or in 'data' field
            # Adjust according to actual API response structure
            if (
                isinstance(data, dict)
                and "data" in data
                and isinstance(data["data"], list)
            ):
                return [model["id"] for model in data["data"]]
            elif isinstance(data, list):
                return data
            else:
                return self._handle_unexpected_format(data)
        except requests.exceptions.RequestException as e:
            return self._handle_http_error(e)
