# Requirements Document

## Introduction

本规格定义了对模型列表抓取器的健壮性改进，包含两个层面：

1. **基类层面 (FetchBase)**: 为所有 Fetcher（OpenRouter、SiliconFlow、ModelScope、IFlow、Nova、Zhipu）提供统一的 HTTP Session 复用机制，减少高频调用时的连接开销。

2. **Zhipu 特有层面 (FetchZhipu)**: 增强 HTML 解析的容错能力。由于智谱官方未提供统一的模型列表 API，HTML 解析仍是主要获取方式，需要多策略解析和结构变化检测。

## Glossary

- **FetchBase**: 所有模型列表抓取器的抽象基类
- **FetchZhipu**: 智谱 AI 模型列表抓取器类，继承自 `FetchBase`
- **ZhipuModelParser**: 基于 `HTMLParser` 的智谱文档页面解析器
- **Section ID**: HTML 标题标签（h2/h3）的 id 属性，用于识别模型分类
- **Session**: HTTP 会话对象（`requests.Session`），支持连接复用和持久化配置
- **Connection Pooling**: TCP 连接池，允许多个请求复用同一连接
- **Fallback Strategy**: 主策略失败时的备用解析策略
- **Model Pattern**: 智谱模型名称的命名模式（如 `glm-*`, `chatglm-*`）

## Requirements

### Requirement 1

**User Story:** As a system integrator making frequent API calls across multiple providers, I want HTTP connections to be reused across all Fetcher instances, so that connection overhead is minimized globally.

#### Acceptance Criteria

1. WHEN any Fetcher subclass (OpenRouter, SiliconFlow, ModelScope, IFlow, Nova, Zhipu) makes HTTP requests THEN the FetchBase SHALL provide a shared Session instance for connection reuse
2. WHEN a Session is created THEN the FetchBase SHALL configure it with default timeout (30 seconds) and common headers
3. WHEN the application explicitly requests cleanup THEN the FetchBase SHALL provide a method to close the shared Session and release resources
4. WHEN an HTTP request fails due to connection issues THEN the Fetcher SHALL have the option to retry with a fresh connection

### Requirement 2

**User Story:** As a developer using any Fetcher, I want a consistent HTTP request interface in the base class, so that subclasses can make requests without managing Session lifecycle.

#### Acceptance Criteria

1. WHEN a subclass needs to make a GET request THEN the FetchBase SHALL provide a `_http_get(url, headers, timeout)` method using the shared Session
2. WHEN a subclass needs to make a POST request THEN the FetchBase SHALL provide a `_http_post(url, headers, json, timeout)` method using the shared Session
3. WHEN custom headers are provided THEN the request methods SHALL merge them with default Session headers
4. WHEN timeout is not specified THEN the request methods SHALL use the default timeout of 30 seconds

### Requirement 3

**User Story:** As a developer using FetchZhipu, I want the HTML parser to gracefully handle documentation structure changes, so that minor page updates don't break model list fetching.

#### Acceptance Criteria

1. WHEN the primary parsing strategy (section ID based) fails to extract any models THEN the FetchZhipu SHALL attempt a fallback strategy based on table header detection
2. WHEN both section ID and table header strategies fail THEN the FetchZhipu SHALL attempt a pattern-based extraction using known model name patterns (glm-*, chatglm-*, codegeex-*, cogview-*, cogvideo-*)
3. WHEN all parsing strategies fail to extract models THEN the FetchZhipu SHALL log a warning with diagnostic information and return an empty list
4. WHEN a parsing strategy succeeds THEN the FetchZhipu SHALL log which strategy was used at DEBUG level

### Requirement 4

**User Story:** As a developer, I want the Zhipu parser to detect and report structural changes in the documentation page, so that I can proactively update the parser before it completely fails.

#### Acceptance Criteria

1. WHEN the HTML content lacks expected structural markers (table, tbody, model-related headings) THEN the FetchZhipu SHALL log a warning indicating potential structure change
2. WHEN the number of extracted models is significantly lower than a configurable threshold (default: 5) THEN the FetchZhipu SHALL log a warning suggesting possible parsing degradation
3. WHEN parsing completes successfully THEN the FetchZhipu SHALL include the extraction strategy name and model count in DEBUG log output

### Requirement 5

**User Story:** As a maintainer, I want the Zhipu model name extraction logic to be modular and testable, so that I can easily add or modify parsing strategies.

#### Acceptance Criteria

1. WHEN implementing parsing strategies THEN each strategy SHALL be encapsulated in a separate method with a consistent interface returning `Dict[str, List[str]]`
2. WHEN adding a new parsing strategy THEN the strategy SHALL be registerable without modifying the main extraction logic
3. WHEN testing parsing strategies THEN each strategy SHALL be independently testable with sample HTML fixtures

### Requirement 6

**User Story:** As a developer, I want to optionally provide a static fallback model list for Zhipu, so that the system can return known models when all dynamic parsing fails.

#### Acceptance Criteria

1. WHERE a static fallback list is configured THEN the FetchZhipu SHALL return the fallback list when all parsing strategies fail
2. WHEN using the static fallback THEN the FetchZhipu SHALL log a warning indicating fallback usage
3. WHEN no fallback is configured AND all strategies fail THEN the FetchZhipu SHALL return an empty list as before
