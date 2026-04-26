# Phase 2 상세 설계서: AI 파이프라인

> 상위 문서: [ai-integration-proposal.md](ai-integration-proposal.md)
> 선행 Phase: [ai-phase1-design-pattern-system.md](ai-phase1-design-pattern-system.md)

## 1. 목표

사용자 프롬프트를 받아 **기획서 생성 → 콘텐츠 작성 → 디자인 패턴 적용**까지 수행하는 백엔드 AI 파이프라인을 구축한다.

**Phase 2 결과물:**
- `AISession` 모델 + 마이그레이션
- LLM Adapter 추상 인터페이스 + conf.py 확장
- 4개 서비스: `planner`, `writer`, `designer`, `orchestrator`
- Celery 태스크 + Redis pub/sub + SSE 스트리밍 API
- 프롬프트 템플릿 시스템

---

## 2. 데이터 모델

### 2.1 AISession

```python
# backend/bookstudio/models/ai.py

class AISessionStatusEnum(models.TextChoices):
    PLANNING = "PLANNING", _("Planning")
    REVIEW = "REVIEW", _("Awaiting Review")
    APPROVED = "APPROVED", _("Approved")
    GENERATING = "GENERATING", _("Generating")
    COMPLETE = "COMPLETE", _("Complete")
    FAILED = "FAILED", _("Failed")
    CANCELLED = "CANCELLED", _("Cancelled")


class AISession(models.Model):
    """AI 생성 세션. 하나의 프롬프트 → 하나의 북 생성 과정을 추적."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="bookstudio_ai_sessions",
    )
    book = models.ForeignKey(
        "bookstudio.Book", on_delete=models.CASCADE,
        related_name="ai_sessions",
    )
    edition = models.ForeignKey(
        "bookstudio.BookEdition", on_delete=models.CASCADE,
        related_name="ai_sessions",
    )

    # ── 입력 ──
    prompt = models.TextField(help_text="사용자 요청 텍스트")
    options = models.JSONField(
        default=dict, blank=True,
        help_text='{"tone": "professional", "page_count": 10, "language": "ko"}',
    )

    # ── 상태 ──
    status = models.CharField(
        max_length=20, choices=AISessionStatusEnum.choices,
        default=AISessionStatusEnum.PLANNING,
    )
    error_message = models.TextField(blank=True)

    # ── 기획서 ──
    plan = models.JSONField(
        null=True, blank=True,
        help_text="AI가 생성한 기획서 JSON",
    )

    # ── 디자인 ──
    pattern_set = models.ForeignKey(
        "bookstudio.DesignPatternSet", null=True, blank=True,
        on_delete=models.SET_NULL,
    )

    # ── 진행률 ──
    total_pages = models.PositiveSmallIntegerField(default=0)
    completed_pages = models.PositiveSmallIntegerField(default=0)

    # ── 사용량 추적 ──
    model_used = models.CharField(max_length=50, blank=True)
    total_input_tokens = models.PositiveIntegerField(default=0)
    total_output_tokens = models.PositiveIntegerField(default=0)

    # ── Celery 태스크 추적 ──
    celery_task_id = models.CharField(max_length=50, blank=True)

    # ── 타임스탬프 ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["book", "-created_at"]),
        ]

    def __str__(self):
        return f"AISession {self.id[:8]} ({self.status})"

    def mark_failed(self, message: str):
        self.status = AISessionStatusEnum.FAILED
        self.error_message = message
        self.save(update_fields=["status", "error_message", "updated_at"])

    def mark_complete(self):
        self.status = AISessionStatusEnum.COMPLETE
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def increment_progress(self):
        self.__class__.objects.filter(pk=self.pk).update(
            completed_pages=models.F("completed_pages") + 1
        )

    def add_token_usage(self, input_tokens: int, output_tokens: int):
        self.__class__.objects.filter(pk=self.pk).update(
            total_input_tokens=models.F("total_input_tokens") + input_tokens,
            total_output_tokens=models.F("total_output_tokens") + output_tokens,
        )
```

### 2.2 모델 관계

```
AISession
 ├── → Book
 ├── → BookEdition
 ├── → DesignPatternSet (선택)
 ├── plan (JSON)           ← planner가 생성
 ├── status                ← orchestrator가 관리
 └── 생성된 Page/Panel     ← designer가 PatternApplicator로 생성
```

---

## 3. LLM Adapter 인터페이스

### 3.1 BookStudio 추상 인터페이스

```python
# backend/bookstudio/adapters/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator


@dataclass
class LLMResponse:
    """LLM 응답."""
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


class BaseLLMAdapter(ABC):
    """BookStudio LLM 어댑터 추상 인터페이스."""

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4000,
        response_format: dict | None = None,
    ) -> LLMResponse:
        """동기 완성 생성."""

    @abstractmethod
    def generate_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4000,
    ) -> Generator[str, None, None]:
        """텍스트 스트리밍 생성. 청크 단위로 yield."""

    def generate_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> dict:
        """JSON 응답 생성. 기본 구현: generate() + json.loads()."""
        import json
        response = self.generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return json.loads(response.content)


class BaseImageAdapter(ABC):
    """이미지 생성 어댑터 (Phase 4)."""

    @abstractmethod
    def generate_image(
        self, prompt: str, aspect_ratio: str = "16:9", **kwargs
    ) -> bytes:
        """이미지 생성. bytes 반환."""
```

### 3.2 AIONETRA 브릿지 어댑터

AIONETRA의 `agents/services/llm_client.py`의 `BaseLLMClient`를 BookStudio 인터페이스로 래핑.

