# Phase 1 상세 설계서: 디자인 패턴 시스템

> 상위 문서: [ai-integration-proposal.md](ai-integration-proposal.md)

## 1. 목표

AI가 페이지를 생성할 때 **"어떤 레이아웃과 스타일로 구성할지"** 결정하는 기반 시스템을 구축한다.

**Phase 1 결과물:**
- `DesignPattern`, `DesignPatternSlot`, `DesignPatternSet` 모델 + 마이그레이션
- 패턴 CRUD API
- 레거시 북 데이터에서 패턴 추출하는 관리 커맨드
- 큐레이션 패턴 초기 세트 (PPTX_WIDE 기준 15개)
- 패턴 → Page + Panel 변환 서비스

---

## 2. 데이터 모델

### 2.1 Enum 정의

```python
# backend/bookstudio/models/design_pattern.py

class PatternCategoryEnum(models.TextChoices):
    TITLE = "TITLE", _("Title Slide")
    SECTION = "SECTION", _("Section Divider")
    CONTENT = "CONTENT", _("Content")
    CONTENT_TWO_COL = "CONTENT_2COL", _("Two Column Content")
    IMAGE = "IMAGE", _("Image Focus")
    IMAGE_TEXT = "IMG_TXT", _("Image + Text")
    DATA = "DATA", _("Data / Key Figures")
    COMPARISON = "COMPARISON", _("Comparison")
    QUOTE = "QUOTE", _("Quote / Highlight")
    CLOSING = "CLOSING", _("Closing / CTA")
    BLANK = "BLANK", _("Blank Canvas")

class SlotRoleEnum(models.TextChoices):
    TITLE = "title", _("Title")
    SUBTITLE = "subtitle", _("Subtitle")
    BODY = "body", _("Body Text")
    IMAGE = "image", _("Image")
    ACCENT = "accent", _("Accent / Decoration")
    ICON = "icon", _("Icon / Shape")
    CAPTION = "caption", _("Caption")
    NUMBER = "number", _("Key Number / Stat")

class PatternSourceEnum(models.TextChoices):
    LEGACY = "LEGACY", _("Extracted from Legacy")
    CURATED = "CURATED", _("Curated")
    AI_GENERATED = "AI_GEN", _("AI Generated")
```

### 2.2 DesignPattern

```python
class DesignPattern(models.Model):
    """페이지 레이아웃 + 스타일 템플릿."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=PatternCategoryEnum.choices
    )
    tags = models.JSONField(default=list, blank=True)
    # ["미니멀", "비즈니스", "어두운배경"]

    # 대상 레이아웃 (PPTX_WIDE, BOOK, CD 등). 비율 호환성 판단 기준.
    target_layout = models.CharField(
        max_length=20, choices=BookLayoutEnum.choices, default=BookLayoutEnum.PPTX_WIDE
    )

    # ── 페이지 스타일 ──
    page_background_type = models.CharField(
        max_length=10,
        choices=BackgroundTypeEnum.choices,
        default=BackgroundTypeEnum.COLOR,
    )
    page_background_color = models.CharField(max_length=30, default="#ffffff")
    page_opacity = models.FloatField(default=1.0)

    # ── 색상 팔레트 ──
    palette = models.JSONField(
        default=dict,
        help_text='{"primary":"#...", "secondary":"#...", "accent":"#...", "text":"#...", "background":"#..."}',
    )

    # ── 타이포그래피 ──
    typography = models.JSONField(
        default=dict,
        help_text='{"heading_font":"...", "body_font":"...", "heading_size":32, "body_size":16}',
    )

    # ── 소스 추적 ──
    source = models.CharField(
        max_length=10, choices=PatternSourceEnum.choices, default=PatternSourceEnum.CURATED
    )
    source_page = models.ForeignKey(
        "bookstudio.Page", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="extracted_patterns",
        help_text="레거시 추출 시 원본 페이지",
    )

    # ── 메타 ──
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "-usage_count"]
        indexes = [
            models.Index(fields=["category", "target_layout", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

    def increment_usage(self):
        self.__class__.objects.filter(pk=self.pk).update(
            usage_count=models.F("usage_count") + 1
        )
```

### 2.3 DesignPatternSlot

