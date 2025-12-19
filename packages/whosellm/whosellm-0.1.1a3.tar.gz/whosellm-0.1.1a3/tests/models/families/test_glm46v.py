# filename: test_glm46v.py
# @Time    : 2025/12/11 10:18
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm

"""GLM-4.6V 模型家族测试 / GLM-4.6V model family tests."""

from whosellm.models.base import ModelFamily, parse_date_from_model_name
from whosellm.models.registry import match_model_pattern


def test_glm46v_specific_model_capabilities() -> None:
    """验证 glm-4.6v 精确模型能力是否正确 / Validate glm-4.6v specific model capabilities"""
    matched = match_model_pattern("glm-4.6v")

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_VISION
    assert matched["variant"] == "base"
    assert matched["version"] == "4.6"

    capabilities = matched["capabilities"]
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_vision is True
    assert capabilities.supports_video is True
    assert capabilities.supports_pdf is True
    assert capabilities.supports_streaming is True
    assert capabilities.max_tokens == 128000
    assert capabilities.context_window == 128000


def test_glm46v_flash_specific_model_capabilities() -> None:
    """验证 glm-4.6v-flash 精确模型能力 / Validate glm-4.6v-flash specific model capabilities"""
    matched = match_model_pattern("glm-4.6v-flash")

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_VISION
    assert matched["variant"] == "flash"
    assert matched["version"] == "4.6"

    capabilities = matched["capabilities"]
    assert capabilities.supports_thinking is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_vision is True
    assert capabilities.supports_video is True
    assert capabilities.supports_pdf is True
    assert capabilities.supports_streaming is True
    assert capabilities.max_tokens == 128000
    assert capabilities.context_window == 128000


def test_glm46v_mmdd_pattern() -> None:
    """验证 glm-4.6v 带 MMDD 日期后缀模式 / Validate glm-4.6v pattern with MMDD date suffix"""
    model_name = "glm-4.6v-0815"
    matched = match_model_pattern(model_name)

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_VISION
    assert matched["variant"] == "base"
    assert matched["version"] == "4.6"

    parsed = parse_date_from_model_name(model_name)
    assert parsed is not None
    assert parsed.month == 8
    assert parsed.day == 15


def test_glm46v_flash_mmdd_pattern() -> None:
    """验证 glm-4.6v-flash 带 MMDD 日期后缀模式 / Validate glm-4.6v-flash pattern with MMDD date suffix"""
    model_name = "glm-4.6v-flash-1201"
    matched = match_model_pattern(model_name)

    assert matched is not None
    assert matched["family"] == ModelFamily.GLM_VISION
    assert matched["variant"] == "flash"
    assert matched["version"] == "4.6"

    parsed = parse_date_from_model_name(model_name)
    assert parsed is not None
    assert parsed.month == 12
    assert parsed.day == 1
