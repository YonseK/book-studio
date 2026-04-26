# 백엔드 모델 점검 보고서

> 점검일: 2026-04-25
> 수정 완료: 2026-04-25 (`15fea04`)
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
- 마이그레이션과 모델 정의 정합

---

## 2. 발견 및 조치 내역

### 2.1 [수정 완료] WallpaperLayoutEnum 불일치 — 비율 매핑 도입

**커밋:** `15fea04`

`BOOK_LAYOUT_HEIGHTS`에서 필드가 없는 CARD를 제거하고, `LAYOUT_WALLPAPER_MAP` 매핑 테이블을 추가하여 모든 `BookLayoutEnum` 값이 가장 가까운 크롭 비율에 대응되도록 했다.

```python
LAYOUT_WALLPAPER_MAP = {
    "PPTX_WIDE": "CINEMA",  # 16:9
    "PPTX_WP": "BOOK",      # 9:16 → 세로형
    "BOOK": "BOOK",
    "A4_LAND": "CINEMA",    # 가로형
    "CD": "CD",             # 1:1
    "BANNER": None,         # 가변 높이 → 크롭 안 함
    "CUSTOM": None,         # 크롭 안 함
    ...
}
```

`get_layout_image_url()`이 매핑을 통해 적절한 크롭 이미지를 반환한다.

---

### 2.2 [수정 완료] Soft Delete 필터링 추가

**커밋:** `15fea04`

`deleted` 필드를 가진 모델: `Book`, `BookEdition`, `BookCollaborator`, `Page`, `Panel`.

다음 메서드에 `deleted=False` 필터를 추가했다:
- `Book.get_latest_edition()`
- `Book.get_latest_title()`
- `BookEditionManager.get_latest()`
- `BookEdition.latest_version_number()`

---

### 2.3 [수정 완료] `updated_at` → `auto_now=True`

**커밋:** `15fea04`

10개 모델의 `updated_at` 필드를 `default=timezone.now` → `auto_now=True`로 변경. 매 `save()` 시 자동 갱신된다.

대상: Book, BookEdition, Page, Document, PageMemo, PageMemoComment, Panel, PubBook, MediaGalleryMembership, MediaGalleryMember.

---

### 2.4 [수정 완료] `Page.short_key`에 `unique=True` 추가

**커밋:** `15fea04`

---

### 2.5 [수정 완료] `BookCollaborator` 유니크 제약 추가

**커밋:** `15fea04`

```python
constraints = [
    models.UniqueConstraint(
        fields=["user", "book"],
        condition=models.Q(deleted=False),
        name="unique_active_collaborator",
    )
]
```

---

### 2.6 [현행 유지] Pub 모델 OneToOneField

발행 워크플로우에서 Edition 발행 시 원본 Page는 고정되고, 새 Edition에는 클론된 별도 Page가 생성되므로 OneToOne이 올바르다.

재발행 방어 로직을 `PublishService.publish()`에 추가했다 — 이미 발행된 Edition을 다시 발행하면 `ValueError`를 발생시킨다.

---

### 2.7 [수정 완료] Enum export 보완

**커밋:** `15fea04`

`__init__.py`에 7개 Enum 추가: `LicenseEnum`, `PrivacyEnum`, `EditTypeEnum`, `ArrowEnum`, `UseWallpaperEnum`, `WallpaperLayoutEnum`, `ProgressStateEnum`.

---

### 2.8 [수정 완료] Admin 미등록 모델 등록

**커밋:** `15fea04`

4개 모델 등록: `PageMemoComment`, `MediaGalleryMembership`, `MediaGalleryMember`, `PubDocument`.

---

### 2.9 [수정 완료] `WALLPAPER_PAD_WIDTH` 중복 제거

**커밋:** `15fea04`

`media.py`에서 `from bookstudio.conf import WALLPAPER_PAD_WIDTH`로 변경.

---

### 2.10 [변경 없음] BOOK 크롭 시 `image_preview` 미생성

`crop_layout()`은 레이아웃별 view/thumb 2종만 생성하는 것이 원래 설계 의도. `image_preview`는 `AbstractBasePhoto.save_and_resize()`에서 일반 Photo용으로만 사용된다.

---

## 3. 요약 테이블

| # | 항목 | 상태 |
|---|------|------|
| 2.1 | WallpaperLayout 비율 매핑 | 수정 완료 |
| 2.2 | Soft delete 필터링 | 수정 완료 |
| 2.3 | updated_at auto_now | 수정 완료 |
| 2.4 | Page.short_key unique | 수정 완료 |
| 2.5 | 협업자 유니크 제약 | 수정 완료 |
| 2.6 | Pub 모델 OneToOne | 현행 유지 + 재발행 방어 추가 |
| 2.7 | Enum export | 수정 완료 |
| 2.8 | Admin 등록 | 수정 완료 |
| 2.9 | WALLPAPER_PAD_WIDTH | 수정 완료 |
| 2.10 | BOOK 크롭 preview | 변경 없음 (의도적 설계) |
