# 디바운스 자동 저장 설계서

> 작성일: 2026-04-25
> 대상: 프론트엔드 에디터 (`frontend/src/`)

---

## 1. 현황

| 항목 | 상태 |
|------|------|
| API 클라이언트 | Fetch 기반 REST (`api/restClient.ts`) |
| 저장 방식 | 생성/삭제만 API 호출, **수정은 store만 반영 (API 미저장)** |
| debounce/throttle | 없음 |
| WebSocket | `useCollaboration.ts` — 패널/페이지 변경 실시간 브로드캐스트 |
| Undo/Redo | Zustand 기반 히스토리 (메모리, 최대 50개) |
| 로컬 스토리지 백업 | 없음 |

**핵심 문제:** 패널 스타일/위치, 페이지 배경, 문서 텍스트 등의 수정사항이 API에 저장되지 않아 새로고침 시 유실된다.

---

## 2. 설계 원칙

1. **로컬 우선** — store 변경은 즉시 UI 반영, API 저장은 비동기
2. **변경 단위 최소화** — PATCH로 변경된 필드만 전송
3. **디바운스** — 연속 조작 중에는 API 호출을 지연하여 요청 최소화
4. **실패 복원** — API 저장 실패 시 재시도, 최종 실패 시 사용자 알림
5. **협업 연동** — WebSocket으로 브로드캐스트된 변경도 동일한 저장 경로 사용

---

## 3. 저장 전략

### 3.1 카테고리별 디바운스

| 카테고리 | 예시 | 디바운스 | 이유 |
|----------|------|---------|------|
| **구조 변경** | 페이지 추가/삭제/순서, 패널 추가/삭제 | 즉시 (0ms) | 되돌리기 어려운 변경 |
| **패널 스타일** | 위치, 크기, 색상, 폰트, 투명도 등 | 1,000ms | 드래그/슬라이더 조작 중 연속 발생 |
| **텍스트 입력** | Document 본문, 패널 텍스트, 헤드라인 | 2,000ms | 타이핑 중 빈번한 변경 |
| **페이지 속성** | 배경색, 배경 이미지, 투명도 | 1,000ms | 컬러피커 등 연속 조작 |
| **에디션 메타** | 제목, 설명 | 2,000ms | 텍스트 입력 |

### 3.2 디바운스 흐름

```
사용자 조작
  → store.updatePanel(id, changes)    // 즉시 UI 반영
  → saveManager.enqueue("panel", id)  // 디바운스 큐에 등록
  → [1,000ms 대기, 추가 변경 시 타이머 리셋]
  → API PATCH /panels/{id}/          // 변경된 필드만 전송
  → 성공 → saveStatus = "saved"
  → 실패 → 재시도 (최대 3회, 지수 백오프)
  → 최종 실패 → saveStatus = "error", 사용자 알림
```

---

## 4. 구현 계획

### 4.1 `useAutoSave` 훅

```
frontend/src/hooks/useAutoSave.ts
```

에디터 최상위(`BookStudioEditor.tsx`)에서 한 번 호출. store의 변경을 감지하여 API 저장을 관리한다.

**책임:**
- store 변경 구독 (Zustand `subscribe`)
- 카테고리별 디바운스 타이머 관리
- 변경된 필드 추적 (dirty tracking)
- API 호출 및 재시도
- 저장 상태 관리 (`idle` / `saving` / `saved` / `error`)

### 4.2 Dirty Tracking

store의 `updatePanel`, `updatePage` 등이 호출될 때 변경된 필드를 별도로 추적한다.

```typescript
// 예시 구조
dirtyMap: {
  panels: {
    "panel-id-1": { left: 100, top: 200 },      // 변경된 필드만
    "panel-id-2": { color: "#ff0000" },
  },
  pages: {
    "page-id-1": { background_color: "#000" },
  },
  edition: { title: "새 제목" },
}
```

디바운스 만료 시 해당 엔트리의 dirty 필드를 PATCH로 전송하고, 성공 시 엔트리 제거.

### 4.3 SaveManager

```
frontend/src/services/saveManager.ts
```

디바운스/재시도/상태 관리를 담당하는 순수 클래스.

```typescript
class SaveManager {
  enqueue(category: SaveCategory, entityId: string, changes: object): void
  flush(): Promise<void>          // 즉시 전송 (페이지 이탈 시)
  getStatus(): SaveStatus
  onStatusChange(cb: (status: SaveStatus) => void): void
}
```

