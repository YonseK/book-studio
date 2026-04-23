# BookStudio 프론트엔드 UI 설계 명세서

> 원본: `plus.bookooroo.store/editor/R7fkdE2z3A1`
> 대상: `/Users/yonsekim/Developer/Projects/BOOKSTUDIO/frontend/`
> 작성일: 2026-04-16
> 상태: 설계 완료, 구현 대기

---

## 1. 전체 레이아웃 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                    상단 바 (PositionBar)                              │
│  패널 선택 시: TOP:392px LEFT:219px WIDTH:361px HEIGHT:88px ROTATE:0° │
│  비선택 시: 우측에 검색 박스만 표시                                      │
├──────┬──────────┬──────┬──────────────────┬──────┬──────────────────┤
│ 앱   │ 좌측 패널  │ 툴바  │                  │ 미니 │ 페이지 목록       │
│ 네비 │          │      │                  │ 아이 │                  │
│      │ 제목 입력  │ 컬러  │                  │ 콘   │ [+ 새 페이지]    │
│ 메모 │          │ 스워치│                  │ 바   │                  │
│      │ 4탭      │      │     캔버스        │      │ ┌──────────┐   │
│ 페이 │ ────     │ T    │                  │ 복사 │ │ 썸네일 1  │   │
│ 지   │          │ T    │                  │      │ │ 1        │   │
│ 편집 │ 탭 콘텐츠 │ 이미지│                  │ 잘라 │ ├──────────┤   │
│      │ (월페이퍼 │ 도형  │                  │ 내기 │ │ 썸네일 2  │   │
│ ──── │  뱅크    │ 임베드│                  │      │ │ 2        │   │
│      │  등)     │ 파일  │                  │      │ ├──────────┤   │
│ 책장 │          │ 비디오│                  │      │ │ ...      │   │
│ 설정 │          │ 노트  │                  │      │ └──────────┘   │
│      │          │      │                  │      │                  │
│ 40px │  260px   │ 40px │    flex-grow     │ 40px │    200px         │
└──────┴──────────┴──────┴──────────────────┴──────┴──────────────────┘
```

**전체 크기**: 뷰포트 100vw x 100vh, 스크롤 없음 (overflow: hidden)
**배경색**: #1e1e1e (다크 테마 기본)

---

## 2. 컬러 시스템

### 2.1 다크 테마 (기본값)

| 변수명 | 값 | 용도 |
|--------|------|------|
| `--bs-bg-primary` | `#1e1e1e` | 앱 네비, 사이드바 배경 |
| `--bs-bg-secondary` | `#2a2a2a` | 좌측 패널 배경 |
| `--bs-bg-tertiary` | `#333333` | 입력 필드, 호버 배경 |
| `--bs-bg-canvas` | `#3a3a3a` | 캔버스 영역 배경 |
| `--bs-bg-hover` | `#3a3a3a` | 버튼 호버 |
| `--bs-text-primary` | `#e0e0e0` | 주요 텍스트 |
| `--bs-text-secondary` | `#999999` | 보조 텍스트, 라벨 |
| `--bs-text-muted` | `#666666` | 비활성 텍스트 |
| `--bs-accent` | `#7cc576` | 선택 핸들, 활성 상태 (초록) |
| `--bs-accent-yellow` | `#e8c840` | 강조, 태그 (노란) |
| `--bs-border` | `#444444` | 기본 보더 |
| `--bs-border-light` | `#555555` | 밝은 보더 |
| `--bs-danger` | `#e85050` | 삭제 버튼 |

### 2.2 라이트 테마

| 변수명 | 값 |
|--------|------|
| `--bs-bg-primary` | `#ffffff` |
| `--bs-bg-secondary` | `#f5f5f5` |
| `--bs-bg-tertiary` | `#eeeeee` |
| `--bs-bg-canvas` | `#e0e0e0` |
| `--bs-text-primary` | `#333333` |
| `--bs-text-secondary` | `#666666` |
| `--bs-border` | `#dddddd` |