```python
# AIONETRA 측 — 호스트 앱이 제공
# config/adapters/bookstudio_llm.py

from bookstudio.adapters.base import BaseLLMAdapter, LLMResponse
from apps.agents.services.llm_client import LLMClient


class AIOnetraLLMAdapter(BaseLLMAdapter):
    """AIONETRA의 LLMClient를 BookStudio 어댑터로 래핑."""

    def __init__(self, task_type: str = "content_writing"):
        self.task_type = task_type
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = LLMClient.get_client_for_task(self.task_type)
        return self._client

    def generate(self, messages, temperature=0.3, max_tokens=4000, response_format=None):
        response = self.client.generate_sync(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=response.content,
            model=response.model,
            input_tokens=response.usage.get("input_tokens", 0),
            output_tokens=response.usage.get("output_tokens", 0),
        )

    def generate_stream(self, messages, temperature=0.3, max_tokens=4000):
        return self.client.generate_stream(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
```

### 3.3 conf.py 확장

```python
# backend/bookstudio/conf.py 에 추가

# ── AI 설정 ──
AI_LLM_ADAPTER = getattr(
    settings, "BOOKSTUDIO_AI_LLM_ADAPTER",
    "bookstudio.adapters.base.BaseLLMAdapter",
)

AI_IMAGE_ADAPTER = getattr(
    settings, "BOOKSTUDIO_AI_IMAGE_ADAPTER",
    None,
)

AI_TASK_ROUTING = getattr(
    settings, "BOOKSTUDIO_AI_TASK_ROUTING",
    {
        "planning": {},       # 기획서 생성
        "writing": {},        # 콘텐츠 작성
        "design": {},         # 패턴 선택
    },
)

# Celery 사용 여부 (호스트 앱에 Celery가 없으면 동기 fallback)
AI_USE_CELERY = getattr(settings, "BOOKSTUDIO_AI_USE_CELERY", False)

# Redis 채널 (SSE 브릿지용)
AI_REDIS_CHANNEL_PREFIX = getattr(
    settings, "BOOKSTUDIO_AI_REDIS_CHANNEL_PREFIX", "bookstudio:ai"
)
```

### 3.4 어댑터 팩토리

```python
# backend/bookstudio/adapters/factory.py

from django.utils.module_loading import import_string
from bookstudio import conf


def get_llm_adapter(task_type: str = "writing") -> "BaseLLMAdapter":
    """설정에서 LLM 어댑터를 로드하고 task_type으로 초기화."""
    adapter_class = import_string(conf.AI_LLM_ADAPTER)

    # task_type별 설정이 있으면 전달
    task_config = conf.AI_TASK_ROUTING.get(task_type, {})
    if task_config:
        return adapter_class(task_type=task_type, **task_config)
    return adapter_class()


def get_image_adapter() -> "BaseImageAdapter | None":
    """이미지 어댑터 로드. 설정 없으면 None."""
    if not conf.AI_IMAGE_ADAPTER:
        return None
    return import_string(conf.AI_IMAGE_ADAPTER)()
```

---

## 4. 프롬프트 템플릿

### 4.1 구조

```
backend/bookstudio/services/ai/prompts/
├── planner.py       # 기획서 생성 프롬프트
├── writer.py        # 콘텐츠 작성 프롬프트
└── designer.py      # 디자인 패턴 선택 프롬프트
```

### 4.2 기획서 생성 프롬프트 (planner.py)

```python
PLANNING_SYSTEM = """당신은 프레젠테이션/문서 기획 전문가입니다.
사용자의 요청을 분석하여 페이지별 구성안을 JSON으로 작성합니다.

## 출력 형식
반드시 아래 JSON 스키마를 따르세요:
{
  "title": "문서 제목",
  "total_pages": 숫자,
  "tone": "톤/분위기 설명",
  "target_audience": "대상 독자",
  "color_mood": "색상 분위기 (dark/light/colorful/mono)",
  "pages": [
    {
      "index": 0,
      "role": "TITLE | SECTION | CONTENT | CONTENT_2COL | IMAGE | IMG_TXT | DATA | COMPARISON | QUOTE | CLOSING",
      "purpose": "이 페이지의 목적",
      "key_points": ["포함할 핵심 내용"],
      "suggested_pattern_category": "role과 동일",
      "needs_image": true/false
    }
  ]
}

## 규칙
- 첫 페이지는 반드시 TITLE
- 마지막 페이지는 CLOSING 권장
- 7~15페이지가 적정 (사용자가 명시하지 않은 경우)
- CONTENT 류가 50% 이상
- 데이터/비교 페이지는 핵심 메시지를 key_points에 명시
- needs_image는 시각적 효과가 필요한 페이지에만 true
"""

PLANNING_USER = """다음 요청에 맞는 프레젠테이션 구성안을 작성해주세요.

요청: {prompt}

레이아웃: {layout_label} ({layout_width}x{layout_height})
{options_text}
"""
```

### 4.3 콘텐츠 작성 프롬프트 (writer.py)

```python
WRITING_SYSTEM = """당신은 프레젠테이션 콘텐츠 작성 전문가입니다.
주어진 페이지 기획에 맞는 텍스트 콘텐츠를 JSON으로 작성합니다.

## 출력 형식
{
  "slots": [
    {
      "role": "title | subtitle | body | caption | number",
      "headline": "제목 텍스트 (HL 패널용, role이 title/subtitle일 때)",
      "text": "본문 텍스트 (TXT 패널용)",
      "document_html": "<p>긴 텍스트용 HTML</p> (body role이고 텍스트가 긴 경우)"
    }
  ],
  "image_prompt": "이미지 생성 프롬프트 (needs_image가 true인 경우)"
}

## 규칙
- headline은 한 줄, 간결하게 (최대 50자)
- body text는 슬라이드에 맞게 짧게 (3~5문장, 최대 200자)
- number role은 핵심 수치 + 단위 (예: "98%", "₩2.4조")
- caption은 한 줄 설명 (최대 30자)
- 전체 문서의 톤과 일관성 유지
- 이전 페이지 내용과 자연스럽게 이어지도록
"""

WRITING_USER = """## 전체 문서 정보
- 제목: {plan_title}
- 톤: {plan_tone}
- 대상: {plan_audience}

## 현재 페이지
- 인덱스: {page_index}/{total_pages}
- 역할: {page_role}
- 목적: {page_purpose}
- 핵심 내용: {key_points}
- 이미지 필요: {needs_image}

## 이 페이지의 패턴 슬롯
{slot_roles}

## 이전 페이지 요약
{previous_summary}

위 슬롯에 맞는 콘텐츠를 작성해주세요.
"""
```