```python
class DesignPatternSlot(models.Model):
    """패턴 내 개별 패널 슬롯 (상대 좌표)."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    pattern = models.ForeignKey(
        DesignPattern, related_name="slots", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=SlotRoleEnum.choices)
    media_type = models.CharField(
        max_length=20, choices=MediaTypeEnum.choices, default=MediaTypeEnum.TXT
    )

    # ── 상대 좌표 (레이아웃 대비 %) ──
    left_pct = models.FloatField(help_text="0~100")
    top_pct = models.FloatField(help_text="0~100")
    width_pct = models.FloatField(help_text="0~100")
    height_pct = models.FloatField(help_text="0~100")

    # ── 스타일 오버라이드 (Panel 필드 서브셋) ──
    style = models.JSONField(
        default=dict,
        help_text="Panel 스타일 필드 서브셋. 예: {font_size: 32, color: '#333', text_align: 'center'}",
    )

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.pattern.name} / {self.role} ({self.media_type})"

    def to_absolute(self, layout_width: int, layout_height: int) -> dict:
        """상대 좌표를 절대 좌표(px)로 변환."""
        return {
            "left": round(layout_width * self.left_pct / 100),
            "top": round(layout_height * self.top_pct / 100),
            "width": round(layout_width * self.width_pct / 100),
            "height": round(layout_height * self.height_pct / 100),
        }
```

### 2.4 DesignPatternSet

```python
class DesignPatternSet(models.Model):
    """여러 패턴을 하나의 테마로 묶음. AI가 세트 단위로 선택."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # 세트 전체 팔레트 (개별 패턴의 palette보다 우선)
    palette = models.JSONField(default=dict, blank=True)

    target_layout = models.CharField(
        max_length=20, choices=BookLayoutEnum.choices, default=BookLayoutEnum.PPTX_WIDE
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_pattern(self, category: str) -> "DesignPattern | None":
        """카테고리로 패턴 조회. priority 높은 것 우선."""
        membership = (
            self.memberships.filter(pattern__category=category, pattern__is_active=True)
            .order_by("priority")
            .select_related("pattern")
            .first()
        )
        return membership.pattern if membership else None

    def get_patterns_by_category(self) -> dict[str, list["DesignPattern"]]:
        """카테고리별 패턴 목록 반환."""
        result: dict[str, list[DesignPattern]] = {}
        for m in self.memberships.select_related("pattern").order_by("priority"):
            result.setdefault(m.pattern.category, []).append(m.pattern)
        return result


class DesignPatternSetMembership(models.Model):
    """패턴세트 ↔ 패턴 연결 + 우선순위."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    pattern_set = models.ForeignKey(
        DesignPatternSet, related_name="memberships", on_delete=models.CASCADE
    )
    pattern = models.ForeignKey(
        DesignPattern, related_name="set_memberships", on_delete=models.CASCADE
    )
    priority = models.PositiveSmallIntegerField(
        default=0, help_text="같은 카테고리 내 우선순위 (0이 최우선)"
    )

    class Meta:
        unique_together = [("pattern_set", "pattern")]
        ordering = ["priority"]
```

### 2.5 모델 관계도

```
DesignPatternSet
 │ (M2M through Membership)
 └─ DesignPattern
     │ (1:N)
     └─ DesignPatternSlot
         └─ role, media_type, 상대좌표, 스타일

사용 시:
  DesignPattern + Content + LayoutConfig
    → Page (background) + Panel[] (절대좌표 + 스타일)
```

---

## 3. DesignPatternSlot.style 스키마

`style` JSON 필드에 저장 가능한 Panel 필드 서브셋. 누락된 필드는 Panel 기본값을 사용한다.

```typescript
// 프론트엔드 타입 참조용
interface SlotStyle {
  // 텍스트
  font_size?: number        // 기본값 16
  font_family?: string      // 기본값 "initial"
  font_weight?: string      // "initial" | "bold" | "300" | ...
  font_style?: string       // "initial" | "italic"
  font_bold?: boolean
  font_italic?: boolean
  color?: string            // 텍스트 색상
  text_align?: string       // "initial" | "left" | "center" | "right"
  letter_spacing?: number
  line_height?: number
  text_decoration?: string

  // 배경/테두리
  background_color?: string
  background_opacity?: number
  padding?: number
  border_width?: number
  border_radius?: number
  border_color?: string
  border_style?: string
  border_opacity?: number

  // 그림자
  box_shadow?: string
  box_shadow_px?: number
  text_shadow?: string
  text_shadow_px?: number

  // 변환
  opacity?: number
  rotate?: number

  // 도형
  shape_type?: number
  stroke_width?: number
}
```

**팔레트 매핑 규칙** — `style`에 색상이 명시되지 않은 경우, 패턴(또는 세트)의 `palette`에서 role 기반으로 자동 매핑:

| slot.role | palette 키 → 적용 대상 |
|-----------|----------------------|
| title | `text` → `color` |
| subtitle | `secondary` → `color` |
| body | `text` → `color` |
| number | `accent` → `color` |
| accent | `accent` → `background_color` |
| caption | `text` → `color` (opacity 0.7) |
| image | — (이미지 패널) |
| icon | `primary` → `color` |

---

## 4. 서비스: PatternApplicator

