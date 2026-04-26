# Phase 3 상세 설계서: 프론트엔드 AI 세션

> 상위 문서: [ai-integration-proposal.md](ai-integration-proposal.md)
> 선행 Phase: [ai-phase2-pipeline.md](ai-phase2-pipeline.md)

## 1. 목표

에디터 좌측 사이드바에 **AI 세션 패널**을 추가하여, 사용자가 프롬프트를 입력하면 기획서 검토 → 승인 → 실시간 페이지 생성까지의 전 과정을 UI에서 수행할 수 있게 한다.

**Phase 3 결과물:**
- `aiStore` (Zustand) — AI 세션 상태 관리
- `AIChatPanel` 컴포넌트 — 사이드바 AI 탭
- `useAISession` 훅 — SSE 클라이언트 + 에디터 스토어 연동
- restClient AI 확장 — 세션 CRUD + 스트림
- 에디터 캔버스 실시간 반영 — 생성된 페이지/패널 즉시 표시
- CSS 스타일

---

## 2. 상태 관리: aiStore

### 2.1 상태 정의

```typescript
// frontend/src/stores/aiStore.ts

import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

export type AIPhase =
  | 'idle'          // 초기 상태
  | 'planning'      // 기획서 생성 중
  | 'reviewing'     // 기획서 검토 대기
  | 'generating'    // 콘텐츠 + 디자인 생성 중
  | 'complete'      // 완료
  | 'error'         // 오류

export interface AIPlan {
  title: string
  total_pages: number
  tone: string
  target_audience: string
  color_mood: string
  pages: AIPagePlan[]
}

export interface AIPagePlan {
  index: number
  role: string
  purpose: string
  key_points: string[]
  suggested_pattern_category: string
  needs_image: boolean
}

export interface AIPageProgress {
  index: number
  role: string
  status: 'pending' | 'generating' | 'complete' | 'error'
  pageId?: string           // 생성된 Page.id
  error?: string
}

export interface AIMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

export interface AIState {
  // ── 세션 ──
  sessionId: string | null
  phase: AIPhase
  errorMessage: string | null

  // ── 기획서 ──
  plan: AIPlan | null

  // ── 진행률 ──
  progress: AIPageProgress[]
  generatingPageIndex: number | null  // 현재 생성 중인 페이지

  // ── 대화 ──
  messages: AIMessage[]

  // ── UI ──
  isOpen: boolean                     // AI 패널 열림 여부

  // ── 액션 ──
  setSession: (sessionId: string) => void
  setPhase: (phase: AIPhase) => void
  setPlan: (plan: AIPlan) => void
  setProgress: (progress: AIPageProgress[]) => void
  updatePageProgress: (index: number, update: Partial<AIPageProgress>) => void
  setGeneratingPage: (index: number | null) => void
  addMessage: (message: Omit<AIMessage, 'id' | 'timestamp'>) => void
  setError: (message: string) => void
  setOpen: (open: boolean) => void
  reset: () => void
}

const initialState = {
  sessionId: null,
  phase: 'idle' as AIPhase,
  errorMessage: null,
  plan: null,
  progress: [],
  generatingPageIndex: null,
  messages: [],
  isOpen: false,
}

export const useAIStore = create<AIState>()(
  immer((set) => ({
    ...initialState,

    setSession: (sessionId) => set((s) => { s.sessionId = sessionId }),
    setPhase: (phase) => set((s) => { s.phase = phase; s.errorMessage = null }),
    setPlan: (plan) => set((s) => {
      s.plan = plan
      s.progress = plan.pages.map((p) => ({
        index: p.index,
        role: p.role,
        status: 'pending',
      }))
    }),
    setProgress: (progress) => set((s) => { s.progress = progress }),
    updatePageProgress: (index, update) => set((s) => {
      const item = s.progress.find((p) => p.index === index)
      if (item) Object.assign(item, update)
    }),
    setGeneratingPage: (index) => set((s) => { s.generatingPageIndex = index }),
    addMessage: (msg) => set((s) => {
      s.messages.push({
        ...msg,
        id: crypto.randomUUID(),
        timestamp: Date.now(),
      })
    }),
    setError: (message) => set((s) => {
      s.phase = 'error'
      s.errorMessage = message
    }),
    setOpen: (open) => set((s) => { s.isOpen = open }),
    reset: () => set(() => ({ ...initialState })),
  }))
)
```

### 2.2 상태 전이 다이어그램

```
idle ──[사용자: 프롬프트 입력]──► planning
  │                                  │
  │                          [SSE: planning_complete]
  │                                  ▼
  │                              reviewing
  │                                  │
  │              ┌───[승인]──────────┤
  │              │           [수정 요청]──► planning
  │              ▼
  │          generating
  │              │
  │     [SSE: page_complete x N]
  │              │
  │     [SSE: generation_complete]
  │              ▼
  │           complete
  │
  └───────── [리셋] ◄──── error ◄── [any stage failure]
```

