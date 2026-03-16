from hello_agents import HelloAgentsLLM
from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    获取 LLM 实例（单例模式）

      Returns:
        HelloAgentsLLM 实例
    """
    global _llm_instance

    if _llm_instance is None:
        settings = get_settings()
        _llm_instance = HelloAgentsLLM()

        print(f"✅ LLM服务初始化成功")
        print(f"  提供商: {_llm_instance.provider}")
        print(f"  模型:{_llm_instance.model}")

    return _llm_instance
