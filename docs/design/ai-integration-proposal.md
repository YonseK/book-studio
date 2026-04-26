# AI 통합 구현 기획서

## 1. 목표

BookStudio에 AI 기반 문서 자동 생성 파이프라인을 추가한다. 사용자가 주제만 제시하면 AI가 **기획 → 콘텐츠 작성 → 디자인 적용**까지 수행하여 완성된 프레젠테이션/문서를 생성한다.

---

## 2. 사용자 시나리오

```
사용자: "친환경 에너지 사업 제안서 만들어줘"

[Phase 1] 기획서 생성
  AI → 목차/구성안 제시 (10페이지, 섹션별 목적)
  사용자 → 수정/승인

[Phase 2] 콘텐츠 생성
  AI → 페이지별 텍스트 콘텐츠 스트리밍 생성
  (제목, 본문, 키포인트, 데이터 요약 등)

[Phase 3] 디자인 적용
  AI → 디자인 패턴 선택/생성 + 패널 배치 + 스타일 적용
  (배경색, 폰트, 레이아웃, 색상 팔레트)

[Phase 4] 이미지 생성 (선택)
  AI → 필요한 페이지에 이미지 생성 (Google Imagen 등)

결과: 완성된 BookEdition (pages + panels + documents)
```

### 세부 흐름

1. 사용자가 **AI 세션창**을 열고 주제/목적을 입력
2. AI가 **기획서(방향서)** 생성 — 페이지 수, 각 페이지 역할, 전체 톤
3. 사용자가 기획서 검토 후 승인 (또는 수정 요청)
4. AI가 승인된 기획서 기반으로 **페이지별 콘텐츠** 스트리밍 생성
5. 동시에 **디자인 패턴** 선택/적용 — 패널 위치, 크기, 스타일
6. 각 페이지가 완성될 때마다 에디터 캔버스에 실시간 반영
7. 완료 후 사용자가 자유롭게 편집

---

## 3. 핵심 개념: 디자인 패턴 시스템

> **가장 중요한 요소.** AI가 "어떤 스타일로 페이지를 구성할지" 알기 위한 기반.

### 3.1 디자인 패턴이란

하나의 **페이지 템플릿**으로, 다음을 포함한다:

```typescript
interface DesignPattern {
  id: string
  name: string                    // "제목 슬라이드", "본문 2단", "이미지 + 캡션"
  description: string
  category: PatternCategory       // TITLE, CONTENT, IMAGE, DATA, CLOSING, ...
  tags: string[]                  // ["미니멀", "비즈니스", "어두운"]

  // 페이지 스타일
  page_style: {
    background_type: 'CLR' | 'WP'
    background_color: string
    opacity: number
  }

  // 패널 슬롯 정의 (상대 좌표, %)
  slots: DesignSlot[]

  // 색상 팔레트
  palette: {
    primary: string
    secondary: string
    accent: string
    text: string
    background: string
  }

  // 타이포그래피
  typography: {
    heading_font: string
    body_font: string
    heading_size: number
    body_size: number
  }

  // 소스 정보
  source: 'LEGACY' | 'CURATED' | 'AI_GENERATED'
  source_page_id?: string         // 레거시 추출 시 원본 페이지
}

interface DesignSlot {
  role: 'title' | 'subtitle' | 'body' | 'image' | 'accent' | 'decoration'
  media_type: MediaType           // TXT, HL, IMG, SHA 등
  // 상대 위치 (레이아웃 크기 대비 %)
  left_pct: number
  top_pct: number
  width_pct: number
  height_pct: number
  // 기본 스타일
  style: Partial<PanelStyle>      // font_size, color, text_align, ...
}
```

### 3.2 디자인 패턴 소스

#### A. 레거시 북 추출 (LEGACY)

기존 DB에 있는 북 데이터에서 디자인 패턴을 **역공학**으로 추출한다.

