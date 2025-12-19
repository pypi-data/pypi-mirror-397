# filename: test_qwen3_vl_models.py
# @Time    : 2025/12/16 18:38
# @Author  : JQQ
# @Software: PyCharm
"""
测试 qwen3-vl-plus 和 qwen3-vl-flash 模型配置 / Test qwen3-vl-plus and qwen3-vl-flash model configuration
"""

from whosellm import LLMeta
from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_specific_model_config, match_model_pattern


def test_qwen3_vl_plus_pattern_match() -> None:
    """测试 qwen3-vl-plus 模式匹配 / Test qwen3-vl-plus pattern match"""
    matched = match_model_pattern("qwen3-vl-plus")

    assert matched is not None
    assert matched["family"] == ModelFamily.QWEN
    assert matched["version"] == "3"
    assert matched["variant"] == "vl-plus"


def test_qwen3_vl_plus_specific_config() -> None:
    """测试 qwen3-vl-plus 特定配置 / Test qwen3-vl-plus specific config"""
    config = get_specific_model_config("qwen3-vl-plus")

    assert config is not None
    version, variant, capabilities = config
    assert version == "3"
    assert variant == "vl-plus"

    # 验证多模态输入能力 / Verify multimodal input capabilities
    assert capabilities.supports_vision is True  # 支持图片 / Support images
    assert capabilities.supports_video is True  # 支持视频 / Support videos

    # 验证文本输出能力 / Verify text output capabilities
    assert capabilities.supports_function_calling is True  # 支持 func call
    assert capabilities.supports_structured_outputs is True  # 支持 JSON 输出
    assert capabilities.supports_streaming is True  # 支持流式输出
    assert capabilities.supports_thinking is True  # 支持思考模式

    assert capabilities.max_tokens == 32000
    assert capabilities.context_window == 256000


def test_qwen3_vl_plus_auto_register() -> None:
    """测试 qwen3-vl-plus 自动注册 / Test qwen3-vl-plus auto register"""
    meta = LLMeta("qwen3-vl-plus")

    assert meta.family == ModelFamily.QWEN
    assert meta.version == "3"
    assert meta.variant == "vl-plus"

    # 验证多模态输入能力 / Verify multimodal input capabilities
    assert meta.capabilities.supports_vision is True
    assert meta.capabilities.supports_video is True

    # 验证文本输出能力 / Verify text output capabilities
    assert meta.capabilities.supports_function_calling is True
    assert meta.capabilities.supports_structured_outputs is True
    assert meta.capabilities.supports_streaming is True
    assert meta.capabilities.supports_thinking is True


def test_qwen3_vl_flash_pattern_match() -> None:
    """测试 qwen3-vl-flash 模式匹配 / Test qwen3-vl-flash pattern match"""
    matched = match_model_pattern("qwen3-vl-flash")

    assert matched is not None
    assert matched["family"] == ModelFamily.QWEN
    assert matched["version"] == "3"
    assert matched["variant"] == "vl-flash"


def test_qwen3_vl_flash_specific_config() -> None:
    """测试 qwen3-vl-flash 特定配置 / Test qwen3-vl-flash specific config"""
    config = get_specific_model_config("qwen3-vl-flash")

    assert config is not None
    version, variant, capabilities = config
    assert version == "3"
    assert variant == "vl-flash"

    # 验证多模态输入能力 / Verify multimodal input capabilities
    assert capabilities.supports_vision is True  # 支持图片 / Support images
    assert capabilities.supports_video is True  # 支持视频 / Support videos

    # 验证文本输出能力 / Verify text output capabilities
    assert capabilities.supports_function_calling is True  # 支持 func call
    assert capabilities.supports_structured_outputs is True  # 支持 JSON 输出
    assert capabilities.supports_streaming is True  # 支持流式输出
    assert capabilities.supports_thinking is True  # 支持思考模式

    assert capabilities.max_tokens == 32000
    assert capabilities.context_window == 256000


def test_qwen3_vl_flash_auto_register() -> None:
    """测试 qwen3-vl-flash 自动注册 / Test qwen3-vl-flash auto register"""
    meta = LLMeta("qwen3-vl-flash")

    assert meta.family == ModelFamily.QWEN
    assert meta.version == "3"
    assert meta.variant == "vl-flash"

    # 验证多模态输入能力 / Verify multimodal input capabilities
    assert meta.capabilities.supports_vision is True
    assert meta.capabilities.supports_video is True

    # 验证文本输出能力 / Verify text output capabilities
    assert meta.capabilities.supports_function_calling is True
    assert meta.capabilities.supports_structured_outputs is True
    assert meta.capabilities.supports_streaming is True
    assert meta.capabilities.supports_thinking is True


def test_qwen3_vl_models_with_date_suffix() -> None:
    """测试带日期后缀的模型 / Test models with date suffix"""
    # 测试 qwen3-vl-plus 带日期
    meta_plus = LLMeta("qwen3-vl-plus-2025-12-16")
    assert meta_plus.family == ModelFamily.QWEN
    assert meta_plus.variant == "vl-plus"
    assert meta_plus.capabilities.supports_vision is True
    assert meta_plus.capabilities.supports_video is True
    assert meta_plus.capabilities.supports_function_calling is True
    assert meta_plus.capabilities.supports_structured_outputs is True

    # 测试 qwen3-vl-flash 带日期
    meta_flash = LLMeta("qwen3-vl-flash-2025-12-16")
    assert meta_flash.family == ModelFamily.QWEN
    assert meta_flash.variant == "vl-flash"
    assert meta_flash.capabilities.supports_vision is True
    assert meta_flash.capabilities.supports_video is True
    assert meta_flash.capabilities.supports_function_calling is True
    assert meta_flash.capabilities.supports_structured_outputs is True


if __name__ == "__main__":
    test_qwen3_vl_plus_pattern_match()
    test_qwen3_vl_plus_specific_config()
    test_qwen3_vl_plus_auto_register()
    test_qwen3_vl_flash_pattern_match()
    test_qwen3_vl_flash_specific_config()
    test_qwen3_vl_flash_auto_register()
    test_qwen3_vl_models_with_date_suffix()
    print("所有测试通过！/ All tests passed!")
