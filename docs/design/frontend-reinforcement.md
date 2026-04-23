# BookStudio 프론트엔드 보강 설계서

> 원본: Vue2 프로젝트 (`2022-Refactoring---0224--(vue2).zip`)
> 대상: `/Users/yonsekim/Developer/Projects/BOOKSTUDIO/frontend/`
> 작성일: 2026-04-19
> 구현일: 2026-04-23
> 상태: **구현 완료**

---

## 1. 배경 및 목적

### 1.1 상황

원본 Vue2 프론트엔드 소스를 분실한 상태에서 빌드 파일 기반으로 React 프론트엔드를 구축했으나, 원본 소스를 찾음(`2022-Refactoring---0224--(vue2).zip`). 원본 분석 결과 현재 React 구현에 **치명적 버그 4건**, **기능 누락 10+건**, **디자인 불일치** 다수 발견.

### 1.2 목적

1. 원본의 기능을 완벽하게 재현 (누락된 기능 추가, 버그 수정)
2. 원본의 디자인을 정확히 재현 (레이아웃, 컬러, 상호작용)
3. 기존 React 코드의 구조를 유지하며 점진적 보강

### 1.3 원본 Vue2 핵심 구조 요약

```
editor/
├── LayoutEditor.vue          — 3단 레이아웃 (330px 좌 | flex 중앙 | 190px 우)
├── designer/
│   ├── Designer.vue           — 좌측 패널 컨테이너 (280px + 50px 옵션)
│   ├── DesignerCreatePanel.vue — 패널 생성 버튼 8종
│   ├── DesignerOptions.vue     — 월페이퍼/색상 선택 라디오, 업로드 버튼
│   ├── FileOptions.vue         — 그리드/가이드/테마 옵션
│   ├── buttons/                — CreatePanelHeadline, Text, Image, Shape 등
│   ├── controllers/            — Text/Image/Shape/Background/Webscrap 컨트롤러
│   ├── itembanks/              — Wallpaper/Color/Font/Shape 뱅크
│   └── menus/                  — File/Insert/Share 메뉴
├── media-pad/
│   └── MediaPad.vue            — 캔버스 (768px 기준 + scale)
├── panels/
│   ├── MediaBox.vue            — vue-moveable 기반 드래그/리사이즈/회전
│   ├── PanelContents.vue       — TipTap 에디터 + 패널 분기
│   └── media-box-inners/       — 각 패널 타입별 렌더러 + shapes/ (24종)
├── page-list/
│   ├── PageList.vue            — SortableJS 드래그 정렬
│   ├── LiPageList.vue          — 축소 BookViewer 썸네일 (scale 0.1041)
│   └── GroupMenuPageList.vue   — 컨텍스트 메뉴
├── modules/
│   ├── WallpaperUploadController.vue — 크롭 슬라이더 UI
│   ├── WallpaperUploadPad.vue  — 크롭 미리보기
│   ├── StickyNoteEditor.vue    — 드래그 가능 메모
│   └── Collaborators.vue       — 협업자 아바타 목록
└── book-viewer/                — 읽기 전용 뷰어 + 패널 8종
```

---

## 2. 보강 전 React 구현 분석 (2026-04-19 시점)

### 2.1 치명적 버그 (반드시 수정)

| # | 버그 | 원인 | 영향 |
|---|------|------|------|
| B1 | **Selection state 이중 관리** | `editorStore.selectedPanelIds`와 `selectionStore.selectedPanelIds` 독립 존재 | PanelWrapper는 selectionStore에 쓰고, EditorCanvas는 selectionStore만 클리어 → editorStore의 selection은 안 지워짐 → 유령 선택 |
| B2 | **Zoom 미반영 드래그/리사이즈** | `PanelWrapper.handleMouseDown`에서 `dx = ev.clientX - startX` (원시 픽셀) | zoom > 1이면 패널이 마우스보다 빠르게 이동, zoom < 1이면 느리게 이동 |
| B3 | **TextPanel 커서 점핑** | `contentEditable` + `dangerouslySetInnerHTML` + `onInput`으로 스토어 업데이트 → re-render시 innerHTML 재설정 | 타이핑 중 커서가 처음으로 돌아감 |
| B4 | **DevApp 카운터 리셋** | `let pageCounter = 4`, `let panelCounter = 100`이 컴포넌트 함수 본문에 선언 | 매 렌더마다 초기화 → 중복 ID 생성 가능 |

### 2.2 기능 누락 (원본 대비)

