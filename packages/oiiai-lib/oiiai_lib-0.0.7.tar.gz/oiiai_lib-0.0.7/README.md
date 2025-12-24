# oiiai

[![PyPI version](https://img.shields.io/pypi/v/oiiai-lib.svg)](https://pypi.org/project/oiiai-lib/)
[![Python versions](https://img.shields.io/pypi/pyversions/oiiai-lib.svg)](https://pypi.org/project/oiiai-lib/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

oiiai 是一个简单的 AI 模型调用工具包，提供模型列表获取和模型调用功能。

## 特性

- 🚀 支持多个 AI 提供商的模型列表获取
- 📦 统一的 API 接口
- 🛠️ 简单易用的设计
- 🔧 可扩展的架构
- 📝 统一的日志记录系统（支持 JSON 格式和异步日志）
- 🔄 HTTP Session 复用，减少连接开销
- 🛡️ 智谱 AI 多策略解析，增强容错能力

## 支持的提供商

| 提供商        | 模型获取            | 说明                                     |
| ------------- | ------------------- | ---------------------------------------- |
| 智谱 AI       | ✅ FetchZhipu       | 从官方文档页面解析模型列表（多策略解析） |
| OpenRouter    | ✅ FetchOpenRouter  | 通过 API 获取模型列表                    |
| ModelScope    | ✅ FetchModelScope  | 通过 API 获取模型列表                    |
| SiliconFlow   | ✅ FetchSiliconFlow | 通过 API 获取模型列表                    |
| IFlow         | ✅ FetchIFlow       | 通过 API 获取模型列表                    |
| Nova (Amazon) | ✅ FetchNova        | 通过 API 获取模型列表                    |
| Groq          | ✅ FetchGroq        | 通过 API 获取模型列表                    |
| Zenmux        | ✅ FetchZenmux      | 通过 API 获取模型列表                    |
| Chutes        | ✅ FetchChutes      | 通过 API 获取模型列表                    |

## 安装

### 使用 pip

```bash
pip install oiiai-lib
```

### 使用 uv

```bash
uv add oiiai-lib
```

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

## API 参考

### 基类 FetchBase

所有模型获取器的抽象基类，提供共享 HTTP Session 和统一的请求方法。

```python
from oiiai import FetchBase

class MyFetcher(FetchBase):
    @property
    def provider(self) -> str:
        return "my_provider"

    def fetch_models(self) -> List[str]:
        # 使用共享 Session 发起请求
        response = self._http_get("https://api.example.com/models")
        return response.json()["models"]
```

#### Session 管理

所有 Fetcher 子类共享同一个 HTTP Session，自动复用 TCP 连接：

```python
from oiiai import FetchBase

# 程序退出前可选择关闭共享 Session
FetchBase.close_session()
```

### 可用提供商

| 类名               | 提供商      | API Key | 环境变量              | 特殊方法             |
| ------------------ | ----------- | ------- | --------------------- | -------------------- |
| `FetchZhipu`       | 智谱 AI     | 不需要  | -                     | -                    |
| `FetchModelScope`  | ModelScope  | 不需要  | -                     | -                    |
| `FetchIFlow`       | IFlow       | 不需要  | -                     | -                    |
| `FetchOpenRouter`  | OpenRouter  | 可选    | `OPENROUTER_API_KEY`  | -                    |
| `FetchSiliconFlow` | SiliconFlow | 需要    | `SILICONFLOW_API_KEY` | -                    |
| `FetchNova`        | Amazon Nova | 需要    | `NOVA_API_KEY`        | `fetch_models_raw()` |
| `FetchGroq`        | Groq        | 需要    | `GROQ_API_KEY`        | `fetch_models_raw()` |
| `FetchZenmux`      | Zenmux      | 需要    | `ZENMUX_API_KEY`      | `fetch_models_raw()` |
| `FetchChutes`      | Chutes      | 需要    | `CHUTES_API_KEY`      | `fetch_models_raw()` |

### 使用示例

#### 使用异步获取 (推荐)

对于需要同时从多个提供商获取模型列表的场景，可以使用 `asyncio.to_thread` 实现并发获取：

```python
import asyncio
from oiiai import fetch_models, list_providers

async def fetch_and_print(provider):
    # 使用 to_thread 在线程中运行同步的网络请求
    models = await asyncio.to_thread(fetch_models, provider)
    print(f"[{provider}] 模型列表: {models}")

async def main():
    providers = list_providers()
    # 并发执行所有获取任务
    await asyncio.gather(*(fetch_and_print(p) for p in providers))

if __name__ == "__main__":
    asyncio.run(main())
```

### 需要 API Key 的提供商

```python
from oiiai import FetchNova

# 方式一：直接传入 API Key
fetcher = FetchNova(api_key="your-api-key")

# 方式二：从环境变量读取
fetcher = FetchNova()  # 需设置 NOVA_API_KEY

models = fetcher.fetch_models()

# Nova 特有：获取原始 API 响应
raw_response = fetcher.fetch_models_raw()
```

#### 不需要 API Key 的提供商

```python
from oiiai import FetchZhipu

fetcher = FetchZhipu()
models = fetcher.fetch_models()
```

#### FetchZhipu 高级配置

FetchZhipu 支持多策略解析和静态 fallback，使用 BeautifulSoup 作为主要解析器：

```python
from oiiai import FetchZhipu

# 配置静态 fallback 列表（当所有解析策略失败时使用）
fetcher = FetchZhipu(
    fallback_models=["glm-4", "glm-4-flash", "glm-4-plus"],
    min_model_threshold=5  # 模型数量低于此值时记录警告
)
models = fetcher.fetch_models()
```

解析策略优先级：

1. **BeautifulSoup** - 最健壮的解析方式，支持复杂 HTML 结构
2. **Section ID** - 通过 h2/h3 标题的 id 属性识别模型分类
3. **Table Header** - 检测包含"模型"或"Model"的表头
4. **Pattern** - 使用正则表达式匹配已知模型名称模式

## 日志配置

oiiai 提供统一的日志记录系统，支持 JSON 格式输出和异步日志。

### 基本配置

```python
import logging
from oiiai import configure_logging, shutdown_logging

# 配置日志级别为 DEBUG，使用 JSON 格式输出
configure_logging(level=logging.DEBUG)

# 使用完毕后关闭日志（清理异步日志资源）
shutdown_logging()
```

### 配置选项

```python
configure_logging(
    level=logging.WARNING,    # 日志级别（默认: WARNING）
    handler=None,             # 自定义 Handler（默认: NullHandler）
    use_json=True,            # 是否使用 JSON 格式（默认: True）
    async_enabled=False,      # 是否启用异步日志（默认: False）
)
```

### 自定义 Handler

```python
import logging
from oiiai import configure_logging

# 使用文件 Handler
file_handler = logging.FileHandler("oiiai.log")
configure_logging(level=logging.INFO, handler=file_handler)
```

### 异步日志

在高并发场景下，可以启用异步日志避免阻塞：

```python
from oiiai import configure_logging, shutdown_logging

# 启用异步日志
configure_logging(level=logging.INFO, async_enabled=True)

# 程序退出前务必调用 shutdown_logging() 确保日志写入完成
shutdown_logging()
```

### JSON 日志格式

启用 JSON 格式后，日志输出包含以下字段：

| 字段      | 说明                |
| --------- | ------------------- |
| timestamp | ISO 8601 格式时间戳 |
| level     | 日志级别            |
| provider  | Provider 标识符     |
| message   | 日志消息            |
| module    | 模块名称            |
| function  | 函数名称            |
| line      | 行号                |
| exc_info  | 异常堆栈（可选）    |

## 开发

### 克隆仓库

```bash
git clone https://github.com/weisiren000/oiiai
cd oiiai
```

### 安装开发依赖

```bash
uv sync --dev
```

### 运行测试

```bash
uv run pytest
```

### 代码格式化

```bash
uv run ruff format .
uv run ruff check .
```

## 扩展

实现自定义获取器只需继承 `FetchBase` 并实现 `provider` 属性和 `fetch_models()` 方法。

## 许可证

MIT License. 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 链接

- [GitHub 仓库](https://github.com/weisiren000/oiiai)
- [PyPI 页面](https://pypi.org/project/oiiai-lib/)
- [文档](https://github.com/weisiren000/oiiai/docs)