```
기존 Page + Panels
  → 패널 역할 분류 (제목? 본문? 이미지? 장식?)
  → 상대 좌표로 변환
  → 스타일 추출 (색상, 폰트, 그림자 등)
  → 클러스터링 (유사한 레이아웃 그룹핑)
  → DesignPattern 레코드 생성
```

**추출 기준:**
- 패널 위치/크기의 상대 좌표 (레이아웃 크기 기준 %)
- 사용된 색상 팔레트 (배경, 텍스트, 강조)
- 폰트 조합 (제목 vs 본문)
- 패널 수와 역할 분배

#### B. 큐레이션 패턴 (CURATED)

직접 설계한 고품질 패턴. 카테고리별 최소 5~10개.

| 카테고리 | 예시 패턴 |
|----------|----------|
| TITLE | 중앙 대제목, 이미지 배경 제목, 그라데이션 제목 |
| CONTENT | 본문 1단, 본문 2단, 번호 목록, 인용 |
| IMAGE | 전체 이미지, 이미지+캡션, 이미지 그리드 |
| DATA | 표, 차트 영역, 키 수치 강조 |
| COMPARISON | 좌우 비교, Before/After |
| CLOSING | 감사 슬라이드, CTA, 연락처 |

#### C. AI 생성 패턴 (AI_GENERATED)

LLM이 콘텐츠에 맞춰 기존 패턴을 변형하거나 새 패턴을 생성.

### 3.3 디자인 패턴 → BookStudio 데이터 변환

```
DesignPattern + 콘텐츠
  → Page 생성 (background_color, background_type)
  → Slot별 Panel 생성
    → role=title → media_type=HL, text=AI생성제목
    → role=body  → media_type=TXT, text=AI생성본문
    → role=image → media_type=IMG, image=AI생성이미지
  → 상대좌표 → 절대좌표 변환 (layout.width * left_pct / 100)
  → 스타일 필드 매핑
```

---

## 4. 기술 방향

### 4.1 LLM 선택

| 용도 | 모델 | 이유 |
|------|------|------|
| 기획서 생성 | Claude Opus 4.6 / GPT-5.4 | 구조화된 문서 기획 능력 |
| 콘텐츠 작성 | Claude Opus 4.6 / GPT-5.4 | 긴 텍스트, 톤 유지 |
| 디자인 패턴 선택 | Claude Sonnet 4.6 | 패턴 매칭, JSON 출력 (비용 효율) |
| 이미지 생성 | Google Imagen 3+ | 고품질 이미지 (선택적) |

> 호스트 앱이 API 키를 주입하는 구조. BookStudio 패키지 자체는 특정 LLM에 종속되지 않는다.

### 4.2 아키텍처

```
┌─ Frontend ──────────────────────────────────┐
│                                             │
│  BookStudioEditor                           │
│  ├── AI 세션창 (AIChatPanel)                │
│  │   ├── 대화 UI (스트리밍 표시)             │
│  │   ├── 기획서 미리보기/승인                │
│  │   └── 생성 진행률 표시                    │
│  └── EditorCanvas (실시간 반영)              │
│                                             │
│  restClient ← SSE/EventSource 확장          │
│                                             │
└─────────────┬───────────────────────────────┘
              │ HTTP + SSE (Server-Sent Events)
              ▼
┌─ Backend ───────────────────────────────────┐
│                                             │
│  api/views/ai.py                            │
│  ├── POST /api/studio/ai/sessions/         세션 생성    │
│  ├── POST /api/studio/ai/sessions/{id}/generate/       │
│  │   → SSE 스트리밍 응답 (ASGI 필수)         │
│  ├── POST /api/studio/ai/sessions/{id}/approve/        │
│  │   → 기획서 승인 → 콘텐츠 생성 시작        │
│  └── GET  /api/studio/ai/design-patterns/              │
│                                             │
│  services/ai/                               │
│  ├── orchestrator.py  — 전체 파이프라인 조율  │
│  ├── planner.py       — 기획서 생성          │
│  ├── writer.py        — 콘텐츠 작성          │
│  ├── designer.py      — 디자인 패턴 선택/적용 │
│  ├── image_gen.py     — 이미지 생성 (선택)    │
│  └── pattern_extractor.py — 레거시 패턴 추출  │
│                                             │
│  models/ai.py                               │
│  ├── AISession         — 세션 상태 관리       │
│  ├── DesignPattern     — 디자인 패턴 저장     │
│  └── DesignPatternSlot — 패턴 내 슬롯        │
│                                             │
│  LLM Adapter (호스트 앱 주입)                 │
│  ├── AnthropicAdapter                       │
│  ├── OpenAIAdapter                          │
│  └── GoogleImagenAdapter                    │
│                                             │
└─────────────────────────────────────────────┘
```

