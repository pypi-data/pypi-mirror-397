# fetchModelList 模块

获取各 AI 提供商的可用模型列表。

## 快速开始

```python
from oiiai import fetch_models, list_providers

# 查看支持的提供商
print(list_providers())
# ['chutes', 'groq', 'iflow', 'modelscope', 'nova', 'openrouter', 'siliconflow', 'zenmux', 'zhipu']

# 一行获取模型列表
models = fetch_models("zhipu")
models = fetch_models("groq")              # 自动读取 GROQ_API_KEY 环境变量
models = fetch_models("groq", api_key="xxx")
raw = fetch_models("groq", raw=True)       # 获取原始 API 响应
```

## 安装依赖

```bash
pip install oiiai-lib
# or
uv pip install oiiai-lib
# In your project
uv add oiiai-lib
```

## 基类

### FetchBase

所有模型获取器的抽象基类，提供统一的 HTTP Session 管理、日志记录和错误处理方法。

```python
from oiiai import FetchBase
from typing import List

class MyFetcher(FetchBase):
    @property
    def provider(self) -> str:
        return "my_provider"
    
    def fetch_models(self) -> List[str]:
        try:
            # 使用共享 Session 发起 GET 请求
            response = self._http_get("https://api.example.com/models")
            return response.json()["models"]
        except Exception as e:
            return self._handle_http_error(e)
```

#### Session 管理

FetchBase 提供共享的 HTTP Session，所有 Fetcher 子类自动复用 TCP 连接，减少高频调用时的连接开销。

| 方法 | 说明 |
|------|------|
| `_get_session()` | 获取或创建共享 Session 实例（线程安全） |
| `close_session()` | 关闭共享 Session 并释放资源（类方法） |
| `_http_get(url, headers, timeout)` | 使用共享 Session 发起 GET 请求 |
| `_http_post(url, json, headers, timeout)` | 使用共享 Session 发起 POST 请求 |

```python
from oiiai import FetchBase

# 程序退出前关闭共享 Session（可选）
FetchBase.close_session()
```

默认配置：
- 超时时间：30 秒
- User-Agent：Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

#### 日志方法

| 方法 | 说明 |
|------|------|
| `_log_error(message, exc_info=False)` | 记录 ERROR 级别日志 |
| `_log_warning(message)` | 记录 WARNING 级别日志 |
| `_log_info(message)` | 记录 INFO 级别日志 |
| `_log_debug(message)` | 记录 DEBUG 级别日志 |

#### 错误处理方法

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `_handle_http_error(error)` | 处理 HTTP 请求错误 | `[]` |
| `_handle_unexpected_format(data)` | 处理意外的 API 响应格式 | `[]` |
| `_handle_missing_env_var(var_name)` | 处理缺失的环境变量 | `[]` |

## 工厂函数

### list_providers

获取所有支持的提供商名称列表。

```python
from oiiai import list_providers

providers = list_providers()
# ['groq', 'iflow', 'modelscope', 'nova', 'openrouter', 'siliconflow', 'zhipu']
```

### fetch_models

简化的一行式 API，自动选择对应的 Fetcher 类。

```python
from oiiai import fetch_models

models = fetch_models(provider, api_key=None, raw=False, **kwargs)
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `provider` | `str` | 提供商名称（不区分大小写） |
| `api_key` | `str` | API Key（可选，未提供时从环境变量读取） |
| `raw` | `bool` | 是否返回原始 API 响应（仅 nova、groq 支持） |
| `**kwargs` | - | 传递给 Fetcher 构造函数的额外参数 |

```python
# 示例
models = fetch_models("zhipu")
models = fetch_models("groq")                    # 读取 GROQ_API_KEY
models = fetch_models("siliconflow", api_key="xxx")
raw = fetch_models("nova", raw=True)