---

## 3. SSE 클라이언트: useAISession 훅

```typescript
// frontend/src/hooks/useAISession.ts

import { useCallback, useRef, useEffect } from 'react'
import { useAIStore } from '../stores/aiStore'
import { useEditorStore } from '../stores/editorStore'
import { withRemoteUpdate } from '../stores/editorStore'
import type { BookStudioClient } from '../api/restClient'
import type { Page } from '../types/page'
import type { Panel } from '../types/panel'

interface UseAISessionOptions {
  client: BookStudioClient
  enabled?: boolean
}

export function useAISession({ client, enabled = true }: UseAISessionOptions) {
  const eventSourceRef = useRef<EventSource | null>(null)
  const {
    sessionId, phase,
    setSession, setPhase, setPlan, updatePageProgress,
    setGeneratingPage, addMessage, setError, reset,
  } = useAIStore()
  const { addPage, setPanels, setActivePage } = useEditorStore()

  // ── SSE 연결 ──
  const connectStream = useCallback((sid: string) => {
    // 기존 연결 정리
    eventSourceRef.current?.close()

    // restClient에 getBaseURL() 추가 필요 (섹션 4 참조)
    const baseURL = client.getBaseURL()
    const url = `${baseURL}/ai/sessions/${sid}/stream/`
    const es = new EventSource(url, { withCredentials: true })
    eventSourceRef.current = es

    // 초기 상태
    es.addEventListener('session_status', (e) => {
      const data = JSON.parse(e.data)
      if (data.plan) {
        setPlan(data.plan)
        // 이미 완료된 페이지 반영
        if (data.completed_pages > 0) {
          for (let i = 0; i < data.completed_pages; i++) {
            updatePageProgress(i, { status: 'complete' })
          }
        }
      }
      if (data.status === 'REVIEW') setPhase('reviewing')
      else if (data.status === 'GENERATING') setPhase('generating')
      else if (data.status === 'COMPLETE') setPhase('complete')
      else if (data.status === 'FAILED') setError(data.error_message || 'Unknown error')
    })

    // 기획서 완료
    es.addEventListener('planning_complete', (e) => {
      const data = JSON.parse(e.data)
      setPlan(data.plan)
      setPhase('reviewing')
      addMessage({ role: 'assistant', content: '기획서를 작성했습니다. 검토해주세요.' })
    })

    // 페이지 생성 시작
    es.addEventListener('page_start', (e) => {
      const data = JSON.parse(e.data)
      setGeneratingPage(data.page_index)
      updatePageProgress(data.page_index, { status: 'generating' })
    })

    // 페이지 생성 완료
    es.addEventListener('page_complete', (e) => {
      const data = JSON.parse(e.data)
      const page: Page = data.page
      const panels: Panel[] = data.panels

      // 에디터 스토어에 반영 (dirty 이벤트 억제)
      withRemoteUpdate(() => {
        addPage(page)
        setPanels(page.id, panels)
      })

      updatePageProgress(data.page_index, {
        status: 'complete',
        pageId: page.id,
      })

      // 첫 페이지 완료 시 자동 이동
      if (data.page_index === 0) {
        setActivePage(page.id)
      }
    })

    // 페이지 생성 오류 (개별)
    es.addEventListener('page_error', (e) => {
      const data = JSON.parse(e.data)
      updatePageProgress(data.page_index, {
        status: 'error',
        error: data.error,
      })
    })

    // 전체 생성 완료
    es.addEventListener('generation_complete', (e) => {
      setPhase('complete')
      setGeneratingPage(null)
      addMessage({
        role: 'assistant',
        content: '모든 페이지가 생성되었습니다. 자유롭게 편집하세요.',
      })
    })

    // 에러
    es.addEventListener('error', (e) => {
      const data = e.data ? JSON.parse(e.data) : {}
      setError(data.message || 'Connection error')
    })

    // SSE done
    es.addEventListener('done', () => {
      es.close()
    })

    // 연결 오류 (재연결)
    es.onerror = () => {
      // EventSource는 자동 재연결. 3번 실패 시 포기.
      // 브라우저 기본 동작에 위임.
    }
  }, [client, setPlan, setPhase, updatePageProgress, setGeneratingPage, addMessage, setError, addPage, setPanels, setActivePage])

  // ── 세션 시작 ──
  const startSession = useCallback(async (
    bookId: string,
    editionId: string,
    prompt: string,
    options?: Record<string, unknown>,
  ) => {
    try {
      reset()
      setPhase('planning')
      addMessage({ role: 'user', content: prompt })

      const session = await client.ai.createSession({
        book: bookId,
        edition: editionId,
        prompt,
        options: options || {},
      })

      setSession(session.id)
      connectStream(session.id)
    } catch (err: any) {
      setError(err.message || 'Failed to start session')
    }
  }, [client, reset, setPhase, addMessage, setSession, connectStream, setError])

  // ── 기획서 승인 ──
  const approvePlan = useCallback(async (editedPlan?: any) => {
    if (!sessionId) return
    try {
      setPhase('generating')
      addMessage({ role: 'user', content: '이대로 진행합니다.' })

      await client.ai.approveSession(sessionId, { plan: editedPlan })

      // SSE가 이미 연결되어 있으면 이벤트 수신 계속
      // 끊겨 있으면 재연결
      if (!eventSourceRef.current || eventSourceRef.current.readyState === EventSource.CLOSED) {
        connectStream(sessionId)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to approve plan')
    }
  }, [sessionId, client, setPhase, addMessage, connectStream, setError])

  // ── 세션 취소 ──
  const cancelSession = useCallback(async () => {
    if (!sessionId) return
    try {
      await client.ai.cancelSession(sessionId)
      eventSourceRef.current?.close()
      reset()
    } catch (err: any) {
      setError(err.message)
    }
  }, [sessionId, client, reset, setError])

  // ── Cleanup ──
  useEffect(() => {
    return () => {
      eventSourceRef.current?.close()
    }
  }, [])

  return {
    startSession,
    approvePlan,
    cancelSession,
    isConnected: eventSourceRef.current?.readyState === EventSource.OPEN,
  }
}
```

