# BookStudio CSS 디자인 복원 설계서

> 원본 Vue2 에디터의 CSS 디자인 시스템을 현재 React 프론트엔드에 정밀 복원하기 위한 설계 문서

## 0. 범위 정의

이 문서는 두 가지 수준의 복원을 구분한다:

- **Level A (CSS-only)**: CSS 변수, 색상, 그림자, 핸들, 입력 컨트롤, 폰트, 스크롤바 등 **TSX 구조 변경 없이** CSS만으로 복원 가능한 항목. Phase 1, 3, 4, 5가 해당.
- **Level B (구조적)**: 레이아웃 치수 변경, Toolbar 통합, 사이드바 구조 변경 등 **TSX 컴포넌트 마크업 변경이 필요한** 항목. Phase 2가 해당.

Level A만 적용해도 시각적으로 원본에 크게 가까워진다. Level B는 원본과 100% 동일한 레이아웃이 필요할 때만 적용.

## 1. 현황 분석

### 1.1 원본 Vue2 디자인 시스템

원본은 SCSS 기반으로 다음 파일들로 구성:

| 파일 | 역할 |
|------|------|
| `_variables.scss` | 기본 변수, CDN 경로, z-index 가이드 |
| `_default-theme-colors.scss` | 다크/라이트 테마 색상 정의 |
| `_poly-theme-colors.scss` | 4종 악센트 테마 (바이올렛/그린/레드/옐로우) |
| `_common.scss` | 글로벌 컴포넌트 스타일 (2592줄) |
| `_mixins.scss` | 15+ 반응형 브레이크포인트 |
| `_icon-fonts.scss` | Fontello 커스텀 아이콘 폰트 |
| `_editor_drrs.scss` | Moveable 드래그/리사이즈 핸들 스타일 |

### 1.2 현재 React 디자인 시스템

순수 CSS + CSS Variables 기반:

| 파일 | 역할 |
|------|------|
| `variables.css` | CSS 변수 (59줄) |
| `editor.css` | 메인 레이아웃 + 컴포넌트 (1243줄) |
| `reset.css` | 글로벌 리셋 (67줄) |
| `fonts.css` | Google Fonts import (2줄) |

---

## 2. 색상 시스템 복원

### 2.1 다크 테마 배경색

원본은 `#000000` 기반으로 `lighten()`으로 단계 생성. 현재는 `#1e1e1e` 기반으로 훨씬 밝음.

| 용도 | 원본 (계산값) | 현재 | 복원 값 |
|------|-------------|------|--------|
| 카드/패널 배경 (bg-a) | `#262626` (lighten 15%) | `--bs-bg-secondary: #252525` | `#262626` |
| 페이지 중앙 (bg-b) | `#1c1c1c` (lighten 11%) | `--bs-bg-tertiary: #333333` | `#1c1c1c` |
| 에디터 캔버스 (bg-c) | `#171717` (lighten 9%) | `--bs-bg-canvas: #2f2f2f` | `#171717` |
| 전체 배경 (bg-d) | `#0d0d0d` (lighten 5%) | `--bs-bg-primary: #1e1e1e` | `#0d0d0d` |
| 팝업 오버레이 (bg-s) | `rgba(34,34,34,0.8)` | 없음 | `rgba(34,34,34,0.8)` 추가 |
| 호버 | 없음 (g10 사용) | `--bs-bg-hover: #3a3a3a` | `#1a1a1a` |
| 액티브 | 없음 (g20 사용) | `--bs-bg-active: #444444` | `#2a2a2a` |

### 2.2 다크 테마 텍스트/전경색

| 용도 | 원본 | 현재 | 복원 값 |
|------|------|------|--------|
| 기본 텍스트 | 없음 (w80~w100) | `--bs-text-primary: #e0e0e0` | `#e0e0e0` (유지) |
| 보조 텍스트 | `#999999` (fg-gray) | `--bs-text-secondary: #999999` | `#999999` (유지) |
| 비활성 텍스트 | 없음 | `--bs-text-muted: #666666` | `#666666` (유지) |

### 2.3 악센트 색상

원본은 4종 테마 시스템이나, 현재 단일 그린. **Phase 1에서는 그린 테마(poly-b) 기반으로 복원하고, Phase 2에서 멀티 테마 지원.**

