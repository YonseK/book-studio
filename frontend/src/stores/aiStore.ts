import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type { AIPlan, AIPagePlan } from '../types/ai'

export type AIPhase =
  | 'idle'
  | 'planning'
  | 'reviewing'
  | 'generating'
  | 'complete'
  | 'error'

export interface AIPageProgress {
  index: number
  role: string
  status: 'pending' | 'generating' | 'complete' | 'error'
  pageId?: string
  error?: string
}

export interface AIMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

export interface AIState {
  // 세션
  sessionId: string | null
  phase: AIPhase
  errorMessage: string | null

  // 기획서
  plan: AIPlan | null

  // 진행률
  progress: AIPageProgress[]
  generatingPageIndex: number | null

  // 대화
  messages: AIMessage[]

  // UI
  isOpen: boolean

  // 액션
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
  sessionId: null as string | null,
  phase: 'idle' as AIPhase,
  errorMessage: null as string | null,
  plan: null as AIPlan | null,
  progress: [] as AIPageProgress[],
  generatingPageIndex: null as number | null,
  messages: [] as AIMessage[],
  isOpen: false,
}

export const useAIStore = create<AIState>()(
  immer((set) => ({
    ...initialState,

    setSession: (sessionId) => set((s) => { s.sessionId = sessionId }),

    setPhase: (phase) => set((s) => {
      s.phase = phase
      s.errorMessage = null
    }),

    setPlan: (plan) => set((s) => {
      s.plan = plan
      s.progress = plan.pages.map((p) => ({
        index: p.index,
        role: p.role,
        status: 'pending' as const,
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
