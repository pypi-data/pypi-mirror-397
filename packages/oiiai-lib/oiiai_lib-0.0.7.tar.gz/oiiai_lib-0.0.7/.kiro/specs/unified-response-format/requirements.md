# Requirements Document

## Introduction

本功能旨在统一智谱AI provider 的返回格式，使其与其他 provider（OpenRouter、SiliconFlow、ModelScope、IFlow）保持一致。当前智谱AI 使用 dict 格式（按分类组织），而其他 provider 均返回 list 格式。通过调整智谱AI 的返回格式为 list，可以消除调用方的特殊处理逻辑，简化代码。

## Glossary

- **FetchZhipu**: 智谱AI 模型列表获取类，继承自 FetchBase
- **FetchBase**: 模型列表获取的抽象基类

## Requirements

### Requirement 1

**User Story:** As a developer, I want FetchZhipu to return a list format like other providers, so that I can process all providers with the same logic.

#### Acceptance Criteria

1. WHEN FetchZhipu.fetch_models() is called THEN the system SHALL return a list of model ID strings
2. WHEN 智谱AI has models in multiple categories THEN the system SHALL flatten all categories into a single list
3. WHEN the list is returned THEN the system SHALL include all model IDs from all original categories

### Requirement 2

**User Story:** As a developer, I want consistent return types across all providers, so that type checking works correctly.

#### Acceptance Criteria

1. WHEN any provider's fetch_models() method is called THEN the return type SHALL be List[str]
2. WHEN FetchBase defines the abstract method THEN the return type annotation SHALL be List[str]