# 传递额外参数（如 FetchZhipu 的 fallback_models）
models = fetch_models("zhipu", fallback_models=["glm-4", "glm-4-flash"])
```

## 内置实现

### 类式用法

如果需要更细粒度的控制，可以直接使用 Fetcher 类：

```python
from oiiai import Fetch<Provider>

# 需要 API Key 的提供商（以 FetchNova 为例）
fetcher = FetchNova(api_key="your-api-key")  # 或从环境变量读取
models = fetcher.fetch_models()

# 不需要 API Key 的提供商（以 FetchZhipu 为例）
fetcher = FetchZhipu()
models = fetcher.fetch_models()
```

### 可用提供商

| 类名 | 提供商 | API Key | 环境变量 | 特殊方法 |
|------|--------|---------|----------|----------|
| `FetchZhipu` | 智谱 AI | 不需要 | - | - |
| `FetchModelScope` | ModelScope | 不需要 | - | - |
| `FetchIFlow` | IFlow | 不需要 | - | - |
| `FetchOpenRouter` | OpenRouter | 可选 | `OPENROUTER_API_KEY` | - |
| `FetchSiliconFlow` | SiliconFlow | 需要 | `SILICONFLOW_API_KEY` | - |
| `FetchNova` | Amazon Nova | 需要 | `NOVA_API_KEY` | `fetch_models_raw()` |
| `FetchGroq` | Groq | 需要 | `GROQ_API_KEY` | `fetch_models_raw()` |
| `FetchZenmux` | Zenmux | 需要 | `ZENMUX_API_KEY` | `fetch_models_raw()` |
| `FetchChutes` | Chutes | 需要 | `CHUTES_API_KEY` | `fetch_models_raw()` |

### 详细示例

#### 需要 API Key 的提供商

```python
from oiiai import FetchNova

# 方式一：直接传入 API Key
fetcher = FetchNova(api_key="your-api-key")

# 方式二：从环境变量读取（设置 NOVA_API_KEY）
fetcher = FetchNova()

# 获取模型列表
models = fetcher.fetch_models()
print(models)  # ['amazon.nova-pro-v1:0', 'amazon.nova-lite-v1:0', ...]

# Nova 特有：获取原始 API 响应
raw_response = fetcher.fetch_models_raw()
```

#### 不需要 API Key 的提供商

```python
from oiiai import FetchZhipu

fetcher = FetchZhipu()
models = fetcher.fetch_models()
print(models)  # ['glm-4-flash', 'glm-4', ...]
```

### FetchZhipu 高级配置

FetchZhipu 支持多策略 HTML 解析、结构变化检测和静态 fallback 机制，增强对智谱官方文档页面变化的容错能力。

**依赖**：`beautifulsoup4` 和 `lxml`（已包含在 oiiai-lib 依赖中）

#### 多策略解析

FetchZhipu 按以下顺序尝试解析策略，直到成功提取模型列表：

1. **BeautifulSoup 策略**（推荐）：使用 BeautifulSoup + lxml 进行健壮的 HTML 解析，支持复杂的 Next.js 渲染页面
2. **Section ID 策略**：通过 h2/h3 标题的 id 属性识别模型分类
3. **Table Header 策略**：检测包含"模型"或"Model"的表头
4. **Pattern 策略**：使用正则表达式匹配已知模型名称模式（glm-*, chatglm-*, codegeex-*, cogview-*, cogvideo-* 等）

BeautifulSoup 策略会自动识别以下模型分类：
- 文本模型
- 视觉模型
- 图像生成模型
- 视频生成模型
- 语音模型
- 向量模型
- 知识检索模型

#### 配置选项

```python
from oiiai import FetchZhipu

fetcher = FetchZhipu(
    fallback_models=["glm-4", "glm-4-flash", "glm-4-plus"],  # 静态 fallback 列表
    min_model_threshold=5  # 模型数量阈值（低于此值记录警告）
)
models = fetcher.fetch_models()
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `fallback_models` | `List[str]` | `None` | 所有解析策略失败时返回的静态模型列表 |
| `min_model_threshold` | `int` | `5` | 模型数量阈值，低于此值时记录警告 |