패턴 + 콘텐츠 → Page + Panel[] 변환. Phase 2 AI 파이프라인이 이 서비스를 호출한다.

```python
# backend/bookstudio/services/pattern_applicator.py

from bookstudio.models import Page, Panel, Document
from bookstudio.models.design_pattern import DesignPattern, DesignPatternSlot
from bookstudio.services.layout import LayoutConfig


@dataclass
class SlotContent:
    """AI가 생성한 슬롯별 콘텐츠."""
    role: str
    text: str = ""
    headline: str = ""
    image_id: str | None = None     # Photo.id
    document_html: str | None = None


@dataclass
class PatternApplyResult:
    page: Page
    panels: list[Panel]
    document: Document | None


class PatternApplicator:
    """DesignPattern → Page + Panels 변환."""

    # style JSON에서 Panel 필드로 매핑할 수 있는 키 목록
    ALLOWED_STYLE_KEYS = {
        "font_size", "font_family", "font_weight", "font_style",
        "font_bold", "font_italic", "color", "text_align",
        "letter_spacing", "line_height", "text_decoration",
        "background_color", "background_opacity", "padding",
        "border_width", "border_radius", "border_color",
        "border_style", "border_opacity",
        "box_shadow", "box_shadow_px", "text_shadow", "text_shadow_px",
        "opacity", "rotate", "shape_type", "stroke_width",
    }

    def apply(
        self,
        pattern: DesignPattern,
        layout: LayoutConfig,
        contents: list[SlotContent],
        edition_id: str,
        user_id: str,
        page_order: int,
        palette_override: dict | None = None,
    ) -> PatternApplyResult:
        """
        패턴을 적용하여 Page + Panel을 생성한다.

        Args:
            pattern: 적용할 디자인 패턴
            layout: 레이아웃 설정 (width, height)
            contents: 슬롯별 콘텐츠 (role로 매칭)
            edition_id: 대상 BookEdition.id
            user_id: 생성 사용자 ID
            page_order: 페이지 순서
            palette_override: 패턴세트의 팔레트로 오버라이드 (선택)
        """
        palette = palette_override or pattern.palette

        # 1) Page 생성
        page = Page.objects.create(
            book_edition_id=edition_id,
            user_id=user_id,
            background_type=pattern.page_background_type,
            background_color=self._resolve_bg_color(pattern, palette),
            opacity=pattern.page_opacity,
            order=page_order,
        )

        # 2) 콘텐츠를 role로 인덱싱
        content_map: dict[str, SlotContent] = {}
        for c in contents:
            content_map.setdefault(c.role, c)

        # 3) Slot → Panel 변환
        panels = []
        slots = pattern.slots.order_by("order")
        for slot in slots:
            content = content_map.get(slot.role, SlotContent(role=slot.role))
            panel = self._create_panel(
                slot=slot,
                content=content,
                page=page,
                layout=layout,
                user_id=user_id,
                palette=palette,
                typography=pattern.typography,
                panel_order=slot.order,
            )
            panels.append(panel)

        # 4) Document 생성 (body 콘텐츠의 document_html이 있는 경우)
        document = None
        body_content = content_map.get("body")
        if body_content and body_content.document_html:
            document = Document.objects.create(
                page=page,
                user_id=user_id,
                contents=body_content.document_html,
                edit_type="WYSIWYG",
            )

        # 5) 패턴 사용 카운트 증가
        pattern.increment_usage()

        return PatternApplyResult(page=page, panels=panels, document=document)

    def _create_panel(
        self, slot, content, page, layout, user_id, palette, typography, panel_order
    ) -> Panel:
        # 좌표 변환
        coords = slot.to_absolute(layout.width, layout.height)

        # 기본 스타일 (slot.style에서)
        style_kwargs = {}
        for key, value in (slot.style or {}).items():
            if key in self.ALLOWED_STYLE_KEYS:
                style_kwargs[key] = value

        # 팔레트 기반 색상 자동 적용 (style에 명시되지 않은 경우만)
        if "color" not in style_kwargs:
            style_kwargs["color"] = self._color_for_role(slot.role, palette)

        # 타이포그래피 자동 적용
        if "font_family" not in style_kwargs and typography:
            if slot.role in ("title", "subtitle", "number"):
                style_kwargs.setdefault("font_family", typography.get("heading_font", "initial"))
            else:
                style_kwargs.setdefault("font_family", typography.get("body_font", "initial"))

        if "font_size" not in style_kwargs and typography:
            if slot.role == "title":
                style_kwargs.setdefault("font_size", typography.get("heading_size", 32))
            elif slot.role == "subtitle":
                style_kwargs.setdefault("font_size", typography.get("heading_size", 32) - 8)

        return Panel.objects.create(
            page=page,
            user_id=user_id,
            media_type=slot.media_type,
            text=content.text,
            headline=content.headline,
            image_id=content.image_id,
            order=panel_order,
            **coords,
            **style_kwargs,
        )

    @staticmethod
    def _color_for_role(role: str, palette: dict) -> str:
        """role에 따른 팔레트 색상 매핑."""
        mapping = {
            "title": "text",
            "subtitle": "secondary",
            "body": "text",
            "number": "accent",
            "caption": "text",
            "icon": "primary",
        }
        key = mapping.get(role, "text")
        return palette.get(key, "#333333")

    @staticmethod
    def _resolve_bg_color(pattern: DesignPattern, palette: dict) -> str:
        """페이지 배경색. palette.background 우선, 없으면 패턴 기본값."""
        return palette.get("background", pattern.page_background_color)
```