### 4.3 스트리밍 방식: SSE (Server-Sent Events)

WebSocket은 이미 협업에 사용 중. AI 스트리밍은 **단방향**이므로 SSE가 적합.

> **주의**: SSE는 Django ASGI 환경이 필수. 현재 백엔드가 WSGI 기반이라면 AI 엔드포인트에 한해 ASGI(Daphne/Uvicorn) 전환 필요. 기존 WebSocket(`BookStudioConsumer`)도 ASGI를 이미 전제하므로, 호스트 앱이 ASGI로 구동하는 것이 권장됨.

```
클라이언트                          서버
   │                                │
   ├─ POST /ai/sessions/           │
   │  {book_id, prompt}            │
   │◄─ {session_id, status}        │
   │                                │
   ├─ POST /sessions/{id}/generate/│
   │  Accept: text/event-stream    │
   │◄─ event: plan_chunk           │  ← 기획서 스트리밍
   │◄─ event: plan_chunk           │
   │◄─ event: plan_complete        │
   │                                │
   ├─ POST /sessions/{id}/approve/ │
   │  {approved: true}             │
   │◄─ SSE stream                  │
   │◄─ event: page_start {idx, pattern} │  ← 페이지 생성 시작
   │◄─ event: content_chunk        │  ← 콘텐츠 스트리밍
   │◄─ event: page_complete        │  ← 페이지 완료 (panels 데이터)
   │◄─ event: page_start           │
   │◄─ ...                         │
   │◄─ event: generation_complete  │
   │                                │
```

### 4.4 LLM Adapter 패턴

호스트 앱이 LLM 접근 방식을 주입한다. BookStudio는 추상 인터페이스만 정의.

```python
# backend/bookstudio/conf.py
class BookStudioConf:
    LLM_BACKEND = 'bookstudio.adapters.AnthropicAdapter'
    LLM_CONFIG = {}  # API key, model name 등 호스트 앱이 설정

# backend/bookstudio/adapters/base.py
class BaseLLMAdapter(ABC):
    @abstractmethod
    async def generate_stream(self, messages, **kwargs) -> AsyncIterator[str]:
        """텍스트 스트리밍 생성"""

    @abstractmethod
    async def generate_json(self, messages, schema, **kwargs) -> dict:
        """구조화된 JSON 응답 생성 (디자인 패턴 선택 등)"""

class BaseImageAdapter(ABC):
    @abstractmethod
    async def generate_image(self, prompt, **kwargs) -> bytes:
        """이미지 생성"""
```

---

## 5. AI 세션창 UI

에디터 좌측 사이드바에 **새로운 탭**으로 추가.

