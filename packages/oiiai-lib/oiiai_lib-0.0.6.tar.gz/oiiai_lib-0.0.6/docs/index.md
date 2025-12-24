# oiiai 文档

oiiai 是一个简单的 AI 模型调用工具包，提供模型列表获取和模型调用功能。

## 安装

```bash
pip install oiiai-lib
```

## 快速开始

```python
from oiiai import Fetch<Provider>

# 需要 API Key 的提供商
fetcher = FetchNova(api_key="your-api-key")  # 或设置环境变量 NOVA_API_KEY
models = fetcher.fetch_models()

# 不需要 API Key 的提供商
fetcher = FetchZhipu()
models = fetcher.fetch_models()

# 程序退出前关闭共享 Session（可选）
from oiiai import FetchBase
FetchBase.close_session()
```

## 模块文档

- [fetchModelList](./fetchModelList.md) - 模型列表获取、Session 管理与日志配置

## 日志配置

oiiai 提供统一的日志记录系统，详见 [fetchModelList 文档](./fetchModelList.md#日志配置)。

```python
import logging
from oiiai import configure_logging, shutdown_logging

# 配置日志
configure_logging(level=logging.DEBUG)

# 程序退出前关闭日志
shutdown_logging()
```

## 支持的提供商

| 提供商 | 类名 | API Key | 环境变量 | 特性 |
|--------|------|---------|----------|------|
| 智谱 AI | `FetchZhipu` | 不需要 | - | 多策略解析、fallback 支持 |
| ModelScope | `FetchModelScope` | 不需要 | - | - |
| IFlow | `FetchIFlow` | 不需要 | - | - |
| OpenRouter | `FetchOpenRouter` | 可选 | `OPENROUTER_API_KEY` | - |
| SiliconFlow | `FetchSiliconFlow` | 需要 | `SILICONFLOW_API_KEY` | - |
| Nova (Amazon) | `FetchNova` | 需要 | `NOVA_API_KEY` | `fetch_models_raw()` |

## 核心特性

### HTTP Session 复用

所有 Fetcher 子类共享同一个 HTTP Session，自动复用 TCP 连接，减少高频调用时的连接开销。详见 [fetchModelList 文档](./fetchModelList.md#session-管理)。

### 智谱 AI 多策略解析

FetchZhipu 支持多策略 HTML 解析和静态 fallback，增强对官方文档页面变化的容错能力。详见 [fetchModelList 文档](./fetchModelList.md#fetchzhipu-高级配置)。
