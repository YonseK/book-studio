# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# 가상환경 활성화 후 설치 (from backend/)
source .venv/bin/activate
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_models.py

# Run a specific test
pytest tests/test_models.py::TestBookModel::test_create_book -v

# 개발 서버 실행 (테스트용 settings 사용, DB는 SQLite :memory:이므로 매 실행마다 초기화됨)
DJANGO_SETTINGS_MODULE=tests.settings python -m django migrate && DJANGO_SETTINGS_MODULE=tests.settings python -m django runserver

# Django management (tests use tests.settings)
DJANGO_SETTINGS_MODULE=tests.settings python -m django <command>
```

## Architecture

Django + DRF backend for a collaborative HTML-based presentation/document editor. The entire app lives in the `bookstudio` package.

### Layer Structure

```
bookstudio/
  models/           # Domain entities
    book.py         # Book → BookEdition → BookCollaborator
    page.py         # Page, Document, PageMemo
    panel.py        # Panel (60+ 스타일 필드)
    design_pattern.py  # DesignPattern, DesignPatternSlot, DesignPatternSet (AI Phase 1)
    ai.py           # AISession (AI Phase 2)
    media.py        # Photo, WallpaperImage
    publishing.py   # PubBook/PubPage/PubPanel/PubDocument
  services/
    cloning.py, publishing.py, permissions.py, layout.py, page_renderer.py
    html_export.py, html_import.py, pdf_export.py
    pattern_applicator.py  # DesignPattern → Page+Panel 변환 (AI Phase 1)
    ai/                    # AI 파이프라인 (AI Phase 2)
      planner.py           # 기획서 생성
      writer.py            # 콘텐츠 작성
      designer.py          # 디자인 패턴 선택
      orchestrator.py      # 전체 파이프라인 조율
      runner.py            # Celery/동기 분기
      prompts/             # LLM 프롬프트 템플릿
  adapters/                # LLM 어댑터 (AI Phase 2)
    base.py                # BaseLLMAdapter (추상), LLMResponse
    factory.py             # get_llm_adapter() — 호스트 앱 settings에서 어댑터 로드
  api/
    views/          # DRF ViewSets (nested routers: book > edition > page > panel)
      ai.py         # DesignPattern/Set CRUD + AISession CRUD + approve/cancel
      ai_stream.py  # SSE 스트리밍 엔드포인트
    serializers/    # Multiple serializers per model
  tasks.py          # Celery 태스크 (run_ai_planning, run_ai_generation)
  consumers.py      # Django Channels WebSocket consumer
  conf.py           # App-specific settings (+ AI_LLM_ADAPTER, AI_USE_CELERY 등)
  admin.py          # Django Admin registration
  management/commands/
    extract_design_patterns.py  # 레거시 북에서 디자인 패턴 추출
  fixtures/
    curated_patterns.json       # 큐레이션 패턴 15개 + 1세트
```

### Key Domain Concepts

- **Book → BookEdition → Page → Panel**: Core hierarchy. BookEdition enables versioned snapshots; Panels are individual design elements on a Page with 60+ styling fields.
- **Document**: OneToOne with Page for WYSIWYG/Markdown text content.
- **Publishing workflow**: `PublishService.publish(edition)` creates immutable Pub* copies (PubBook/PubPage/PubPanel/PubDocument) and a new edition for continued editing.
- **CloneService**: Transaction-wrapped deep copy at panel/page/book level. Used by both user cloning and the publish workflow.
- **Soft deletes**: Models use `deleted` boolean + `mark_as_deleted()` instead of hard deletes.
- **Touch pattern**: `touch()` cascades timestamps upward (Document → Page → BookEdition).
- **Latest/version pattern**: `BookEdition.latest` and `PubBook.latest` booleans track current versions via `set_as_latest()`.

### AI System

- **DesignPattern → DesignPatternSlot**: 페이지 레이아웃 템플릿. 상대 좌표(%) + 스타일 JSON. `PatternApplicator`가 Page+Panel로 변환.
- **DesignPatternSet**: 여러 패턴을 하나의 테마로 묶음. Membership through 테이블로 우선순위 관리.
- **AISession**: AI 생성 세션. 상태: `PLANNING→REVIEW→APPROVED→GENERATING→COMPLETE`. 기획서(plan JSON) + 진행률 + 토큰 사용량 추적.
- **LLM Adapter**: `BaseLLMAdapter` 추상 인터페이스. 호스트 앱이 `BOOKSTUDIO_AI_LLM_ADAPTER` settings로 구현체 주입.
- **AI Pipeline**: `PlannerService` → `DesignerService` → `WriterService` → `PatternApplicator`. `OrchestratorService`가 조율.
- **Celery/동기 분기**: `BOOKSTUDIO_AI_USE_CELERY=True`면 Celery 태스크, `False`면 동기 실행. `runner.py`가 분기.

### API URL Structure

Nested routing under `/api/studio/`:
- `books/{book_pk}/editions/{edition_pk}/pages/` — page CRUD
- `pages/{page_pk}/panels/` — panel CRUD
- `pages/{page_pk}/documents/` — document CRUD
- `pages/{page_pk}/memos/` — memo CRUD
- `export/html/...`, `export/pdf/...` — export endpoints
- `import/html/` — HTML import
- `ai/design-patterns/` — DesignPattern CRUD + `{id}/slots/` nested
- `ai/design-pattern-sets/` — DesignPatternSet CRUD
- `ai/sessions/` — AISession CRUD + `{id}/approve/`, `{id}/cancel/`
- `ai/sessions/{id}/stream/` — SSE 스트리밍

### WebSocket (consumers.py)

`BookStudioConsumer` groups by `book_{book_id}`. Message types: `page.*`, `panel.*`, `cursor.move`, `user.join/leave`. Broadcasts to all except sender.

### Media Handling

- **Photo**: Stores original + view/preview/thumb resized versions via `save_and_resize()`.
- **WallpaperImage**: Layout-specific crops (BOOK/MBOOK/CD/CINEMA/BANNER) via `crop_layout()`.
- **MediaBank**: Per-book asset library. **MediaGallery**: Shared asset collections.

## Test Configuration

- pytest with `pytest-django` — settings in `tests/settings.py` (SQLite in-memory)
- `DJANGO_SETTINGS_MODULE = tests.settings` configured in `pytest.ini`
