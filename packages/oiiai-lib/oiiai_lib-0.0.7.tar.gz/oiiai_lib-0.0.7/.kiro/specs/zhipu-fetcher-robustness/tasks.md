# Implementation Plan

- [x] 1. Implement Session management in FetchBase
  - [x] 1.1 Add shared Session with thread-safe initialization
    - Add `_session` class variable and `_session_lock` for thread safety
    - Implement `_get_session()` classmethod that creates or returns existing Session
    - Configure default headers (User-Agent) and timeout (30s) on Session creation
    - _Requirements: 1.1, 1.2_
  - [ ]* 1.2 Write property test for Session sharing
    - **Property 1: Session Sharing**
    - **Validates: Requirements 1.1**
  - [x] 1.3 Implement `close_session()` classmethod
    - Close the shared Session if it exists
    - Set `_session` to None after closing
    - _Requirements: 1.3_
  - [x] 1.4 Implement `_http_get()` method
    - Use shared Session for GET requests
    - Merge custom headers with Session defaults
    - Use provided timeout or default 30s
    - _Requirements: 2.1, 2.3, 2.4_
  - [x] 1.5 Implement `_http_post()` method
    - Use shared Session for POST requests
    - Support JSON payload
    - Merge custom headers with Session defaults
    - _Requirements: 2.2, 2.3, 2.4_
  - [ ]* 1.6 Write property test for header merging
    - **Property 2: Header Merging**
    - **Validates: Requirements 2.3**
  - [ ]* 1.7 Write unit tests for Session management
    - Test `_get_session()` returns same instance
    - Test `close_session()` cleanup
    - Test default timeout behavior
    - _Requirements: 1.1, 1.2, 1.3, 2.4_

- [x] 2. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Migrate existing Fetchers to use new HTTP methods
  - [x] 3.1 Update FetchOpenRouter to use `_http_get()`
    - Replace `requests.get()` with `self._http_get()`
    - Remove redundant timeout parameter if using default
    - _Requirements: 1.1_
  - [x] 3.2 Update FetchSiliconFlow to use `_http_get()`
    - Replace `requests.get()` with `self._http_get()`
    - _Requirements: 1.1_
  - [x] 3.3 Update FetchModelScope to use `_http_get()`
    - Replace `requests.get()` with `self._http_get()`
    - _Requirements: 1.1_
  - [x] 3.4 Update FetchIFlow to use `_http_post()`
    - Replace `requests.post()` with `self._http_post()`
    - _Requirements: 1.1_
  - [x] 3.5 Update FetchNova to use `_http_get()`
    - Replace `requests.get()` with `self._http_get()`
    - Update both `fetch_models()` and `fetch_models_raw()`
    - _Requirements: 1.1_
  - [x] 3.6 Update FetchZhipu to use `_http_get()`
    - Replace `urllib.request` with `self._http_get()`
    - Remove manual gzip/brotli decompression (requests handles this)
    - _Requirements: 1.1_

- [x] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement multi-strategy parsing for FetchZhipu
  - [x] 5.1 Refactor existing parser as `_parse_by_section_id()`
    - Extract current ZhipuModelParser logic into dedicated method
    - Return `Dict[str, List[str]]` or empty dict on failure
    - _Requirements: 3.1, 5.1_
  - [x] 5.2 Implement `_parse_by_table_headers()` strategy
    - Detect tables by looking for header cells containing "模型" or "Model"
    - Extract first column values as model names
    - Return empty dict if no suitable tables found
    - _Requirements: 3.1, 5.1_
  - [x] 5.3 Implement `_parse_by_model_pattern()` strategy
    - Use regex patterns for known model names (glm-*, chatglm-*, etc.)
    - Scan entire HTML for matches
    - Return models under "unknown" category
    - _Requirements: 3.2, 5.1_
  - [x] 5.4 Implement strategy cascade in `_extract_model_names()`

    - Try strategies in order: section_id → table_headers → pattern
    - Stop on first successful strategy (non-empty result)
    - Log which strategy succeeded at DEBUG level
    - _Requirements: 3.1, 3.2, 3.4_
  - [ ]* 5.5 Write property test for strategy cascade
    - **Property 3: Strategy Cascade**
    - **Validates: Requirements 3.1, 3.2, 3.3**
  - [ ]* 5.6 Write property test for strategy independence
    - **Property 7: Strategy Independence**
    - **Validates: Requirements 5.3**

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement structure validation and degradation detection
  - [x] 7.1 Implement `_validate_structure()` method
    - Check for expected markers: table, tbody, headings with "模型"
    - Return False if markers missing
    - _Requirements: 4.1_
  - [x] 7.2 Add degradation detection in `fetch_models()`
    - Log warning if `_validate_structure()` returns False
    - Log warning if model count < `min_model_threshold` (default: 5)
    - _Requirements: 4.1, 4.2_
  - [x] 7.3 Add success logging
    - Log strategy name and model count at DEBUG level on success
    - _Requirements: 3.4, 4.3_
  - [ ]* 7.4 Write property test for degradation detection
    - **Property 4: Degradation Detection**
    - **Validates: Requirements 4.1, 4.2**
  - [ ]* 7.5 Write property test for success logging
    - **Property 5: Success Logging**
    - **Validates: Requirements 3.4, 4.3**