### 4.4 디자인 패턴 선택 프롬프트 (designer.py)

```python
PATTERN_SELECTION_SYSTEM = """당신은 프레젠테이션 디자인 전문가입니다.
주어진 페이지 기획과 사용 가능한 패턴 목록을 보고 최적의 패턴을 선택합니다.

## 출력 형식
{
  "pattern_id": "선택한 패턴 ID",
  "reason": "선택 이유 (한 줄)"
}

## 선택 기준
1. 카테고리 일치 (가장 중요)
2. 슬롯 구성이 콘텐츠에 적합한지
3. 같은 세트 내에서 중복 패턴 회피
4. 이미지가 필요한 페이지에는 image 슬롯이 있는 패턴
"""

PATTERN_SELECTION_USER = """## 페이지 기획
- 역할: {page_role}
- 목적: {page_purpose}
- 이미지 필요: {needs_image}

## 사용 가능한 패턴 목록
{patterns_json}

## 이미 사용된 패턴 (중복 회피)
{used_patterns}

최적의 패턴을 선택해주세요.
"""
```

---

## 5. 서비스 계층

### 5.1 아키텍처 개요

```
orchestrator.py (전체 조율)
 ├── planner.py      기획서 생성
 ├── designer.py     패턴 선택 + 적용
 ├── writer.py       콘텐츠 작성
 └── (Phase 1)
     └── pattern_applicator.py  패턴 → Page+Panel 변환
```

### 5.2 Planner — 기획서 생성

```python
# backend/bookstudio/services/ai/planner.py

from dataclasses import dataclass
from bookstudio.adapters.factory import get_llm_adapter
from bookstudio.services.ai.prompts.planner import PLANNING_SYSTEM, PLANNING_USER
from bookstudio.services.layout import get_layout


@dataclass
class Plan:
    title: str
    total_pages: int
    tone: str
    target_audience: str
    color_mood: str
    pages: list[dict]
    raw: dict  # 원본 JSON

    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        return cls(
            title=data["title"],
            total_pages=data["total_pages"],
            tone=data["tone"],
            target_audience=data.get("target_audience", ""),
            color_mood=data.get("color_mood", "dark"),
            pages=data["pages"],
            raw=data,
        )


class PlannerService:
    """사용자 프롬프트 → 기획서 JSON 생성."""

    def generate_plan(
        self,
        prompt: str,
        layout_preset: str,
        options: dict | None = None,
    ) -> tuple[Plan, int, int]:
        """
        Returns:
            (plan, input_tokens, output_tokens)
        """
        adapter = get_llm_adapter(task_type="planning")
        layout = get_layout(layout_preset)

        options = options or {}
        options_text = ""
        if options.get("page_count"):
            options_text += f"페이지 수: {options['page_count']}매\n"
        if options.get("tone"):
            options_text += f"톤: {options['tone']}\n"
        if options.get("language"):
            options_text += f"언어: {options['language']}\n"

        messages = [
            {"role": "system", "content": PLANNING_SYSTEM},
            {"role": "user", "content": PLANNING_USER.format(
                prompt=prompt,
                layout_label=layout.label,
                layout_width=layout.width,
                layout_height=layout.height,
                options_text=options_text,
            )},
        ]

        response = adapter.generate(
            messages=messages,
            temperature=0.3,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )

        import json
        plan_data = json.loads(response.content)
        plan = Plan.from_dict(plan_data)

        return plan, response.input_tokens, response.output_tokens
```

### 5.3 Designer — 패턴 선택

```python
# backend/bookstudio/services/ai/designer.py

from bookstudio.models.design_pattern import (
    DesignPattern, DesignPatternSet, PatternCategoryEnum,
)
from bookstudio.adapters.factory import get_llm_adapter
from bookstudio.services.ai.prompts.designer import (
    PATTERN_SELECTION_SYSTEM, PATTERN_SELECTION_USER,
)


class DesignerService:
    """페이지 기획 + 패턴 세트 → 최적 패턴 선택."""

    def select_pattern(
        self,
        page_plan: dict,
        pattern_set: DesignPatternSet | None,
        used_pattern_ids: list[str],
        available_patterns: list[DesignPattern] | None = None,
    ) -> DesignPattern:
        """
        단일 페이지에 적용할 패턴 선택.
        1) 세트 내에서 카테고리 매칭 시도
        2) 없으면 LLM에 선택 위임
        3) 그래도 없으면 카테고리 기본 패턴 fallback
        """
        category = page_plan.get("suggested_pattern_category", "CONTENT")

        # 1단계: 패턴 세트에서 직접 매칭
        if pattern_set:
            pattern = pattern_set.get_pattern(category)
            if pattern and pattern.id not in used_pattern_ids:
                return pattern

        # 2단계: LLM 선택
        candidates = available_patterns or self._get_candidates(category)
        if len(candidates) > 1:
            pattern = self._llm_select(page_plan, candidates, used_pattern_ids)
            if pattern:
                return pattern

        # 3단계: fallback — 카테고리 첫 번째 또는 CONTENT
        if candidates:
            return candidates[0]
        return DesignPattern.objects.filter(
            category=PatternCategoryEnum.CONTENT, is_active=True
        ).first()

    def select_pattern_set(self, plan: dict) -> DesignPatternSet | None:
        """기획서의 color_mood에 맞는 패턴 세트 선택."""
        color_mood = plan.get("color_mood", "dark")

        # TODO: DesignPatternSet에 tags 필드 추가 후 매칭 로직 구현.
        # 현재는 활성 세트 중 첫 번째를 반환 (초기 큐레이션 세트 1개 전제).
        # Phase 4에서 color_mood 기반 매칭으로 고도화 예정.
        pattern_set = DesignPatternSet.objects.filter(is_active=True).first()
        return pattern_set

    def _get_candidates(self, category: str) -> list[DesignPattern]:
        return list(
            DesignPattern.objects.filter(
                category=category, is_active=True
            ).order_by("-usage_count")[:5]
        )

    def _llm_select(self, page_plan, candidates, used_ids) -> DesignPattern | None:
        """LLM에게 패턴 선택 위임."""
        adapter = get_llm_adapter(task_type="design")

        patterns_json = [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "slot_count": p.slots.count(),
                "slots": [
                    {"role": s.role, "media_type": s.media_type}
                    for s in p.slots.all()
                ],
            }
            for p in candidates
        ]

        import json
        messages = [
            {"role": "system", "content": PATTERN_SELECTION_SYSTEM},
            {"role": "user", "content": PATTERN_SELECTION_USER.format(
                page_role=page_plan.get("role", ""),
                page_purpose=page_plan.get("purpose", ""),
                needs_image=page_plan.get("needs_image", False),
                patterns_json=json.dumps(patterns_json, ensure_ascii=False),
                used_patterns=json.dumps(used_ids),
            )},
        ]

        try:
            result = adapter.generate_json(messages=messages, temperature=0.1)
            selected_id = result.get("pattern_id")
            return next((p for p in candidates if p.id == selected_id), None)
        except Exception:
            return None
```

