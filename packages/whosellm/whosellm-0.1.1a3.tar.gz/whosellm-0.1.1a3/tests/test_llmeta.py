"""模型元数据测试 / Model metadata tests."""

from datetime import date

from whosellm import LLMeta, ModelFamily, Provider


def test_glm45_base_capabilities() -> None:
    """验证 GLM-4.5 默认型号的能力配置。"""
    model = LLMeta("glm-4.5")

    assert model.provider == Provider.ZHIPU
    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "base"

    capabilities = model.capabilities
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is False
    assert capabilities.supports_streaming is True
    assert capabilities.supports_vision is False
    assert capabilities.supports_video is False
    assert capabilities.max_tokens == 96000
    assert capabilities.context_window == 128000


def test_glm45_variant_priority_order() -> None:
    """确认不同变体的优先级顺序符合产品定位。"""
    flash = LLMeta("glm-4.5-flash")
    air = LLMeta("glm-4.5-air")
    airx = LLMeta("glm-4.5-airx")
    base = LLMeta("glm-4.5")
    x = LLMeta("glm-4.5-x")

    assert flash.variant == "flash"
    assert air.variant == "air"
    assert airx.variant == "airx"
    assert base.variant == "base"
    assert x.variant == "x"

    assert flash < air < airx < base < x


def test_glm45_release_date_parsing() -> None:
    """确保带日期后缀的模型能够正确解析发布日期。"""
    model = LLMeta("glm-4.5-air-2025-11-08")

    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "air"
    assert model.release_date == date(2025, 11, 8)


def test_glm46_capabilities() -> None:
    """验证 GLM-4.6 默认能力满足官方描述。"""
    model = LLMeta("glm-4.6")

    assert model.provider == Provider.ZHIPU
    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "base"

    capabilities = model.capabilities
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is False
    assert capabilities.supports_streaming is True
    assert capabilities.supports_vision is False
    assert capabilities.supports_video is False
    assert capabilities.context_window == 200000
    assert capabilities.max_tokens == 128000


def test_glm46_version_upgrade_over_glm45() -> None:
    """确认 GLM-4.6 相较 GLM-4.5 视为更高版本。"""
    glm45 = LLMeta("glm-4.5")
    glm46 = LLMeta("glm-4.6")

    assert glm45 < glm46


def test_glm46_release_date_parsing() -> None:
    """确保 GLM-4.6 带日期后缀能解析发布日期。"""
    model = LLMeta("glm-4.6-2025-11-08")

    assert model.family == ModelFamily.GLM_TEXT
    assert model.variant == "base"
    assert model.release_date == date(2025, 11, 8)


def test_gpt51_base_capabilities() -> None:
    """验证 GPT-5.1 默认型号的能力配置。"""
    model = LLMeta("gpt-5.1")

    assert model.provider == Provider.OPENAI
    assert model.family == ModelFamily.GPT_5_1
    assert model.variant == "base"

    capabilities = model.capabilities
    assert capabilities.supports_vision is True
    assert capabilities.supports_audio is False
    assert capabilities.supports_video is False
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_json_outputs is True
    assert capabilities.supports_thinking is True
    assert capabilities.max_tokens == 128000
    assert capabilities.context_window == 400000


def test_gpt51_release_date_parsing() -> None:
    """确保 GPT-5.1 带日期后缀能解析发布日期。"""
    model = LLMeta("gpt-5.1-2025-11-13")

    assert model.provider == Provider.OPENAI
    assert model.family == ModelFamily.GPT_5_1
    assert model.variant == "base"
    assert model.release_date == date(2025, 11, 13)


def test_gpt51_different_dates_comparison() -> None:
    """确认 GPT-5.1 不同日期版本可以正确比较。"""
    gpt51_old = LLMeta("gpt-5.1-2025-11-13")
    gpt51_new = LLMeta("gpt-5.1-2025-12-01")

    assert gpt51_old < gpt51_new


def test_claude_sonnet_4_20250514_structured_json() -> None:
    """验证 claude-sonnet-4-20250514 不支持 structured_json。"""
    model = LLMeta("claude-sonnet-4-20250514")

    assert model.provider == Provider.ANTHROPIC
    assert model.family == ModelFamily.CLAUDE
    assert model.variant == "sonnet"
    assert model.version == "4.0"

    capabilities = model.capabilities
    # 验证不支持结构化输出功能 / Verify no structured output support
    assert capabilities.supports_structured_outputs is False
    assert capabilities.supports_json_outputs is True  # 仍然支持基础JSON输出 / Still supports basic JSON output
    assert capabilities.supports_vision is True
    assert capabilities.supports_pdf is True
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.max_tokens == 64000
    assert capabilities.context_window == 200000