| 용도 | 원본 (Green/poly-b) | 현재 | 복원 값 |
|------|---------------------|------|--------|
| 솔리드 악센트 | `#28a082` | `--bs-accent: #7cc576` | `#28a082` |
| 악센트 호버 | 없음 (lighten 10%) | `--bs-accent-hover: #6ab564` | `#32b896` |
| 그라디언트 (H) | `#82be64 → #008278` | 없음 | `--bs-accent-gradient-h` 추가 |
| 그라디언트 (V) | `#82be64 → #008278` | 없음 | `--bs-accent-gradient-v` 추가 |
| 노랑 (포지션바 등) | `#c8b428` (fg-yellow) | `--bs-accent-yellow: #e8c840` | `#c8b428` |
| 위험/삭제 | `#ff5050` (fg-red) | `--bs-danger: #e85050` | `#ff5050` |
| 파랑 (정보) | `#78bedc` (fg-blue) | 없음 | `--bs-info: #78bedc` 추가 |
| 녹색 (활성) | `#28dc78` (fg-green) | 없음 | `--bs-success: #28dc78` 추가 |
| 활성 상태 | `#00b464` | 없음 | `--bs-active: #00b464` 추가 |

### 2.4 라이트 테마

| 용도 | 원본 (계산값) | 현재 | 복원 값 |
|------|-------------|------|--------|
| 전체 배경 | `#ffffff` (darken 0%) | `--bs-bg-primary: #ffffff` | 유지 |
| 카드 배경 | `#fafafa` (darken 2%) | `--bs-bg-secondary: #f5f5f5` | `#fafafa` |
| 입력 배경 | `#f0f0f0` (darken 6%) | `--bs-bg-tertiary: #eeeeee` | `#f0f0f0` |
| 캔버스 | `#ebebeb` (darken 8%) | `--bs-bg-canvas: #e0e0e0` | `#ebebeb` |
| fg-gray | `#555555` | `--bs-text-secondary: #666666` | `#555555` |
| fg-green | `#14aa78` | `--bs-accent: #5ea858` | `#14aa78` |

### 2.5 원본 불투명도 스케일 시스템

원본은 0~100 스케일의 CSS 변수를 생성하여 불투명도 기반 색상 체계 사용:

```css
--color-g{0-100}: rgba(130, 130, 130, {i * 0.01})   /* 회색 */
--color-ga{0-100}: rgba(110, 110, 110, {i * 0.01})  /* 대안 회색 */
--color-k{0-100}: rgba(0, 0, 0, {i * 0.01})         /* 검정 */
--color-w{0-100}: rgba(255, 255, 255, {i * 0.01})   /* 흰색 */
```

**복원 방침**: 전체 스케일 재현은 과도하므로, 실제 사용되는 값만 `--bs-*` 변수로 매핑:

| 원본 변수 | 용도 | 복원 변수 |
|-----------|------|----------|
| `--color-g10` | 버튼 호버 배경 | `--bs-btn-hover: rgba(130,130,130,0.1)` |
| `--color-g15` | 스크롤바 트랙, 검색 배경 | `--bs-input-bg: rgba(130,130,130,0.15)` |
| `--color-g20` | 버튼 액티브 | `--bs-btn-active: rgba(130,130,130,0.2)` |
| `--color-g30` | 스크롤바, 체크박스 | `--bs-control-bg: rgba(130,130,130,0.3)` |
| `--color-g50` | 보더, 박스쉐도우 | `--bs-border-strong: rgba(130,130,130,0.5)` |
| `--color-g80` | 슬라이더 트랙 | `--bs-slider-track: rgba(130,130,130,0.8)` |
| `--color-g100` | 아이콘 메뉴 보더 | `--bs-border-icon: rgba(130,130,130,1)` |
| `--color-ga30` | 사이드바 구분선 | `--bs-divider: rgba(110,110,110,0.3)` |
| `--color-ga40` | 탑바 하단선, 사이드바 내부선 | `--bs-divider-strong: rgba(110,110,110,0.4)` |
| `--color-k15` | 탑바 그림자 | `--bs-shadow-subtle: rgba(0,0,0,0.15)` |
| `--color-k20` | 사이드바 그림자 | `--bs-shadow-light: rgba(0,0,0,0.2)` |
| `--color-k30` | 캔버스 그림자, 핸들 그림자 | `--bs-shadow-medium: rgba(0,0,0,0.3)` |
| `--color-k40` | 페이지 내부 그림자 | `--bs-shadow-heavy: rgba(0,0,0,0.4)` |
| `--color-k70` | 인포 아이콘 배경 | `--bs-overlay-bg: rgba(0,0,0,0.7)` |
| `--color-w60` | 유저 아바타 보더 | `--bs-avatar-border: rgba(255,255,255,0.6)` |