### 5.4 Writer — 콘텐츠 작성

```python
# backend/bookstudio/services/ai/writer.py

from dataclasses import dataclass
from bookstudio.adapters.factory import get_llm_adapter
from bookstudio.services.ai.prompts.writer import WRITING_SYSTEM, WRITING_USER
from bookstudio.services.pattern_applicator import SlotContent


@dataclass
class PageContent:
    """AI가 생성한 페이지 콘텐츠."""
    slots: list[SlotContent]
    image_prompt: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class WriterService:
    """기획서 + 패턴 슬롯 정보 → 슬롯별 콘텐츠 생성."""

    def __init__(self):
        self._previous_summaries: list[str] = []

    def generate_page_content(
        self,
        plan: dict,
        page_plan: dict,
        slot_roles: list[dict],
    ) -> PageContent:
        """
        단일 페이지의 콘텐츠를 생성.

        Args:
            plan: 전체 기획서
            page_plan: 현재 페이지 기획
            slot_roles: 패턴 슬롯 정보 [{"role": "title", "media_type": "HL"}, ...]
        """
        adapter = get_llm_adapter(task_type="writing")

        slot_roles_text = "\n".join(
            f"- {s['role']} ({s['media_type']})" for s in slot_roles
        )

        previous_summary = "\n".join(self._previous_summaries[-3:]) or "없음 (첫 페이지)"

        messages = [
            {"role": "system", "content": WRITING_SYSTEM},
            {"role": "user", "content": WRITING_USER.format(
                plan_title=plan.get("title", ""),
                plan_tone=plan.get("tone", ""),
                plan_audience=plan.get("target_audience", ""),
                page_index=page_plan["index"],
                total_pages=plan["total_pages"],
                page_role=page_plan["role"],
                page_purpose=page_plan["purpose"],
                key_points=", ".join(page_plan.get("key_points", [])),
                needs_image=page_plan.get("needs_image", False),
                slot_roles=slot_roles_text,
                previous_summary=previous_summary,
            )},
        ]

        response = adapter.generate(
            messages=messages,
            temperature=0.5,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        import json
        data = json.loads(response.content)

        # SlotContent 변환
        slots = []
        for slot_data in data.get("slots", []):
            slots.append(SlotContent(
                role=slot_data["role"],
                text=slot_data.get("text", ""),
                headline=slot_data.get("headline", ""),
                document_html=slot_data.get("document_html"),
            ))

        # 이전 페이지 요약 업데이트
        summary = f"[{page_plan['role']}] {page_plan['purpose']}"
        self._previous_summaries.append(summary)

        return PageContent(
            slots=slots,
            image_prompt=data.get("image_prompt"),
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )

    def reset(self):
        """세션 시작 시 상태 초기화."""
        self._previous_summaries = []
```

### 5.5 Orchestrator — 전체 파이프라인 조율