### 4.4 UI 피드백

에디터 상태바(하단 또는 상단)에 저장 상태 표시:

| 상태 | 표시 |
|------|------|
| `idle` | 표시 없음 |
| `saving` | "저장 중..." |
| `saved` | "저장됨" (3초 후 fade) |
| `error` | "저장 실패 — 재시도" (클릭 시 수동 재시도) |

### 4.5 페이지 이탈 보호

저장되지 않은 변경이 있을 때 `beforeunload` 이벤트로 경고.

```typescript
window.addEventListener('beforeunload', (e) => {
  if (saveManager.hasPendingChanges()) {
    saveManager.flush()   // 동기적 전송 시도
    e.preventDefault()
  }
})
```

---

## 5. 기존 코드 변경 범위

| 파일 | 변경 내용 |
|------|-----------|
| `stores/editorStore.ts` | `updatePanel`, `updatePage` 호출 시 dirty 필드 기록 |
| `components/Editor/BookStudioEditor.tsx` | `useAutoSave()` 훅 연결 |
| `api/restClient.ts` | 변경 없음 (기존 `panels.update`, `pages.update` 사용) |
| `hooks/useCollaboration.ts` | WebSocket 수신 변경은 dirty 마킹 제외 (원격 변경이므로) |

### 신규 파일

| 파일 | 역할 |
|------|------|
| `hooks/useAutoSave.ts` | 자동 저장 훅 |
| `services/saveManager.ts` | 디바운스/재시도/상태 관리 |
| `components/Editor/SaveStatus.tsx` | 저장 상태 UI 컴포넌트 |

---

## 6. 엣지 케이스

### 6.1 빈 북 생성 방지

북을 새로 생성한 직후, 사용자가 콘텐츠를 추가하지 않고 이탈하면 빈 북이 대량으로 쌓일 수 있다.

**대응:** 새 북은 사용자가 최초 콘텐츠 변경(빈 페이지 추가 포함)을 수행하기 전까지 API에 저장하지 않는다.

- 북 생성 시 `isNewUnsaved: true` 플래그를 store에 설정
- 첫 번째 구조 변경(페이지 추가/삭제, 패널 추가 등) 또는 콘텐츠 수정 발생 시 플래그 해제 → 이때 비로소 CREATE API 호출
- 플래그가 `true`인 동안 `SaveManager`는 해당 북의 enqueue를 무시
- 콘텐츠 변경 없이 페이지를 이탈하면 store에서 해당 북을 제거 (API 호출 없음)

### 6.2 빠른 페이지 전환

사용자가 패널을 수정 후 즉시 다른 페이지로 이동할 때, 디바운스 대기 중인 변경이 유실될 수 있다.

**대응:** 페이지 전환 시 `flush()` 호출하여 대기 중인 변경을 즉시 전송.

### 6.3 협업 충돌

두 사용자가 같은 패널을 동시에 수정할 때.

**대응:** Last-write-wins. 백엔드의 `auto_now=True`로 최신 수정 시간이 자동 기록된다. 향후 필요 시 OT(Operational Transformation) 도입 가능.

### 6.4 오프라인

네트워크 끊김 시 API 호출 실패.

**대응:** 재시도 큐에 보관, 네트워크 복구 시 자동 재시도. `navigator.onLine` 이벤트 감지.

### 6.5 Undo/Redo와의 상호작용

Undo 시 이전 상태가 store에 복원되면, 해당 변경도 dirty로 마킹되어 API에 저장된다. Undo 자체가 하나의 "수정"으로 취급된다.

---

## 7. 구현 순서

| 단계 | 작업 | 의존성 |
|------|------|--------|
| 1 | `SaveManager` 클래스 구현 | 없음 |
| 2 | `useAutoSave` 훅 구현 | SaveManager |
| 3 | `editorStore`에 dirty tracking 추가 | 없음 |
| 4 | `BookStudioEditor`에 훅 연결 | 1, 2, 3 |
| 5 | `SaveStatus` UI 컴포넌트 | 4 |
| 6 | 페이지 이탈 보호 (`beforeunload`) | 4 |
| 7 | 협업 훅 연동 (원격 변경 dirty 제외) | 4 |