| # | 기능 | 원본 상태 | 현재 상태 |
|---|------|----------|----------|
| F1 | Shape 24종 | SVG viewBox 24x24 기반 24개 도형 | 5개 (rect, ellipse, triangle, diamond, star) |
| F2 | Context-sensitive 컨트롤러 | Text/Image/Shape/Background/Webscrap별 전용 컨트롤러 | TextBank + ImageBankPanel만 존재, Shape/Embed/Video 컨트롤러 없음 |
| F3 | 회전 핸들 | vue-moveable 기반 시각적 회전 핸들 | rotate 프로퍼티만 존재, UI 핸들 없음 |
| F4 | 스냅 투 그리드 | throttleDrag/throttleResize = 10px | snapToGrid 토글만 존재, 로직 미구현 |
| F5 | 가이드라인 | 패널 정렬 가이드 표시 | showGuides 토글만 존재, 렌더링 없음 |
| F6 | 페이지 드래그 정렬 | SortableJS 기반 | 버튼 only (Move Up/Down) |
| F7 | 페이지 축소 미리보기 | scale(0.1041) BookViewer 썸네일 | 배경색만 표시 |
| F8 | 월페이퍼 업로드/크롭 | 파일 업로드 → 슬라이더 크롭 UI | 업로드 버튼 onClick 없음 |
| F9 | 폰트 로딩 | 27종 폰트 사용 | font-family 참조만 있고 실제 로딩 없음 |
| F10 | Undo/Redo | (원본도 미완성) | historyStore 존재하나 push() 미호출 |
| F11 | 클립보드 (Ctrl+C/V) | Ctrl+Shift+C/V로 패널 복제 | DevApp에만 존재, 프로덕션 에디터에 없음 |
| F12 | 키보드 이동 | (원본 미구현) | 미구현 |
| F13 | 이미지 마스크 | None/Circle/Top/Bottom/Left/Right linear | masked_image 프로퍼티만 존재 |
| F14 | 패널 경계 제한 | bounds 계산으로 캔버스 내 제한 | 무제한 드래그 |

### 2.3 디자인 불일치

| # | 항목 | 원본 | 현재 |
|---|------|------|------|
| D1 | 컬러 뱅크 배치 | 팔레트별 분리 (Vivid, UltraLight, Gray 등 16그룹) | 통합 spectrum 그리드 |
| D2 | 페이지 목록 활성 표시 | 좌측 녹색 3px 세로 바 + 체크 아이콘 | 배경색만 구분 |
| D3 | Shape 뱅크 레이아웃 | 3열 그리드, 골드 하이라이트, 전용 사이드바 | 미존재 |
| D4 | 패널 선택 핸들 | 8방향 핸들 + 점선 보더 (원본과 동일, 현재 잘 구현됨) | ✅ 구현 완료 |

---

## 3. 설계: 7단계 구현

### Step 1: 치명적 버그 수정 (기반 안정화)

#### 1-1. Selection State 통합

**변경**: `selectionStore.ts` 삭제, 모든 selection state를 `editorStore.ts`로 통합

**editorStore.ts 추가 필드:**
```typescript
// 기존 selectedPanelIds 유지 (이미 존재)
hoveredPanelId: string | null     // selectionStore에서 이전
isDragging: boolean               // selectionStore에서 이전
isResizing: boolean               // selectionStore에서 이전

// 액션
setHoveredPanel: (id: string | null) => void
setDragging: (v: boolean) => void
setResizing: (v: boolean) => void
toggleSelectPanel: (id: string) => void  // shift-click용
```

**영향 파일 및 변경:**

| 파일 | 변경 |
|------|------|
| `stores/selectionStore.ts` | 삭제 |
| `stores/editorStore.ts` | hoveredPanelId, isDragging, isResizing, 관련 액션 추가 |
| `components/Panel/PanelWrapper.tsx` | `useSelectionStore` → `useEditorStore` |
| `components/Editor/EditorCanvas.tsx` | `useSelectionStore` → `useEditorStore` |
| `components/Editor/PositionBar.tsx` | `useSelectionStore` → `useEditorStore` |
| `components/Sidebar/TextBank.tsx` | `useSelectionStore` → `useEditorStore` |
| `components/Sidebar/SidebarTabs.tsx` | (간접 참조 확인) |

#### 1-2. Zoom 반영 드래그/리사이즈

**변경**: `PanelWrapper.tsx`

```typescript
// 드래그
const zoom = useEditorStore((s) => s.zoom)
const dx = (ev.clientX - dragRef.current.startX) / zoom
const dy = (ev.clientY - dragRef.current.startY) / zoom

// 리사이즈도 동일하게 / zoom 적용
```

