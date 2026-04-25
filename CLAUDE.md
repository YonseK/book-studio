# CLAUDE.md

## 프로젝트 개요

BookStudio는 **HTML 기반 프레젠테이션/문서 에디터 엔진**으로, 호스트 앱(AIONETRA 등)에 패키지로 임베드하여 사용한다. PPTX를 대체하는 독립 Django 앱(백엔드) + React 컴포넌트 라이브러리(프론트엔드)로 구성된다.

### 패키지 소비 방식

```python
# 호스트 앱 백엔드 (Django)
INSTALLED_APPS = ['bookstudio']
path('api/studio/', include('bookstudio.api.urls'))
```

```tsx
// 호스트 앱 프론트엔드 (React)
import { BookStudioEditor, restClient } from '@bookstudio/react'
const client = restClient({ baseURL: '/api/studio' })
<BookStudioEditor client={client} bookId={id} />
```

---

## 디렉토리 구조

```
BOOKSTUDIO/
├── backend/                  # Django 패키지 (pip install)
│   ├── bookstudio/
│   │   ├── models/           # Book → BookEdition → Page → Panel/Document
│   │   ├── services/         # 클론, 발행, 권한, 레이아웃, 렌더링, 내보내기
│   │   ├── api/
│   │   │   ├── views/        # DRF ViewSets (중첩 라우터)
│   │   │   └── serializers/  # 모델별 다중 시리얼라이저
│   │   ├── consumers.py      # WebSocket 실시간 협업
│   │   ├── conf.py           # 앱 설정
│   │   └── admin.py
│   └── tests/                # pytest + SQLite
├── frontend/                 # React 패키지 (@bookstudio/react)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Editor/       # BookStudioEditor, EditorCanvas, EditorLayout, SaveStatus
│   │   │   ├── Panel/        # PanelWrapper, TextPanel, ImagePanel, ShapePanel, VideoPanel, EmbedPanel
│   │   │   ├── Sidebar/      # SidebarTabs, WallpaperBank, EditorOptions, SharePanel 등
│   │   │   ├── Toolbar/      # ToolbarStrip
│   │   │   ├── PageList/     # PageListPanel
│   │   │   ├── Viewer/       # BookViewer (읽기 전용)
│   │   │   └── common/       # GridOverlay, ColorPalettePicker, AspectRatioSelector
│   │   ├── stores/           # Zustand (editorStore, historyStore)
│   │   ├── hooks/            # useAutoSave, useCollaboration
│   │   ├── services/         # SaveManager (디바운스 자동 저장)
│   │   ├── api/              # restClient (Fetch 기반 REST)
│   │   ├── types/            # Book, Page, Panel, Layout 타입
│   │   ├── styles/           # CSS (variables, editor, reset, fonts)
│   │   └── dev/              # DevApp (오프라인 UI), DevApiApp (백엔드 연동 테스트)
│   ├── index.ts              # 패키지 export
│   └── vite.config.ts        # 라이브러리 빌드 (build.lib)
└── docs/                     # 설계 문서 (인덱스: docs/README.md)
```

---

## 백엔드

### 도메인 모델 계층

```
Book (사용자별, soft delete)
 └─ BookEdition (버전, latest 플래그)
     └─ Page (순서, 배경색/배경 이미지, soft delete)
         ├─ Panel (60+ 스타일 필드, 미디어 타입별 분기)
         └─ Document (1:1, WYSIWYG 텍스트 콘텐츠)
```

발행 시 `PublishService.publish(edition)` → 불변 Pub* 복사본 생성 + 새 Edition 생성.

### API URL 구조 (`/api/studio/` 하위)

| 경로 | 설명 |
|------|------|
| `books/` | 북 CRUD, clone, publish |
| `books/{book_pk}/editions/` | 에디션 CRUD |
| `books/{book_pk}/editions/{edition_pk}/pages/` | 페이지 CRUD, sort |
| `pages/{page_pk}/panels/` | 패널 CRUD, sort |
| `pages/{page_pk}/documents/` | 문서 CRUD |
| `export/html/page/{id}/` | HTML 내보내기 |
| `import/html/` | HTML 가져오기 |

### 주요 패턴

- **Soft delete**: `deleted` 불리언 + `mark_as_deleted()`. 기본 매니저는 필터링 없음 — 조회 시 `.filter(deleted=False)` 명시 필요
- **Touch**: `touch()` 타임스탬프가 Document → Page → Edition으로 전파
- **Latest/Version**: `BookEdition.latest` 불리언으로 현재 버전 추적
- **WebSocket**: `BookStudioConsumer` — `book_{id}` 그룹, 메시지 타입: `page.*`, `panel.*`, `cursor.move`, `user.join/leave`

### 명령어

```bash
cd backend
source .venv/bin/activate
pip install -e ".[dev]"
pytest                                    # 테스트 (SQLite :memory:)

# 개발 서버 (파일 기반 SQLite, AutoLogin 미들웨어)
DJANGO_SETTINGS_MODULE=tests.settings python -m django migrate
DJANGO_SETTINGS_MODULE=tests.settings python -m django runserver
```

---

## 프론트엔드

### 핵심 진입점

`BookStudioEditor` — `client: BookStudioClient`와 `bookId: string`을 받아 에디터 전체를 렌더링.

### 상태 관리

- **editorStore** (Zustand + immer): book, edition, pages, panels, UI 상태
- **historyStore**: Undo/Redo (메모리, 최대 50개)
- **dirty change 이벤트**: `updatePanel`/`updatePage`/`updateEdition` 호출 시 `onDirtyChange` 구독자에게 알림
- **withRemoteUpdate()**: WebSocket 수신 변경 시 dirty 마킹 제외

### 자동 저장 (SaveManager + useAutoSave)

| 카테고리 | 디바운스 | 예시 |
|----------|---------|------|
| 구조 변경 | 0ms | 페이지/패널 추가/삭제 |
| 패널 스타일 | 1,000ms | 위치, 크기, 색상 |
| 텍스트 입력 | 2,000ms | 본문, 헤드라인 |
| 페이지 속성 | 1,000ms | 배경색, 투명도 |
| 에디션 메타 | 2,000ms | 제목, 설명 |

실패 시 지수 백오프 재시도 (최대 3회), 오프라인 복구, beforeunload 보호, 페이지 전환 시 flush.

### 개발 서버 (Vite)

```bash
cd frontend && npm install && npx vite
```

- `http://localhost:5174` — DevApp (오프라인, 가짜 데이터로 UI 확인)
- `http://localhost:5174/#api` — DevApiApp (백엔드 연동, 자동 저장 테스트)

DevApiApp 사용 시 백엔드가 :8000에서 구동 중이어야 함. Vite proxy가 `/api` → `localhost:8000`으로 전달.

### 빌드

```bash
cd frontend && npm run build    # dist/index.js (ES 모듈 라이브러리)
npx tsc --noEmit                # 타입 체크
```

---

## 커밋 컨벤션

- 한글로 작성
- `docs/`에 파일 생성 시 `docs/README.md` 인덱스에 추가

## 설계 문서

`docs/README.md` 참조. 대규모 구현 전 `docs/design/`에 설계 문서를 먼저 작성할 것.