#### 降级检测

FetchZhipu 会自动检测以下情况并记录警告：

- HTML 结构缺少预期标记（table、tbody、模型相关标题）
- 提取的模型数量低于配置阈值
- 所有解析策略失败（使用 fallback 或返回空列表）

### fetch_models_raw()（FetchNova / FetchGroq / FetchZenmux / FetchChutes）

返回 API 的原始 JSON 响应，包含完整的模型元数据。

#### FetchNova 响应示例

```python
{
    "object": "list",
    "data": [
        {
            "created": 1234567890,
            "description": "Model description",
            "display name": "Human-readable name",
            "id": "model-id",
            "owned_by": "amazon",
            "type": "model"
        },
        ...
    ]
}
```

#### FetchGroq 响应示例

```python
from oiiai import FetchGroq

fetcher = FetchGroq(api_key="your-api-key")  # 或设置 GROQ_API_KEY 环境变量
raw = fetcher.fetch_models_raw()
```

```python
{
    "object": "list",
    "data": [
        {
            "id": "llama-3.3-70b-versatile",
            "object": "model",
            "created": 1733447754,
            "owned_by": "Meta",
            "active": true,
            "context_window": 131072,
            "max_completion_tokens": 32768
        },
        ...
    ]
}
```

## 扩展

实现自定义获取器只需继承 `FetchBase` 并实现 `provider` 属性和 `fetch_models()` 方法。

## 日志配置

fetchModelList 模块提供统一的日志记录系统，支持 JSON 格式输出和异步日志。

### configure_logging

配置全局日志设置。

```python
import logging
from oiiai import configure_logging

# 基本配置
configure_logging(level=logging.DEBUG)

# 完整配置
configure_logging(
    level=logging.WARNING,    # 日志级别（默认: WARNING）
    handler=None,             # 自定义 Handler（默认: NullHandler）
    use_json=True,            # 是否使用 JSON 格式（默认: True）
    async_enabled=False,      # 是否启用异步日志（默认: False）
)
```

### shutdown_logging

关闭异步日志并清理资源。在程序退出前调用以确保所有日志写入完成。

```python
from oiiai import shutdown_logging

shutdown_logging()
```

### 自定义 Handler

```python
import logging
from oiiai import configure_logging

# 输出到文件
file_handler = logging.FileHandler("oiiai.log")
configure_logging(level=logging.INFO, handler=file_handler)

# 输出到控制台
stream_handler = logging.StreamHandler()
configure_logging(level=logging.DEBUG, handler=stream_handler)
```

### 异步日志

在高并发场景下启用异步日志避免阻塞：

```python
from oiiai import configure_logging, shutdown_logging

configure_logging(level=logging.INFO, async_enabled=True)

# 程序退出前务必调用
shutdown_logging()
```

### JSON 日志格式

| 字段 | 类型 | 说明 |
|------|------|------|
| timestamp | string | ISO 8601 格式时间戳 |
| level | string | 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| provider | string | Provider 标识符 |
| message | string | 日志消息 |
| module | string | 模块名称 |
| function | string | 函数名称 |
| line | int | 行号 |
| exc_info | string | 异常堆栈信息（可选） |

### 错误处理

所有 provider 在遇到错误时会自动记录日志并返回空列表，不会抛出异常：

- HTTP 请求失败 → ERROR 级别日志
- API 响应格式异常 → WARNING 级别日志
- 环境变量缺失 → WARNING 级别日志

```python
from oiiai import FetchSiliconFlow, configure_logging
import logging

# 启用日志查看错误信息
configure_logging(level=logging.WARNING, handler=logging.StreamHandler())

fetcher = FetchSiliconFlow()
models = fetcher.fetch_models()  # 如果出错，返回 [] 并记录日志
```