#### 1-3. TextPanel 커서 점핑 수정

**변경**: `TextPanel.tsx`

```typescript
// AS-IS: dangerouslySetInnerHTML 매 렌더시 재설정
<div dangerouslySetInnerHTML={{ __html: text }} />

// TO-BE: useRef로 초기값만 1회 설정, onInput으로만 업데이트
const initializedRef = useRef(false)

useEffect(() => {
  if (ref.current && !initializedRef.current) {
    ref.current.innerHTML = text
    initializedRef.current = true
  }
}, [])

// isEditing 종료 시 최종값 동기화
useEffect(() => {
  if (!isEditing && ref.current) {
    initializedRef.current = false // 다음 편집 시 재초기화 허용
  }
}, [isEditing])
```

`React.memo`로 감싸서 부모 re-render에 의한 불필요한 re-render 방지.

#### 1-4. DevApp 카운터 수정

```typescript
// AS-IS
let pageCounter = 4
let panelCounter = 100

// TO-BE
const pageCounterRef = useRef(4)
const panelCounterRef = useRef(100)
```

---

### Step 2: Shape 시스템 확장 (5종 → 24종)

#### 2-1. ShapePanel.tsx 재작성

**ID 체계**: 1-indexed (원본 호환). 기존 0~4 매핑 제거.

**원본 SVG 도형 24종** (모두 `viewBox="0 0 24 24"` 기반):

| ID | 이름 | SVG 경로 |
|----|------|----------|
| 1 | ArrowBasic | `M2,10 L2,14 L16,14 L16,19 L22,12 L16,5 L16,10 Z` |
| 2 | ArrowBoth | `M6,5 L6,10 L2,10 L2,14 L6,14 L6,19 L12,14 L18,19 L18,14 L22,14 L22,10 L18,10 L18,5 L12,10 Z` |
| 3 | TitleBoxA | `M0,2 L18,2 L24,12 L18,22 L0,22 Z` (오각형 리본) |
| 4 | TitleBoxB | `M3,2 L18,2 L24,12 L18,22 L3,22 L9,12 Z` (쉐브론) |
| 5 | TitleBoxC | `M3,2 L21,2 L24,12 L21,22 L3,22 L0,12 Z` (육각 리본) |
| 6 | TitleBoxD | `M4,2 Q0,2 0,12 Q0,22 4,22 L20,22 Q24,22 24,12 Q24,2 20,2 Z` (스타디움) |
| 7 | Circle | `<circle cx="12" cy="12" r="11" />` |
| 8 | Triangle | `M12,2 L22,22 L2,22 Z` |
| 9 | Square | `M1,4 L23,4 L23,20 L1,20 Z` |
| 10 | Pentagon | 정오각형 좌표 계산 |
| 11 | Hexagon | 정육각형 좌표 계산 |
| 12 | Octagon | 정팔각형 좌표 계산 |
| 13 | Heart | `M12,21 C5,15 1,11 1,7 C1,4 4,2 7,2 C9,2 11,4 12,6 C13,4 15,2 17,2 C20,2 23,4 23,7 C23,11 19,15 12,21 Z` |
| 14 | Star | 5꼭지 별 (outer r=11, inner r=4.2) |
| 15 | BadgeA | 방사형 뱃지 (12포인트) |
| 16 | ArrowPlain | `M2,9 L22,9 L22,15 L2,15 Z` (두꺼운 바) |
| 17 | LineSolid | `M1,11.5 L23,11.5` (stroke line) |
| 18 | LineDotHead | `M1,12 L23,12` + circles r=2 양끝 |
| 19 | LineArrowHead | `M1,12 L20,12` + arrow tip + circle r=2 |
| 20 | TitleBoxE | `M4,2 L24,2 L20,22 L0,22 Z` (평행사변형) |
| 21 | TitleBoxF | `M0,2 Q0,0 2,0 L22,0 Q24,0 24,2 L24,22 Q24,24 22,24 L2,24 Q0,24 0,22 Z` (둥근 사각형) |
| 22 | BalloonLeft | 말풍선 + 좌하 꼬리 |
| 23 | BalloonCenter | 말풍선 + 중앙하 꼬리 |
| 24 | BalloonRight | 말풍선 + 우하 꼬리 |

**구현 방식**: `SHAPE_PATHS` 객체에 ID → SVG renderer 함수 매핑.

