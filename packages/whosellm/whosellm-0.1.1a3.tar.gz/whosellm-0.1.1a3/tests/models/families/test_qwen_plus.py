# filename: test_qwen_plus.py
# @Time    : 2025/12/16 18:35
# @Author  : JQQ
# @Software: PyCharm
"""
测试 qwen-plus 和 qwen-flash 模型配置 / Test qwen-plus and qwen-flash model configuration
"""

from whosellm import LLMeta
from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_specific_model_config, match_model_pattern


def test_qwen_plus_pattern_match() -> None:
    """测试 qwen-plus 模式匹配 / Test qwen-plus pattern match"""
    matched = match_model_pattern("qwen-plus")

    assert matched is not None
    assert matched["family"] == ModelFamily.QWEN
    assert matched["version"] == "1.0"
    assert matched["variant"] == "plus"


def test_qwen_plus_specific_config() -> None:
    """测试 qwen-plus 特定配置 / Test qwen-plus specific config"""
    config = get_specific_model_config("qwen-plus")

    assert config is not None
    version, variant, capabilities = config
    assert version == "1.0"
    assert variant == "plus"

    # 验证仅支持文本输入输出 / Verify text input/output only
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_vision is False  # 关键：不支持视觉 / Key: no vision support
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 32000


def test_qwen_plus_auto_register() -> None:
    """测试 qwen-plus 自动注册 / Test qwen-plus auto register"""
    meta = LLMeta("qwen-plus")

    assert meta.family == ModelFamily.QWEN
    assert meta.version == "1.0"
    assert meta.variant == "plus"
    assert meta.capabilities.supports_function_calling is True
    assert meta.capabilities.supports_streaming is True
    assert meta.capabilities.supports_structured_outputs is True
    assert meta.capabilities.supports_vision is False  # 关键：不支持视觉 / Key: no vision support
    assert meta.capabilities.max_tokens == 8192
    assert meta.capabilities.context_window == 32000


def test_qwen_plus_with_date_suffix() -> None:
    """测试带日期后缀的 qwen-plus / Test qwen-plus with date suffix"""
    meta = LLMeta("qwen-plus-2025-12-16")

    assert meta.family == ModelFamily.QWEN
    assert meta.version == "1.0"
    assert meta.variant == "plus"
    assert meta.release_date.year == 2025
    assert meta.release_date.month == 12
    assert meta.release_date.day == 16
    assert meta.capabilities.supports_vision is False  # 关键：不支持视觉 / Key: no vision support


def test_qwen_flash_pattern_match() -> None:
    """测试 qwen-flash 模式匹配 / Test qwen-flash pattern match"""
    matched = match_model_pattern("qwen-flash")

    assert matched is not None
    assert matched["family"] == ModelFamily.QWEN
    assert matched["version"] == "1.0"
    assert matched["variant"] == "flash"


def test_qwen_flash_specific_config() -> None:
    """测试 qwen-flash 特定配置 / Test qwen-flash specific config"""
    config = get_specific_model_config("qwen-flash")

    assert config is not None
    version, variant, capabilities = config
    assert version == "1.0"
    assert variant == "flash"

    # 验证仅支持文本输入输出 / Verify text input/output only
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_structured_outputs is True
    assert capabilities.supports_vision is False  # 关键：不支持视觉 / Key: no vision support
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 32000


def test_qwen_flash_auto_register() -> None:
    """测试 qwen-flash 自动注册 / Test qwen-flash auto register"""
    meta = LLMeta("qwen-flash")

    assert meta.family == ModelFamily.QWEN
    assert meta.version == "1.0"
    assert meta.variant == "flash"
    assert meta.capabilities.supports_function_calling is True
    assert meta.capabilities.supports_streaming is True
    assert meta.capabilities.supports_structured_outputs is True
    assert meta.capabilities.supports_vision is False  # 关键：不支持视觉 / Key: no vision support
    assert meta.capabilities.max_tokens == 8192
    assert meta.capabilities.context_window == 32000


def test_qwen3_max_no_vision() -> None:
    """测试 qwen3-max 不支持视觉 / Test qwen3-max does not support vision"""
    meta = LLMeta("qwen3-max")

    assert meta.family == ModelFamily.QWEN
    assert meta.version == "3"
    assert meta.variant == "max"
    # qwen3-max 的配置中没有设置 supports_vision，所以默认为 False
    assert meta.capabilities.supports_vision is False
    assert meta.capabilities.supports_function_calling is True
    assert meta.capabilities.supports_structured_outputs is True
