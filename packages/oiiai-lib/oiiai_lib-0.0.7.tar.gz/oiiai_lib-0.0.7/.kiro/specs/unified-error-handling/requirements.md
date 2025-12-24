# Requirements Document

## Introduction

本功能旨在统一 `fetchModelList` 模块中的错误处理和日志记录机制。当前多个 provider 实现使用 `print()` 输出错误信息，这不利于生产环境中的日志管理和调试。通过引入 `logging` 模块并在基类中添加通用错误处理方法，可以减少子类重复代码，提高代码质量和可维护性。

## Glossary

- **FetchBase**: 模型列表获取的抽象基类，定义了所有 provider 必须实现的接口
- **Provider**: 模型服务提供商，如 OpenRouter、SiliconFlow、Zhipu 等
- **Logger**: Python `logging` 模块中的日志记录器对象
- **Log Level**: 日志级别，包括 DEBUG、INFO、WARNING、ERROR、CRITICAL
- **QueueHandler**: Python logging 模块中的异步日志处理器，用于避免高并发场景下的日志写入阻塞
- **Structured Logging**: 结构化日志，使用 JSON 格式输出便于自动化处理和分析

## Requirements

### Requirement 1

**User Story:** As a developer, I want a centralized logging configuration in the base class, so that all providers use consistent logging behavior.

#### Acceptance Criteria

1. WHEN the FetchBase class is initialized THEN the system SHALL create a logger instance with the provider name as identifier
2. WHEN a subclass inherits from FetchBase THEN the system SHALL automatically inherit the logging configuration
3. WHEN logging is configured THEN the system SHALL support all standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
4. WHEN a custom log level is needed THEN the system SHALL allow configuration of the log level via parameter or environment variable

### Requirement 2

**User Story:** As a developer, I want common error handling methods in the base class, so that I can reduce duplicate error handling code in provider implementations.

#### Acceptance Criteria

1. WHEN an HTTP request fails THEN the system SHALL log the error with ERROR level including provider name and error details
2. WHEN an API returns unexpected data format THEN the system SHALL log a WARNING with the actual data structure received
3. WHEN an environment variable is missing THEN the system SHALL log a WARNING with the variable name and provider context
4. WHEN any error occurs during model fetching THEN the system SHALL return an empty list and log the error instead of raising an exception
5. WHEN a critical system error occurs THEN the system SHALL log with CRITICAL level

### Requirement 3

**User Story:** As a developer, I want all print() statements replaced with proper logging calls, so that error output can be managed in production environments.

#### Acceptance Criteria

1. WHEN the siliconflow module encounters an error THEN the system SHALL use logger.error() instead of print()
2. WHEN the iflow module encounters an error THEN the system SHALL use logger.error() instead of print()
3. WHEN the modelscope module encounters an error THEN the system SHALL use logger.error() instead of print()
4. WHEN any provider logs an error THEN the log message SHALL include the provider name for identification

### Requirement 4

**User Story:** As a system administrator, I want to configure logging output format and destination, so that I can integrate with existing logging infrastructure.

#### Acceptance Criteria

1. WHEN the logging system is initialized THEN the system SHALL use JSON format as the default output format for structured logging
2. WHEN a custom handler is provided THEN the system SHALL use the custom handler instead of the default
3. WHEN no explicit configuration is provided THEN the system SHALL use NullHandler to avoid "No handler found" warnings
4. WHEN JSON format is used THEN the log output SHALL include timestamp, level, provider name, message, and optional extra fields

### Requirement 5

**User Story:** As a system administrator, I want async logging support, so that logging does not block application execution in high-concurrency scenarios.

#### Acceptance Criteria

1. WHEN async logging is enabled THEN the system SHALL use QueueHandler to buffer log records
2. WHEN QueueHandler is used THEN the system SHALL process log records in a separate thread
3. WHEN async logging is not explicitly enabled THEN the system SHALL use synchronous logging as default