---

## 5. API

### 5.1 URL 구조

```
/api/studio/ai/                          ← 신규 AI 네임스페이스
├── design-patterns/                     (DesignPatternViewSet)
│   ├── GET    /                          목록 (필터: category, target_layout, source, tags)
│   ├── POST   /                          생성
│   ├── GET    /{id}/                     상세 (slots 포함)
│   ├── PUT    /{id}/                     수정
│   ├── DELETE /{id}/                     삭제
│   └── POST   /{id}/preview/            미리보기 (패턴 → 임시 Page HTML 렌더링)
│
├── design-pattern-sets/                 (DesignPatternSetViewSet)
│   ├── GET    /                          목록
│   ├── POST   /                          생성
│   ├── GET    /{id}/                     상세 (memberships + 패턴 목록)
│   ├── PUT    /{id}/                     수정
│   └── DELETE /{id}/                     삭제
│
└── design-pattern-slots/                (DesignPatternSlotViewSet — 패턴 하위)
    ├── GET    /                          패턴 내 슬롯 목록
    ├── POST   /                          슬롯 추가
    ├── PUT    /{id}/                     슬롯 수정
    └── DELETE /{id}/                     슬롯 삭제
```

### 5.2 URL 등록

```python
# backend/bookstudio/api/urls.py 에 추가

from bookstudio.api.views.ai import (
    DesignPatternViewSet,
    DesignPatternSetViewSet,
    DesignPatternSlotViewSet,
)

# ──── AI namespace ────
ai_router = DefaultRouter()
ai_router.register(r"design-patterns", DesignPatternViewSet, basename="design-pattern")
ai_router.register(r"design-pattern-sets", DesignPatternSetViewSet, basename="design-pattern-set")

ai_slot_router = DefaultRouter()
ai_slot_router.register(r"slots", DesignPatternSlotViewSet, basename="pattern-slot")

urlpatterns += [
    path("ai/", include((ai_router.urls, "ai"))),
    path(
        "ai/design-patterns/<str:pattern_pk>/",
        include((ai_slot_router.urls, "pattern-slot-nested")),
    ),
]
```

### 5.3 Serializer

```python
# backend/bookstudio/api/serializers/ai.py

class DesignPatternSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignPatternSlot
        fields = [
            "id", "role", "media_type",
            "left_pct", "top_pct", "width_pct", "height_pct",
            "style", "order",
        ]

class DesignPatternSerializer(serializers.ModelSerializer):
    slots = DesignPatternSlotSerializer(many=True, read_only=True)
    slot_count = serializers.IntegerField(source="slots.count", read_only=True)

    class Meta:
        model = DesignPattern
        fields = [
            "id", "name", "description", "category", "tags",
            "target_layout",
            "page_background_type", "page_background_color", "page_opacity",
            "palette", "typography",
            "source", "source_page",
            "is_active", "usage_count",
            "slots", "slot_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "usage_count", "created_at", "updated_at"]

class DesignPatternListSerializer(serializers.ModelSerializer):
    """목록용 경량 시리얼라이저 (slots 제외)."""
    slot_count = serializers.IntegerField(source="slots.count", read_only=True)

    class Meta:
        model = DesignPattern
        fields = [
            "id", "name", "category", "tags", "target_layout",
            "palette", "source", "is_active", "usage_count", "slot_count",
        ]

class DesignPatternSetSerializer(serializers.ModelSerializer):
    patterns = serializers.SerializerMethodField()

    class Meta:
        model = DesignPatternSet
        fields = [
            "id", "name", "description", "palette",
            "target_layout", "is_active", "patterns", "created_at",
        ]

    def get_patterns(self, obj):
        memberships = obj.memberships.select_related("pattern").order_by("priority")
        return [
            {
                "pattern": DesignPatternListSerializer(m.pattern).data,
                "priority": m.priority,
            }
            for m in memberships
        ]

class DesignPatternSetCreateSerializer(serializers.ModelSerializer):
    pattern_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = DesignPatternSet
        fields = ["name", "description", "palette", "target_layout", "pattern_ids"]

    def create(self, validated_data):
        pattern_ids = validated_data.pop("pattern_ids", [])
        pattern_set = DesignPatternSet.objects.create(**validated_data)
        for i, pid in enumerate(pattern_ids):
            DesignPatternSetMembership.objects.create(
                pattern_set=pattern_set, pattern_id=pid, priority=i
            )
        return pattern_set
```