```
┌────────────────────────────────────────────────────────┐
│ [파일] [입력] [옵션] [공유] [AI]  ← 새 탭 추가         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌─ AI 세션 ─────────────────────────────────────────┐ │
│  │                                                    │ │
│  │  🤖 무엇을 만들어 드릴까요?                        │ │
│  │                                                    │ │
│  │  ┌────────────────────────────────────────┐       │ │
│  │  │ 친환경 에너지 사업 제안서를 만들어줘.    │       │ │
│  │  │ 10페이지, 투자자 대상, 미니멀 디자인     │       │ │
│  │  └────────────────────────────────────────┘       │ │
│  │                                    [생성 시작]     │ │
│  │                                                    │ │
│  │  ── 기획서 ──────────────────────────────────      │ │
│  │  1. 표지 — 제목 + 회사 로고                        │ │
│  │  2. 목차 — 발표 구성 안내                          │ │
│  │  3. 문제 정의 — 에너지 위기 현황                    │ │
│  │  4. 솔루션 — 우리의 접근법                         │ │
│  │  5. 기술 상세 — 핵심 기술 설명                     │ │
│  │  ...                                               │ │
│  │                                                    │ │
│  │  [수정 요청]              [이대로 진행]             │ │
│  │                                                    │ │
│  │  ── 생성 중 ─────────────────────────────────      │ │
│  │  ✓ 1/10 표지 완료                                  │ │
│  │  ✓ 2/10 목차 완료                                  │ │
│  │  ● 3/10 문제 정의 생성 중...                       │ │
│  │  ○ 4/10 대기                                      │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 상태 관리

```typescript
// 별도 aiStore (Zustand)
interface AIState {
  sessionId: string | null
  phase: 'idle' | 'planning' | 'reviewing' | 'generating' | 'complete' | 'error'
  plan: AIPlan | null              // 기획서
  progress: PageProgress[]         // 페이지별 진행률
  messages: AIMessage[]            // 대화 히스토리
  selectedPatternSet: string | null // 디자인 패턴 세트
}
```

---

## 6. 데이터 모델 (신규)

### 6.1 DesignPattern (백엔드)

```python
class DesignPattern(models.Model):
    id = UUIDField(primary_key=True)
    name = CharField(max_length=100)
    description = TextField(blank=True)
    category = CharField(choices=PatternCategoryEnum)  # TITLE, CONTENT, IMAGE, DATA, ...
    tags = JSONField(default=list)                     # ["미니멀", "비즈니스"]

    # 페이지 기본 스타일
    page_style = JSONField(default=dict)               # {background_color, opacity, ...}

    # 색상 팔레트
    palette = JSONField(default=dict)                  # {primary, secondary, accent, text, bg}

    # 타이포그래피
    typography = JSONField(default=dict)               # {heading_font, body_font, sizes}

    # 소스
    source = CharField(choices=['LEGACY', 'CURATED', 'AI_GENERATED'])
    source_page = ForeignKey('Page', null=True, blank=True)

    # 메타
    is_active = BooleanField(default=True)
    usage_count = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)

class DesignPatternSlot(models.Model):
    id = UUIDField(primary_key=True)
    pattern = ForeignKey(DesignPattern, related_name='slots')
    role = CharField(choices=['title', 'subtitle', 'body', 'image', 'accent', 'decoration'])
    media_type = CharField(choices=MediaTypeEnum)

    # 상대 좌표 (%)
    left_pct = FloatField()
    top_pct = FloatField()
    width_pct = FloatField()
    height_pct = FloatField()

    # 기본 스타일 (Panel 필드 서브셋)
    style = JSONField(default=dict)

    order = PositiveSmallIntegerField(default=0)

class DesignPatternSet(models.Model):
    """여러 패턴을 하나의 테마로 묶음 (예: "미니멀 비즈니스 세트")"""
    id = UUIDField(primary_key=True)
    name = CharField(max_length=100)
    description = TextField(blank=True)
    patterns = ManyToManyField(DesignPattern, through='DesignPatternSetMembership')
    palette = JSONField(default=dict)          # 세트 전체 색상 팔레트 (개별 패턴의 palette보다 우선 적용)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)

class DesignPatternSetMembership(models.Model):
    pattern_set = ForeignKey(DesignPatternSet)
    pattern = ForeignKey(DesignPattern)
    category_priority = IntegerField(default=0)  # 같은 카테고리에서 우선순위
