import pytest

MOCK_ADAPTER_PATH = "tests.mock_llm.MockLLMAdapter"


@pytest.fixture
def mock_llm_settings(settings):
    """LLM 어댑터를 Mock으로 교체."""
    settings.BOOKSTUDIO_AI_LLM_ADAPTER = MOCK_ADAPTER_PATH
    return settings