렌더링:
```typescript
<svg width="100%" height="100%" viewBox="0 0 24 24" preserveAspectRatio="none">
  {SHAPE_PATHS[panel.shape_type]?.(fill, stroke, strokeWidth)}
</svg>
```

#### 2-2. ShapeBankPanel.tsx (신규)

사이드바에 표시되는 도형 선택/컨트롤 패널.

**레이아웃** (원본 ShapeBank.vue 재현):
```
┌─────────────────────────────┐
│ ◆ 도형                      │
├─────────────────────────────┤
│ Shape 컨트롤러               │
│  도형 투명도: [━━━━━━] 0.8   │
│  도형 색상: [■]              │
│  테두리 두께: [━━━━] 2       │
│  테두리 색상: [■]            │
│  테두리 투명도: [━━━━] 1     │
│  그림자: [━━━━] 0            │
├─────────────────────────────┤
│ ◆ 도형 뱅크                  │
│ ┌────┐ ┌────┐ ┌────┐        │
│ │ →  │ │ ↔  │ │ ▷  │        │
│ └────┘ └────┘ └────┘        │
│ ┌────┐ ┌────┐ ┌────┐        │
│ │ ◁▷ │ │ ⬡  │ │ ◎  │        │
│ └────┘ └────┘ └────┘        │
│         ...                  │
└─────────────────────────────┘
```

- 3열 그리드 (`grid-template-columns: repeat(3, 1fr); gap: 0.6em`)
- 각 셀: 정사각형, `background-color: var(--bs-bg-tertiary)`
- 활성: 골드 fill `#d2a000`, 밝은 배경
- 호버: 골드 fill, inset box-shadow

---

### Step 3: 사이드바 컨텍스트 확장

#### 3-1. sidebarContext 타입 확장

**editorStore.ts:**
```typescript
// AS-IS
sidebarContext: 'default' | 'text' | 'image' | 'wallpaper'

// TO-BE
sidebarContext: 'default' | 'text' | 'image' | 'wallpaper' | 'shape' | 'embed' | 'video'
```

#### 3-2. PanelWrapper 사이드바 연결 보강

```typescript
// 패널 클릭 시 사이드바 컨텍스트 전환
if (type === 'TXT' || type === 'HL' || type === 'DOC') setSidebarContext('text')
else if (type === 'IMG') setSidebarContext('image')
else if (type === 'SHA') setSidebarContext('shape')      // 추가
else if (type === 'EV' || type === 'WS') setSidebarContext('embed')  // 추가
else if (type === 'VOD' || type === 'AUDIO') setSidebarContext('video')  // 추가
else setSidebarContext('default')
```

#### 3-3. SidebarTabs 분기 보강

```typescript
// 컨텍스트별 사이드바 콘텐츠
if (sidebarContext === 'text') return <TextBank />
if (sidebarContext === 'image') return <ImageBankPanel />
if (sidebarContext === 'shape') return <ShapeBankPanel />   // 추가
if (sidebarContext === 'wallpaper') return <WallpaperBank />
// embed, video는 default와 동일 (향후 전용 패널 추가 가능)
```

#### 3-4. ImageBankPanel 마스크 기능 추가

원본의 6가지 이미지 마스크 (ControllersImage.vue):

| 마스크 | 값 | CSS 구현 |
|--------|-----|---------|
| None | `'none'` | mask 없음 |
| Circle | `'CIRCLE'` | `border-radius: 50%` |
| Top Linear | `'TOP_LINEAR'` | `mask-image: linear-gradient(to bottom, transparent, black)` |
| Bottom Linear | `'BOTTOM_LINEAR'` | `mask-image: linear-gradient(to top, transparent, black)` |
| Left Linear | `'LEFT_LINEAR'` | `mask-image: linear-gradient(to right, transparent, black)` |
| Right Linear | `'RIGHT_LINEAR'` | `mask-image: linear-gradient(to left, transparent, black)` |

UI: 6개 버튼 (아이콘 + 라벨), 활성 시 녹색 보더.

---

### Step 4: 패널 상호작용 보강

#### 4-1. 회전 핸들

**PanelWrapper.tsx에 추가:**

```
         ⟳  ← 회전 핸들 (top: -30px)
         │  ← 연결선
    [TL]───────[TR]
     │            │
    [ML]        [MR]
     │            │
    [BL]───────[BR]
```

- 회전 핸들: 원형 12x12px, 배경 white, 보더 2px `--bs-accent`
- 연결선: 1px dashed `--bs-accent`, height 20px
- 드래그 시: 패널 중심을 기준으로 마우스 각도 계산 → `panel.rotate` 업데이트
- `Math.atan2(dy, dx)` 기반, 1도 단위 스냅 (`throttleRotate: 1`)

