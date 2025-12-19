# filename: test_gpt4o.py
# @Time    : 2025/12/11 15:07
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm

from datetime import date

from whosellm import LLMeta, ModelFamily, Provider


def test_gpt4o_default_capabilities() -> None:
    """验证 GPT-4o 默认 omni 型号的基础能力 / Validate default capabilities of GPT-4o omni model."""
    model = LLMeta("gpt-4o")

    assert model.provider == Provider.OPENAI
    assert model.family == ModelFamily.GPT_4O
    assert model.variant == "omni"

    capabilities = model.capabilities
    assert capabilities.supports_vision is True
    assert capabilities.supports_audio is False
    assert capabilities.supports_streaming is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_json_outputs is True
    assert capabilities.supports_fine_tuning is True
    assert capabilities.supports_predicted_outputs is True
    assert capabilities.context_window == 128000
    assert capabilities.max_tokens == 16384


def test_gpt4o_release_date_parsing() -> None:
    """确保 GPT-4o 带日期后缀能解析发布日期 / Ensure GPT-4o models with date suffix parse release_date correctly."""
    model = LLMeta("gpt-4o-2025-06-03")

    assert model.family == ModelFamily.GPT_4O
    assert model.variant == "omni"
    assert model.release_date == date(2025, 6, 3)


def test_gpt4o_mini_capabilities_and_date() -> None:
    """验证 GPT-4o mini 型号的能力与日期解析 / Validate capabilities and date parsing for GPT-4o mini models."""
    base = LLMeta("gpt-4o-mini")
    dated = LLMeta("gpt-4o-mini-2025-06-03")

    for model in (base, dated):
        assert model.provider == Provider.OPENAI
        assert model.family == ModelFamily.GPT_4O
        assert model.variant == "mini"

        capabilities = model.capabilities
        assert capabilities.supports_vision is True
        assert capabilities.supports_audio is False
        assert capabilities.supports_streaming is True
        assert capabilities.supports_function_calling is True
        assert capabilities.supports_structured_outputs is True
        assert capabilities.supports_json_outputs is True
        assert capabilities.supports_fine_tuning is True
        # mini 不是 audio 型号 / mini is not an audio model
        assert capabilities.supports_audio is False


def test_gpt4o_audio_preview_capabilities() -> None:
    """验证 GPT-4o audio-preview 型号的音频能力配置 / Validate audio capabilities of GPT-4o audio-preview models."""
    base = LLMeta("gpt-4o-audio-preview")
    dated = LLMeta("gpt-4o-audio-preview-2024-12-17")

    for model in (base, dated):
        assert model.provider == Provider.OPENAI
        assert model.family == ModelFamily.GPT_4O
        assert model.variant == "audio-preview"

        capabilities = model.capabilities
        assert capabilities.supports_audio is True
        assert capabilities.supports_vision is False
        assert capabilities.supports_streaming is True
        assert capabilities.supports_function_calling is True
        assert capabilities.supports_structured_outputs is False
        assert capabilities.supports_json_outputs is False
        assert capabilities.supports_fine_tuning is False
        assert capabilities.supports_distillation is False
        assert capabilities.supports_predicted_outputs is False


def test_gpt4o_mini_audio_preview_capabilities() -> None:
    """验证 GPT-4o mini-audio-preview 型号的音频能力配置 / Validate audio capabilities of GPT-4o mini-audio-preview models."""
    base = LLMeta("gpt-4o-mini-audio-preview")
    dated = LLMeta("gpt-4o-mini-audio-preview-2024-12-17")

    for model in (base, dated):
        assert model.provider == Provider.OPENAI
        assert model.family == ModelFamily.GPT_4O
        assert model.variant == "mini-audio-preview"

        capabilities = model.capabilities
        assert capabilities.supports_audio is True
        assert capabilities.supports_vision is False
        assert capabilities.supports_streaming is True
        assert capabilities.supports_function_calling is True
        assert capabilities.supports_structured_outputs is False
        assert capabilities.supports_json_outputs is False
        assert capabilities.supports_fine_tuning is False
        assert capabilities.supports_distillation is False
        assert capabilities.supports_predicted_outputs is False