### 5.4 ViewSet

```python
# backend/bookstudio/api/views/ai.py

class DesignPatternViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ["category", "target_layout", "source", "is_active"]

    def get_queryset(self):
        qs = DesignPattern.objects.filter(is_active=True)
        tags = self.request.query_params.get("tags")
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            qs = qs.filter(tags__contains=tag_list)
        return qs.prefetch_related("slots")

    def get_serializer_class(self):
        if self.action == "list":
            return DesignPatternListSerializer
        return DesignPatternSerializer

    @action(detail=True, methods=["post"])
    def preview(self, request, pk=None):
        """패턴을 임시 페이지로 렌더링하여 HTML 반환."""
        pattern = self.get_object()
        layout = get_layout(pattern.target_layout)
        html = PatternPreviewService.render(pattern, layout)
        return Response({"html": html})


class DesignPatternSetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DesignPatternSet.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return DesignPatternSetCreateSerializer
        return DesignPatternSetSerializer


class DesignPatternSlotViewSet(viewsets.ModelViewSet):
    """패턴 하위 슬롯 CRUD."""
    permission_classes = [IsAuthenticated]
    serializer_class = DesignPatternSlotSerializer

    def get_queryset(self):
        return DesignPatternSlot.objects.filter(
            pattern_id=self.kwargs["pattern_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(pattern_id=self.kwargs["pattern_pk"])
```

---

## 6. 레거시 패턴 추출 (Management Command)

### 6.1 추출 알고리즘 상세

```python
# backend/bookstudio/management/commands/extract_design_patterns.py

class Command(BaseCommand):
    help = "기존 북 데이터에서 디자인 패턴을 추출"

    def add_arguments(self, parser):
        parser.add_argument("--book-layout", default="PPTX_WIDE", help="대상 레이아웃")
        parser.add_argument("--book-id", help="특정 북에서만 추출")
        parser.add_argument("--min-panels", type=int, default=2, help="최소 패널 수")
        parser.add_argument("--dry-run", action="store_true", help="DB 저장 없이 결과만 출력")

    def handle(self, **options):
        pages = self._collect_pages(options)
        raw_patterns = [self._extract_from_page(p) for p in pages]
        deduplicated = self._deduplicate(raw_patterns)
        if not options["dry_run"]:
            self._save_patterns(deduplicated)
        self.stdout.write(f"추출 완료: {len(deduplicated)}개 패턴")
```

### 6.2 패널 역할 추론 규칙

```python
def _infer_role(self, panel: Panel, layout: LayoutConfig) -> str:
    """패널의 속성으로 역할을 추론."""

    # 1. media_type 기반
    if panel.media_type == MediaTypeEnum.HL:
        return "title" if panel.font_size >= 28 else "subtitle"

    if panel.media_type == MediaTypeEnum.IMG:
        return "image"

    if panel.media_type == MediaTypeEnum.SHA:
        area_pct = (panel.width * panel.height) / (layout.width * layout.height) * 100
        return "accent" if area_pct < 10 else "icon"

    # 2. TXT 패널: 폰트 크기 + 텍스트 길이로 분류
    if panel.media_type == MediaTypeEnum.TXT:
        text_len = len(panel.text)
        if panel.font_size >= 28:
            return "title"
        if panel.font_size >= 20 or text_len < 50:
            return "subtitle" if text_len < 100 else "number"
        if text_len < 30:
            return "caption"
        return "body"

    return "body"  # fallback
```

### 6.3 좌표 정규화

```python
def _normalize_coords(self, panel: Panel, layout: LayoutConfig) -> dict:
    """절대 좌표 → 상대 좌표(%) + 5% 단위 스냅."""

    def snap(value: float) -> float:
        """5% 단위로 반올림. 예: 23.7 → 25.0"""
        return round(value / 5) * 5

    return {
        "left_pct": snap(panel.left / layout.width * 100),
        "top_pct": snap(panel.top / layout.height * 100),
        "width_pct": snap(panel.width / layout.width * 100),
        "height_pct": snap(panel.height / layout.height * 100),
    }
```

### 6.4 스타일 추출