---

## 4. restClient AI 확장

```typescript
// frontend/src/api/restClient.ts 에 추가

// ─── Base URL 접근자 (SSE EventSource 구성에 필요) ───
getBaseURL: () => baseURL,

// ─── AI ─── (restClient 반환 객체에 추가)
ai: {
  createSession: (data: {
    book: string
    edition: string
    prompt: string
    options?: Record<string, unknown>
    pattern_set?: string
  }) => request<AISessionResponse>('/ai/sessions/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getSession: (id: string) =>
    request<AISessionResponse>(`/ai/sessions/${id}/`),

  approveSession: (id: string, data?: { plan?: any; pattern_set_id?: string }) =>
    request<AISessionResponse>(`/ai/sessions/${id}/approve/`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    }),

  cancelSession: (id: string) =>
    request<AISessionResponse>(`/ai/sessions/${id}/cancel/`, {
      method: 'POST',
    }),

  // 디자인 패턴 (Phase 1 API)
  listPatterns: (params?: { category?: string; target_layout?: string }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString()
    return request<DesignPatternListItem[]>(`/ai/design-patterns/?${qs}`)
  },

  listPatternSets: () =>
    request<DesignPatternSet[]>('/ai/design-pattern-sets/'),
},
```

### 4.1 API 응답 타입

```typescript
// frontend/src/types/ai.ts

export interface AISessionResponse {
  id: string
  book: string
  edition: string
  prompt: string
  options: Record<string, unknown>
  status: 'PLANNING' | 'REVIEW' | 'APPROVED' | 'GENERATING' | 'COMPLETE' | 'FAILED' | 'CANCELLED'
  error_message: string
  plan: AIPlan | null
  pattern_set: string | null
  total_pages: number
  completed_pages: number
  model_used: string
  total_input_tokens: number
  total_output_tokens: number
  created_at: string
  updated_at: string
  completed_at: string | null
}
```

---

## 5. 컴포넌트 구조

### 5.1 컴포넌트 트리

```
SidebarTabs
 └─ AIChatPanel (sidebarContext === 'ai' 또는 isOpen)
     ├─ AIPromptInput          (idle 상태)
     ├─ AIPlanReview           (reviewing 상태)
     ├─ AIGenerationProgress   (generating 상태)
     ├─ AICompleteMessage      (complete 상태)
     └─ AIErrorMessage         (error 상태)
```

### 5.2 AIChatPanel — 메인 AI 패널