---

## 3. 상단 바 (PositionBar)

### 3.1 구조
- 높이: 40px
- 배경: `--bs-bg-primary`
- 전체 너비

### 3.2 패널 비선택 시
- 좌측: 비어있음 (or 로고)
- 우측: 검색 입력 박스 (둥근 모서리, 다크 배경)

### 3.3 패널 선택 시
- 중앙에 위치/크기 정보 표시
- 형식: `TOP: {top}px  LEFT: {left}px  WIDTH: {width}px  HEIGHT: {height}px  ROTATE: {rotate}°`
- 폰트: 12px, 모노스페이스 느낌, `--bs-text-secondary`
- 각 라벨(TOP, LEFT 등)은 밝은 색, 값은 약간 더 밝은 색

---

## 4. 좌측 앱 네비게이션 (AppNav)

### 4.1 구조
- 너비: 40px
- 높이: 100% (상단 바 제외)
- 배경: `--bs-bg-primary`
- 우측 보더: `--bs-border` 1px
- 아이콘들 세로 정렬, 중앙 배치

### 4.2 아이콘 목록

| 순서 | 아이콘 | Lucide 아이콘명 | 기능 | 동작 |
|------|--------|----------------|------|------|
| 1 | 에디터 | `BookOpen` | 에디터 모드 (현재 활성) | 항상 활성 표시 |
| 2 | 메모 | `StickyNote` | 페이지 메모/주석 | 클릭 → 모달 오버레이 |
| 3 | 페이지 편집 | `LayoutGrid` | 페이지 이동/삭제/정렬 | 클릭 → 모달 오버레이 |
| — | separator | — | 구분선 | 1px 수평선, `--bs-border` |
| 4 | 새 책 | `FilePlus` | 새 책 만들기 | 콜백 or 라우팅 |
| 5 | 책장 | `Library` | 책 목록/관리 | 콜백 or 라우팅 |
| 6 | 설정 | `Settings` | 에디터 설정 | 클릭 → 설정 패널 |

### 4.3 아이콘 스타일
- 크기: 20px x 20px
- 색상: `--bs-text-secondary` (기본), `--bs-accent` (활성)
- 호버: `--bs-bg-hover` 배경, 라운드 4px
- 패딩: 상하 8px
- 활성 아이콘: 좌측에 `--bs-accent` 2px 세로선 표시

### 4.4 활성 상태 표시
- 현재 활성 메뉴: 좌측에 초록색 세로 바 (2px width, 24px height)
- 아이콘 색상: `--bs-accent`로 변경

---

## 5. 좌측 패널 (Sidebar)

### 5.1 구조
- 너비: 260px
- 배경: `--bs-bg-secondary`
- 우측 보더: `--bs-border` 1px

### 5.2 상단 제목 영역
- 높이: ~40px
- 패딩: 0 12px
- 텍스트 입력 (contentEditable or input)
- 기본값: "제목 없음" (placeholder)
- 현재 값: edition.title
- 폰트: 13px, `--bs-text-primary`
- 배경: transparent, 호버 시 `--bs-bg-tertiary`
- 보더: 없음, 포커스 시 하단 1px `--bs-accent`

### 5.3 탭 바
- 높이: 36px
- 4개 탭: 파일 | 입력 | 옵션 | 공유
- 각 탭: 아이콘 + 텍스트 (아이콘은 Lucide)
- 레이아웃: 균등 분할 (flex, justify: space-around)
- 비활성: `--bs-text-secondary`, 배경 없음
- 활성: `--bs-text-primary`, 하단 2px `--bs-accent` 보더
- 호버: `--bs-bg-hover`

**탭 아이콘 매핑:**

| 탭 | Lucide 아이콘 | 텍스트 |
|----|--------------|--------|
| 파일 | `File` | 파일 |
| 입력 | `PenLine` | 입력 |
| 옵션 | `Settings2` | 옵션 |
| 공유 | `Share2` | 공유 |

