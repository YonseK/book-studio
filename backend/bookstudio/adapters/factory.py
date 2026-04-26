"""LLM/이미지 어댑터 팩토리."""

from django.conf import settings
from django.utils.module_loading import import_string

from bookstudio.adapters.base import BaseLLMAdapter, BaseImageAdapter


def _get_setting(name: str, default=None):
    """settings에서 동적으로 읽어 테스트 시 override 가능."""
    return getattr(settings, name, default)


def get_llm_adapter(task_type: str = "writing") -> BaseLLMAdapter:
    """설정에서 LLM 어댑터를 로드하고 task_type으로 초기화."""
    adapter_path = _get_setting(
        "BOOKSTUDIO_AI_LLM_ADAPTER",
        "bookstudio.adapters.base.BaseLLMAdapter",
    )
    adapter_class = import_string(adapter_path)
    task_routing = _get_setting("BOOKSTUDIO_AI_TASK_ROUTING", {})
    task_config = task_routing.get(task_type, {})
    if task_config:
        return adapter_class(task_type=task_type, **task_config)
    return adapter_class()


def get_image_adapter() -> BaseImageAdapter | None:
    """이미지 어댑터 로드. 설정 없으면 None."""
    adapter_path = _get_setting("BOOKSTUDIO_AI_IMAGE_ADAPTER", None)
    if not adapter_path:
        return None
    return import_string(adapter_path)()
