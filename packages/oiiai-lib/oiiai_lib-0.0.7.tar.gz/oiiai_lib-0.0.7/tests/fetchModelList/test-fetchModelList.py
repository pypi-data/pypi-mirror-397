import asyncio
import logging
from oiiai import fetch_models, list_providers

# 禁用库内部的实时日志打印，防止干扰最终结果输出
logging.getLogger("oiiai").setLevel(logging.CRITICAL)


async def fetch_provider_models(provider):
    try:
        # 使用 to_thread 在线程中运行同步的网络请求
        models = await asyncio.to_thread(fetch_models, provider)
        return provider, models
    except Exception as e:
        return provider, f"Error: {str(e)}"


async def main():
    provider_list = list_providers()

    # 并发执行所有获取任务并收集结果
    results = await asyncio.gather(*(fetch_provider_models(p) for p in provider_list))

    # 按照提供商名称排序，确保输出顺序稳定
    results.sort(key=lambda x: x[0])

    print("\n" + "=" * 40)
    print("模型抓取汇总对照")
    print("=" * 40)

    # 按照用户要求的对照格式输出
    for provider, models in results:
        # 清理提供商名称
        p_name = str(provider).strip()
        print(f"\n提供商: {p_name}")
        print(f"输出内容: {models}")
        print("-" * 20)


if __name__ == "__main__":
    asyncio.run(main())