### 5.4 탭 콘텐츠 — 파일

드롭다운 메뉴 스타일 (클릭 시 나타남):

| 메뉴 항목 | 아이콘 | 동작 |
|----------|--------|------|
| 새 책 만들기 | `FilePlus` | onNewBook 콜백 |
| 작업중인 책 보관함 | `FolderOpen` | onOpenLibrary 콜백 |
| 공유된 책 보관함 | `FolderHeart` | onOpenShared 콜백 |
| — | separator | — |
| 게시된 책 버전 업데이트 | `Upload` | onPublish 콜백 |
| 복제 | `Copy` | onClone 콜백 |
| — | separator | — |
| 삭제 | `Trash2` | onDelete 콜백 (빨간색) |

- 배경: `--bs-bg-tertiary`
- 보더: `--bs-border` 1px
- border-radius: 6px
- box-shadow: `0 4px 16px rgba(0,0,0,0.3)`
- 각 항목: 높이 36px, 호버 시 `--bs-bg-hover`
- 삭제: color `--bs-danger`

### 5.5 탭 콘텐츠 — 입력

책 정보 입력 폼:

| 필드 | 타입 | 설명 |
|------|------|------|
| 제목 | text input | edition.title |
| 설명 | textarea | edition.description |
| 레이아웃 | select | LayoutPreset 선택 (AspectRatioSelector) |
| 프라이버시 | select | PRIVATE/PUBLIC/FRIENDS |

- 입력 스타일: 다크 배경 (`--bs-bg-tertiary`), 밝은 텍스트, 보더 없음
- 라벨: 12px, `--bs-text-secondary`, 마진 바텀 4px

### 5.6 탭 콘텐츠 — 옵션

원본 UI와 동일한 구조:

```
┌─────────────────────────────┐
│ ⚙ 옵션                   ✕ │
├─────────────────────────────┤
│                             │
│ 그리드 보이기/감추기           │
│ [● ○] (토글 스위치)          │
│                             │
│ 그리드 색상 선택              │
│ [▦] [▦] [▦] [▦] (4종 밀도)  │
│                             │
│ 그리드에 자석                │
│ [○ ●] (토글 스위치)          │
│                             │
│ ──────────────────────      │
│                             │
│ 가이드 라인 보이기/감추기      │
│ [● ○] ON (초록 토글)        │
│                             │
│ ──────────────────────      │
│                             │
│ 컬러 테마                   │
│ [라이트 ✓] [다크]            │
│                             │
└─────────────────────────────┘
```

**토글 스위치 스타일:**
- 너비: 36px, 높이: 20px
- 트랙: 둥근 모서리 (10px radius)
- OFF: `--bs-bg-tertiary` 트랙, `#999` 원형 thumb
- ON: `--bs-accent` 트랙, `#fff` 원형 thumb
- thumb 크기: 16px, 좌우 이동 애니메이션

**그리드 밀도 아이콘:**
- 4개 정사각형 버튼 (28x28px)
- 각각 다른 그리드 밀도를 표시하는 SVG 패턴
- 선택된 항목: `--bs-accent` 보더
- gridSize 매핑: 10, 20, 40, 80

**테마 선택:**
- 2개 썸네일 카드 (80x60px)
- 라이트: 밝은 배경 미리보기
- 다크: 어두운 배경 미리보기
- 선택된 항목: 체크마크 오버레이 + `--bs-accent` 보더

### 5.7 탭 콘텐츠 — 공유

게시/출판 관련:

| 항목 | 동작 |
|------|------|
| 게시된 책 버전 업데이트 | 출판 API 호출 |

- 현재는 간단한 버튼 1개
- 향후: 공유 링크 복사, QR 코드, 임베드 코드 등

### 5.8 월페이퍼 뱅크

탭 콘텐츠 아래에 항상 표시 (기본 탭이 "파일"일 때 메인 콘텐츠):