```

### 6.2 AISession (백엔드)

```python
class AISession(models.Model):
    id = UUIDField(primary_key=True)
    user = ForeignKey(User)
    book = ForeignKey(Book)
    edition = ForeignKey(BookEdition)

    # 입력
    prompt = TextField()                          # 사용자 요청

    # 상태
    status = CharField(choices=['PLANNING', 'REVIEW', 'GENERATING', 'COMPLETE', 'FAILED'])

    # 결과
    plan = JSONField(null=True)                   # 생성된 기획서
    pattern_set = ForeignKey(DesignPatternSet, null=True)

    # 메타
    model_used = CharField(max_length=50)         # 사용된 LLM 모델명
    total_tokens = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True)
```

---

## 7. 파이프라인 상세

### Phase 1: 기획서 생성 (planner.py)

```
입력: 사용자 프롬프트 + 레이아웃(PPTX_WIDE 등) + 디자인 패턴 세트(선택)
출력: AIPlan (JSON)

{
  "title": "친환경 에너지 사업 제안서",
  "total_pages": 10,
  "tone": "전문적, 설득력 있는",
  "target_audience": "투자자",
  "pages": [
    {
      "index": 0,
      "role": "TITLE",
      "purpose": "제목 및 회사 소개",
      "key_points": ["프로젝트명", "회사명", "날짜"],
      "suggested_pattern_category": "TITLE",
      "needs_image": false
    },
    {
      "index": 1,
      "role": "CONTENT",
      "purpose": "목차",
      "key_points": ["발표 순서 6개 항목"],
      "suggested_pattern_category": "CONTENT",
      "needs_image": false
    },
    ...
  ]
}
```

### Phase 2: 콘텐츠 + 디자인 생성 (orchestrator.py)

페이지별 순차 처리 (스트리밍):

```python
async def generate_book(session: AISession, plan: dict):
    pattern_set = session.pattern_set or select_best_pattern_set(plan)

    for page_plan in plan['pages']:
        # 1. 디자인 패턴 선택
        pattern = designer.select_pattern(
            category=page_plan['suggested_pattern_category'],
            pattern_set=pattern_set
        )

        # 2. 콘텐츠 생성 (스트리밍)
        content = await writer.generate_page_content(
            page_plan=page_plan,
            overall_plan=plan,
            pattern=pattern  # 슬롯 정보 참고하여 분량 조절
        )

        # 3. 페이지 + 패널 생성 (DB)
        page, panels = designer.apply_pattern(
            edition=session.edition,
            pattern=pattern,
            content=content,
            layout=session.book.get_layout_config()
        )

        # 4. 이미지 생성 (필요시)
        if page_plan.get('needs_image'):
            image = await image_gen.generate(
                prompt=content.image_prompt,
                aspect_ratio=calculate_aspect(pattern, 'image')
            )
            # 이미지 패널에 연결

        # 5. SSE 이벤트 전송
        yield sse_event('page_complete', {
            'index': page_plan['index'],
            'page': PageSerializer(page).data,
            'panels': PanelSerializer(panels, many=True).data
        })
```

### Phase 3: 디자인 패턴 적용 (designer.py)

```python
def apply_pattern(edition, pattern, content, layout):
    """DesignPattern → Page + Panels 변환"""

    # 페이지 생성
    page = Page.objects.create(
        book_edition=edition,
        user=edition.book.user,
        background_type=pattern.page_style.get('background_type', 'CLR'),
        background_color=pattern.page_style.get('background_color', '#ffffff'),
        opacity=pattern.page_style.get('opacity', 1.0),
        order=next_order(edition)
    )

    panels = []
    for slot in pattern.slots.order_by('order'):
        # 상대 좌표 → 절대 좌표
        left = round(layout.width * slot.left_pct / 100)
        top = round(layout.height * slot.top_pct / 100)
        width = round(layout.width * slot.width_pct / 100)
        height = round(layout.height * slot.height_pct / 100)

        # 콘텐츠 매핑
        text_content = content.get_for_role(slot.role)

        panel = Panel.objects.create(
            page=page,
            user=edition.book.user,
            media_type=slot.media_type,
            text=text_content.get('text', ''),
            headline=text_content.get('headline', ''),
            left=left, top=top,
            width=width, height=height,
            **slot.style,  # 폰트, 색상, 정렬 등
            **pattern.palette_to_style(slot.role)  # 팔레트 적용
        )
        panels.append(panel)

    # Document 생성 (WYSIWYG 텍스트 콘텐츠)
    if content.document_html:
        Document.objects.create(
            page=page,
            user=edition.book.user,
            contents=content.document_html,
            edit_type='WYSIWYG'
        )

    return page, panels