---

## 3. 레이아웃 치수 복원

### 3.1 전체 구조

```
원본:
┌─ Header (50px, fixed, z:9) ──────────────────────────────┐
├─ Left Sidebar (330px = 280 content + 50 icon) ───────────┤
│  ├─ Designer Container (280px, padding: 50px 10px 10px)  │
│  └─ Option Menu (50px)                                   │
├─ Canvas (flex:1, shadow: 8px 8px 15px)                   │
├─ Right Sidebar (190px = 140 list + 50 collab)            │
│  ├─ List Container (140px, padding: 8px 16px 10px 10px)  │
│  └─ Collaborator (50px)                                  │
└──────────────────────────────────────────────────────────-┘

현재:
┌─ TopBar (36px) ──────────────────────────────────────────┐
├─ AppNav (40px) ──────────────────────────────────────────┤
├─ Sidebar (260px) ────────────────────────────────────────┤
├─ Toolbar (40px) ─────────────────────────────────────────┤
├─ Canvas (flex:1) ────────────────────────────────────────┤
├─ Minibar (40px) ─────────────────────────────────────────┤
├─ PageList (200px) ───────────────────────────────────────┤
└──────────────────────────────────────────────────────────┘
```

### 3.2 치수 변경 사항

| 영역 | 원본 | 현재 | 복원 값 | 비고 |
|------|------|------|--------|------|
| 탑바 높이 | 50px | 36px | **50px** | 원본 일치 |
| 좌측 사이드바 총 폭 | 330px | 40+260=300px | **330px** (280+50) | 원본 구조 |
| 사이드바 콘텐츠 폭 | 280px | 260px | **280px** | 원본 일치 |
| 사이드바 아이콘메뉴 폭 | 50px | 40px (AppNav) | **50px** | 원본 일치 |
| 툴바 폭 | 없음 (사이드바에 통합) | 40px | **삭제** | 원본에 별도 툴바 없음. 도구 버튼은 사이드바 아이콘메뉴에 위치 |
| 우측 페이지목록 총 폭 | 190px | 40+200=240px | **190px** (140+50) | 원본 일치 |
| 페이지목록 콘텐츠 폭 | 140px | 200px | **140px** | 원본 일치 |
| 미니바 폭 | 없음 | 40px | 우측 사이드바 아이콘 영역으로 통합 (50px) | |
| 사이드바 패딩 | 50px 10px 10px 10px | 12px | **10px** (좌우), **50px** (상단) | 원본 일치 |
| 축소 시 사이드바 | 50px (아이콘만) | 0px | **50px** | 아이콘메뉴는 항상 보임 |
| 축소 시 페이지목록 | 50px (협업바만) | 0px | **50px** | 협업바는 항상 보임 |
| 캔버스 그림자 | `8px 8px 15px var(--color-k30)` | `0 2px 20px rgba(0,0,0,0.3)` | 원본 값 | 그림자 방향 복원 |

### 3.3 레이아웃 구조 변경

현재의 5-column 구조 (AppNav | Sidebar | Toolbar | Canvas | Minibar | PageList)를 원본의 3-column 구조로 변경:

```
복원 구조:
┌─ Header (50px, fixed, z:9) ────────────────────────────────┐
│  [로고] [제목] [정보바] [검색] [유저]                         │
├────────────────────────────────────────────────────────────-┤
│ Left (330px)        │ Canvas (flex:1)  │ Right (190px)      │
│ ┌──────────┬──────┐ │                  │ ┌──────┬─────────┐ │
│ │ Content  │ Icon │ │                  │ │Collab│  List   │ │
│ │ (280px)  │(50px)│ │                  │ │(50px)│ (140px) │ │
│ │          │      │ │   Page + Panels  │ │      │         │ │
│ │ [탭]     │ [도구]│ │                  │ │      │ [썸네일]│ │
│ │ [속성]   │ [배경]│ │                  │ │      │         │ │
│ │ [폰트]   │ [도형]│ │                  │ │      │         │ │
│ └──────────┴──────┘ │                  │ └──────┴─────────┘ │
└─────────────────────┴──────────────────┴───────────────────-┘
```