```
┌─────────────────────────────┐
│ 📁 월페이퍼 뱅크          🗑 │
├─────────────────────────────┤
│ ┌────┐ ┌────┐ ┌────┐      │
│ │    │ │    │ │    │      │
│ │ 흰색│ │ 베이│ │ 크림│      │
│ └────┘ └────┘ └────┘      │
│ ┌────┐ ┌────┐ ┌────┐      │
│ │노트 │ │벽돌 │ │나무 │      │
│ │패턴 │ │패턴 │ │결   │      │
│ └────┘ └────┘ └────┘      │
│ ┌────┐ ┌────┐ ┌────┐      │
│ │대리 │ │풍경 │ │도시 │      │
│ │석   │ │    │ │    │      │
│ └────┘ └────┘ └────┘      │
│         ...                │
└─────────────────────────────┘
```

- 헤더: "월페이퍼 뱅크" + 삭제 아이콘
- 그리드: 3열, gap 4px
- 각 썸네일: 정사각형 (aspect-ratio: 1), border-radius 2px
- 선택된 항목: `--bs-accent` 체크마크 오버레이
- 클릭: 현재 페이지 배경으로 적용
- 스크롤: 세로 스크롤 (overflow-y: auto, 커스텀 스크롤바)

---

## 6. 중앙 툴바 (ToolbarStrip)

### 6.1 구조
- 너비: 40px
- 배경: `--bs-bg-primary`
- 좌측 보더: `--bs-border` 1px
- 우측 보더: `--bs-border` 1px
- 아이콘 세로 정렬, 중앙 배치
- 상단 패딩: 8px

### 6.2 도구 목록

| 순서 | 아이콘 | 설명 | MediaType | 특이사항 |
|------|--------|------|-----------|---------|
| 1 | 컬러 스워치 | 배경색 선택 | — | 2개 겹친 정사각형 (현재색/보조색), 클릭 → 컬러피커 |
| 2 | 흰색 스워치 | 배경 흰색 | — | 흰색 정사각형 (보더 있음) |
| — | gap (16px) | — | — | — |
| 3 | 월페이퍼 업로드 | 배경 이미지 업로드 | — | `ImageUp` 아이콘 |
| 4 | **T** (굵은) | 헤드라인 텍스트 | `HL` | 굵은 세리프 T, 크게 (20px) |
| 5 | T (얇은) | 본문 텍스트 | `TXT` | 얇은 T, 작게 (16px) |
| 6 | 이미지 | 이미지 패널 | `IMG` | `Image` 아이콘 |
| 7 | 도형 | SVG 도형 | `SHA` | `Pentagon` 아이콘 |
| 8 | 웹 임베드 | URL 임베드 | `EV` | `Code` 아이콘 |
| 9 | 링크/파일 | 파일 업로드 | `FILE` | `Paperclip` 아이콘 |
| 10 | 비디오 | 비디오/오디오 | `VOD` | `Play` 아이콘 |
| 11 | 노트 | 페이지 내 노트 | `DOC` | `FileText` 아이콘 |

### 6.3 아이콘 스타일
- 버튼 크기: 32x32px
- 아이콘 크기: 18px
- 색상: `--bs-text-secondary`
- 호버: `--bs-bg-hover` 배경, border-radius 4px
- 활성 (도구 선택 중): `--bs-accent` 색상
- T 아이콘: Lucide 대신 직접 텍스트 렌더링 (font-weight로 구분)

### 6.4 배경색 스워치
- 크기: 24x24px (2개 겹침: 뒤 20x20 + 앞 20x20, 오프셋 4px)
- 뒤 스워치: 현재 페이지 배경색
- 앞 스워치: 보조색 (흰색 or 검정)
- 보더: 1px `--bs-border`
- 클릭 → 컬러 피커 팝업 (향후)

---

## 7. 캔버스 (EditorCanvas)

