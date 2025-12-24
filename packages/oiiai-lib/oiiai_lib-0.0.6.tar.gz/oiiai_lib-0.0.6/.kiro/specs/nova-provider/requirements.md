# Requirements Document

## Introduction

This document specifies the requirements for implementing a Nova (Amazon) provider for the fetchModelList module. The Nova provider will fetch available AI models from Amazon's Nova API and return them in the unified format used by other providers in the oiiai library, while also supporting an option to return the raw API response.

## Glossary

- **Nova**: Amazon's AI model service accessible via API at `api.nova.amazon.com`
- **Provider**: A class that fetches model lists from a specific AI service (e.g., OpenRouter, SiliconFlow, Nova)
- **Unified Format**: The standard `List[str]` return type containing model IDs used across all providers
- **Raw Response**: The original JSON response body returned by the Nova API without transformation
- **NOVA_API_KEY**: Environment variable containing the Bearer token for Nova API authentication

## Requirements

### Requirement 1

**User Story:** As a developer, I want to fetch the list of available models from Amazon Nova API, so that I can discover and use Nova's AI models in my applications.

#### Acceptance Criteria

1. WHEN a user calls `fetch_models()` on FetchNova THEN the system SHALL return a list of model ID strings extracted from the Nova API response
2. WHEN the Nova API returns a response with a `data` array THEN the system SHALL extract the `id` field from each item in the array
3. WHEN the NOVA_API_KEY environment variable is not set and no API key is provided THEN the system SHALL log a warning and return an empty list
4. WHEN the Nova API request fails due to network or HTTP errors THEN the system SHALL log the error and return an empty list

### Requirement 2

**User Story:** As a developer, I want to optionally retrieve the raw API response from Nova, so that I can access additional model metadata like description, display name, and ownership information.

#### Acceptance Criteria

1. WHEN a user calls `fetch_models_raw()` on FetchNova THEN the system SHALL return the complete JSON response from the Nova API as a dictionary
2. WHEN the raw response is requested and the API call succeeds THEN the system SHALL return the full response including `object`, `data` array with all fields (created, description, display name, id, owned_by, type)
3. WHEN the raw response is requested and the API call fails THEN the system SHALL return an empty dictionary and log the error

### Requirement 3

**User Story:** As a developer, I want to provide the Nova API key either programmatically or via environment variable, so that I can flexibly configure authentication.

#### Acceptance Criteria

1. WHEN a user instantiates FetchNova with an `api_key` parameter THEN the system SHALL use that key for API authentication
2. WHEN a user instantiates FetchNova without an `api_key` parameter THEN the system SHALL read the key from the NOVA_API_KEY environment variable
3. WHEN making API requests THEN the system SHALL include the Authorization header in the format `Bearer {api_key}`

### Requirement 4

**User Story:** As a developer, I want the Nova provider to follow the same patterns as other providers, so that I can use it consistently with the rest of the library.

#### Acceptance Criteria

1. WHEN FetchNova is implemented THEN the system SHALL extend the FetchBase abstract class
2. WHEN FetchNova is implemented THEN the system SHALL implement the `provider` property returning "nova"
3. WHEN FetchNova is implemented THEN the system SHALL implement the `fetch_models()` method returning `List[str]`
4. WHEN FetchNova is added to the module THEN the system SHALL export it from `__init__.py`
