# 백엔드 모델 점검 보고서

> 점검일: 2026-04-25
> 대상: `backend/bookstudio/models/` 전체 (book, page, panel, media, media_bank, item_bank, publishing)

---

## 1. 전체 구조

```
Book ─→ BookEdition ─→ Page ─→ Panel
                           ├→ Document (1:1)
                           └→ PageMemo ─→ PageMemoComment

BookCollaborator ─→ Book

Photo / WallpaperImage  (AbstractBasePhoto 상속)

MediaBank ─→ Book, Photo, WallpaperImage
MediaGallery ─→ Photo, WallpaperImage
MediaGalleryMember ─→ MediaGalleryMembership, MediaGallery

PubItem  (AbstractBasePhoto 상속)

PubBook (1:1 BookEdition) ─→ PubPage (1:1 Page) ─→ PubPanel (1:1 Panel)
                                                 └→ PubDocument (1:1 PubPage)
```

- 계층 관계와 FK 방향은 논리적으로 올바름
- `__init__.py`의 `__all__` 목록과 실제 정의 일치
- 마이그레이션(`0001_initial.py`)과 모델 정의 정합

---

## 2. 발견된 문제점

### 2.1 [높음] WallpaperLayoutEnum 불일치 — BANNER/CARD 크롭 실패

**위치:** `models/media.py:168-175`, `models/media.py:236-304`

`BookLayoutEnum`에는 PPTX 계열 4종 + A4_LANDSCAPE + CUSTOM이 추가되었으나, `WallpaperImage`의 레이아웃별 크롭은 원본 6종(`BOOK, MBOOK, CD, CARD, CINEMA, BANNER`)만 고려한다.

세부 문제:

| 레이아웃 | `BOOK_LAYOUT_HEIGHTS`에 높이 존재 | 이미지 필드 존재 | 결과 |
|----------|----------------------------------|-----------------|------|
| BOOK | O (1086) | 기본 image_view/thumb | 정상 |
| MBOOK | O (960) | mbook_image_view/thumb | 정상 |
| CD | O (768) | cd_image_view/thumb | 정상 |
| CARD | O (552) | **X** (card_image_view/thumb 없음) | **크롭 실패 (field가 None)** |
| CINEMA | O (432) | cinema_image_view/thumb | 정상 |
| BANNER | **X** (높이 매핑 없음) | banner_image_view/thumb 존재 | **크롭 실행 안 됨** |
| PPTX 계열 | X | X | 미지원 |

**권장 조치:**
- `BOOK_LAYOUT_HEIGHTS`에 `BANNER` 높이 추가
- `card_image_view`, `card_image_thumb` 필드 추가 (또는 CARD를 heights에서 제거)
- PPTX/A4/CUSTOM 레이아웃의 배경화면 크롭 전략 결정

---

### 2.2 [높음] Soft Delete 필터링 누락

**위치:** `models/book.py`, `models/page.py`, `models/panel.py`

`deleted` 필드를 가진 모델은 `Book`, `BookEdition`, `BookCollaborator`, `Page`, `Panel` 5개이다. `mark_as_deleted()` 패턴으로 soft delete를 수행하지만, **기본 매니저에서 `deleted=False` 필터링이 없다.**

```python
# 현재: 삭제된 데이터도 포함되어 반환
Book.objects.all()  # deleted=True인 레코드 포함

# 영향받는 메서드 예시
Book.get_latest_title()        # deleted 에디션도 조회
BookEdition.get_latest()       # deleted 에디션도 반환 가능
BookEdition.latest_version_number()  # deleted 에디션도 집계
```

**권장 조치:**
- 커스텀 매니저에 `deleted=False` 기본 필터 추가, 또는
- 각 QuerySet에서 `.filter(deleted=False)` 명시

---

### 2.3 [중간] `updated_at` 자동 갱신 안 됨

**위치:** 모든 모델의 `updated_at` 필드

```python
# 현재
updated_at = models.DateTimeField(default=timezone.now)

# touch() 메서드로 수동 갱신
def touch(self):
    self.updated_at = timezone.now()
    self.save(update_fields=["updated_at"])
```

일반 필드 변경 후 `save()` 호출 시 `updated_at`이 갱신되지 않는다. Serializer의 `update()` 에서도 `touch()`를 호출하지 않으므로, API를 통한 수정 시 `updated_at`이 변경 시점을 반영하지 못한다.

**권장 조치:**
- `auto_now=True` 사용, 또는
- `save()` 오버라이드에서 `updated_at` 자동 갱신, 또는
- Serializer/View에서 `touch()` 호출 보장

---

### 2.4 [중간] `Page.short_key`에 `unique=True` 누락

**위치:** `models/page.py:71-75`

```python
# Book — unique 있음
short_key = models.CharField(max_length=36, default=short_key, unique=True, editable=False)

# Page — unique 없음
short_key = models.CharField(max_length=36, default=short_key, editable=False)
```