```python
STYLE_EXTRACT_FIELDS = [
    "font_size", "font_family", "font_weight", "font_style",
    "font_bold", "font_italic", "color", "text_align",
    "letter_spacing", "line_height",
    "background_color", "background_opacity", "padding",
    "border_width", "border_radius", "border_color",
    "opacity", "shape_type",
]

def _extract_style(self, panel: Panel) -> dict:
    """패널에서 기본값과 다른 스타일만 추출."""
    defaults = {f.name: f.default for f in Panel._meta.get_fields() if hasattr(f, "default")}
    style = {}
    for field_name in self.STYLE_EXTRACT_FIELDS:
        value = getattr(panel, field_name, None)
        default = defaults.get(field_name)
        if value is not None and value != default:
            style[field_name] = value
    return style
```

### 6.5 색상 팔레트 추출

```python
def _extract_palette(self, page: Page, panels: list[Panel]) -> dict:
    """페이지 + 패널들에서 색상 팔레트 추론."""
    colors = {
        "background": page.background_color,
        "text": "#333333",
        "primary": "#333333",
        "secondary": "#666666",
        "accent": "#0066cc",
    }

    text_colors = [p.color for p in panels if p.media_type in ("TXT", "HL") and p.color != "#ffffff"]
    bg_colors = [p.background_color for p in panels if p.background_color not in ("transparent", "#ffffff", "#000000")]

    if text_colors:
        # 가장 많이 쓰인 텍스트 색상
        colors["text"] = max(set(text_colors), key=text_colors.count)

    if bg_colors:
        colors["accent"] = max(set(bg_colors), key=bg_colors.count)

    # 제목 패널의 색상 → primary
    title_panels = [p for p in panels if p.media_type == MediaTypeEnum.HL]
    if title_panels:
        colors["primary"] = title_panels[0].color

    return colors
```

### 6.6 중복 제거 (레이아웃 유사도)

```python
def _deduplicate(self, patterns: list[dict], threshold: float = 0.85) -> list[dict]:
    """슬롯 좌표 유사도 기반 중복 제거."""
    unique = []
    for p in patterns:
        is_dup = False
        for u in unique:
            if self._layout_similarity(p["slots"], u["slots"]) > threshold:
                # 사용 빈도가 높은 쪽을 대표로
                is_dup = True
                break
        if not is_dup:
            unique.append(p)
    return unique

def _layout_similarity(self, slots_a: list, slots_b: list) -> float:
    """두 슬롯 목록의 좌표 유사도 (0~1). IoU 기반."""
    if len(slots_a) != len(slots_b):
        return 0.0

    # role별 매칭 후 좌표 거리 계산
    total_sim = 0.0
    matched = 0
    for sa in slots_a:
        for sb in slots_b:
            if sa["role"] == sb["role"]:
                # 좌표 4개의 평균 차이 (%)
                diff = sum(
                    abs(sa[k] - sb[k])
                    for k in ("left_pct", "top_pct", "width_pct", "height_pct")
                ) / 4
                total_sim += max(0, 1 - diff / 20)  # 20% 이상 차이면 0
                matched += 1
                break

    return total_sim / max(len(slots_a), 1)
```

---

## 7. 큐레이션 패턴 초기 세트

PPTX_WIDE (1280x720) 기준 15개 패턴. `loaddata`로 로드.

### 7.1 패턴 목록

| # | name | category | slots (role: 위치 개요) |
|---|------|----------|----------------------|
| 1 | 중앙 대제목 | TITLE | title(중앙 40%), subtitle(하단 20%) |
| 2 | 좌측 제목 + 장식 | TITLE | title(좌측 60%), accent(우측 세로줄), subtitle(좌하단) |
| 3 | 이미지 배경 제목 | TITLE | image(전체 100%), title(중앙 오버레이), subtitle(하단 오버레이) |
| 4 | 섹션 구분 | SECTION | number(좌측 큰 숫자), title(우측 40%), accent(하단 라인) |
| 5 | 본문 1단 | CONTENT | title(상단 15%), body(중앙 70%), accent(좌측 세로줄) |
| 6 | 본문 2단 | CONTENT_2COL | title(상단 15%), body(좌 45%), body(우 45%) |
| 7 | 번호 목록 | CONTENT | title(상단 15%), number(좌측 3개), body(우측 3개) |
| 8 | 좌 이미지 + 우 텍스트 | IMG_TXT | image(좌 50%), title(우상단), body(우하단) |
| 9 | 우 이미지 + 좌 텍스트 | IMG_TXT | title(좌상단), body(좌하단), image(우 50%) |
| 10 | 전체 이미지 + 캡션 | IMAGE | image(전체 85%), caption(하단 15%) |
| 11 | 키 수치 3열 | DATA | title(상단), number(3개 균등), caption(3개 하단) |
| 12 | 좌우 비교 | COMPARISON | title(상단), body(좌 45%), body(우 45%), accent(중앙 세로줄) |
| 13 | 인용문 | QUOTE | accent(큰 따옴표 아이콘), body(중앙 60%), caption(하단 저자) |
| 14 | 감사/CTA | CLOSING | title(중앙 30%), subtitle(하단 20%), accent(상단 장식) |
| 15 | 빈 캔버스 | BLANK | — (슬롯 없음, 자유 배치용) |