```typescript
const handleRotate = (e: MouseEvent) => {
  const rect = wrapperRef.current.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height / 2

  const onMove = (ev: globalThis.MouseEvent) => {
    const angle = Math.atan2(ev.clientY - cy, ev.clientX - cx) * 180 / Math.PI + 90
    updatePanel(panel.id, { rotate: Math.round(angle) })
  }
  // mouseup에서 remove listener
}
```

#### 4-2. 스냅 투 그리드

```typescript
const snap = (value: number) => {
  if (!snapToGrid) return value
  return Math.round(value / gridSize) * gridSize
}

// 드래그에 적용
updatePanel(panel.id, {
  left: snap(dragRef.current.origLeft + dx / zoom),
  top: snap(dragRef.current.origTop + dy / zoom),
})
```

#### 4-3. 가이드라인 (`common/GuideLines.tsx`)

드래그 중 표시되는 정렬 가이드:

1. **페이지 중앙 가이드** (빨간 점선):
   - 수평 중앙: `y = pageHeight / 2`
   - 수직 중앙: `x = pageWidth / 2`
   - 패널 중심이 ±5px 이내일 때 표시 + 스냅

2. **패널 정렬 가이드** (파란 점선):
   - 다른 패널의 left, right, top, bottom, centerX, centerY와 비교
   - ±5px 이내일 때 표시 + 스냅

**렌더링**: EditorCanvas 내부, SVG 오버레이로 표시 (pointer-events: none)

```typescript
interface GuideLine {
  type: 'horizontal' | 'vertical'
  position: number  // px
  color: 'red' | 'blue'
}
```

#### 4-4. 키보드 화살표 이동

**EditorLayout.tsx에 전역 keydown 리스너 추가:**

```typescript
if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) {
  if (selectedPanelIds.length === 0) return
  if (target.isContentEditable || target.tagName === 'INPUT') return
  e.preventDefault()
  const step = e.shiftKey ? 10 : 1
  const delta = {
    ArrowUp: { top: -step },
    ArrowDown: { top: step },
    ArrowLeft: { left: -step },
    ArrowRight: { left: step },
  }[e.key]
  selectedPanelIds.forEach(id => updatePanel(id, delta))
}
```

#### 4-5. 클립보드 EditorLayout 통합

**editorStore.ts 추가:**
```typescript
clipboard: Panel[] | null

copyToClipboard: () => void   // 선택된 패널 복사
pasteFromClipboard: () => void // 붙여넣기
deleteSelectedPanels: () => void
```

**EditorLayout.tsx에 전역 keydown:**
- `Ctrl+C`: `copyToClipboard()`
- `Ctrl+V`: `pasteFromClipboard()`
- `Delete/Backspace`: `deleteSelectedPanels()`

DevApp에서 중복 코드 제거.

#### 4-6. 패널 경계 제한

```typescript
// 드래그 시 클램핑 (최소 20px 보이게)
const clampedLeft = Math.max(-panel.width + 20, Math.min(pageWidth - 20, newLeft))
const clampedTop = Math.max(-panel.height + 20, Math.min(pageHeight - 20, newTop))
```

---

### Step 5: 페이지 목록 보강

#### 5-1. 축소 미리보기

**PageListPanel.tsx:**

원본 방식: 실제 캔버스와 동일한 구조를 `transform: scale()` 로 축소.

```typescript
const thumbScale = 120 / layoutConfig.width  // 120px 너비 기준

<div style={{
  width: layoutConfig.width,
  height: layoutConfig.height,
  transform: `scale(${thumbScale})`,
  transformOrigin: 'top left',
  position: 'relative',
  // 배경색/월페이퍼 적용
}}>
  {/* 미니 패널 렌더링 (텍스트만 간략히) */}
  {pagePanels.map(p => (
    <div key={p.id} style={{
      position: 'absolute',
      left: p.left, top: p.top,
      width: p.width, height: p.height,
      fontSize: p.font_size,
      color: p.color,
      overflow: 'hidden',
    }}>
      {p.media_type === 'HL' ? p.headline : p.media_type === 'TXT' ? p.text : null}
    </div>
  ))}
</div>
```

컨테이너에 `overflow: hidden`으로 실제 표시 크기 제한:
```typescript
<div style={{
  width: 120,
  height: 120 * layoutConfig.height / layoutConfig.width,
  overflow: 'hidden',
}}>
  {/* 위의 축소 렌더링 */}
</div>
```

