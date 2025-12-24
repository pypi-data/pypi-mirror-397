import requests
from typing import List
from .__base__ import FetchBase


class FetchIFlow(FetchBase):
    """IFlow model list fetcher"""

    @property
    def provider(self) -> str:
        return "iflow"

    def fetch_models(self) -> List[str]:
        """
        Fetch model list from IFlow
        """
        url = "https://iflow.cn/api/platform/models/list"

        headers = {
            "Content-Type": "application/json",
            # "Cookie": "..." # Tested, this interface does not require Cookie to access
        }

        payload = {}

        try:
            # POST request using shared Session
            response = self._http_post(url, json=payload, headers=headers)

            response.raise_for_status()
            data = response.json()

            models = []

            if (
                isinstance(data, dict)
                and "data" in data
                and isinstance(data["data"], dict)
            ):
                for category, model_list in data["data"].items():
                    if isinstance(model_list, list):
                        for model in model_list:
                            if isinstance(model, dict):
                                # Prioritize using modelName, if not available try other fields
                                model_name = (
                                    model.get("modelName")
                                    or model.get("showName")
                                    or model.get("id")
                                )
                                if model_name:
                                    models.append(str(model_name))

            return models

        except requests.exceptions.RequestException as e:
            return self._handle_http_error(e)
