"""테스트용 Mock LLM 어댑터."""

import json
from typing import Generator

from bookstudio.adapters.base import BaseLLMAdapter, LLMResponse

# 기본 기획서 응답
DEFAULT_PLAN = {
    "title": "테스트 프레젠테이션",
    "total_pages": 3,
    "tone": "전문적",
    "target_audience": "일반",
    "color_mood": "dark",
    "pages": [
        {
            "index": 0, "role": "TITLE", "purpose": "제목 슬라이드",
            "key_points": ["제목"], "suggested_pattern_category": "TITLE",
            "needs_image": False,
        },
        {
            "index": 1, "role": "CONTENT", "purpose": "본문 내용",
            "key_points": ["핵심 내용"], "suggested_pattern_category": "CONTENT",
            "needs_image": False,
        },
        {
            "index": 2, "role": "CLOSING", "purpose": "마무리",
            "key_points": ["감사"], "suggested_pattern_category": "CLOSING",
            "needs_image": False,
        },
    ],
}

# 기본 콘텐츠 응답
DEFAULT_CONTENT = {
    "slots": [
        {"role": "title", "headline": "테스트 제목", "text": ""},
        {"role": "subtitle", "headline": "", "text": "부제목 텍스트"},
    ],
    "image_prompt": None,
}

# 기본 패턴 선택 응답
DEFAULT_PATTERN_SELECTION = {
    "pattern_id": "curated-title-center-01",
    "reason": "카테고리 일치",
}


class MockLLMAdapter(BaseLLMAdapter):
    """테스트용 LLM 어댑터."""

    def __init__(self, responses: list[str] | None = None, **kwargs):
        self._responses = responses or [json.dumps(DEFAULT_PLAN)]
        self._call_count = 0
        self._calls: list[dict] = []

    def generate(self, messages, temperature=0.3, max_tokens=4000, response_format=None):
        content = self._responses[self._call_count % len(self._responses)]
        self._calls.append({"messages": messages, "temperature": temperature})
        self._call_count += 1
        return LLMResponse(
            content=content, model="mock-model",
            input_tokens=10, output_tokens=50,
        )

    def generate_stream(self, messages, temperature=0.3, max_tokens=4000):
        content = self._responses[self._call_count % len(self._responses)]
        self._call_count += 1
        for word in content.split():
            yield word + " "

    @property
    def call_count(self):
        return self._call_count

    @property
    def calls(self):
        return self._calls