### 7.1 캔버스 영역
- 배경: `--bs-bg-canvas`
- 중앙 정렬: flexbox center center
- 패딩: 40px
- overflow: auto (캔버스가 크면 스크롤)

### 7.2 페이지 렌더링
- 페이지 크기: layoutConfig.width x layoutConfig.height (px)
- 배경: page.background_color or 월페이퍼 이미지
- box-shadow: `0 2px 20px rgba(0,0,0,0.3)` (떠있는 효과)
- transform: `scale(${zoom})`, transformOrigin: center center
- overflow: hidden (패널이 페이지 밖으로 나가면 잘림)

### 7.3 줌 컨트롤
- Ctrl+Wheel: 줌 인/아웃 (0.1 ~ 5.0)
- 현재 줌 레벨: PositionBar 우측에 표시 (e.g. "100%")
- 별도 줌 버튼 UI 없음 (키보드/마우스 전용)

### 7.4 Undo/Redo
- Ctrl+Z: Undo, Ctrl+Shift+Z: Redo
- 원본에서 별도 UI 버튼 없음 (키보드 전용)
- 기존 EditorHeader의 Undo/Redo 버튼은 제거, 키보드 단축키만 유지

---

## 8. 패널 선택 UI

### 8.1 비선택 상태
- 보더: 없음 (투명 1px)
- 호버: 연한 점선 보더 (`--bs-border`, dashed)

### 8.2 선택 상태 — 핸들

```
    [M-T]
[TL]───────────[TR]
 │               │
[M-L]           [M-R]
 │               │
[BL]───────────[BR]
    [M-B]
```