#### 5-2. 드래그 정렬

**의존성**: `@dnd-kit/core`, `@dnd-kit/sortable` 추가

```typescript
import { DndContext, closestCenter } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable'

// 각 페이지 아이템을 SortableItem으로 감싸기
// onDragEnd에서 reorderPages() 호출
```

#### 5-3. 활성 페이지 표시

```css
.bs-pagelist__item--active {
  border-left: 3px solid var(--bs-accent);
}
.bs-pagelist__item--active .bs-pagelist__check {
  display: flex; /* 체크 아이콘 표시 */
}
```

#### 5-4. 페이지 복제

```typescript
const handleDuplicate = (pageId: string) => {
  const page = pages.find(p => p.id === pageId)
  if (!page) return
  const newId = `page-dup-${Date.now()}`
  const newPage = { ...page, id: newId, order: pages.length }
  addPage(newPage)
  // 패널 딥카피
  const srcPanels = panels[pageId] || []
  const newPanels = srcPanels.map((p, i) => ({
    ...p, id: `panel-dup-${Date.now()}-${i}`, page: newId
  }))
  setPanels(newId, newPanels)
}
```

---

### Step 6: 폰트 로딩 + Undo/Redo

#### 6-1. Google Fonts 로딩

**`styles/fonts.css` 신규:**
```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;400;700;900&family=Nanum+Gothic:wght@400;700&family=Nanum+Brush+Script&family=Nanum+Pen+Script&family=Roboto:wght@100;400;700;900&family=Montserrat:wght@100;400;900&family=Anton&family=Lobster&family=Playball&family=Monoton&display=swap');
```

`dev/main.tsx`와 `index.ts`에서 import.

#### 6-2. Undo/Redo 연결

**전략**: Zustand middleware로 구현하지 않고, 명시적 push 방식 유지.

```typescript
// historyStore 활용
// 변경 시점: mouseUp (드래그/리사이즈 완료), panel/page CRUD 후
const pushHistory = () => {
  const { pages, panels } = useEditorStore.getState()
  useHistoryStore.getState().push(JSON.stringify({ pages, panels }))
}

// undo
const undo = () => {
  const snapshot = useHistoryStore.getState().undo()
  if (snapshot) {
    const { pages, panels } = JSON.parse(snapshot)
    useEditorStore.setState({ pages, panels })
  }
}
```

**push 시점:**
- `PanelWrapper`: drag mouseDown 시 push (이동 전 상태 저장), resize mouseDown 시 push
- `addPanel`, `removePanel`, `addPage`, `removePage` 호출 시
- TextPanel `onBlur` 시 (편집 완료)

---

### Step 7: DevApp 통합 및 디자인 정리

#### 7-1. 패널 기본 크기 (원본 맞춤)

| 타입 | 너비 | 높이 | 비고 |
|------|------|------|------|
| HL | 400 | 80 | 리사이즈 가능 |
| TXT | 200 | 80 | 리사이즈 가능 |
| IMG | 300 | 300 | 비율 유지 (코너 핸들) |
| SHA | 200 | 200 | 고정 |
| EV | 500 | 182 | 고정 |
| VOD | 300 | 165 | 기본 위치 X: 400 |

#### 7-2. BookInfoPanel 연결

```typescript
// AS-IS: defaultValue (uncontrolled)
<input defaultValue={edition?.title} />

// TO-BE: controlled + debounced update
<input
  value={edition?.title || ''}
  onChange={(e) => setEdition({ ...edition, title: e.target.value })}
/>
```

#### 7-3. SidebarTabs title 연결

제목 입력 `onChange` → `useEditorStore.getState().setEdition(...)` 호출.

---

## 4. 구현 결과 (2026-04-23)

### 4.1 구현 완료 항목