```

---

## 8. 레거시 패턴 추출 (pattern_extractor.py)

기존 DB의 북 데이터에서 디자인 패턴을 추출하는 **일회성/배치 서비스**.

### 추출 알고리즘

```
1. 대상 페이지 수집
   - 활성 상태, 패널 2개 이상
   - BookLayout별 그룹핑

2. 패널 역할 추론
   - media_type=HL → title/subtitle
   - media_type=TXT + font_size > 20 → subtitle
   - media_type=TXT + 긴 텍스트 → body
   - media_type=IMG → image
   - media_type=SHA → decoration/accent
   - z_index 낮은 큰 패널 → background/decoration

3. 좌표 정규화
   - 절대좌표 → 레이아웃 대비 % 변환
   - 유사 위치 반올림 (5% 단위)

4. 스타일 추출
   - 색상 팔레트 추출 (background_color, color 수집 → 클러스터링)
   - 폰트 조합 추출 (제목 폰트 + 본문 폰트)

5. 중복 제거 / 클러스터링
   - 슬롯 레이아웃 유사도 비교
   - 유사 패턴 병합 (대표 패턴 선정)

6. DesignPattern 레코드 저장
```

### 관리 커맨드

```bash
python manage.py extract_design_patterns --book-layout PPTX_WIDE --min-panels 2
python manage.py extract_design_patterns --book-id <uuid>  # 특정 북에서 추출
```

---

## 9. 구현 단계 (Phase)

### Phase 1: 기반 — 디자인 패턴 시스템 + 레거시 추출

**범위:** 디자인 패턴 모델, CRUD API, 레거시 추출 도구, 큐레이션 패턴 초기 세트

**결과물:**
- `DesignPattern`, `DesignPatternSlot`, `DesignPatternSet` 모델 + 마이그레이션
- 패턴 CRUD API (`/ai/design-patterns/`)
- `extract_design_patterns` 관리 커맨드
- 큐레이션 패턴 10~20개 (PPTX_WIDE 기준)

### Phase 2: AI 파이프라인 — 기획 + 콘텐츠 + 디자인 적용

**범위:** LLM Adapter, AI 서비스 계층, SSE 스트리밍 API

**결과물:**
- `AISession` 모델
- LLM Adapter 인터페이스 + Anthropic/OpenAI 구현체
- `planner.py`, `writer.py`, `designer.py`, `orchestrator.py`
- SSE 스트리밍 엔드포인트

### Phase 3: 프론트엔드 — AI 세션창

**범위:** AI 세션 UI, 스트리밍 수신, 에디터 실시간 반영

**결과물:**
- `aiStore` (Zustand)
- `AIChatPanel` 컴포넌트 (사이드바 탭)
- SSE 클라이언트 (`EventSource` 래퍼)
- 생성된 페이지/패널 실시간 반영

### Phase 4: 이미지 생성 + 고도화

**범위:** 이미지 생성 연동, 패턴 자동 생성, 사용자 피드백 반영

**결과물:**
- Google Imagen Adapter
- AI 기반 패턴 변형/생성
- "이 페이지 다시 만들어줘" 등 부분 재생성
- 디자인 패턴 추천 고도화 (사용 빈도 기반)

---

## 10. 결정 사항 (AIONETRA 호스트 앱 기반)

> AIONETRA(`/Users/yonsekim/Developer/Projects/AIONETRA`)를 호스트 앱으로 사용.
> AIONETRA에 이미 LLM Adapter 인프라, ASGI(Daphne+Channels), Celery, S3 등이 갖춰져 있음.

| # | 질문 | 결정 | 근거 |
|---|------|------|------|
| 1 | LLM API 키 주입 방식 | **호스트 앱 settings에서 주입** | AIONETRA에 이미 `LLM_TASK_ROUTING` + `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` 환경변수 체계가 있음. BookStudio `conf.py`에서 호스트 settings를 참조하면 됨. 사용자별 키 입력은 불필요. |
| 2 | AI 생성 중 수동 편집 | **생성 중 캔버스 읽기 전용 + 완료된 페이지는 편집 가능** | 생성 중인 페이지만 잠금. 이미 완료된 페이지는 즉시 편집 허용. `aiStore.phase === 'generating'`일 때 현재 생성 중 페이지의 패널 선택/드래그 비활성화. |
| 3 | 사용자 커스텀 패턴 세트 | **Phase 1에서는 시스템 제공만, Phase 4에서 사용자 커스텀 허용** | 초기에는 큐레이션 + 레거시 추출 패턴으로 충분. 사용자 피드백 후 커스텀 기능 추가. |
| 4 | 이미지 생성 비용 관리 | **호스트 앱의 테넌트 플랜에 위임** | AIONETRA에 `TenantPlan` (Free/Starter/Professional/Enterprise) + 리소스 제한 체계 존재. BookStudio는 `LLMUsageLog`로 사용량만 기록하고, 제한 판단은 호스트 앱 미들웨어에 위임. |
| 5 | 기존 에디션에 AI 생성 시 | **append (기존 페이지 뒤에 추가)** | 사용자 작업물 보호 원칙. replace가 필요하면 "새 에디션 생성" 옵션 제공. |
| 6 | 다국어 지원 | **사용자 프롬프트 언어를 그대로 사용** | LLM이 입력 언어를 감지해서 같은 언어로 응답. UI 라벨은 별도 i18n (Phase 4). 초기에는 한국어/영어 집중. |
| 7 | ASGI 전환 | **전환 불필요 — AIONETRA가 이미 ASGI** | Daphne + Channels가 이미 구동 중. BookStudio의 SSE 엔드포인트는 `StreamingHttpResponse`로 구현하면 ASGI 환경에서 자연스럽게 동작. |
| 8 | 레거시 북 DB | **같은 DB, 같은 앱 내 접근** | 기존 Book/Page/Panel 데이터가 BookStudio 모델에 있으므로 별도 연결 불필요. `extract_design_patterns` 커맨드가 동일 ORM으로 직접 조회. |

---

## 11. LLM Adapter 연동 전략 (AIONETRA 활용)

BookStudio가 독립 패키지로서 LLM에 직접 종속되지 않으면서, AIONETRA의 기존 인프라를 최대한 활용하는 구조.

### 11.1 BookStudio 측 (패키지)

```python
# backend/bookstudio/conf.py
class BookStudioConf:
    # 호스트 앱이 오버라이드
    LLM_ADAPTER_CLASS = 'bookstudio.adapters.base.BaseLLMAdapter'
    IMAGE_ADAPTER_CLASS = None  # 이미지 생성 미사용 시 None

    # 태스크별 모델 라우팅 (호스트 앱이 주입)
    LLM_TASK_ROUTING = {
        'book_planning': {},      # 기획서 생성
        'content_writing': {},    # 콘텐츠 작성
        'pattern_selection': {},  # 디자인 패턴 선택
        'image_generation': {},   # 이미지 생성
    }
