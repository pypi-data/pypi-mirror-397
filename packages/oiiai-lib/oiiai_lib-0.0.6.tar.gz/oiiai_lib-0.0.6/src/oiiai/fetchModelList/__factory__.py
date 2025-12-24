"""
Factory function for simplified model fetching
"""

from typing import Any, Dict, List, Optional, Union

from .zhipu import FetchZhipu
from .openrouter import FetchOpenRouter
from .modelscope import FetchModelScope
from .siliconflow import FetchSiliconFlow
from .iflow import FetchIFlow
from .nova import FetchNova
from .groq import FetchGroq

# Provider name to class mapping
_PROVIDERS = {
    "zhipu": FetchZhipu,
    "openrouter": FetchOpenRouter,
    "modelscope": FetchModelScope,
    "siliconflow": FetchSiliconFlow,
    "iflow": FetchIFlow,
    "nova": FetchNova,
    "groq": FetchGroq,
}

# Providers that require API key
_KEY_REQUIRED = {"siliconflow", "nova", "groq"}
_KEY_OPTIONAL = {"openrouter"}


def list_providers() -> List[str]:
    """
    List all supported provider names.

    Returns:
        Sorted list of provider names.

    Examples:
        >>> from oiiai import list_providers
        >>> list_providers()
        ['groq', 'iflow', 'modelscope', 'nova', 'openrouter', 'siliconflow', 'zhipu']
    """
    return sorted(_PROVIDERS.keys())


def fetch_models(
    provider: str, api_key: Optional[str] = None, raw: bool = False, **kwargs
) -> Union[List[str], Dict[str, Any]]:
    """
    Fetch model list from specified provider.

    Args:
        provider: Provider name (zhipu, openrouter, modelscope, siliconflow, iflow, nova, groq)
        api_key: API key (optional for some providers, reads from env var if not provided)
        raw: If True, return raw API response (only supported by nova, groq)
        **kwargs: Additional arguments passed to the fetcher constructor

    Returns:
        List of model IDs, or raw API response dict if raw=True

    Raises:
        ValueError: If provider is not supported

    Examples:
        >>> from oiiai import fetch_models
        >>> models = fetch_models("zhipu")
        >>> models = fetch_models("groq", api_key="xxx")
        >>> models = fetch_models("groq")  # reads from GROQ_API_KEY
        >>> raw = fetch_models("groq", raw=True)
    """
    provider_lower = provider.lower()

    if provider_lower not in _PROVIDERS:
        supported = ", ".join(sorted(_PROVIDERS.keys()))
        raise ValueError(f"Unknown provider: {provider}. Supported: {supported}")

    fetcher_class = _PROVIDERS[provider_lower]

    # Build constructor arguments
    if provider_lower in _KEY_REQUIRED or provider_lower in _KEY_OPTIONAL:
        fetcher = fetcher_class(api_key=api_key, **kwargs)
    else:
        fetcher = fetcher_class(**kwargs)

    # Fetch models
    if raw:
        if hasattr(fetcher, "fetch_models_raw"):
            return fetcher.fetch_models_raw()
        else:
            # Fallback: return empty dict for providers without raw support
            return {}

    return fetcher.fetch_models()