| Step | 항목 | 구현 상태 | 비고 |
|------|------|----------|------|
| 1-1 | Selection state 통합 | ✅ 완료 | `selectionStore.ts` 삭제, `editorStore`로 통합. `index.ts` re-export도 제거. |
| 1-2 | Zoom 반영 드래그/리사이즈 | ✅ 완료 | `useEditorStore.getState().zoom`으로 실시간 참조, `dx / zoom` 적용 |
| 1-3 | TextPanel 커서 점핑 | ✅ 완료 | `dangerouslySetInnerHTML` 제거, `initializedRef`로 1회 설정, `React.memo` 적용 |
| 1-4 | DevApp 카운터 | ✅ 완료 | `useRef`로 변경 |
| 2-1 | Shape 24종 확장 | ✅ 완료 | 1-indexed (1~24), `viewBox="0 0 24 24"`, `SHAPE_IDS_ORDERED` export |
| 2-2 | ShapeBankPanel | ✅ 완료 | 3열 그리드 + 컨트롤러 (투명도/색상/테두리/그림자) |
| 3-1 | sidebarContext 확장 | ✅ 완료 | `'shape' \| 'embed' \| 'video'` 추가 |
| 3-2 | PanelWrapper 컨텍스트 연결 | ✅ 완료 | SHA→shape, EV/WS→embed, VOD/AUDIO→video |
| 3-3 | SidebarTabs 분기 | ✅ 완료 | shape 컨텍스트 → ShapeBankPanel 표시 |
| 4-1 | 회전 핸들 | ✅ 완료 | 원형 핸들 + 점선 연결선, `Math.atan2` 기반 회전 |
| 4-2 | 스냅 투 그리드 | ✅ 완료 | 드래그/리사이즈 모두 snap 적용 |
| 4-4 | 키보드 화살표 이동 | ✅ 완료 | Arrow 1px, Shift+Arrow 10px |
| 4-5 | 클립보드 통합 | ✅ 완료 | `EditorLayout`에서 Ctrl+C/V/Delete 전역 처리, DevApp 중복 제거 |
| 4-6 | 패널 경계 제한 | ✅ 완료 | 최소 20px 보이게 클램핑 |
| 5-1 | 페이지 축소 미리보기 | ✅ 완료 | `transform: scale()` + 배경/패널 미니 렌더 (thumbWidth=140) |
| 5-3 | 활성 페이지 표시 | ✅ 완료 | 좌측 녹색 3px 바 + Check 아이콘 |
| 5-4 | 페이지 복제 | ✅ 완료 | 로컬 딥카피 (page + panels) |
| 6-1 | Google Fonts 로딩 | ✅ 완료 | `fonts.css` 신규, 10종 폰트 패밀리 |
| 6-2 | Undo/Redo 연결 | ✅ 완료 | `pushHistory()` → drag/resize 시작, paste/delete 전 push. Ctrl+Z/Shift+Z 동작 |
| 7-1 | 패널 기본 크기 | ✅ 완료 | HL:400x80, TXT:200x80, SHA:200x200, EV:500x182, VOD:300x165 |
| 7-2 | BookInfoPanel controlled | ✅ 완료 | `value` + `onChange` → 스토어 연결 |
| 7-3 | SidebarTabs title | ✅ 완료 | `value` + `onChange` → `setEdition()` |

### 4.2 추가 구현 (2026-04-23 2차)

| Step | 항목 | 구현 상태 | 비고 |
|------|------|----------|------|
| 4-3 | 가이드라인 렌더링 | ✅ 완료 | `GuideLines.tsx` 신규 — SVG 오버레이, 페이지 중앙/엣지 (빨간 점선) + 패널 정렬 (파란 점선), 5px threshold |
| 5-2 | 페이지 드래그 정렬 | ✅ 완료 | `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities` 설치. `SortablePageThumbnail` + `GripVertical` 드래그 핸들 |
| 3-4 | ImageBankPanel 마스크 UI | ✅ 완료 | 6종 마스크 버튼 (None, Circle, Top/Bottom/Left/Right Linear). `ImagePanel.tsx`에 `mask-image` CSS 적용 |
| F8 | 월페이퍼 업로드 | ✅ 완료 | ToolbarStrip에 hidden file input + `handleFileChange`. 로컬 `URL.createObjectURL` fallback. `onUploadWallpaper` prop으로 프로덕션 연결 가능. 크롭 UI는 미구현 |

### 4.3 미구현 항목 (향후 작업)

| 항목 | 사유 |
|------|------|
| 월페이퍼 크롭 슬라이더 UI | 원본의 `WallpaperUploadController.vue` 수준의 크롭 슬라이더. 현재는 업로드 즉시 적용 |

### 4.4 실제 수정된 파일 목록

