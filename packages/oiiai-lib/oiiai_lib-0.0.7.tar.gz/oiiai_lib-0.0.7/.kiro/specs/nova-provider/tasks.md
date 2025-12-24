# Implementation Plan

- [x] 1. Create FetchNova class implementation
  - [x] 1.1 Create `src/oiiai/fetchModelList/nova.py` with FetchNova class
    - Implement `__init__` with api_key parameter and NOVA_API_KEY env var fallback
    - Implement `provider` property returning "nova"
    - Implement `fetch_models()` returning `List[str]`
    - Implement `fetch_models_raw()` returning `Dict[str, Any]`
    - Use requests library for HTTP GET to `https://api.nova.amazon.com/v1/models`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

  - [x] 1.2 Update `src/oiiai/fetchModelList/__init__.py` to export FetchNova
    - Add import for FetchNova
    - Add FetchNova to `__all__` list
    - _Requirements: 4.4_

- [x] 2. Implement tests for FetchNova
  - [x] 2.1 Create unit tests in `tests/fetchModelList/test_nova.py`
    - Test constructor with explicit API key
    - Test constructor with environment variable fallback
    - Test missing API key returns empty list
    - Test provider property returns "nova"
    - Test FetchNova is instance of FetchBase
    - _Requirements: 1.3, 3.1, 3.2, 4.1, 4.2, 4.3_

  - [ ]* 2.2 Write property test for model ID extraction
    - **Property 1: Model ID Extraction Completeness**
    - **Validates: Requirements 1.1, 1.2**
    - Use hypothesis to generate random valid API responses
    - Verify fetch_models extracts all id fields from data array

  - [ ]* 2.3 Write property test for raw response preservation
    - **Property 2: Raw Response Preservation**
    - **Validates: Requirements 2.1, 2.2**
    - Use hypothesis to generate random valid API responses
    - Verify fetch_models_raw returns identical response

  - [ ]* 2.4 Write property test for authorization header format
    - **Property 3: Authorization Header Format**
    - **Validates: Requirements 3.1, 3.2, 3.3**
    - Use hypothesis to generate random API key strings
    - Verify Authorization header is formatted as `Bearer {api_key}`

- [x] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update README and Docs

- [x] 5. 更新文档的协作风格，现在的文档将所有供应商的写法都写了一边，比较低效率，可以使用个例的写法，需要api_key的写一个例子，不需要的写一个例子。其他就用占位符加上可选参数列表的方式写示例。