```python
# backend/bookstudio/services/ai/orchestrator.py

import logging
from bookstudio.models import BookEdition
from bookstudio.models.ai import AISession, AISessionStatusEnum
from bookstudio.models.design_pattern import DesignPattern
from bookstudio.services.ai.planner import PlannerService
from bookstudio.services.ai.writer import WriterService
from bookstudio.services.ai.designer import DesignerService
from bookstudio.services.pattern_applicator import PatternApplicator
from bookstudio.services.layout import get_layout

logger = logging.getLogger(__name__)


class OrchestratorService:
    """AI 북 생성 전체 파이프라인 조율."""

    def __init__(self, event_callback=None):
        """
        Args:
            event_callback: 이벤트 발행 함수.
                signature: (event_type: str, data: dict) -> None
                Celery 태스크에서는 Redis pub/sub으로 연결.
                동기 모드에서는 no-op 또는 로깅.
        """
        self.planner = PlannerService()
        self.writer = WriterService()
        self.designer = DesignerService()
        self.applicator = PatternApplicator()
        self.emit = event_callback or (lambda t, d: None)

    def run_planning(self, session: AISession) -> dict:
        """Phase 1: 기획서 생성."""
        self.emit("planning_start", {"session_id": session.id})

        plan, in_tok, out_tok = self.planner.generate_plan(
            prompt=session.prompt,
            layout_preset=session.book.book_layout,
            options=session.options,
        )

        session.plan = plan.raw
        session.total_pages = plan.total_pages
        session.status = AISessionStatusEnum.REVIEW
        session.model_used = "planning"
        session.save(update_fields=["plan", "total_pages", "status", "model_used", "updated_at"])
        session.add_token_usage(in_tok, out_tok)

        self.emit("planning_complete", {
            "session_id": session.id,
            "plan": plan.raw,
        })

        return plan.raw

    def run_generation(self, session: AISession):
        """
        Phase 2: 기획서 승인 후 콘텐츠 + 디자인 생성.
        페이지별 순차 처리. 각 페이지 완료 시 이벤트 발행.
        """
        from bookstudio.api.serializers.page import PageSerializer
        from bookstudio.api.serializers.panel import PanelSerializer

        plan = session.plan
        edition = session.edition
        layout = get_layout(session.book.book_layout)

        # 디자인 패턴 세트 선택
        pattern_set = session.pattern_set or self.designer.select_pattern_set(plan)

        # 사용 패턴 추적 (중복 회피)
        used_pattern_ids: list[str] = []

        # Writer 초기화
        self.writer.reset()

        # 기존 페이지 수 (append 모드)
        existing_page_count = edition.pages.filter(deleted=False).count()

        session.status = AISessionStatusEnum.GENERATING
        session.save(update_fields=["status", "updated_at"])

        self.emit("generation_start", {
            "session_id": session.id,
            "total_pages": plan["total_pages"],
        })

        for page_plan in plan["pages"]:
            page_index = page_plan["index"]

            try:
                self.emit("page_start", {
                    "session_id": session.id,
                    "page_index": page_index,
                    "page_role": page_plan["role"],
                })

                # 1. 패턴 선택
                pattern = self.designer.select_pattern(
                    page_plan=page_plan,
                    pattern_set=pattern_set,
                    used_pattern_ids=used_pattern_ids,
                )
                used_pattern_ids.append(pattern.id)

                # 2. 슬롯 정보 추출
                slot_roles = [
                    {"role": s.role, "media_type": s.media_type}
                    for s in pattern.slots.order_by("order")
                ]

                # 3. 콘텐츠 생성
                page_content = self.writer.generate_page_content(
                    plan=plan,
                    page_plan=page_plan,
                    slot_roles=slot_roles,
                )

                # 4. 패턴 적용 → Page + Panel 생성
                palette_override = pattern_set.palette if pattern_set and pattern_set.palette else None
                result = self.applicator.apply(
                    pattern=pattern,
                    layout=layout,
                    contents=page_content.slots,
                    edition_id=str(edition.id),
                    user_id=str(session.user_id),
                    page_order=existing_page_count + page_index,
                    palette_override=palette_override,
                )

                # 5. 토큰 사용량 기록
                session.add_token_usage(
                    page_content.input_tokens,
                    page_content.output_tokens,
                )

                # 6. 진행률 업데이트 + 이벤트 발행
                session.increment_progress()

                self.emit("page_complete", {
                    "session_id": session.id,
                    "page_index": page_index,
                    "page": PageSerializer(result.page).data,
                    "panels": PanelSerializer(result.panels, many=True).data,
                })

            except Exception as e:
                logger.error(f"Page {page_index} generation failed: {e}", exc_info=True)
                self.emit("page_error", {
                    "session_id": session.id,
                    "page_index": page_index,
                    "error": str(e),
                })
                # 개별 페이지 실패해도 계속 진행
                continue

        # 완료
        session.mark_complete()
        self.emit("generation_complete", {
            "session_id": session.id,
            "completed_pages": session.completed_pages,
        })
```

---

## 6. Celery 태스크 + 이벤트 브릿지

### 6.1 태스크 정의

```python
# backend/bookstudio/tasks.py

import logging
from celery import shared_task
from bookstudio.models.ai import AISession, AISessionStatusEnum

logger = logging.getLogger(__name__)


def _make_redis_emitter(session_id: str):
    """Celery 워커에서 Redis pub/sub으로 이벤트 발행하는 콜백 생성."""
    from bookstudio import conf

    def emit(event_type: str, data: dict):
        try:
            import django.core.cache
            from django.core.serializers.json import DjangoJSONEncoder
            import json

            cache = django.core.cache.caches["default"]
            # Redis pub/sub 채널로 발행
            channel = f"{conf.AI_REDIS_CHANNEL_PREFIX}:{session_id}"
            message = json.dumps(
                {"event": event_type, "data": data},
                cls=DjangoJSONEncoder,
            )
            # Redis PUBLISH (cache 백엔드가 Redis일 때)
            if hasattr(cache, "client"):
                cache.client.get_client().publish(channel, message)
            else:
                # Channels layer fallback
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync

                layer = get_channel_layer()
                if layer:
                    async_to_sync(layer.group_send)(
                        f"ai_session_{session_id}",
                        {"type": "ai.event", "event": event_type, "data": data},
                    )
        except Exception as e:
            logger.warning(f"Failed to emit event {event_type}: {e}")

    return emit


@shared_task(bind=True, max_retries=0, ignore_result=False)
def run_ai_planning(self, session_id: str) -> dict:
    """기획서 생성 태스크."""
    from bookstudio.services.ai.orchestrator import OrchestratorService

    session = AISession.objects.select_related("book", "edition").get(pk=session_id)
    session.celery_task_id = self.request.id
    session.save(update_fields=["celery_task_id"])

    try:
        emitter = _make_redis_emitter(session_id)
        orchestrator = OrchestratorService(event_callback=emitter)
        plan = orchestrator.run_planning(session)
        return {"status": "ok", "plan": plan}
    except Exception as exc:
        session.mark_failed(str(exc))
        raise


@shared_task(bind=True, max_retries=1, default_retry_delay=5)
def run_ai_generation(self, session_id: str) -> dict:
    """콘텐츠 + 디자인 생성 태스크."""
    from bookstudio.services.ai.orchestrator import OrchestratorService

    session = AISession.objects.select_related(
        "book", "edition", "pattern_set"
    ).get(pk=session_id)

    if session.status != AISessionStatusEnum.APPROVED:
        return {"status": "skipped", "reason": f"status is {session.status}"}

    session.celery_task_id = self.request.id
    session.save(update_fields=["celery_task_id"])

    try:
        emitter = _make_redis_emitter(session_id)
        orchestrator = OrchestratorService(event_callback=emitter)
        orchestrator.run_generation(session)
        return {"status": "ok", "completed_pages": session.completed_pages}
    except Exception as exc:
        session.mark_failed(str(exc))
        raise self.retry(exc=exc)
```