**핵심 변경**: 현재 `Toolbar` (캔버스 좌측 세로 버튼바)는 원본에 없음. 원본에서 도구 버튼(배경, 텍스트, 이미지, 도형 등)은 좌측 사이드바의 **아이콘 메뉴** (50px 영역)에 위치.

---

## 4. 선택/핸들 스타일 복원

### 4.1 원본 Moveable 핸들

```scss
/* 선택 아웃라인 */
.moveable-line {
  background-color: rgba(255, 250, 80, 1);  /* 밝은 노랑 */
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.5);
  --zoompx: 2px;
}

/* 리사이즈 핸들 */
.moveable-control {
  width: 14px;
  height: 14px;
  border-radius: 50%;         /* 원형 */
  background-color: rgba(190, 255, 110, 1);  /* 밝은 연두 */
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3);
  margin: -7px;
}

/* 회전 핸들 */
.moveable-rotation-line .moveable-control {
  width: 26px;
  height: 26px;
  margin-top: -14px;
  margin-left: -12px;
  background-color: rgba(190, 255, 110, 1);
}
```

### 4.2 현재 핸들

```css
.bs-handle {
  background: #ffffff;              /* 흰색 */
  border: 2px solid var(--bs-accent);  /* 초록 보더 */
}
.bs-handle--corner { width: 8px; height: 8px; }   /* 사각형 */
.bs-panel--selected { outline: 1px dashed var(--bs-accent); }  /* 초록 점선 */
```

### 4.3 복원 변경

| 항목 | 현재 | 복원 |
|------|------|------|
| 선택 아웃라인 색 | 초록 점선 | **노랑 실선** `rgba(255, 250, 80, 1)` + 검정 외곽 그림자 |
| 선택 아웃라인 스타일 | `1px dashed` | **1px solid** (원본은 moveable의 실선) |
| 핸들 모양 | 사각형 8x8 | **원형 14x14** |
| 핸들 배경색 | 흰색 | **연두** `rgba(190, 255, 110, 1)` |
| 핸들 보더 | 2px solid 초록 | **없음**, 대신 `box-shadow: 0 0 0 1px rgba(0,0,0,0.3)` |
| 회전 핸들 크기 | 14x14 | **26x26** |
| 회전 핸들 색 | 흰색 배경 + 초록 보더 | **연두 배경** `rgba(190, 255, 110, 1)` |
| 호버 아웃라인 | 점선 | **노랑 점선** (구분용) |

---

## 5. 스크롤바 복원

### 5.1 원본 (17px 두꺼운 스크롤바)

```scss
::-webkit-scrollbar { width: 17px; height: 17px; }
::-webkit-scrollbar-track {
  box-shadow: inset 1px 0 0 0 var(--color-g30);
  background-color: var(--color-g15);
}
::-webkit-scrollbar-thumb {
  border-radius: 4px;
  border: 2px/3px transparent;
  box-shadow: inset 0 0 0 1px var(--color-g30);
  background-color: var(--color-g30);
  background-clip: content-box;
}
```

### 5.2 현재 (6px 얇은 스크롤바)

```css
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 3px; }
```

### 5.3 복원 방침

원본의 17px는 에디터 전체에 적용된 기본값이고, 사이드바 내부 등은 8px 얇은 스크롤바(`.element__scrollbar--inbox`)를 사용. 현재의 6px 얇은 스타일이 모던하고 현재 레이아웃에 맞으므로 **기본은 현재 유지하되, 원본 색상 톤만 복원**:

```css
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track {
  background-color: rgba(130, 130, 130, 0.05);
}
::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background-color: rgba(130, 130, 130, 0.3);
}
::-webkit-scrollbar-thumb:hover {
  background-color: rgba(130, 130, 130, 0.5);
}
```

---

## 6. 버튼 시스템 복원

### 6.1 원본 버튼

원본은 `.button__box` 기반으로 `::after` pseudo-element를 hover 패널로 사용:

```scss
.button__box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5em;
  border-radius: 0.2em;
  cursor: pointer;
}
.button__box::after {
  position: absolute;
  inset: 0;
  transform: scale(0, 1);
  border-radius: 0.3em;
  background-color: var(--color-g10);
  transition: transform 0.2s ease-in-out;
  content: "";
}
.button__box:hover::after {
  transform: scale(1, 1);
}
.button__box.status__active::after {
  box-shadow: inset 0 0 0 1px var(--color-g50);
  transform: scale(1, 1);
  opacity: 0.7;
}
```

### 6.2 현재 버튼

```css
.bs-toolbar__btn {
  width: 32px; height: 32px;
  border-radius: 4px;
  transition: background-color 0.15s, color 0.15s;
}
.bs-toolbar__btn:hover {
  background-color: var(--bs-bg-hover);
}
```

### 6.3 복원 방침

원본의 `::after` 애니메이션 호버는 독특한 시각적 효과. **pseudo-element 기반 호버 시스템 도입**:

- 기본 버튼 (`.bs-btn`): `::after`로 scale 애니메이션
- 토글 버튼 활성 상태: `inset box-shadow`로 표시
- 활성 색상: `#00b464` (원본의 status__active)
- 트랜지션: `transform 0.2s ease-in-out`

---

## 7. 입력 컨트롤 복원

### 7.1 텍스트 입력

| 항목 | 원본 | 현재 | 복원 |
|------|------|------|------|
| 높이 | `2.4em` | 다양 (26-32px) | **2.4em** (약 31px at 13px base) |
| 패딩 | `0 0.5em` | `0 8px` | `0 0.5em` |
| 보더 반경 | `0.3em` | `4px` | `0.3em` |
| 포커스 | `box-shadow: inset 0 0 0 1px (theme)` | `box-shadow: 0 1px 0 accent` | 원본 포커스 링 |

### 7.2 레인지 슬라이더

원본은 커스텀 스타일링이 상세함:

```scss
/* 원본 */
input[type="range"] {
  height: 6px;
}
::-webkit-slider-runnable-track {
  height: 100%;
  border-radius: 20px;
  background-color: var(--color-g80);  /* 진한 회색 트랙 */
}
::-webkit-slider-thumb {
  width: 18px; height: 18px;
  margin-top: -6px;
  border-radius: 50%;
  box-shadow: 0 0 0 1px var(--color-k20), 2px 2px 3px var(--color-k30);
  background-color: #fff;
}
```

현재는 `accent-color: var(--bs-accent)`만 적용. **원본의 커스텀 슬라이더 복원**.

### 7.3 체크박스/라디오

원본:
```scss
input[type="checkbox"], input[type="radio"] {
  width: 1.8em; height: 1.8em;
  font-size: 0.76em;
  background-color: var(--color-g30);
}
input[type="checkbox"] { border-radius: 0.25em; }
input[type="radio"] { border-radius: 50%; }
```

현재: 브라우저 기본. **원본 커스텀 스타일 복원**.

### 7.4 토글 스위치

| 항목 | 원본 | 현재 | 복원 |
|------|------|------|------|
| 크기 | 42x24px | 36x20px | **42x24px** |
| 활성 배경 | `#5ac832` | `var(--bs-accent)` | `#5ac832` |
| 썸 이동 | `translateX(18px)` | `left: 18px` | `translateX(18px)` (성능) |
| 트랜지션 | `transform 0.2s` | `left 0.2s` | `transform 0.2s` |

---

## 8. 그림자 시스템 복원

### 8.1 그림자 토큰

| 용도 | 원본 | 현재 | 복원 변수 |
|------|------|------|----------|
| 사이드바 외부 | `1px 0 0 0 ga30, 3px 0 15px k20` | `border-right: 1px solid` | `--bs-shadow-sidebar` |
| 탑바 하단 | `inset 0 -1px 0 0 ga40, 0 1px 7px k15` | `border-bottom: 1px solid` | `--bs-shadow-topbar` |
| 캔버스 페이지 | `8px 8px 15px k30` | `0 2px 20px rgba(0,0,0,0.3)` | `--bs-shadow-page` |
| 사이드바 내부 구분 | `inset -1px 0 0 0 ga40` | `border-right: 1px solid` | `--bs-shadow-divider` |
| 페이지 썸네일 보더 | `inset 0 0 10px k40, inset 0 0 0 1px k30` | `0 1px 4px rgba(0,0,0,0.2)` | 원본 값 |

