# filename: test_o1.py
# @Time    : 2025/12/11 15:24
# @Author  : JQQ
# @Email   : jqq1716@gmail.com
# @Software: PyCharm

from whosellm.models.base import ModelFamily
from whosellm.models.registry import (
    get_default_capabilities,
    get_specific_model_config,
    match_model_pattern,
)


def test_o1_base_defaults():
    """验证 O1 家族默认能力 / Validate O1 family default capabilities"""
    capabilities = get_default_capabilities(ModelFamily.O1)

    assert capabilities.supports_vision is True
    assert capabilities.supports_streaming is True
    assert capabilities.supports_function_calling is True
    assert capabilities.supports_structured_outputs is True


def _assert_specific_config(
    name: str,
    variant: str,
    *,
    supports_vision: bool | None = None,
    streaming: bool,
    function_calling: bool,
    structured_outputs: bool,
) -> None:
    """通用 O1 具体模型断言 / Generic O1 specific model assertions"""
    config = get_specific_model_config(name)

    assert config is not None
    version, cfg_variant, capabilities = config
    assert version == "1.0"
    assert cfg_variant == variant
    assert capabilities is not None
    if supports_vision is not None:
        assert capabilities.supports_vision is supports_vision
    assert capabilities.supports_streaming is streaming
    assert capabilities.supports_function_calling is function_calling
    assert capabilities.supports_structured_outputs is structured_outputs


def test_o1_base_specific_model():
    """验证 o1 基础模型能力 / Validate o1 base model capabilities"""
    _assert_specific_config(
        "o1",
        "base",
        supports_vision=True,
        streaming=True,
        function_calling=True,
        structured_outputs=True,
    )


def test_o1_base_with_date_pattern():
    """验证带日期的 o1 模型匹配 / Validate dated o1 model pattern"""
    matched = match_model_pattern("o1-2025-04-16")

    assert matched is not None
    assert matched["family"] == ModelFamily.O1
    assert matched["_from_specific_model"] == "o1"
    assert matched["variant"] == "base"

    # 通过具体模型配置验证视觉能力 / Validate vision capability via specific model config
    config = get_specific_model_config(matched["_from_specific_model"])
    assert config is not None
    _, _, capabilities = config
    assert capabilities.supports_vision is True


def test_o1_mini_specific_model():
    """验证 o1-mini 模型能力 / Validate o1-mini model capabilities"""
    _assert_specific_config(
        "o1-mini",
        "mini",
        supports_vision=False,
        streaming=True,
        function_calling=True,
        structured_outputs=True,
    )


def test_o1_mini_with_date_pattern():
    """验证带日期的 o1-mini 模型匹配 / Validate dated o1-mini model pattern"""
    matched = match_model_pattern("o1-mini-2025-01-31")

    assert matched is not None
    assert matched["family"] == ModelFamily.O1
    assert matched["_from_specific_model"] == "o1-mini"
    assert matched["variant"] == "mini"


def test_o1_pro_specific_model():
    """验证 o1-pro 模型能力 / Validate o1-pro model capabilities"""
    _assert_specific_config(
        "o1-pro",
        "pro",
        supports_vision=True,
        streaming=False,
        function_calling=True,
        structured_outputs=True,
    )


def test_o1_pro_with_date_pattern():
    """验证带日期的 o1-pro 模型匹配 / Validate dated o1-pro model pattern"""
    matched = match_model_pattern("o1-pro-2025-06-10")

    assert matched is not None
    assert matched["family"] == ModelFamily.O1
    assert matched["_from_specific_model"] == "o1-pro"
    assert matched["variant"] == "pro"

    # 通过具体模型配置验证视觉能力 / Validate vision capability via specific model config
    config = get_specific_model_config(matched["_from_specific_model"])
    assert config is not None
    _, _, capabilities = config
    assert capabilities.supports_vision is True