- **코너 핸들 (TL, TR, BL, BR)**: 정사각형 8x8px
  - 배경: `#ffffff`
  - 보더: 2px solid `--bs-accent` (#7cc576)
  - 커서: nw-resize, ne-resize, sw-resize, se-resize
- **중간 핸들 (M-T, M-B, M-L, M-R)**: 직사각형
  - 가로 (M-T, M-B): 12x6px
  - 세로 (M-L, M-R): 6x12px
  - 배경: `#ffffff`
  - 보더: 2px solid `--bs-accent`
  - 커서: n-resize, s-resize, w-resize, e-resize
- **선택 보더**: 1px dashed `--bs-accent`
- **핸들 위치**: 보더 바깥쪽으로 offset (-4px)

### 8.3 드래그 중
- 커서: `move`
- 가이드라인 표시 (showGuides 활성 시):
  - 페이지 중앙 정렬: 빨간 점선
  - 다른 패널 정렬: 파란 점선

### 8.4 리사이즈 중
- 핸들 방향에 따라 크기 변경
- 최소 크기: 20x20px
- Shift 누르면 비율 유지

---

## 9. 우측 미니 아이콘 바

### 9.1 구조
- 너비: 40px
- 배경: `--bs-bg-primary`
- 좌측 보더: `--bs-border` 1px

### 9.2 아이콘 목록

| 아이콘 | Lucide | 기능 |
|--------|--------|------|
| 복사 | `Copy` | 현재 페이지 복사 |
| 가위 | `Scissors` | 현재 페이지 잘라내기 |
| 붙여넣기 | `ClipboardPaste` | 페이지 붙여넣기 |

- 아이콘 크기: 16px
- 색상: `--bs-text-muted`
- 호버: `--bs-text-secondary`

---

## 10. 우측 페이지 목록 (PageList)

### 10.1 구조
- 너비: 200px
- 배경: `--bs-bg-primary`
- 좌측 보더: `--bs-border` 1px

### 10.2 상단 영역

```
┌────────────────────────────┐
│  [접기 ◀]  [새 페이지 추가 +] │
└────────────────────────────┘
```

- 접기 버튼: `ChevronLeft` 아이콘, 클릭 → 페이지 목록 숨김 (너비 0)
- 새 페이지 추가: `Plus` 아이콘 + "새 페이지 추가" 텍스트
- 높이: 40px
- 배경: `--bs-bg-secondary`

### 10.3 페이지 썸네일

```
┌─────────────────────────┐
│ ...   ← 컨텍스트 메뉴    │
│                         │
│     (페이지 미리보기)     │
│                         │
│ 1    ← 페이지 번호       │
│                    👤   │ ← 협업자 아바타
└─────────────────────────┘
```

- 비율: layoutConfig 비율에 맞춤 (BOOK이면 세로, PPTX_WIDE면 가로)
- 배경: page.background_color
- 번호: 좌측 중앙, `--bs-accent` 색상, 14px bold
- "..." 버튼: 우상단, `MoreHorizontal` 아이콘, 호버 시만 표시
- 활성 페이지: 좌측에 `--bs-accent` 3px 세로 보더 + 체크 아이콘
- 비활성: 보더 없음
- 간격: 8px
- 마진: 좌우 8px

### 10.4 페이지 컨텍스트 메뉴 ("...")

클릭 시 드롭다운:

| 항목 | 아이콘 | 동작 |
|------|--------|------|
| 복제 | `Copy` | 페이지 딥클론 |
| 삭제 | `Trash2` | 페이지 삭제 (빨간색) |
| 위로 이동 | `ChevronUp` | 순서 변경 |
| 아래로 이동 | `ChevronDown` | 순서 변경 |

- 스타일: 파일 메뉴와 동일 (다크 드롭다운)

### 10.5 접기/펼치기
- 접힌 상태: 페이지 목록 너비 0, 화살표 `ChevronRight`로 변경
- 펼친 상태: 기본 200px
- 애니메이션: transition width 0.2s ease

---

## 11. 컴포넌트 트리

```
BookStudioEditor (or DevApp)
├── EditorLayout
│   ├── PositionBar           ← 상단 바 (위치 정보 or 검색)
│   ├── AppNav                ← 좌측 앱 네비게이션
│   ├── Sidebar               ← 좌측 패널
│   │   ├── SidebarHeader     ← 제목 입력
│   │   ├── SidebarTabs       ← 파일/입력/옵션/공유 탭 바
│   │   ├── TabContent        ← 탭별 콘텐츠
│   │   │   ├── FileMenu
│   │   │   ├── BookInfoPanel
│   │   │   ├── EditorOptions
│   │   │   └── SharePanel
│   │   └── WallpaperBank     ← 월페이퍼 뱅크 (하단)
│   ├── ToolbarStrip           ← 중앙 도구 모음
│   │   ├── WallpaperColorPicker
│   │   └── ToolButtons
│   ├── EditorCanvas           ← 캔버스
│   │   ├── GridOverlay
│   │   └── PanelWrapper[]
│   │       ├── SelectionHandles
│   │       ├── TextPanel
│   │       ├── ImagePanel
│   │       ├── ShapePanel
│   │       ├── VideoPanel
│   │       └── EmbedPanel
│   ├── MiniIconBar            ← 우측 미니 아이콘 바
│   └── PageListPanel          ← 우측 페이지 목록
│       ├── PageListHeader
│       └── PageThumbnail[]
│           └── PageContextMenu
```

---

## 12. 상태 관리 확장

### editorStore 추가 필드

```typescript
interface EditorState {
  // 기존 필드 유지...

  // 추가
  activeSidebarTab: 'file' | 'input' | 'options' | 'share'
  setActiveSidebarTab: (tab: string) => void

  isPageListCollapsed: boolean
  togglePageList: () => void

  clipboard: { type: 'page' | 'panel', data: any } | null
  copyToClipboard: (type: string, data: any) => void
  pasteFromClipboard: () => void
}
```

---

## 13. CSS 아키텍처

### 13.1 파일 구조

```
frontend/src/styles/
├── variables.css     ← CSS 커스텀 속성 (다크/라이트 테마)
├── reset.css         ← 기본 리셋 (margin, padding, box-sizing)
└── editor.css        ← 에디터 전체 레이아웃

frontend/src/components/
├── AppNav/AppNav.css
├── Sidebar/SidebarTabs.css
├── Sidebar/WallpaperBank.css
├── Toolbar/ToolbarStrip.css
├── Panel/PanelWrapper.css
├── PageList/PageListPanel.css
└── Editor/PositionBar.css
```

### 13.2 네이밍 컨벤션
- BEM 기반 + `bs-` 접두사
- 예: `bs-appnav`, `bs-appnav__icon`, `bs-appnav__icon--active`
- 테마: `.bs-theme-dark`, `.bs-theme-light` 클래스로 CSS 변수 전환

### 13.3 CSS 변수 전환 방식

```css
.bs-theme-dark {
  --bs-bg-primary: #1e1e1e;
  /* ... */
}

.bs-theme-light {
  --bs-bg-primary: #ffffff;
  /* ... */
}

/* 컴포넌트에서 변수 사용 */
.bs-appnav {
  background-color: var(--bs-bg-primary);
}
```

---

## 14. 아이콘 라이브러리

**선택: `lucide-react`**

- MIT 라이선스
- 트리쉐이킹 지원 (필요한 아이콘만 번들)
- 원본 에디터의 라인 아이콘 스타일과 유사
- React 네이티브 컴포넌트

```typescript
import { BookOpen, StickyNote, Settings, Image, Play } from 'lucide-react'

// 사용
<BookOpen size={20} strokeWidth={1.5} />
```

---

## 15. 구현 순서 (6단계)

| Step | 내용 | 핵심 파일 |
|------|------|----------|
| **1** | CSS 기반 + 다크 테마 + 레이아웃 셸 | variables.css, editor.css, EditorLayout.tsx |
| **2** | AppNav + SidebarTabs | AppNav.tsx, SidebarTabs.tsx, FileMenu.tsx |
| **3** | 툴바 + 월페이퍼 뱅크 | ToolbarStrip.tsx, WallpaperBank.tsx |
| **4** | 패널 선택 핸들 + PositionBar | SelectionHandles.tsx, PositionBar.tsx |
| **5** | 페이지 목록 리디자인 | PageListPanel.tsx, PageThumbnail.tsx |
| **6** | 패널 편집 UX | TextToolbar.tsx, PanelContextMenu.tsx |

각 Step 완료 후 `npm run dev`로 시각적 검증.

---

## 16. 검증 체크리스트

### Step 1 완료 시
- [ ] 다크 테마 적용됨
- [ ] 레이아웃 6열 구조 (AppNav|Sidebar|Toolbar|Canvas|MiniIcons|PageList)
- [ ] CSS 변수로 컬러 관리
- [ ] 기존 기능 (드래그, 리사이즈, 텍스트 편집) 유지

### Step 2 완료 시
- [ ] 좌측 아이콘 스트립 표시
- [ ] 4탭 전환 동작
- [ ] 파일 메뉴 드롭다운 열림/닫힘
- [ ] 옵션 패널 토글 스위치 동작

### Step 3 완료 시
- [ ] 툴바 아이콘 원본과 일치
- [ ] 배경색 스워치 표시
- [ ] 월페이퍼 뱅크 3열 그리드
- [ ] 월페이퍼 클릭 → 배경 변경

### Step 4 완료 시
- [ ] 초록색 8개 핸들 표시
- [ ] 8방향 리사이즈 동작
- [ ] PositionBar에 위치/크기 표시
- [ ] 비선택 시 PositionBar 숨김

### Step 5 완료 시
- [ ] 페이지 썸네일 배경색 반영
- [ ] 번호 표시
- [ ] "..." 컨텍스트 메뉴
- [ ] 접기/펼치기 동작

### Step 6 완료 시
- [ ] 더블클릭 텍스트 편집
- [ ] 우클릭 컨텍스트 메뉴
- [ ] Ctrl+C/V 패널 복사/붙여넣기
- [ ] Delete 키 삭제