| 파일 | 작업 | Step |
|------|------|------|
| `stores/editorStore.ts` | selection 통합, sidebarContext 확장, clipboard/undo 액션, `pushHistory()` export | 1,3,4,6 |
| `stores/selectionStore.ts` | **삭제** | 1 |
| `components/Panel/PanelWrapper.tsx` | selectionStore→editorStore, zoom 반영, 회전 핸들, 스냅, 경계 제한, 사이드바 컨텍스트 확장, pushHistory 연결 | 1,3,4,6 |
| `components/Panel/TextPanel.tsx` | `dangerouslySetInnerHTML` 제거, ref 기반 초기화, `React.memo` | 1 |
| `components/Panel/ShapePanel.tsx` | 24종 SVG 도형 재작성, `SHAPE_IDS_ORDERED` export | 2 |
| `components/Panel/ImagePanel.tsx` | 마스크 6종 CSS (`mask-image`, `border-radius`) | 3-4 |
| `components/Editor/EditorCanvas.tsx` | selectionStore→editorStore, `GuideLines` import/렌더 | 1,4-3 |
| `components/Editor/EditorLayout.tsx` | 전역 키보드 (Arrow/Ctrl+C/V/Delete/Ctrl+Z), pushHistory/historyStore import | 4,6 |
| `components/Editor/PositionBar.tsx` | selectionStore→editorStore | 1 |
| `components/Sidebar/SidebarTabs.tsx` | ShapeBankPanel import, shape 컨텍스트 분기, title controlled input | 3,7 |
| `components/Sidebar/TextBank.tsx` | selectionStore→editorStore | 1 |
| `components/Sidebar/ImageBankPanel.tsx` | selectionStore→editorStore, 마스크 6종 버튼 UI | 1,3-4 |
| `components/Sidebar/ShapeBankPanel.tsx` | **신규** — 도형 선택 그리드 + 컨트롤러 | 2,3 |
| `components/Sidebar/BookInfoPanel.tsx` | `defaultValue` → `value` + `onChange` controlled | 7 |
| `components/common/GuideLines.tsx` | **신규** — 정렬 가이드 SVG 오버레이 | 4-3 |
| `components/PageList/PageListPanel.tsx` | 축소 미리보기, 활성 표시, 복제, dnd-kit 드래그 정렬 | 5 |
| `components/Toolbar/ToolbarStrip.tsx` | 월페이퍼 업로드 (hidden file input + objectURL fallback) | F8 |
| `dev/DevApp.tsx` | `useRef` 카운터, 키보드 핸들러 제거 (EditorLayout으로 이전), 패널 기본 크기 | 1,7 |
| `styles/editor.css` | 회전 핸들, 가이드라인, Shape Bank, 페이지 목록, 드래그 핸들 CSS | 2,4,5 |
| `styles/fonts.css` | **신규** — Google Fonts @import (10종) | 6 |
| `dev/main.tsx` | fonts.css import 추가 | 6 |
| `index.ts` | `useSelectionStore` re-export 제거 | 1 |

### 4.5 빌드 결과

```
npm run build → 성공
dist/index.js  192.83 kB │ gzip: 48.11 kB  (dnd-kit 추가로 증가)
tsc --noEmit → 에러 없음
```

---

## 5. 검증 방법

```bash
cd frontend && npm run dev
```

| # | 검증 항목 | 기대 결과 | 구현 상태 |
|---|----------|----------|----------|
| V1 | 줌 50%/200%에서 드래그 | 마우스 이동량 = 패널 이동량 | ✅ |
| V2 | 텍스트 더블클릭 → 타이핑 | 커서 위치 유지, 점핑 없음 | ✅ |
| V3 | Shape 추가 → 사이드바 24종 변경 | 모든 도형 정확히 렌더링 | ✅ |
| V4 | Shape 클릭 → 사이드바 ShapeBankPanel | 색상/투명도/테두리 슬라이더 동작 | ✅ |
| V5 | 회전 핸들 드래그 | 패널 자유 회전 | ✅ |
| V6 | 스냅 ON + 드래그 | 그리드 간격으로 스냅 | ✅ |
| V7 | 페이지 목록 드래그 정렬 | 드래그로 순서 변경 | ✅ |
| V8 | 페이지 썸네일 | 배경 + 패널 축소 표시 | ✅ |
| V9 | Ctrl+Z | 직전 변경 undo | ✅ |
| V10 | 폰트 뱅크 선택 | 실제 폰트 적용 (렌더링 확인) | ✅ |
| V11 | `npm run build` | 빌드 성공, 에러 없음 | ✅ |
| V12 | 드래그 중 가이드라인 | 페이지 중앙(빨간) + 패널 정렬(파란) 점선 표시 | ✅ |
| V13 | 이미지 마스크 선택 | 6종 마스크 버튼 → 이미지에 mask 적용 | ✅ |
| V14 | 월페이퍼 업로드 | 툴바 버튼 → 파일 선택 → 배경 적용 | ✅ |