### 7.2 fixture 예시 (1번: 중앙 대제목)

```json
{
  "model": "bookstudio.designpattern",
  "pk": "curated-title-center-01",
  "fields": {
    "name": "중앙 대제목",
    "description": "큰 제목이 중앙에 위치하고 부제목이 아래에 오는 타이틀 슬라이드",
    "category": "TITLE",
    "tags": ["미니멀", "범용"],
    "target_layout": "PPTX_WIDE",
    "page_background_type": "CLR",
    "page_background_color": "#1a1a2e",
    "page_opacity": 1.0,
    "palette": {
      "primary": "#e94560",
      "secondary": "#533483",
      "accent": "#e94560",
      "text": "#ffffff",
      "background": "#1a1a2e"
    },
    "typography": {
      "heading_font": "Pretendard",
      "body_font": "Pretendard",
      "heading_size": 48,
      "body_size": 18
    },
    "source": "CURATED",
    "is_active": true
  }
}
```

슬롯:

```json
[
  {
    "model": "bookstudio.designpatternslot",
    "fields": {
      "pattern": "curated-title-center-01",
      "role": "title",
      "media_type": "HL",
      "left_pct": 10, "top_pct": 30,
      "width_pct": 80, "height_pct": 20,
      "style": {
        "font_size": 48, "font_bold": true,
        "text_align": "center", "color": "#ffffff"
      },
      "order": 0
    }
  },
  {
    "model": "bookstudio.designpatternslot",
    "fields": {
      "pattern": "curated-title-center-01",
      "role": "subtitle",
      "media_type": "TXT",
      "left_pct": 20, "top_pct": 55,
      "width_pct": 60, "height_pct": 10,
      "style": {
        "font_size": 20, "text_align": "center",
        "color": "#cccccc", "letter_spacing": 1.5
      },
      "order": 1
    }
  }
]
```

### 7.3 패턴 세트 (1개)

```json
{
  "model": "bookstudio.designpatternset",
  "pk": "curated-set-minimal-dark",
  "fields": {
    "name": "미니멀 다크",
    "description": "어두운 배경, 깔끔한 타이포그래피의 비즈니스 프레젠테이션 세트",
    "palette": {
      "primary": "#e94560",
      "secondary": "#533483",
      "accent": "#e94560",
      "text": "#ffffff",
      "background": "#1a1a2e"
    },
    "target_layout": "PPTX_WIDE",
    "is_active": true
  }
}
```

> 전체 fixture 파일: `backend/bookstudio/fixtures/curated_patterns.json`

---

## 8. 프론트엔드 타입 (참조용)

Phase 3에서 사용할 타입. Phase 1에서는 백엔드만 구현하지만 API 응답 형태를 미리 정의.

```typescript
// frontend/src/types/designPattern.ts

interface DesignPatternSlot {
  id: string
  role: SlotRole
  media_type: MediaType
  left_pct: number
  top_pct: number
  width_pct: number
  height_pct: number
  style: Partial<PanelStyle>
  order: number
}

interface DesignPattern {
  id: string
  name: string
  description: string
  category: PatternCategory
  tags: string[]
  target_layout: LayoutPreset
  page_background_type: string
  page_background_color: string
  page_opacity: number
  palette: ColorPalette
  typography: Typography
  source: 'LEGACY' | 'CURATED' | 'AI_GEN'
  is_active: boolean
  usage_count: number
  slots: DesignPatternSlot[]
  slot_count: number
}

interface DesignPatternSet {
  id: string
  name: string
  description: string
  palette: ColorPalette
  target_layout: LayoutPreset
  patterns: { pattern: DesignPattern; priority: number }[]
}

interface ColorPalette {
  primary: string
  secondary: string
  accent: string
  text: string
  background: string
}

interface Typography {
  heading_font: string
  body_font: string
  heading_size: number
  body_size: number
}

type PatternCategory =
  | 'TITLE' | 'SECTION' | 'CONTENT' | 'CONTENT_2COL'
  | 'IMAGE' | 'IMG_TXT' | 'DATA' | 'COMPARISON'
  | 'QUOTE' | 'CLOSING' | 'BLANK'

type SlotRole =
  | 'title' | 'subtitle' | 'body' | 'image'
  | 'accent' | 'icon' | 'caption' | 'number'
```

