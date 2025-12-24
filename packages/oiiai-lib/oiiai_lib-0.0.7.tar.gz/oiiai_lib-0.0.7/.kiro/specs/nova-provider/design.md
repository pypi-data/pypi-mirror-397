# Design Document: Nova Provider

## Overview

This document describes the technical design for implementing a Nova (Amazon) provider for the fetchModelList module. The Nova provider will fetch available AI models from Amazon's Nova API (`https://api.nova.amazon.com/v1/models`) and return them in the unified format used by other providers, while also supporting an option to return the raw API response.

## Architecture

The Nova provider follows the existing provider architecture pattern established in the codebase:

```
┌─────────────────────────────────────────────────────────┐
│                      FetchBase                          │
│  (Abstract base class with logging and error handling)  │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │ extends
┌─────────────────────────────────────────────────────────┐
│                      FetchNova                          │
│  - api_key: str                                         │
│  - provider: "nova"                                     │
│  + fetch_models() -> List[str]                          │
│  + fetch_models_raw() -> Dict[str, Any]                 │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### FetchNova Class

```python
class FetchNova(FetchBase):
    """Nova (Amazon) model list fetcher"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Nova model fetcher.
        
        Args:
            api_key: Nova API key. If not provided, reads from NOVA_API_KEY env var.
        """
        
    @property
    def provider(self) -> str:
        """Returns 'nova'"""
        
    def fetch_models(self) -> List[str]:
        """
        Fetch model list in unified format.
        
        Returns:
            List of model ID strings extracted from the API response.
        """
        
    def fetch_models_raw(self) -> Dict[str, Any]:
        """
        Fetch raw API response.
        
        Returns:
            Complete JSON response from Nova API as dictionary.
        """
```

### API Configuration

| Parameter | Value |
|-----------|-------|
| Base URL | `https://api.nova.amazon.com/v1/models` |
| Method | GET |
| Auth Header | `Authorization: Bearer {api_key}` |
| Content-Type | `application/json` |
| Timeout | 30 seconds |

## Data Models

### Nova API Response Structure

```python
# Raw API Response
{
    "object": "list",
    "data": [
        {
            "created": int,           # Unix timestamp
            "description": str,       # Model description
            "display name": str,      # Human-readable name
            "id": str,                # Model identifier (extracted for unified format)
            "owned_by": str,          # Owner (e.g., "amazon", "developeralias1")
            "type": str               # "model" or "agent"
        },
        ...
    ]
}

# Unified Format (fetch_models return)
List[str]  # e.g., ["model1", "model2", "agent1"]
```

### Type Definitions

```python
from typing import List, Dict, Any, Optional

NovaModelItem = Dict[str, Any]  # Single model/agent entry
NovaRawResponse = Dict[str, Any]  # Complete API response
UnifiedModelList = List[str]  # List of model IDs
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the prework analysis, the following correctness properties have been identified:

### Property 1: Model ID Extraction Completeness

*For any* valid Nova API response containing a `data` array, calling `fetch_models()` SHALL return a list containing exactly the `id` field value from each item in the `data` array, preserving order.

**Validates: Requirements 1.1, 1.2**

### Property 2: Raw Response Preservation

*For any* valid Nova API response, calling `fetch_models_raw()` SHALL return the complete response dictionary unchanged, including all fields (`object`, `data` array with `created`, `description`, `display name`, `id`, `owned_by`, `type`).

**Validates: Requirements 2.1, 2.2**

### Property 3: Authorization Header Format

*For any* non-empty API key string, the HTTP request SHALL include an `Authorization` header with the value `Bearer {api_key}` where `{api_key}` is the exact key provided.

**Validates: Requirements 3.1, 3.2, 3.3**

## Error Handling

| Scenario | Behavior | Return Value |
|----------|----------|--------------|
| Missing API key (no param, no env var) | Log warning via `_handle_missing_env_var` | `[]` for fetch_models, `{}` for fetch_models_raw |
| Network/HTTP error | Log error via `_handle_http_error` | `[]` for fetch_models, `{}` for fetch_models_raw |
| Unexpected response format | Log warning via `_handle_unexpected_format` | `[]` for fetch_models |
| Empty `data` array | Normal processing | `[]` |

## Testing Strategy

### Unit Tests

Unit tests will cover:
- Constructor with explicit API key
- Constructor with environment variable fallback
- Missing API key handling
- Provider property returns "nova"
- Class inheritance from FetchBase
- Module export in `__init__.py`

### Property-Based Tests

Using `hypothesis` library (consistent with Python ecosystem):

1. **Property 1 Test**: Generate random valid API responses with varying `data` arrays, verify `fetch_models()` extracts all and only the `id` fields.

2. **Property 2 Test**: Generate random valid API responses, verify `fetch_models_raw()` returns identical data.

3. **Property 3 Test**: Generate random API key strings, verify the Authorization header is correctly formatted.

### Test Configuration

- Property tests: minimum 100 iterations per property
- Each property test annotated with: `**Feature: nova-provider, Property {N}: {description}**`
- Tests located in `tests/fetchModelList/test_nova.py`
