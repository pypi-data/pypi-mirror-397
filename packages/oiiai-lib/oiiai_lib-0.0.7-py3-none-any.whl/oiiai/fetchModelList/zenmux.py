"""
Zenmux 模型列表获取
"""

import os
import requests
from typing import Any, Dict, List

from .__base__ import FetchBase

ZENMUX_API_URL = "https://zenmux.ai/api/v1/models"


class FetchZenmux(FetchBase):
    """Zenmux 模型列表获取器"""

    def __init__(self, api_key: str = None):
        """
        初始化 Zenmux 模型获取器。

        Args:
            api_key: Zenmux API Key，未提供时从环境变量 ZENMUX_API_KEY 读取
        """
        self._api_key = api_key or os.getenv("ZENMUX_API_KEY", "")

    @property
    def provider(self) -> str:
        return "zenmux"

    def fetch_models(self) -> List[str]:
        """
        获取模型列表（统一格式）。

        Returns:
            模型 ID 字符串列表
        """
        if not self._api_key:
            return self._handle_missing_env_var("ZENMUX_API_KEY")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._http_get(ZENMUX_API_URL, headers=headers)
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
        获取原始 API 响应。

        Returns:
            完整的 JSON 响应字典
        """
        if not self._api_key:
            self._log_warning(f"[{self.provider}] 缺少环境变量: ZENMUX_API_KEY")
            return {}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._http_get(ZENMUX_API_URL, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._log_error(f"[{self.provider}] HTTP 请求失败: {e}", exc_info=True)
            return {}