---

## 9. 테스트 계획

### 9.1 모델 테스트

```python
# tests/test_design_pattern.py

class TestDesignPattern:
    def test_create_pattern_with_slots(self):
        """패턴 + 슬롯 생성 확인"""

    def test_slot_to_absolute_pptx_wide(self):
        """PPTX_WIDE(1280x720)에서 상대→절대 좌표 변환"""
        # left_pct=10, width_pct=80 → left=128, width=1024

    def test_slot_to_absolute_book(self):
        """BOOK(768x1086)에서 좌표 변환"""

    def test_increment_usage(self):
        """usage_count 원자적 증가"""

    def test_pattern_set_get_pattern_by_category(self):
        """카테고리별 패턴 조회 + priority 정렬"""

    def test_pattern_set_palette_override(self):
        """세트 팔레트가 개별 패턴보다 우선"""
```

### 9.2 서비스 테스트

```python
class TestPatternApplicator:
    def test_apply_creates_page_and_panels(self):
        """패턴 적용 시 Page 1개 + Panel N개 생성"""

    def test_apply_coordinates_match_layout(self):
        """절대 좌표가 레이아웃 크기에 비례"""

    def test_apply_palette_color_mapping(self):
        """role별 팔레트 색상 자동 매핑"""

    def test_apply_typography_mapping(self):
        """title은 heading_font, body는 body_font 사용"""

    def test_apply_with_document(self):
        """document_html이 있으면 Document 생성"""

    def test_apply_without_document(self):
        """document_html 없으면 Document 미생성"""

    def test_apply_with_palette_override(self):
        """세트 팔레트 오버라이드 적용"""

    def test_style_allowlist(self):
        """허용되지 않은 style 키는 무시"""
```

### 9.3 추출 커맨드 테스트

```python
class TestExtractDesignPatterns:
    def test_extract_from_page_with_title_and_body(self):
        """HL + TXT 패널이 있는 페이지에서 패턴 추출"""

    def test_role_inference_headline(self):
        """HL 패널 → title 역할"""

    def test_role_inference_large_text(self):
        """font_size >= 28 TXT → title"""

    def test_coordinate_normalization_snap(self):
        """좌표 5% 단위 스냅"""

    def test_deduplication(self):
        """유사 레이아웃 중복 제거"""

    def test_palette_extraction(self):
        """페이지 + 패널에서 팔레트 추출"""

    def test_dry_run(self):
        """--dry-run 시 DB 저장 없음"""
```

### 9.4 API 테스트

```python
class TestDesignPatternAPI:
    def test_list_patterns_filter_category(self):
        """category 필터링"""

    def test_list_patterns_filter_layout(self):
        """target_layout 필터링"""

    def test_list_patterns_filter_tags(self):
        """tags 필터링 (contains)"""

    def test_detail_includes_slots(self):
        """상세 응답에 slots 포함"""

    def test_create_pattern_set_with_patterns(self):
        """패턴세트 생성 시 membership 자동 생성"""

    def test_slot_crud_under_pattern(self):
        """패턴 하위 슬롯 CRUD"""
```

---

## 10. 파일 구조 (신규/수정)

```
backend/bookstudio/
├── models/
│   ├── __init__.py                    # + DesignPattern, DesignPatternSlot, DesignPatternSet export
│   └── design_pattern.py             # [신규] 3개 모델 + Enum
├── services/
│   └── pattern_applicator.py         # [신규] PatternApplicator
├── api/
│   ├── views/
│   │   └── ai.py                     # [신규] ViewSets
│   ├── serializers/
│   │   └── ai.py                     # [신규] Serializers
│   └── urls.py                        # [수정] ai/ 라우트 추가
├── management/
│   └── commands/
│       └── extract_design_patterns.py # [신규] 레거시 추출 커맨드
├── fixtures/
│   └── curated_patterns.json         # [신규] 큐레이션 패턴 15개 + 세트 1개
└── conf.py                           # [수정 예정, Phase 2] LLM 설정 추가

tests/
├── test_design_pattern.py            # [신규] 모델 + 서비스 테스트
└── test_design_pattern_api.py        # [신규] API 테스트
```

---

## 11. 마이그레이션 참고

```bash
cd backend
DJANGO_SETTINGS_MODULE=tests.settings python -m django makemigrations bookstudio
DJANGO_SETTINGS_MODULE=tests.settings python -m django migrate

# 큐레이션 패턴 로드
DJANGO_SETTINGS_MODULE=tests.settings python -m django loaddata curated_patterns
```

호스트 앱(AIONETRA)에서는:
```bash
python manage.py migrate bookstudio
python manage.py loaddata curated_patterns
```
