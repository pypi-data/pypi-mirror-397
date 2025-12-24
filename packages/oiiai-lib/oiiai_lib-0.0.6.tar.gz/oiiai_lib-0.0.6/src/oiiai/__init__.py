"""
oiiai - 简单的 AI 模型调用工具包

提供模型列表获取和模型调用功能。
"""

from .fetchModelList import (
    FetchBase,
    FetchZhipu,
    FetchOpenRouter,
    FetchModelScope,
    FetchSiliconFlow,
    FetchIFlow,
    FetchNova,
    FetchGroq,
    fetch_models,
    list_providers,
    configure_logging,
    shutdown_logging,
)

__all__ = [
    # 模型列表获取
    "FetchBase",
    "FetchZhipu",
    "FetchOpenRouter",
    "FetchModelScope",
    "FetchSiliconFlow",
    "FetchIFlow",
    "FetchNova",
    "FetchGroq",
    "fetch_models",
    "list_providers",
    # 日志配置
    "configure_logging",
    "shutdown_logging",
]