def test_claude_family_variant_priority_order() -> None:
    """确认 Claude 不同变体的优先级顺序符合产品定位。"""
    haiku = LLMeta("claude-3-haiku")
    sonnet = LLMeta("claude-sonnet-4-0")
    opus = LLMeta("claude-opus-4-0")

    assert haiku.variant == "haiku"
    assert sonnet.variant == "sonnet"
    assert opus.variant == "opus"

    # haiku (0) < sonnet (3) < opus (5)
    assert haiku < sonnet < opus


def test_claude_45_family_structured_outputs_support() -> None:
    """验证 Claude 4.5 系列支持结构化输出。"""
    sonnet_45 = LLMeta("claude-sonnet-4-5")
    haiku_45 = LLMeta("claude-haiku-4-5")

    # 4.5 系列都支持结构化输出
    assert sonnet_45.capabilities.supports_structured_outputs is True
    assert haiku_45.capabilities.supports_structured_outputs is True

    # 其他基础能力
    assert sonnet_45.capabilities.supports_vision is True
    assert sonnet_45.capabilities.supports_pdf is True
    assert sonnet_45.capabilities.supports_thinking is True
    assert sonnet_45.capabilities.supports_function_calling is True
    assert sonnet_45.capabilities.max_tokens == 64000
    assert sonnet_45.capabilities.context_window == 200000


def test_claude_opus_41_capabilities() -> None:
    """验证 Claude Opus 4.1 的完整能力配置。"""
    model = LLMeta("claude-opus-4-1")

    assert model.provider == Provider.ANTHROPIC
    assert model.family == ModelFamily.CLAUDE
    assert model.variant == "opus"
    assert model.version == "4.1"

    capabilities = model.capabilities
    # Opus 4.1 支持所有高级功能
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_json_outputs is True
    assert capabilities.supports_vision is True
    assert capabilities.supports_pdf is True
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    # Opus 系列输出限制较小
    assert capabilities.max_tokens == 32000
    assert capabilities.context_window == 200000


def test_claude_3_5_haiku_no_thinking() -> None:
    """验证 Claude 3.5 Haiku 不支持思考模式。"""
    model = LLMeta("claude-3-5-haiku")

    assert model.variant == "haiku"
    assert model.version == "3.5"

    capabilities = model.capabilities
    # 3.5 Haiku 不支持思考模式
    assert capabilities.supports_thinking is False
    # 但支持其他基础功能
    assert capabilities.supports_vision is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_structured_outputs is False
    # Haiku 系列输出限制最小
    assert capabilities.max_tokens == 8000
    assert capabilities.context_window == 200000


def test_claude_3_haiku_base_capabilities() -> None:
    """验证 Claude 3 Haiku 基础型号的能力配置。"""
    model = LLMeta("claude-3-haiku")

    assert model.variant == "haiku"
    assert model.version == "3.0"

    capabilities = model.capabilities
    # 3.0 Haiku 基础功能
    assert capabilities.supports_thinking is False
    assert capabilities.supports_vision is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_structured_outputs is False
    # 最小的输出限制
    assert capabilities.max_tokens == 4000
    assert capabilities.context_window == 200000


def test_claude_version_upgrade_comparison() -> None:
    """确认 Claude 版本升级比较正确。"""
    claude_3_haiku = LLMeta("claude-3-haiku")
    claude_3_5_haiku = LLMeta("claude-3-5-haiku")
    claude_4_0_sonnet = LLMeta("claude-sonnet-4-0")
    claude_4_1_opus = LLMeta("claude-opus-4-1")
    claude_4_5_sonnet = LLMeta("claude-sonnet-4-5")

    # 版本升级顺序（基于版本号）
    assert claude_3_haiku < claude_3_5_haiku < claude_4_0_sonnet < claude_4_1_opus < claude_4_5_sonnet


def test_gemini_3_pro_default_version() -> None:
    """验证 Gemini 3 Pro 默认模型版本解析为 3.0 而不是 2.5。 / Verify Gemini 3 Pro default model resolves to version 3.0 instead of 2.5."""
    model = LLMeta("gemini-3-pro")

    assert model.provider == Provider.GOOGLE
    assert model.family == ModelFamily.GEMINI
    assert model.version == "3.0"
    assert model.variant == "pro"