```tsx
// frontend/src/components/AI/AIChatPanel.tsx

import React from 'react'
import { useAIStore } from '../../stores/aiStore'
import { useAISession } from '../../hooks/useAISession'
import { useEditorStore } from '../../stores/editorStore'
import { AIPromptInput } from './AIPromptInput'
import { AIPlanReview } from './AIPlanReview'
import { AIGenerationProgress } from './AIGenerationProgress'
import type { BookStudioClient } from '../../api/restClient'

interface AIChatPanelProps {
  client: BookStudioClient
}

export function AIChatPanel({ client }: AIChatPanelProps) {
  const { phase, messages, plan, progress, errorMessage } = useAIStore()
  const { book, edition } = useEditorStore()
  const { startSession, approvePlan, cancelSession } = useAISession({ client })

  const handleSubmit = (prompt: string, options?: Record<string, unknown>) => {
    if (!book || !edition) return
    startSession(book.id, edition.id, prompt, options)
  }

  return (
    <div className="bs-ai">
      {/* 대화 히스토리 */}
      <div className="bs-ai__messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`bs-ai__message bs-ai__message--${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      {/* Phase별 UI */}
      <div className="bs-ai__content">
        {phase === 'idle' && (
          <AIPromptInput onSubmit={handleSubmit} />
        )}

        {phase === 'planning' && (
          <div className="bs-ai__loading">
            <div className="bs-ai__spinner" />
            <span>기획서를 작성하고 있습니다...</span>
          </div>
        )}

        {phase === 'reviewing' && plan && (
          <AIPlanReview
            plan={plan}
            onApprove={(editedPlan) => approvePlan(editedPlan)}
            onRegenerate={() => {
              // 기획서 재생성: 수정 요청 메시지로 새 세션
              if (!book || !edition) return
              const lastUserMsg = messages.findLast((m) => m.role === 'user')
              startSession(book.id, edition.id, lastUserMsg?.content || '', {
                regenerate: true,
              })
            }}
            onCancel={cancelSession}
          />
        )}

        {phase === 'generating' && (
          <AIGenerationProgress
            progress={progress}
            onCancel={cancelSession}
            onPageClick={(pageId) => {
              if (pageId) useEditorStore.getState().setActivePage(pageId)
            }}
          />
        )}

        {phase === 'complete' && (
          <div className="bs-ai__complete">
            <div className="bs-ai__complete-icon">&#10003;</div>
            <p>생성 완료! 자유롭게 편집하세요.</p>
            <button
              className="bs-ai__btn bs-ai__btn--secondary"
              onClick={() => useAIStore.getState().reset()}
            >
              새로 만들기
            </button>
          </div>
        )}

        {phase === 'error' && (
          <div className="bs-ai__error">
            <p>{errorMessage}</p>
            <button
              className="bs-ai__btn bs-ai__btn--secondary"
              onClick={() => useAIStore.getState().reset()}
            >
              다시 시도
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
```

### 5.3 AIPromptInput — 프롬프트 입력

```tsx
// frontend/src/components/AI/AIPromptInput.tsx

import React, { useState } from 'react'

interface AIPromptInputProps {
  onSubmit: (prompt: string, options?: Record<string, unknown>) => void
}

export function AIPromptInput({ onSubmit }: AIPromptInputProps) {
  const [prompt, setPrompt] = useState('')
  const [showOptions, setShowOptions] = useState(false)
  const [pageCount, setPageCount] = useState<number | ''>('')
  const [tone, setTone] = useState('')

  const handleSubmit = () => {
    if (!prompt.trim()) return
    const options: Record<string, unknown> = {}
    if (pageCount) options.page_count = pageCount
    if (tone) options.tone = tone
    onSubmit(prompt.trim(), options)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="bs-ai__prompt">
      <div className="bs-ai__prompt-header">
        무엇을 만들어 드릴까요?
      </div>

      <textarea
        className="bs-ai__prompt-input"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="예: 친환경 에너지 사업 제안서, 10페이지, 투자자 대상"
        rows={3}
      />

      {/* 옵션 토글 */}
      <button
        className="bs-ai__options-toggle"
        onClick={() => setShowOptions(!showOptions)}
      >
        {showOptions ? '옵션 숨기기' : '옵션 설정'}
      </button>

      {showOptions && (
        <div className="bs-ai__options">
          <label className="bs-ai__option-label">
            <span>페이지 수</span>
            <input
              type="number"
              min={3}
              max={30}
              value={pageCount}
              onChange={(e) => setPageCount(e.target.value ? Number(e.target.value) : '')}
              placeholder="자동"
              className="bs-ai__option-input"
            />
          </label>
          <label className="bs-ai__option-label">
            <span>톤</span>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="bs-ai__option-select"
            >
              <option value="">자동</option>
              <option value="professional">전문적</option>
              <option value="casual">캐주얼</option>
              <option value="creative">창의적</option>
              <option value="academic">학술적</option>
            </select>
          </label>
        </div>
      )}

      <button
        className="bs-ai__btn bs-ai__btn--primary"
        onClick={handleSubmit}
        disabled={!prompt.trim()}
      >
        생성 시작
      </button>
    </div>
  )
}
```

### 5.4 AIPlanReview — 기획서 검토

```tsx
// frontend/src/components/AI/AIPlanReview.tsx

import React, { useState } from 'react'
import type { AIPlan } from '../../stores/aiStore'

interface AIPlanReviewProps {
  plan: AIPlan
  onApprove: (editedPlan?: AIPlan) => void
  onRegenerate: () => void
  onCancel: () => void
}

export function AIPlanReview({ plan, onApprove, onRegenerate, onCancel }: AIPlanReviewProps) {
  const [editedPlan, setEditedPlan] = useState<AIPlan>(plan)
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div className="bs-ai__plan">
      <div className="bs-ai__plan-header">
        <h4>{editedPlan.title}</h4>
        <span className="bs-ai__plan-meta">
          {editedPlan.total_pages}페이지 / {editedPlan.tone}
        </span>
      </div>

      <div className="bs-ai__plan-pages">
        {editedPlan.pages.map((page, i) => (
          <div key={i} className="bs-ai__plan-page">
            <span className="bs-ai__plan-page-num">{i + 1}</span>
            <div className="bs-ai__plan-page-info">
              <span className="bs-ai__plan-page-role">{page.role}</span>
              <span className="bs-ai__plan-page-purpose">{page.purpose}</span>
              {isEditing && (
                <input
                  className="bs-ai__plan-page-edit"
                  value={page.purpose}
                  onChange={(e) => {
                    const updated = { ...editedPlan }
                    updated.pages = [...updated.pages]
                    updated.pages[i] = { ...updated.pages[i], purpose: e.target.value }
                    setEditedPlan(updated)
                  }}
                />
              )}
            </div>
            {page.needs_image && (
              <span className="bs-ai__plan-page-badge">IMG</span>
            )}
          </div>
        ))}
      </div>

      <div className="bs-ai__plan-actions">
        <button
          className="bs-ai__btn bs-ai__btn--text"
          onClick={() => setIsEditing(!isEditing)}
        >
          {isEditing ? '편집 완료' : '수정'}
        </button>
        <button
          className="bs-ai__btn bs-ai__btn--text"
          onClick={onRegenerate}
        >
          다시 만들기
        </button>
        <button
          className="bs-ai__btn bs-ai__btn--text"
          onClick={onCancel}
        >
          취소
        </button>
        <button
          className="bs-ai__btn bs-ai__btn--primary"
          onClick={() => onApprove(isEditing ? editedPlan : undefined)}
        >
          이대로 진행
        </button>
      </div>
    </div>
  )
}
```

### 5.5 AIGenerationProgress — 생성 진행률

```tsx
// frontend/src/components/AI/AIGenerationProgress.tsx

import React from 'react'
import type { AIPageProgress } from '../../stores/aiStore'

interface AIGenerationProgressProps {
  progress: AIPageProgress[]
  onCancel: () => void
  onPageClick: (pageId?: string) => void
}

export function AIGenerationProgress({ progress, onCancel, onPageClick }: AIGenerationProgressProps) {
  const completedCount = progress.filter((p) => p.status === 'complete').length
  const totalCount = progress.length
  const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

  return (
    <div className="bs-ai__progress">
      {/* 프로그레스 바 */}
      <div className="bs-ai__progress-bar">
        <div
          className="bs-ai__progress-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="bs-ai__progress-label">
        {completedCount}/{totalCount} 페이지 완료
      </div>

      {/* 페이지별 상태 */}
      <div className="bs-ai__progress-list">
        {progress.map((p) => (
          <button
            key={p.index}
            className={`bs-ai__progress-item bs-ai__progress-item--${p.status}`}
            onClick={() => p.pageId && onPageClick(p.pageId)}
            disabled={p.status === 'pending'}
          >
            <span className="bs-ai__progress-icon">
              {p.status === 'complete' && '\u2713'}
              {p.status === 'generating' && '\u25CF'}
              {p.status === 'pending' && '\u25CB'}
              {p.status === 'error' && '\u2717'}
            </span>
            <span className="bs-ai__progress-text">
              {p.index + 1}. {p.role}
            </span>
          </button>
        ))}
      </div>

      <button
        className="bs-ai__btn bs-ai__btn--text bs-ai__btn--danger"
        onClick={onCancel}
      >
        생성 취소
      </button>
    </div>
  )
}
```

---

## 6. 사이드바 통합

### 6.1 editorStore 확장

```typescript
// activeSidebarTab 타입 확장
activeSidebarTab: 'file' | 'input' | 'options' | 'share' | 'ai'
```

기존 `activeSidebarTab` 타입에 `'ai'`를 추가하지 **않는다**. 대신 `aiStore.isOpen`으로 독립적으로 관리하여 기존 사이드바 동작에 영향을 주지 않는다.

### 6.2 SidebarTabs 수정

```tsx
// SidebarTabs.tsx 변경사항

import { Sparkles } from 'lucide-react'  // AI 아이콘
import { useAIStore } from '../../stores/aiStore'
import { AIChatPanel } from '../AI/AIChatPanel'

export function SidebarTabs(props: SidebarTabsProps) {
  const { isOpen: isAIOpen } = useAIStore()
  // ... 기존 코드

  return (
    <>
      {/* ── Title ── */}
      <div className="bs-sidebar__header">
        {/* 기존 제목 input */}
      </div>

      {/* ── Menu bar ── */}
      <div className="bs-sidebar__menubox" ref={menuRef}>
        {/* 기존 4개 버튼 */}
        <button className="bs-sidebar__menu-btn" onClick={() => handleMenuClick('file')}>...</button>
        <button className="bs-sidebar__menu-btn" onClick={() => handleMenuClick('insert')}>...</button>
        <button className="bs-sidebar__menu-btn" onClick={() => handleMenuClick('options')}>...</button>
        <button className="bs-sidebar__menu-btn" onClick={() => handleMenuClick('share')}>...</button>

        {/* AI 버튼 (신규) */}
        <button
          className={`bs-sidebar__menu-btn${isAIOpen ? ' bs-sidebar__menu-btn--active' : ''}`}
          onClick={() => {
            useAIStore.getState().setOpen(!isAIOpen)
            setOpenMenu(null)
            setShowOptions(false)
          }}
        >
          <Sparkles size={15} strokeWidth={1.5} />
          <span>AI</span>
        </button>

        {/* 기존 드롭다운 메뉴들 */}
      </div>

      {/* ── Main content area ── */}
      <div className="bs-sidebar__content">
        {/* AI 패널 (최상위 우선) */}
        {isAIOpen ? (
          <AIChatPanel client={props.client} />
        ) : (
          <>
            {/* 기존 Options/BookInfo/Context banks */}
          </>
        )}
      </div>
    </>
  )
}
```

### 6.3 SidebarTabs Props 확장

```tsx
interface SidebarTabsProps {
  client: BookStudioClient  // 신규: AI API 호출용
  onNewBook?: () => void
  onOpenLibrary?: () => void
  onOpenShared?: () => void
  onPublish?: () => void
  onClone?: () => void
  onDelete?: () => void
}
```

`BookStudioEditor`에서 `SidebarTabs`에 `client`를 전달하도록 수정.

---

## 7. 에디터 캔버스 연동

### 7.1 생성 중 잠금

AI가 페이지를 생성하는 동안 **현재 생성 중인 페이지**만 편집 비활성화.

```tsx
// EditorCanvas.tsx 에서
import { useAIStore } from '../../stores/aiStore'

export function EditorCanvas() {
  const { phase, generatingPageIndex, progress } = useAIStore()
  const { activePageId } = useEditorStore()

  // 현재 활성 페이지가 생성 중인지 확인
  const isCurrentPageGenerating = phase === 'generating'
    && generatingPageIndex !== null
    && progress.find(p => p.index === generatingPageIndex)?.pageId === activePageId

  return (
    <div className={`bs-canvas ${isCurrentPageGenerating ? 'bs-canvas--ai-generating' : ''}`}>
      {/* 기존 캔버스 렌더링 */}
      {isCurrentPageGenerating && (
        <div className="bs-canvas__ai-overlay">
          <div className="bs-ai__spinner" />
          <span>AI가 이 페이지를 만들고 있습니다...</span>
        </div>
      )}
    </div>
  )
}
```

### 7.2 페이지 목록 실시간 반영

`useAISession` 훅의 `page_complete` 핸들러에서 `withRemoteUpdate(() => addPage(page))`를 호출하므로, `PageListPanel`은 별도 수정 없이 자동으로 새 페이지를 표시한다.

### 7.3 생성 완료 페이지 자동 이동

`page_complete` 이벤트에서 첫 페이지 생성 완료 시 `setActivePage(page.id)`를 호출한다. 이후 사용자가 완료된 페이지를 클릭하면 일반적으로 이동.

---

## 8. CSS 스타일

```css
/* frontend/src/styles/ai.css */

/* ── AI 패널 컨테이너 ── */
.bs-ai {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.bs-ai__messages {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bs-ai__message {
  font-size: 0.8rem;
  line-height: 1.4;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  max-width: 90%;
}

.bs-ai__message--user {
  align-self: flex-end;
  background: var(--bs-g20);
  color: var(--bs-w60);
}

.bs-ai__message--assistant {
  align-self: flex-start;
  background: var(--bs-k20);
  color: var(--bs-w60);
}

.bs-ai__content {
  padding: 0.75rem;
}

/* ── 프롬프트 입력 ── */
.bs-ai__prompt-header {
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: var(--bs-w60);
}

.bs-ai__prompt-input {
  width: 100%;
  min-height: 4rem;
  background: var(--bs-k20);
  border: 1px solid var(--bs-g30);
  border-radius: 0.4rem;
  color: inherit;
  font-size: 0.8rem;
  padding: 0.5rem;
  resize: vertical;
  font-family: var(--bs-font-kr);
}

.bs-ai__prompt-input:focus {
  outline: none;
  border-color: var(--bs-g50);
}

/* ── 옵션 ── */
.bs-ai__options-toggle {
  background: none;
  border: none;
  color: var(--bs-g80);
  font-size: 0.75rem;
  cursor: pointer;
  padding: 0.25rem 0;
  text-decoration: underline;
}

.bs-ai__options {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.5rem 0;
}

.bs-ai__option-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--bs-g80);
}

.bs-ai__option-input,
.bs-ai__option-select {
  width: 6rem;
  background: var(--bs-k20);
  border: 1px solid var(--bs-g30);
  border-radius: 0.25rem;
  color: inherit;
  font-size: 0.75rem;
  padding: 0.2rem 0.4rem;
}

/* ── 버튼 ── */
.bs-ai__btn {
  padding: 0.4rem 0.75rem;
  border-radius: 0.3rem;
  font-size: 0.8rem;
  cursor: pointer;
  border: none;
  transition: background 0.15s;
}

.bs-ai__btn--primary {
  background: #e94560;
  color: #fff;
  width: 100%;
  margin-top: 0.5rem;
}

.bs-ai__btn--primary:hover { background: #d63a55; }
.bs-ai__btn--primary:disabled { opacity: 0.5; cursor: not-allowed; }

.bs-ai__btn--secondary {
  background: var(--bs-g20);
  color: var(--bs-w60);
}

.bs-ai__btn--text {
  background: none;
  color: var(--bs-g80);
}

.bs-ai__btn--danger { color: #e94560; }

/* ── 기획서 검토 ── */
.bs-ai__plan {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bs-ai__plan-header h4 {
  font-size: 0.9rem;
  margin: 0;
  color: var(--bs-w60);
}

.bs-ai__plan-meta {
  font-size: 0.7rem;
  color: var(--bs-g80);
}

.bs-ai__plan-pages {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 20rem;
  overflow-y: auto;
}

.bs-ai__plan-page {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.5rem;
  border-radius: 0.25rem;
  background: var(--bs-k15);
  font-size: 0.75rem;
}

.bs-ai__plan-page-num {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--bs-g20);
  font-size: 0.65rem;
}

.bs-ai__plan-page-info {
  flex: 1;
  overflow: hidden;
}

.bs-ai__plan-page-role {
  font-weight: 500;
  margin-right: 0.3rem;
  color: var(--bs-g80);
}

.bs-ai__plan-page-purpose {
  color: var(--bs-w60);
}

.bs-ai__plan-page-badge {
  font-size: 0.6rem;
  padding: 0.1rem 0.3rem;
  border-radius: 0.2rem;
  background: var(--bs-g20);
  color: var(--bs-g80);
}

.bs-ai__plan-actions {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
  align-items: center;
}

.bs-ai__plan-actions .bs-ai__btn--primary {
  width: auto;
  margin-top: 0;
  margin-left: auto;
}

/* ── 진행률 ── */
.bs-ai__progress {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.bs-ai__progress-bar {
  width: 100%;
  height: 4px;
  background: var(--bs-k20);
  border-radius: 2px;
  overflow: hidden;
}

.bs-ai__progress-fill {
  height: 100%;
  background: #e94560;
  transition: width 0.3s ease;
}

.bs-ai__progress-label {
  font-size: 0.75rem;
  color: var(--bs-g80);
  text-align: center;
}

.bs-ai__progress-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 20rem;
  overflow-y: auto;
}

.bs-ai__progress-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.5rem;
  border-radius: 0.25rem;
  background: none;
  border: none;
  font-size: 0.75rem;
  color: var(--bs-w60);
  cursor: pointer;
  text-align: left;
}

.bs-ai__progress-item:disabled { cursor: default; opacity: 0.5; }
.bs-ai__progress-item--complete { color: #4caf50; }
.bs-ai__progress-item--generating { color: #e94560; }
.bs-ai__progress-item--error { color: #ff5252; }

.bs-ai__progress-icon {
  flex-shrink: 0;
  width: 1rem;
  text-align: center;
}

/* ── 로딩 ── */
.bs-ai__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 0;
  color: var(--bs-g80);
  font-size: 0.8rem;
}

.bs-ai__spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid var(--bs-g30);
  border-top-color: #e94560;
  border-radius: 50%;
  animation: bs-ai-spin 0.6s linear infinite;
}

@keyframes bs-ai-spin {
  to { transform: rotate(360deg); }
}

/* ── 완료/에러 ── */
.bs-ai__complete,
.bs-ai__error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 0;
  text-align: center;
  font-size: 0.8rem;
  color: var(--bs-w60);
}

.bs-ai__complete-icon {
  font-size: 2rem;
  color: #4caf50;
}

.bs-ai__error p { color: #ff5252; }

/* ── 캔버스 AI 오버레이 ── */
.bs-canvas--ai-generating { position: relative; }

.bs-canvas__ai-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(0, 0, 0, 0.4);
  border-radius: inherit;
  z-index: 100;
  font-size: 0.8rem;
  color: var(--bs-w60);
}
```

---

## 9. 패키지 Export 확장

```typescript
// frontend/src/index.ts 에 추가

// ──── AI ────
export { AIChatPanel } from './components/AI/AIChatPanel'
export { useAISession } from './hooks/useAISession'
export { useAIStore } from './stores/aiStore'
export type { AIPhase, AIPlan, AIPageProgress } from './stores/aiStore'
```

---

## 10. BookStudioEditor 통합

```tsx
// BookStudioEditor.tsx 수정사항

import { useAISession } from '../../hooks/useAISession'

export function BookStudioEditor({ client, bookId, defaultLayout, features }: BookStudioEditorProps) {
  // 기존 코드...

  // AI 세션 훅 초기화 (SSE 연결 정리 담당)
  useAISession({ client })

  // SidebarTabs에 client 전달
  return (
    <EditorLayout
      sidebar={<SidebarTabs client={client} {...sidebarProps} />}
      // ... 기존 props
    />
  )
}
```

---

## 11. 파일 구조 (신규/수정)

```
frontend/src/
├── components/
│   ├── AI/                               # [신규 디렉토리]
│   │   ├── AIChatPanel.tsx               # [신규] 메인 AI 패널
│   │   ├── AIPromptInput.tsx             # [신규] 프롬프트 입력
│   │   ├── AIPlanReview.tsx              # [신규] 기획서 검토
│   │   └── AIGenerationProgress.tsx      # [신규] 진행률 표시
│   ├── Sidebar/
│   │   └── SidebarTabs.tsx               # [수정] AI 버튼 + AIChatPanel 통합
│   └── Editor/
│       ├── BookStudioEditor.tsx           # [수정] useAISession 초기화, client 전달
│       └── EditorCanvas.tsx              # [수정] AI 생성 중 오버레이
├── stores/
│   └── aiStore.ts                        # [신규] AI 세션 상태
├── hooks/
│   └── useAISession.ts                   # [신규] SSE 클라이언트 + 에디터 연동
├── types/
│   └── ai.ts                             # [신규] AI API 응답 타입
├── api/
│   └── restClient.ts                     # [수정] ai 네임스페이스 추가
├── styles/
│   └── ai.css                            # [신규] AI 패널 스타일
└── index.ts                              # [수정] AI export 추가
```

---

## 12. 테스트 계획

### 12.1 Store 테스트

```typescript
describe('aiStore', () => {
  test('setPlan initializes progress from pages')
  test('updatePageProgress updates specific page')
  test('reset returns to initial state')
  test('setError sets phase to error')
  test('addMessage appends with id and timestamp')
})
```

### 12.2 Hook 테스트

```typescript
describe('useAISession', () => {
  test('startSession creates session and connects SSE')
  test('page_complete event adds page to editorStore')
  test('page_complete uses withRemoteUpdate to suppress dirty')
  test('generation_complete sets phase to complete')
  test('approvePlan calls approve API')
  test('cancelSession closes EventSource')
  test('cleanup closes EventSource on unmount')
})
```

### 12.3 컴포넌트 테스트

```typescript
describe('AIChatPanel', () => {
  test('renders prompt input when idle')
  test('renders plan review when reviewing')
  test('renders progress when generating')
  test('renders complete message when done')
})

describe('AIPromptInput', () => {
  test('calls onSubmit with prompt and options')
  test('Enter key submits, Shift+Enter does not')
  test('disabled when empty prompt')
})

describe('AIPlanReview', () => {
  test('displays all plan pages')
  test('approve button calls onApprove')
  test('editing mode allows purpose modification')
})

describe('AIGenerationProgress', () => {
  test('shows correct progress percentage')
  test('clicking complete page calls onPageClick')
  test('cancel button calls onCancel')
})
```

---

## 13. Phase 2와의 연결점

| Phase 2 결과물 | Phase 3에서 사용하는 곳 |
|---------------|---------------------|
| `AISession` REST API | `restClient.ai.*` 호출 |
| SSE `/stream/` 엔드포인트 | `useAISession` → `EventSource` |
| `planning_complete` SSE 이벤트 | `setPlan()` + `setPhase('reviewing')` |
| `page_complete` SSE 이벤트 | `addPage()` + `setPanels()` (withRemoteUpdate) |
| `generation_complete` SSE 이벤트 | `setPhase('complete')` |
| 패턴 CRUD API (Phase 1) | 향후 패턴 미리보기 (Phase 4) |
