# filename: test_gemini.py
# @Time    : 2025/12/12 13:17
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm
"""
Google Gemini 模型家族测试 / Google Gemini model family tests
"""

import pytest

from whosellm.models.base import ModelFamily
from whosellm.models.registry import get_specific_model_config, match_model_pattern


def test_gemini_3_pro_preview():
    """测试 Gemini 3 Pro Preview 模型 / Test Gemini 3 Pro Preview model"""
    config = get_specific_model_config("gemini-3-pro-preview")
    assert config is not None
    version, variant, capabilities = config
    assert version == "3.0"
    assert variant == "pro"
    assert capabilities.supports_vision is True
    assert capabilities.supports_audio is True
    assert capabilities.supports_video is True
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.max_tokens == 65536
    assert capabilities.context_window == 1048576


def test_gemini_3_pro_image_preview():
    """测试 Gemini 3 Pro Image Preview 模型 / Test Gemini 3 Pro Image Preview model"""
    config = get_specific_model_config("gemini-3-pro-image-preview")
    assert config is not None
    version, variant, capabilities = config
    assert version == "3.0"
    assert variant == "pro-image"
    assert capabilities.supports_vision is True
    assert capabilities.supports_image_generation is True
    assert capabilities.max_tokens == 32768
    assert capabilities.context_window == 65536


def test_gemini_2_5_flash():
    """测试 Gemini 2.5 Flash 模型 / Test Gemini 2.5 Flash model"""
    config = get_specific_model_config("gemini-2.5-flash")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "flash"
    assert capabilities.supports_vision is True
    assert capabilities.supports_audio is True
    assert capabilities.supports_video is True
    assert capabilities.supports_thinking is True
    assert capabilities.max_tokens == 65536
    assert capabilities.context_window == 1048576


def test_gemini_2_5_flash_preview():
    """测试 Gemini 2.5 Flash Preview 模型 / Test Gemini 2.5 Flash Preview model"""
    config = get_specific_model_config("gemini-2.5-flash-preview-09-2025")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "flash"
    assert capabilities.supports_vision is True
    assert capabilities.supports_audio is True
    assert capabilities.supports_video is True
    assert capabilities.max_tokens == 65536
    assert capabilities.context_window == 1048576


def test_gemini_2_5_flash_image():
    """测试 Gemini 2.5 Flash Image 模型 / Test Gemini 2.5 Flash Image model"""
    config = get_specific_model_config("gemini-2.5-flash-image")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "flash-image"
    assert capabilities.supports_vision is True
    assert capabilities.supports_image_generation is True
    assert capabilities.max_tokens == 32768
    assert capabilities.context_window == 65536


def test_gemini_2_5_flash_live():
    """测试 Gemini 2.5 Flash Live 模型 / Test Gemini 2.5 Flash Live model"""
    config = get_specific_model_config("gemini-2.5-flash-native-audio-preview-09-2025")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "flash-live"
    assert capabilities.supports_audio is True
    assert capabilities.supports_video is True
    assert capabilities.supports_audio_generation is True
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 131072


def test_gemini_2_5_flash_tts():
    """测试 Gemini 2.5 Flash TTS 模型 / Test Gemini 2.5 Flash TTS model"""
    config = get_specific_model_config("gemini-2.5-flash-preview-tts")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "flash-tts"
    assert capabilities.supports_audio_generation is True
    assert capabilities.max_tokens == 16384
    assert capabilities.context_window == 8192


def test_gemini_2_5_flash_lite():
    """测试 Gemini 2.5 Flash Lite 模型 / Test Gemini 2.5 Flash Lite model"""
    config = get_specific_model_config("gemini-2.5-flash-lite")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "flash-lite"
    assert capabilities.supports_vision is True
    assert capabilities.supports_audio is True
    assert capabilities.supports_video is True
    assert capabilities.max_tokens == 65536
    assert capabilities.context_window == 1048576


def test_gemini_2_5_pro():
    """测试 Gemini 2.5 Pro 模型 / Test Gemini 2.5 Pro model"""
    config = get_specific_model_config("gemini-2.5-pro")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "pro"
    assert capabilities.supports_vision is True
    assert capabilities.supports_audio is True
    assert capabilities.supports_video is True
    assert capabilities.max_tokens == 65536
    assert capabilities.context_window == 1048576


def test_gemini_2_0_flash():
    """测试 Gemini 2.0 Flash 模型 / Test Gemini 2.0 Flash model"""
    # 测试主要版本
    config = get_specific_model_config("gemini-2.0-flash")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.0"
    assert variant == "flash"
    assert capabilities.supports_vision is True
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 1048576

    # 测试稳定版本
    config = get_specific_model_config("gemini-2.0-flash-001")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.0"
    assert variant == "flash"

    # 测试实验版本
    config = get_specific_model_config("gemini-2.0-flash-exp")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.0"
    assert variant == "flash"


