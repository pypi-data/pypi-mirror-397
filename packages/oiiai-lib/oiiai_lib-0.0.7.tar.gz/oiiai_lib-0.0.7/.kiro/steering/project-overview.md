# oiiai 项目概述

## 项目简介

oiiai 是一个 Python 工具包，用于从多个 AI 提供商获取可用模型列表。项目采用统一的抽象基类设计，支持多种 AI 服务提供商。

## 核心架构

- **FetchBase**: 抽象基类，提供共享 HTTP Session、日志记录和错误处理
- **Provider Fetchers**: 各提供商的具体实现类（FetchZhipu、FetchOpenRouter 等）
- **log_config**: 统一的日志配置模块，支持 JSON 格式和异步日志

## 支持的提供商

| 提供商 | 类名 | API Key 要求 |
|--------|------|-------------|
| 智谱 AI | FetchZhipu | 不需要 |
| OpenRouter | FetchOpenRouter | 可选 |
| ModelScope | FetchModelScope | 不需要 |
| SiliconFlow | FetchSiliconFlow | 需要 |
| IFlow | FetchIFlow | 不需要 |
| Amazon Nova | FetchNova | 需要 |
| Groq | FetchGroq | 需要 |
| Zenmux | FetchZenmux | 需要 |
| Chutes | FetchChutes | 需要 |

## 目录结构

```
src/oiiai/
├── __init__.py              # 包入口，导出所有公共 API
└── fetchModelList/
    ├── __init__.py          # 模块入口
    ├── __base__.py          # FetchBase 抽象基类
    ├── __log_config__.py    # 日志配置
    ├── zhipu.py             # 智谱 AI 实现
    ├── openrouter.py        # OpenRouter 实现
    ├── modelscope.py        # ModelScope 实现
    ├── siliconflow.py       # SiliconFlow 实现
    ├── iflow.py             # IFlow 实现
    ├── nova.py              # Amazon Nova 实现
    ├── groq.py              # Groq 实现
    ├── zenmux.py            # Zenmux 实现
    ├── chutes.py            # Chutes 实现
    └── __factory__.py       # 工厂函数 fetch_models
```

## 技术栈

- Python 3.8+
- requests: HTTP 请求
- beautifulsoup4 + lxml: HTML 解析（智谱 AI）
- zhipuai: 智谱 AI SDK