- [x] 8. Implement static fallback mechanism





  - [x] 8.1 Add fallback configuration to FetchZhipu


    - Add `fallback_models` parameter to `__init__`
    - Add `min_model_threshold` parameter (default: 5)
    - _Requirements: 6.1_

  - [x] 8.2 Implement fallback logic in `fetch_models()`


    - Return fallback list when all strategies fail and fallback is configured
    - Log warning when using fallback
    - Return empty list when no fallback and all strategies fail
    - _Requirements: 6.1, 6.2, 6.3_
  - [ ]* 8.3 Write property test for fallback behavior
    - **Property 6: Fallback Behavior**
    - **Validates: Requirements 6.1, 6.2, 6.3**

- [x] 9. Final Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Update README and Docs


- [x] 11. 创建单侧测试脚本测试真是环境原始输出像“[text](../../../tests/fetchModelList/TestRawData.py)”。

- [x] 12. zhipu.py经过上面的任务的修改之后抓取失败。分析model-overview.html（F12内复制粘贴下来的真实Response内容），为什么会抓取失败，修改强化内容。可以加入的抓取模块（包括但不限于）可以是beautifulsoup、scrapy、pandas强化数据处理。

  **问题分析:**
  1. **Brotli 编码问题**: 原有的 `_fetch_html` 方法请求了 `Accept-Encoding: gzip, deflate, br`，但服务器返回的 brotli 编码响应没有被 requests 库正确解码，导致获取到乱码内容
  2. **HTML 结构变化**: 原有的 `ZhipuSectionIdParser` 查找 `id` 属性中包含 "模型" 的标题（如 `id="xxx模型xxx"`），但实际 HTML 结构中标题的 `id` 是完整的分类名（如 `id="文本模型"`、`id="视觉模型"` 等）
  3. **解析器局限性**: 基于 `HTMLParser` 的解析器对复杂的 Next.js 渲染页面处理能力有限

  **修复内容:**
  1. 添加了 `beautifulsoup4>=4.12.0` 和 `lxml>=5.0.0` 依赖到 `requirements.txt` 和 `pyproject.toml`
  2. 新增了 BeautifulSoup 解析策略 (`_parse_with_beautifulsoup`)，作为最优先的解析方法（Strategy 0）
  3. 定义了已知的分类 ID 列表 `ZHIPU_CATEGORY_IDS = ["文本模型", "视觉模型", "图像生成模型", "视频生成模型", "语音模型", "向量模型", "知识检索模型"]`
  4. 修复了 `_fetch_html` 方法，移除了 brotli 编码请求（改为 `Accept-Encoding: gzip, deflate`）
  5. 更新了 `_validate_structure` 方法以正确检测新的 HTML 结构
  6. 更新了 `ZhipuSectionIdParser` 以支持已知分类 ID
  7. 更新了模型名称正则模式以支持新版本号格式（如 `glm-4.6`, `glm-4.5v`）

  **测试结果:**
  - 成功从智谱官方文档页面抓取到 28 个模型
  - 模型分类: 文本模型(12), 视觉模型(7), 图像生成模型(2), 视频生成模型(5), 向量模型(2)
  - 所有 19 个单元测试通过

- [x] 13. 检查Docs、README是否需要更新，需要更新时更新