`short_key()`는 `uuid4().hex[:8]`로 8자 생성 — 약 40억 가지. 데이터가 수만 건 이상이면 충돌 확률이 무시할 수 없다. `Page.__str__()`과 `PageMemo.__str__()`에서 식별자로 사용하고 있으므로 유니크 제약 추가를 권장한다.

---

### 2.5 [중간] `BookCollaborator` 중복 초대 방지 없음

**위치:** `models/book.py:253-297`

같은 user가 같은 book에 여러 번 초대될 수 있다. `unique_together`나 `UniqueConstraint` 미설정.

**권장 조치:**
```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["user", "book"],
            condition=models.Q(deleted=False),
            name="unique_active_collaborator",
        )
    ]
```

---

### 2.6 [중간] Pub 모델의 `OneToOneField`가 다중 발행 제한

**위치:** `models/publishing.py`

```python
# PubPage
page = models.OneToOneField("bookstudio.Page", related_name="pub_page", ...)

# PubPanel
panel = models.OneToOneField("bookstudio.Panel", related_name="pub_panel", ...)
```

한 Page/Panel은 하나의 PubPage/PubPanel에만 연결 가능하다. BookEdition을 여러 버전 발행하는 시나리오에서, 같은 원본 Page를 다른 PubBook 버전에 연결할 수 없다.

**권장 조치:**
- 다중 발행이 필요하면 `ForeignKey`로 변경
- 현재 1:1이 의도적이라면 문서화

---

### 2.7 [낮음] `__init__.py` Enum export 누락

**위치:** `models/__init__.py`

다음 Enum들이 정의되어 있지만 `__init__.py`에서 export하지 않는다:

| Enum | 정의 위치 |
|------|-----------|
| `LicenseEnum` | `book.py` |
| `PrivacyEnum` | `book.py` |
| `EditTypeEnum` | `page.py` |
| `ArrowEnum` | `page.py` |
| `UseWallpaperEnum` | `media.py` |
| `WallpaperLayoutEnum` | `media.py` |
| `ProgressStateEnum` | `publishing.py` |

외부에서 접근 시 직접 모듈 import가 필요하며 (`from bookstudio.models.book import PrivacyEnum`), `MediaBankTypeEnum`만 export되어 있어 일관성이 부족하다.

---

### 2.8 [낮음] Admin에서 일부 모델 미등록

**위치:** `admin.py`

다음 모델이 Django Admin에 등록되지 않았다:

- `PageMemoComment`
- `MediaGalleryMembership`
- `MediaGalleryMember`
- `PubDocument`

관리자 화면에서 해당 데이터를 직접 조회/수정할 수 없다.

---

### 2.9 [낮음] `conf.py`와 `media.py`의 `WALLPAPER_PAD_WIDTH` 중복 정의

**위치:** `conf.py:16`, `media.py:168`

```python
# conf.py — Django settings에서 오버라이드 가능
WALLPAPER_PAD_WIDTH = getattr(settings, "BOOKSTUDIO_WALLPAPER_PAD_WIDTH", 768)

# media.py — 하드코딩 (conf.py를 참조하지 않음)
WALLPAPER_PAD_WIDTH = 768
```

모델에서는 `media.py`의 값을 직접 사용하므로, `conf.py`의 설정 변경이 실제 크롭 로직에 반영되지 않는다.

**권장 조치:** `media.py`에서 `from bookstudio.conf import WALLPAPER_PAD_WIDTH` 사용

---

### 2.10 [낮음] `WallpaperImage._crop_and_save()` BOOK 레이아웃 처리

**위치:** `models/media.py:289-291`

```python
if layout_name == "BOOK":
    field_name = f"image_{suffix}" if suffix == "thumb" else "image_view"
```

BOOK 레이아웃에서 `image_preview`는 생성되지 않는다. `AbstractBasePhoto`에 `image_preview` 필드가 있으므로 의도적 생략인지 확인 필요.

---

## 3. 요약 테이블

| 심각도 | # | 항목 | 영향 |
|--------|---|------|------|
| 높음 | 2.1 | WallpaperLayout 불일치 | BANNER/CARD 크롭 실패 |
| 높음 | 2.2 | Soft delete 필터링 없음 | 삭제 데이터 노출 |
| 중간 | 2.3 | updated_at 자동 갱신 안 됨 | 수정 시점 추적 불가 |
| 중간 | 2.4 | Page.short_key unique 없음 | 키 충돌 가능 |
| 중간 | 2.5 | 협업자 중복 초대 방지 없음 | 데이터 정합성 |
| 중간 | 2.6 | Pub 모델 OneToOne 제약 | 다중 발행 불가 |
| 낮음 | 2.7 | Enum export 누락 | 일관성 부족 |
| 낮음 | 2.8 | Admin 미등록 모델 | 관리 불편 |
| 낮음 | 2.9 | WALLPAPER_PAD_WIDTH 중복 | 설정 반영 안 됨 |
| 낮음 | 2.10 | BOOK 크롭 시 preview 미생성 | 기능 누락 가능 |