원본은 `border` 대신 `box-shadow`를 구분선으로 사용 (서브픽셀 렌더링으로 더 부드러움). **이 패턴 복원**.

---

## 9. 폰트 시스템 복원

### 9.1 원본 커스텀 폰트

| 폰트명 | 실제 폰트 | 용도 |
|--------|----------|------|
| Bookooroo KR | IBM Plex Sans KR (400) + Noto KR (500) | UI 한글 텍스트 |
| Bookooroo KR Sub | Noto Sans KR (400) | 보조 한글 |
| Bookooroo EN | Roboto (400, 500) | UI 영문 텍스트 |
| Bookooroo Num | Bebas Neue (400) | 숫자 표시 |
| Bookooroo Code | JetBrains Mono (300) | 코드/좌표 표시 |
| Bookooroo Icon | Fontello 커스텀 | 아이콘 |

### 9.2 복원 방침

woff 파일을 번들하기 어려우므로 **Google Fonts 기반 근사치**:

```css
/* UI 텍스트 (한글) */
--bs-font-kr: 'IBM Plex Sans KR', 'Noto Sans KR', sans-serif;

/* UI 텍스트 (영문) */
--bs-font-en: 'Roboto', sans-serif;

/* 숫자 (포지션바 등) */
--bs-font-num: 'Bebas Neue', sans-serif;

/* 코드/좌표 */
--bs-font-code: 'JetBrains Mono', monospace;
```

현재 시스템 폰트 스택 → Google Fonts로 교체. `fonts.css`에 추가 import.

### 9.3 아이콘 폰트

원본 Fontello → 현재 Lucide React. **Lucide 유지** (1:1 복원 불가능하나 기능 커버리지 충분).

---

## 10. 페이지 썸네일 복원

### 10.1 원본

```scss
.li__editor--pagelist {
  width: 80px;
  margin: 0.7em 0;
}
.pagelist__cover {
  border-width: 0.4em;
  border-style: solid;
  border-image-slice: 1;
  box-shadow: inset 0 0 10px var(--color-k40), inset 0 0 0 1px var(--color-k30);
}
```

- 썸네일 폭: 80px
- 테두리: `border-image`로 그라디언트 가능 (테마 악센트)
- 내부 그림자: `inset 0 0 10px` (깊이감)
- 스케일: `scale(0.1041)` (768px → ~80px)

### 10.2 현재

- 썸네일: 전체 콘텐츠 영역(200px) 안에서 `scale(thumbScale)`
- 보더: `box-shadow: 0 0 0 2px accent` (활성 시)
- 번호: 좌하단 초록색

### 10.3 복원 변경

- 콘텐츠 영역 140px, 썸네일 80px 고정
- `border-image`로 테마 그라디언트 테두리
- 내부 `inset box-shadow` 추가
- 인포 아이콘 배지 (원본의 `pagelist__info-icons`)

---

## 11. 구현 순서

### Phase 1: 색상 + 그림자 복원 [Level A — CSS only]

1. `variables.css` — 다크/라이트 테마 색상값 원본 일치로 변경
2. `variables.css` — 불투명도 기반 유틸 변수 추가
3. `variables.css` — 그림자 토큰 추가
4. `editor.css` — `border` → `box-shadow` 구분선 패턴 전환 (원본은 border 대신 box-shadow로 구분선 표현)
5. `editor.css` — 캔버스 페이지 그림자 복원

### Phase 2: 레이아웃 치수 복원 [Level B — 구조적, TSX 변경 필요]

6. `variables.css` — 레이아웃 치수 변경 (사이드바 280+50, 페이지목록 140+50, 탑바 50)
7. `editor.css` — 사이드바 구조 변경 (콘텐츠+아이콘메뉴 분리)
8. `editor.css` — 사이드바 접기/펼치기 (`transform: translateX(-280px)`, 트랜지션 `0.5s` — 현재 `0.2s ease`)
9. `EditorLayout.tsx` — 레이아웃 컴포넌트 구조 변경 (Toolbar 통합, 3-column 구조)