### 6.2 호스트 앱 Celery 라우팅 (AIONETRA)

```python
# AIONETRA config/celery.py 에 추가
app.conf.task_routes.update({
    "bookstudio.tasks.*": {"queue": "bookstudio"},
})
```

### 6.3 동기 Fallback (Celery 없을 때)

```python
# backend/bookstudio/services/ai/runner.py

from bookstudio import conf
from bookstudio.models.ai import AISession


def start_planning(session: AISession):
    """기획서 생성 시작. Celery 유무에 따라 분기."""
    if conf.AI_USE_CELERY:
        from bookstudio.tasks import run_ai_planning
        run_ai_planning.delay(session.id)
    else:
        from bookstudio.services.ai.orchestrator import OrchestratorService
        orchestrator = OrchestratorService()
        orchestrator.run_planning(session)


def start_generation(session: AISession):
    """콘텐츠 생성 시작."""
    if conf.AI_USE_CELERY:
        from bookstudio.tasks import run_ai_generation
        run_ai_generation.delay(session.id)
    else:
        from bookstudio.services.ai.orchestrator import OrchestratorService
        orchestrator = OrchestratorService()
        orchestrator.run_generation(session)
```

---

## 7. SSE 스트리밍 API

### 7.1 SSE 뷰

```python
# backend/bookstudio/api/views/ai_stream.py

import json
import logging
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from bookstudio.models.ai import AISession
from bookstudio import conf

logger = logging.getLogger(__name__)


def _sse_format(event: str, data: dict) -> str:
    """SSE 메시지 포맷."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_session_stream(request, session_id):
    """
    SSE 스트리밍 엔드포인트.
    Celery 워커가 Redis pub/sub으로 발행한 이벤트를 클라이언트에 전달.

    GET /api/studio/ai/sessions/{id}/stream/
    Accept: text/event-stream
    """
    try:
        session = AISession.objects.get(pk=session_id, user=request.user)
    except AISession.DoesNotExist:
        return StreamingHttpResponse(
            _sse_format("error", {"message": "Session not found"}),
            content_type="text/event-stream",
            status=404,
        )

    def event_stream():
        """Redis pub/sub 또는 Channels에서 이벤트를 수신하여 SSE로 전달."""
        import time

        # 초기 상태 전송
        yield _sse_format("session_status", {
            "session_id": session.id,
            "status": session.status,
            "plan": session.plan,
            "completed_pages": session.completed_pages,
            "total_pages": session.total_pages,
        })

        if session.status in ("COMPLETE", "FAILED", "CANCELLED"):
            yield _sse_format("done", {"status": session.status})
            return

        # Redis pub/sub 구독
        channel = f"{conf.AI_REDIS_CHANNEL_PREFIX}:{session_id}"

        try:
            from django.core.cache import caches
            cache = caches["default"]

            if hasattr(cache, "client"):
                # Redis 직접 pub/sub
                pubsub = cache.client.get_client().pubsub()
                pubsub.subscribe(channel)

                try:
                    for message in pubsub.listen():
                        if message["type"] == "message":
                            event_data = json.loads(message["data"])
                            yield _sse_format(
                                event_data["event"],
                                event_data["data"],
                            )
                            # 완료/실패 시 종료
                            if event_data["event"] in ("generation_complete", "error"):
                                yield _sse_format("done", {})
                                return
                finally:
                    pubsub.unsubscribe(channel)
                    pubsub.close()
            else:
                # Redis 없으면 polling fallback
                last_completed = session.completed_pages
                for _ in range(600):  # 최대 10분 (1초 간격)
                    time.sleep(1)
                    session.refresh_from_db()

                    if session.completed_pages > last_completed:
                        yield _sse_format("progress", {
                            "completed_pages": session.completed_pages,
                            "total_pages": session.total_pages,
                        })
                        last_completed = session.completed_pages

                    if session.status in ("COMPLETE", "FAILED", "CANCELLED"):
                        yield _sse_format("done", {"status": session.status})
                        return

                yield _sse_format("timeout", {})

        except GeneratorExit:
            logger.info(f"SSE client disconnected: {session_id}")
        except Exception as e:
            logger.error(f"SSE stream error: {e}", exc_info=True)
            yield _sse_format("error", {"message": str(e)})

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # nginx proxy buffering 비활성화
    return response
```

### 7.2 REST API 뷰