```

### 11.2 AIONETRA 측 (호스트 앱)

```python
# AIONETRA settings.py
BOOKSTUDIO = {
    'LLM_ADAPTER_CLASS': 'asmr.adapters.anthropic.AnthropicLLMAdapter',
    'IMAGE_ADAPTER_CLASS': 'config.adapters.google_imagen.GoogleImagenAdapter',
    'LLM_TASK_ROUTING': {
        'book_planning': {'provider': 'anthropic', 'model': 'claude-opus-4-6'},
        'content_writing': {'provider': 'anthropic', 'model': 'claude-opus-4-6'},
        'pattern_selection': {'provider': 'anthropic', 'model': 'claude-sonnet-4-6'},
        'image_generation': {'provider': 'google', 'model': 'imagen-3'},
    },
}
```

### 11.3 장점

- AIONETRA의 기존 `asmr/adapters/` 재사용 — OpenAI/Anthropic 어댑터 이미 검증됨
- AIONETRA의 `LLM_TASK_ROUTING` 패턴과 일관성 유지
- BookStudio 패키지는 LLM 라이브러리 의존성 없음 (호스트가 주입)
- 다른 호스트 앱에서도 자체 어댑터 주입 가능

---

## 12. 비동기 처리 전략

### SSE vs Celery 하이브리드

단순 SSE만으로는 긴 생성 작업(10페이지 x LLM 호출)에서 연결 끊김 위험. AIONETRA에 이미 Celery가 있으므로 하이브리드 방식 사용.

```
클라이언트                    서버 (ASGI)                Celery Worker
   │                          │                          │
   ├─ POST /ai/sessions/     │                          │
   │  {book_id, prompt}      │                          │
   │◄─ {session_id}          │                          │
   │                          │                          │
   ├─ GET /ai/sessions/{id}/stream/                     │
   │  Accept: text/event-stream                         │
   │                          ├─ Celery task 시작 ──────►│
   │                          │                          ├─ LLM: 기획서 생성
   │◄─ event: plan_chunk     │◄─ Redis pub/sub ─────────┤
   │◄─ event: plan_complete  │                          │
   │                          │                          │
   ├─ POST /approve/         │                          │
   │                          ├─ Celery task 시작 ──────►│
   │                          │                          ├─ 페이지별 생성 루프
   │◄─ event: page_start     │◄─ Redis pub/sub ─────────┤  ├─ LLM: 콘텐츠
   │◄─ event: page_complete  │                          │  ├─ DB: Page+Panel
   │◄─ event: page_start     │                          │  └─ Redis: 이벤트 발행
   │◄─ ...                   │                          │
   │◄─ event: done           │                          │
   │                          │                          │
   (연결 끊겨도 Celery는 계속 생성. 재접속 시 이어서 수신)