### Phase 3: 핸들 + 선택 복원 [Level A — CSS 중심, 일부 마크업 조정]

10. `editor.css` — 선택 아웃라인 노랑 + 핸들 연두 원형 14px
11. `PanelWrapper.tsx` — 핸들 마크업 조정 (사각 → 원형, 크기 변경)
12. `editor.css` — 회전 핸들 26px 복원

### Phase 4: 입력 컨트롤 + 버튼 복원 [Level A — CSS only]

13. `editor.css` — 버튼 `::after` 호버 시스템
14. `editor.css` — 슬라이더 커스텀 스타일
15. `editor.css` — 토글 스위치 크기 복원 (42x24 → 원본)
16. `editor.css` — 체크박스/라디오 커스텀 스타일

### Phase 5: 폰트 + 스크롤바 + 페이지목록 [Level A — CSS only]

17. `fonts.css` — Google Fonts 추가 (IBM Plex Sans KR, Bebas Neue, JetBrains Mono)
18. `variables.css` — 폰트 변수 추가
19. `reset.css` — 스크롤바 스타일 복원 (8px, 회색 톤)
20. `editor.css` — 페이지 썸네일 80px + inset shadow + border-image

### Phase 6 (선택): 멀티 테마 지원 [Level B — TSX 변경 필요]

21. `variables.css` — poly-a~d 테마 색상 추가
22. `EditorLayout.tsx` — 테마 전환 UI

---

## 12. 영향 범위

### CSS 파일 변경

| 파일 | 변경 규모 |
|------|----------|
| `variables.css` | 대규모 — 색상, 치수, 그림자, 폰트 변수 전면 교체 |
| `editor.css` | 대규모 — 레이아웃 구조, 핸들, 버튼, 입력 컨트롤 |
| `reset.css` | 소규모 — 스크롤바, 기본 폰트 |
| `fonts.css` | 소규모 — Google Fonts import 추가 |

### TSX 컴포넌트 변경

| 파일 | 변경 내용 |
|------|----------|
| `EditorLayout.tsx` | 레이아웃 구조 변경 (Toolbar 제거, 사이드바 아이콘메뉴 통합) |
| `PanelWrapper.tsx` | 핸들 마크업 (원형, 크기) |
| `ToolbarStrip.tsx` | 사이드바 아이콘메뉴로 이동 |
| `PageListPanel.tsx` | 썸네일 크기/스타일 조정 |
| `SidebarTabs.tsx` | 사이드바 구조 변경 반영 |
| `PositionBar.tsx` | 탑바 높이 변경 반영 |

### 변경하지 않는 것

- 아이콘 라이브러리 (Lucide 유지)
- 상태 관리 (Zustand)
- 컴포넌트 로직/이벤트 핸들링
- 원본의 반응형 브레이크포인트 (데스크톱 에디터 전용이므로 불필요)
- 원본의 z-index 체계 (현재 체계와 호환)

---

## 13. 검증 기준