```python
# backend/bookstudio/api/views/ai.py 에 추가

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from bookstudio.models.ai import AISession, AISessionStatusEnum
from bookstudio.api.serializers.ai import AISessionSerializer, AISessionCreateSerializer
from bookstudio.services.ai.runner import start_planning, start_generation


class AISessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return AISession.objects.filter(user=self.request.user).select_related(
            "book", "edition", "pattern_set"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return AISessionCreateSerializer
        return AISessionSerializer

    def perform_create(self, serializer):
        """세션 생성 + 기획서 생성 시작."""
        session = serializer.save(user=self.request.user)
        start_planning(session)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """기획서 승인 → 콘텐츠 생성 시작."""
        session = self.get_object()

        if session.status != AISessionStatusEnum.REVIEW:
            return Response(
                {"error": f"Cannot approve session in {session.status} status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 수정된 기획서가 있으면 반영
        if "plan" in request.data:
            session.plan = request.data["plan"]

        # 패턴 세트 선택 (선택적)
        if "pattern_set_id" in request.data:
            session.pattern_set_id = request.data["pattern_set_id"]

        session.status = AISessionStatusEnum.APPROVED
        session.save(update_fields=["plan", "pattern_set", "status", "updated_at"])

        start_generation(session)

        return Response(AISessionSerializer(session).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """세션 취소."""
        session = self.get_object()

        if session.status in (AISessionStatusEnum.COMPLETE, AISessionStatusEnum.CANCELLED):
            return Response(
                {"error": "Session already completed or cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Celery 태스크 취소
        if session.celery_task_id:
            from celery.result import AsyncResult
            AsyncResult(session.celery_task_id).revoke(terminate=True)

        session.status = AISessionStatusEnum.CANCELLED
        session.save(update_fields=["status", "updated_at"])

        return Response(AISessionSerializer(session).data)
```

### 7.3 Serializer

```python
# backend/bookstudio/api/serializers/ai.py 에 추가

class AISessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISession
        fields = [
            "id", "book", "edition", "prompt", "options",
            "status", "error_message",
            "plan", "pattern_set",
            "total_pages", "completed_pages",
            "model_used", "total_input_tokens", "total_output_tokens",
            "created_at", "updated_at", "completed_at",
        ]
        read_only_fields = [
            "id", "status", "error_message", "plan",
            "total_pages", "completed_pages",
            "model_used", "total_input_tokens", "total_output_tokens",
            "created_at", "updated_at", "completed_at",
        ]


class AISessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISession
        fields = ["book", "edition", "prompt", "options", "pattern_set"]

    def validate(self, data):
        # edition이 book에 속하는지 검증
        if data["edition"].book_id != str(data["book"].id):
            raise serializers.ValidationError("Edition does not belong to the book.")
        return data
```

### 7.4 URL 등록

```python
# backend/bookstudio/api/urls.py 에 추가

from bookstudio.api.views.ai import AISessionViewSet
from bookstudio.api.views.ai_stream import ai_session_stream

# ai_router에 추가 (Phase 1에서 생성한 라우터)
ai_router.register(r"sessions", AISessionViewSet, basename="ai-session")

urlpatterns += [
    # SSE 스트리밍 (라우터 밖, 별도 경로)
    path(
        "ai/sessions/<str:session_id>/stream/",
        ai_session_stream,
        name="ai-session-stream",
    ),
]
```

---

## 8. 전체 시퀀스 다이어그램

```
Client                    Django (ASGI)              Celery Worker         Redis
  │                          │                          │                   │
  │ POST /ai/sessions/      │                          │                   │
  │ {book, edition, prompt}  │                          │                   │
  │                          │─ AISession 생성           │                   │
  │                          │─ run_ai_planning.delay()─►│                   │
  │◄─ {session_id, PLANNING} │                          │                   │
  │                          │                          │                   │
  │ GET /ai/sessions/{id}/stream/                       │                   │
  │ Accept: text/event-stream│                          │                   │
  │                          │◄─ SUBSCRIBE ─────────────┼───────────────────┤
  │◄─ event: session_status  │                          │                   │
  │                          │                          │                   │
  │                          │                          │─ LLM: 기획서 생성  │
  │                          │                          │─ PUBLISH ─────────►│
  │◄─ event: planning_start  │◄─────────────────────────┼───────────────────┤
  │                          │                          │─ PUBLISH ─────────►│
  │◄─ event: planning_complete│◄────────────────────────┼───────────────────┤
  │  (plan JSON 포함)        │                          │                   │
  │                          │                          │                   │
  │─ 사용자: 기획서 검토 ──►  │                          │                   │
  │                          │                          │                   │
  │ POST /ai/sessions/{id}/approve/                     │                   │
  │ {approved: true}         │                          │                   │
  │                          │─ status=APPROVED          │                   │
  │                          │─ run_ai_generation.delay()►│                  │
  │◄─ {session, APPROVED}    │                          │                   │
  │                          │                          │                   │
  │ (SSE 스트림 재연결 또는 유지)                        │                   │
  │                          │                          │─ 페이지별 루프:    │
  │                          │                          │  ├─ 패턴 선택      │
  │                          │                          │  ├─ LLM: 콘텐츠    │
  │                          │                          │  ├─ DB: Page+Panel │
  │                          │                          │  └─ PUBLISH ──────►│
  │◄─ event: page_start      │◄─────────────────────────┼───────────────────┤
  │◄─ event: page_complete   │◄─────────────────────────┼───────────────────┤
  │  (page + panels JSON)    │                          │                   │
  │                          │                          │                   │
  │◄─ event: page_start      │                          │  (반복)           │
  │◄─ event: page_complete   │                          │                   │
  │◄─ ...                    │                          │                   │
  │                          │                          │                   │
  │◄─ event: generation_complete                        │                   │
  │◄─ event: done            │                          │                   │
```

---

## 9. 에러 처리

### 9.1 에러 분류

| 에러 유형 | 처리 | SSE 이벤트 |
|----------|------|-----------|
| LLM API 호출 실패 | Celery 재시도 (1회) | `error` |
| LLM 응답 JSON 파싱 실패 | 재시도 후 실패 시 skip | `page_error` |
| 개별 페이지 생성 실패 | 해당 페이지 skip, 나머지 계속 | `page_error` |
| 전체 세션 실패 | `session.mark_failed()` | `error` + `done` |
| SSE 연결 끊김 | Celery는 계속 진행, 재연결 시 이어서 수신 | — |
| 사용자 취소 | Celery revoke + `CANCELLED` | `done` |

### 9.2 SSE 재연결