def test_gemini_2_0_flash_image():
    """测试 Gemini 2.0 Flash Image 模型 / Test Gemini 2.0 Flash Image model"""
    config = get_specific_model_config("gemini-2.0-flash-preview-image-generation")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.0"
    assert variant == "flash-image"
    assert capabilities.supports_vision is True
    assert capabilities.supports_image_generation is True
    assert capabilities.max_tokens == 8192
    assert capabilities.context_window == 32768


def test_gemini_2_0_flash_lite():
    """测试 Gemini 2.0 Flash Lite 模型 / Test Gemini 2.0 Flash Lite model"""
    # 测试主要版本
    config = get_specific_model_config("gemini-2.0-flash-lite")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.0"
    assert variant == "flash-lite"
    assert capabilities.supports_vision is True
    assert capabilities.max_tokens == 8192

    # 测试稳定版本
    config = get_specific_model_config("gemini-2.0-flash-lite-001")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.0"
    assert variant == "flash-lite"


def test_gemini_pattern_matching():
    """测试 Gemini 模式匹配 / Test Gemini pattern matching"""
    # 测试基础模式匹配
    matched = match_model_pattern("gemini-2.5-flash")
    assert matched is not None
    assert matched["family"] == ModelFamily.GEMINI
    assert matched["version"] == "2.5"
    assert matched["variant"] == "flash"

    # 测试版本模式匹配
    matched = match_model_pattern("gemini-2.0-flash")
    assert matched is not None
    assert matched["family"] == ModelFamily.GEMINI
    assert matched["version"] == "2.0"
    assert matched["variant"] == "flash"


def test_gemini_with_date_suffix():
    """测试带日期后缀的 Gemini 模型 / Test Gemini model with date suffix"""
    # 这个测试检查是否能正确处理带日期的模型名称
    # 由于我们的特定模型配置优先级更高，应该匹配到特定配置
    config = get_specific_model_config("gemini-2.5-flash-preview-09-2025")
    assert config is not None
    version, variant, capabilities = config
    assert version == "2.5"
    assert variant == "flash"


def test_gemini_wrong_pattern_matching():
    """测试 Gemini 错误模式匹配 / Test Gemini wrong pattern matching"""
    # 测试一些可能被错误匹配的情况

    # 确保不会错误匹配到其他模型
    matched = match_model_pattern("gemini-unknown")
    if matched:
        # 如果匹配到了，确保是 Gemini 家族
        assert matched["family"] == ModelFamily.GEMINI

    # 测试空字符串
    matched = match_model_pattern("")
    assert matched is None

    # 测试完全不相关的模型
    matched = match_model_pattern("gpt-4")
    if matched:
        # 如果匹配到了，确保不是 Gemini 家族
        assert matched["family"] != ModelFamily.GEMINI


@pytest.mark.parametrize(
    "model_name,expected_tokens,expected_context",
    [
        ("gemini-3-pro-preview", 65536, 1048576),
        ("gemini-3-pro-image-preview", 32768, 65536),
        ("gemini-2.5-flash", 65536, 1048576),
        ("gemini-2.5-flash-image", 32768, 65536),
        ("gemini-2.5-flash-lite", 65536, 1048576),
        ("gemini-2.5-pro", 65536, 1048576),
        ("gemini-2.0-flash", 8192, 1048576),
        ("gemini-2.0-flash-lite", 8192, 1048576),
    ],
)
def test_gemini_max_tokens_and_context(model_name, expected_tokens, expected_context):
    """参数化测试 Gemini 各型号的 max_tokens 和 context_window / Parametrized test for Gemini max_tokens and context_window"""
    config = get_specific_model_config(model_name)
    assert config is not None
    assert config[2].max_tokens == expected_tokens
    assert config[2].context_window == expected_context


@pytest.mark.parametrize(
    "model_name,expected_capabilities",
    [
        ("gemini-3-pro-preview", ["vision", "audio", "video", "thinking", "function_calling"]),
        ("gemini-2.5-flash", ["vision", "audio", "video", "thinking", "function_calling"]),
        ("gemini-2.5-flash-image", ["vision", "image_generation"]),
        ("gemini-2.5-flash-native-audio-preview-09-2025", ["audio", "video", "audio_generation"]),
        ("gemini-2.5-flash-preview-tts", ["audio_generation"]),
        ("gemini-2.0-flash", ["vision", "audio", "video", "thinking", "function_calling"]),
    ],
)
def test_gemini_capabilities(model_name, expected_capabilities):
    """参数化测试 Gemini 各型号的能力 / Parametrized test for Gemini capabilities"""
    config = get_specific_model_config(model_name)
    assert config is not None
    capabilities = config[2]

    for cap in expected_capabilities:
        if cap == "vision":
            assert capabilities.supports_vision is True
        elif cap == "audio":
            assert capabilities.supports_audio is True
        elif cap == "video":
            assert capabilities.supports_video is True
        elif cap == "thinking":
            assert capabilities.supports_thinking is True
        elif cap == "function_calling":
            assert capabilities.supports_function_calling is True
        elif cap == "image_generation":
            assert capabilities.supports_image_generation is True
        elif cap == "audio_generation":
            assert capabilities.supports_audio_generation is True
