import { create } from 'zustand'

interface Snapshot {
  label: string
  state: string // JSON.stringify 된 에디터 상태 (pages + panels)
}

interface HistoryState {
  past: Snapshot[]
  future: Snapshot[]
  maxSize: number

  push: (label: string, state: string) => void
  undo: () => Snapshot | null
  redo: () => Snapshot | null
  canUndo: () => boolean
  canRedo: () => boolean
  clear: () => void
}

export const useHistoryStore = create<HistoryState>((set, get) => ({
  past: [],
  future: [],
  maxSize: 50,

  push: (label, state) =>
    set((s) => ({
      past: [...s.past.slice(-(s.maxSize - 1)), { label, state }],
      future: [],
    })),

  undo: () => {
    const { past, future } = get()
    if (past.length === 0) return null
    const snapshot = past[past.length - 1]
    set({
      past: past.slice(0, -1),
      future: [snapshot, ...future],
    })
    return snapshot
  },

  redo: () => {
    const { past, future } = get()
    if (future.length === 0) return null
    const snapshot = future[0]
    set({
      past: [...past, snapshot],
      future: future.slice(1),
    })
    return snapshot
  },

  canUndo: () => get().past.length > 0,
  canRedo: () => get().future.length > 0,
  clear: () => set({ past: [], future: [] }),
}))