```

### 장점
- SSE 연결이 끊겨도 **Celery 워커가 백그라운드에서 생성 완료**
- 재접속 시 `AISession.status` + 이미 생성된 페이지 확인 → 이어서 스트리밍
- AIONETRA의 기존 Celery 큐(`default` 또는 신규 `bookstudio` 큐) 활용
- Redis pub/sub으로 워커 → ASGI SSE 뷰 간 실시간 브릿지

---

## 13. 제약 조건

- **비용**: LLM API 호출 비용 → 기획서 승인 후에만 대량 생성 시작. 호스트 앱 테넌트 플랜으로 제한.
- **응답 시간**: 전체 북 생성 30초~2분 예상 → SSE로 점진적 표시, Celery로 안정성 확보
- **토큰 제한**: 페이지당 프롬프트 최적화, 컨텍스트 윈도우 관리
- **패키지 독립성**: BookStudio 패키지는 특정 LLM에 종속되지 않음 (Adapter 패턴)
- **기존 기능 호환**: AI 생성 결과도 일반 Page/Panel로 저장 → 기존 편집/저장/발행 흐름 그대로 사용
- **호스트 앱 의존**: Celery, Redis, ASGI는 호스트 앱이 제공. BookStudio 단독 실행 시에는 동기 fallback 지원.