| ID | 검증 항목 | 기준 | 상태 |
|----|----------|------|------|
| V1 | 다크 테마 배경 | 원본과 동일한 어두운 톤 (#0d0d0d 기반) | **완료** |
| V2 | 사이드바 치수 | 330px 총폭 (280+50), 접기/펼치기 동작 | **완료** — 접기/펼치기 포함 |
| V3 | 탑바 높이 | 50px | **완료** |
| V4 | 선택 핸들 | 노랑 아웃라인, 연두 원형 14px 핸들 | **완료** |
| V5 | 캔버스 그림자 | 8px 8px 15px 방향성 그림자 | **완료** |
| V6 | 버튼 호버 | ::after scale 애니메이션 | **완료** |
| V7 | 슬라이더 | 커스텀 트랙+썸 (회색 트랙, 흰 원형 썸) | **완료** |
| V8 | 페이지 썸네일 | inset shadow + border-image 그라디언트 | **완료** |
| V9 | 스크롤바 | 8px, 회색 톤 | **완료** |
| V10 | UI 폰트 | IBM Plex Sans KR / Roboto 적용 | **완료** |
| V11 | 빌드 성공 | `npm run build` 에러 없음 | **완료** — `193.34 kB` |

---

## 14. 구현 결과

### 14.1 Level A 구현 (CSS-only, 2026-04-24)

| 파일 | 변경 내용 |
|------|----------|
| `styles/variables.css` | 전면 재작성 — 다크 테마 `#0d0d0d` 기반, 불투명도 스케일, 그림자 토큰, 폰트 변수, 핸들/선택 색상 변수 |
| `styles/editor.css` | 구분선 `border` → `box-shadow`, 캔버스 그림자, 핸들 원형 14px, 버튼 `::after` 호버, 슬라이더/토글/체크박스 커스텀 |
| `styles/reset.css` | 기본 폰트 `var(--bs-font-kr)`, 스크롤바 8px 회색 톤 |
| `styles/fonts.css` | Google Fonts 추가 (IBM Plex Sans KR, Bebas Neue, JetBrains Mono) |
| `components/Panel/PanelWrapper.tsx` | 핸들 클래스 통합 (`bs-handle--corner/edge` 제거) |

### 14.2 Level B 구현 (레이아웃 구조, 2026-04-24)

| 파일 | 변경 내용 |
|------|----------|
| `styles/variables.css` | 레이아웃 치수 변경 — `--bs-iconmenu-width: 50px`, `--bs-sidebar-width: 280px`, `--bs-pagelist-width: 140px`, `--bs-collabbar-width: 50px`, `--bs-topbar-height: 50px` |
| `styles/editor.css` | 3-column 레이아웃: `.bs-designer` (280+50), `.bs-pagelist-wrap` (50+140), `.bs-iconmenu__btn`, `.bs-collabbar__btn` 추가. `.bs-appnav`, `.bs-toolbar`, `.bs-minibar` 제거/교체 |
| `components/Editor/EditorLayout.tsx` | props 변경: `appNav/toolbar/minibar` → `iconMenu/collabBar`. 3-column 구조 (`bs-designer` + canvas + `bs-pagelist-wrap`) |
| `components/AppNav/AppNav.tsx` | `<nav>` 래퍼 제거, `bs-appnav__btn` → `bs-iconmenu__btn` |
| `components/Editor/BookStudioEditor.tsx` | 새 prop 구조 반영 (`iconMenu`, `collabBar`) |
| `dev/DevApp.tsx` | AppNav + ToolbarStrip을 `iconMenu`에 통합, minibar를 `collabBar`로 변경 |

### 14.3 나머지 구현 (2026-04-24)

| 파일 | 변경 내용 |
|------|----------|
| `stores/editorStore.ts` | `isDesignerCollapsed`, `accentTheme` 상태 + `toggleDesigner`, `setAccentTheme` 액션 추가 |
| `components/Editor/EditorLayout.tsx` | 접기/펼치기 버튼 (PanelLeft/PanelRight 아이콘), `bs-designer--collapsed` / `bs-pagelist-wrap--collapsed` 토글, `bs-poly-{a\|b\|c\|d}` 테마 클래스 |
| `styles/variables.css` | 4종 악센트 테마 CSS 변수 (`.bs-poly-a~d`: accent, gradient, border-image) |
| `styles/editor.css` | `.bs-designer--collapsed`, `.bs-pagelist-wrap--collapsed` (0.5s transition), 접기 버튼 스타일 (원형, inset box-shadow), 페이지 썸네일 `border-image` + `border-width: 0.4em` |
| `components/PageList/PageListPanel.tsx` | 자체 collapsed 분기 제거 (EditorLayout에서 처리) |

### 14.4 최종 빌드 결과

```
dist/index.js  193.34 kB │ gzip: 48.12 kB
```

### 14.5 전체 완료 상태

모든 Phase 구현 완료:

| Phase | 내용 | 상태 |
|-------|------|------|
| 1 | 색상 + 그림자 | **완료** |
| 2 | 레이아웃 구조 (3-column, 330+190) | **완료** |
| 3 | 핸들 + 선택 | **완료** |
| 4 | 입력 컨트롤 + 버튼 | **완료** |
| 5 | 폰트 + 스크롤바 | **완료** |
| 6 | 멀티 테마 (poly-a~d) | **완료** (변수 정의, UI 미제공 — `setAccentTheme` API로 전환 가능) |
| 추가 | 사이드바/페이지목록 접기/펼치기 | **완료** |
| 추가 | 페이지 썸네일 border-image 그라디언트 | **완료** |
