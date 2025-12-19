# filename: openai_gpt_5_1.py
# @Time    : 2025/12/11 15:50
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
from whosellm.capabilities import ModelCapabilities
from whosellm.models.base import ModelFamily
from whosellm.models.config import ModelFamilyConfig
from whosellm.provider import Provider

# ============================================================================
# GPT-5.1 系列 / GPT-5.1 Series
# ============================================================================


GPT_5_1 = ModelFamilyConfig(
    family=ModelFamily.GPT_5_1,
    provider=Provider.OPENAI,
    version_default="5.1",
    variant_priority_default=(1,),  # base 的优先级 / base priority
    patterns=[
        "gpt-5.1-{year:4d}-{month:2d}-{day:2d}",  # gpt-5.1-2025-11-13
        "gpt-5.1",  # gpt-5.1 (base)
    ],
    capabilities=ModelCapabilities(
        supports_vision=True,  # 支持图像输入 / Image input supported
        supports_pdf=False,
        supports_audio=False,  # 不支持音频 / Audio not supported
        supports_video=False,  # 不支持视频 / Video not supported
        supports_function_calling=True,  # 支持函数调用 / Function calling supported
        supports_streaming=True,  # 支持流式传输 / Streaming supported
        supports_structured_outputs=True,  # 支持结构化输出 / Structured outputs supported
        supports_json_outputs=True,
        supports_fine_tuning=False,
        supports_distillation=False,
        supports_thinking=True,  # 支持推理 tokens / Reasoning token support
        max_tokens=128000,  # 最大输出 tokens / Max output tokens
        context_window=400000,  # 上下文窗口 / Context window
    ),
)