클라이언트가 재연결하면 `/stream/` 엔드포인트가 현재 `session.status`와 `completed_pages`를 먼저 전송하여 중간 상태를 복구한다. 이미 생성된 페이지는 일반 REST API (`GET /pages/`)로 조회.

---

## 10. 테스트 계획

### 10.1 모델 테스트

```python
class TestAISession:
    def test_create_session(self)
    def test_mark_failed(self)
    def test_mark_complete(self)
    def test_increment_progress_atomic(self)
    def test_add_token_usage_atomic(self)
```

### 10.2 서비스 테스트 (LLM Mock)

```python
class TestPlannerService:
    """LLM 어댑터를 mock하여 테스트."""
    def test_generate_plan_returns_valid_structure(self)
    def test_generate_plan_with_page_count_option(self)
    def test_generate_plan_respects_layout(self)

class TestWriterService:
    def test_generate_page_content_matches_slots(self)
    def test_previous_summary_accumulates(self)
    def test_reset_clears_state(self)

class TestDesignerService:
    def test_select_pattern_from_set(self)
    def test_select_pattern_avoids_duplicates(self)
    def test_fallback_to_content_pattern(self)

class TestOrchestratorService:
    def test_run_planning_updates_session(self)
    def test_run_generation_creates_pages(self)
    def test_run_generation_emits_events(self)
    def test_page_error_does_not_stop_generation(self)
```

### 10.3 API 테스트

```python
class TestAISessionAPI:
    def test_create_session_starts_planning(self)
    def test_approve_starts_generation(self)
    def test_approve_wrong_status_returns_400(self)
    def test_cancel_revokes_celery_task(self)
    def test_stream_returns_sse_content_type(self)
    def test_stream_sends_initial_status(self)
```

### 10.4 Mock LLM 어댑터 (테스트용)

```python
# tests/mock_llm.py

class MockLLMAdapter(BaseLLMAdapter):
    """테스트용 LLM 어댑터. 사전 정의된 응답 반환."""

    def __init__(self, responses: list[str] | None = None):
        self._responses = responses or []
        self._call_count = 0

    def generate(self, messages, **kwargs):
        response = self._responses[self._call_count % len(self._responses)]
        self._call_count += 1
        return LLMResponse(content=response, model="mock", input_tokens=10, output_tokens=50)

    def generate_stream(self, messages, **kwargs):
        response = self._responses[self._call_count % len(self._responses)]
        self._call_count += 1
        for word in response.split():
            yield word + " "
```

---

## 11. 파일 구조 (신규/수정)

```
backend/bookstudio/
├── models/
│   ├── __init__.py                       # + AISession export
│   └── ai.py                            # [신규] AISession, AISessionStatusEnum
├── adapters/
│   ├── __init__.py                       # [신규]
│   ├── base.py                           # [신규] BaseLLMAdapter, BaseImageAdapter
│   └── factory.py                        # [신규] get_llm_adapter, get_image_adapter
├── services/
│   └── ai/
│       ├── __init__.py                   # [신규]
│       ├── orchestrator.py               # [신규] OrchestratorService
│       ├── planner.py                    # [신규] PlannerService
│       ├── writer.py                     # [신규] WriterService
│       ├── designer.py                   # [신규] DesignerService
│       ├── runner.py                     # [신규] start_planning, start_generation
│       └── prompts/
│           ├── __init__.py               # [신규]
│           ├── planner.py                # [신규] PLANNING_SYSTEM/USER
│           ├── writer.py                 # [신규] WRITING_SYSTEM/USER
│           └── designer.py              # [신규] PATTERN_SELECTION_SYSTEM/USER
├── api/
│   ├── views/
│   │   ├── ai.py                         # [수정] + AISessionViewSet
│   │   └── ai_stream.py                  # [신규] SSE 스트리밍 뷰
│   ├── serializers/
│   │   └── ai.py                         # [수정] + AISession serializers
│   └── urls.py                           # [수정] + sessions/ 라우트, stream/ 경로
├── tasks.py                              # [신규] Celery 태스크
└── conf.py                               # [수정] AI 설정 추가

tests/
├── mock_llm.py                           # [신규] MockLLMAdapter
├── test_ai_session.py                    # [신규] 모델 테스트
├── test_ai_services.py                   # [신규] 서비스 테스트
└── test_ai_api.py                        # [신규] API 테스트
```

---

## 12. AIONETRA 호스트 앱 설정 예시

```python
# AIONETRA settings.py

BOOKSTUDIO_AI_LLM_ADAPTER = "config.adapters.bookstudio_llm.AIOnetraLLMAdapter"
BOOKSTUDIO_AI_IMAGE_ADAPTER = None  # Phase 4에서 추가
BOOKSTUDIO_AI_USE_CELERY = True
BOOKSTUDIO_AI_REDIS_CHANNEL_PREFIX = "bookstudio:ai"
BOOKSTUDIO_AI_TASK_ROUTING = {
    "planning": {"task_type": "book_planning"},
    "writing": {"task_type": "content_writing"},
    "design": {"task_type": "pattern_selection"},
}

# Celery 큐 라우팅
# config/celery.py
app.conf.task_routes.update({
    "bookstudio.tasks.*": {"queue": "bookstudio"},
})
```

---

## 13. Phase 1과의 연결점

| Phase 1 결과물 | Phase 2에서 사용하는 곳 |
|---------------|---------------------|
| `DesignPattern` 모델 | `DesignerService.select_pattern()` |
| `DesignPatternSet` 모델 | `DesignerService.select_pattern_set()` |
| `DesignPatternSlot` 모델 | `WriterService` (슬롯 역할 참조) |
| `PatternApplicator` 서비스 | `OrchestratorService.run_generation()` |
| 큐레이션 패턴 fixture | 패턴 선택 후보군 |
| 패턴 CRUD API | 프론트엔드 패턴 미리보기 (Phase 3) |
