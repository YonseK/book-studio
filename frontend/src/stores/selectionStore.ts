import { create } from 'zustand'

interface SelectionState {
  selectedPanelIds: string[]
  hoveredPanelId: string | null
  isDragging: boolean
  isResizing: boolean

  select: (panelId: string) => void
  selectMultiple: (panelIds: string[]) => void
  toggleSelect: (panelId: string) => void
  clearSelection: () => void
  setHovered: (panelId: string | null) => void
  setDragging: (dragging: boolean) => void
  setResizing: (resizing: boolean) => void
}

export const useSelectionStore = create<SelectionState>((set, get) => ({
  selectedPanelIds: [],
  hoveredPanelId: null,
  isDragging: false,
  isResizing: false,

  select: (panelId) => set({ selectedPanelIds: [panelId] }),
  selectMultiple: (panelIds) => set({ selectedPanelIds: panelIds }),
  toggleSelect: (panelId) =>
    set((s) => ({
      selectedPanelIds: s.selectedPanelIds.includes(panelId)
        ? s.selectedPanelIds.filter((id) => id !== panelId)
        : [...s.selectedPanelIds, panelId],
    })),
  clearSelection: () => set({ selectedPanelIds: [] }),
  setHovered: (panelId) => set({ hoveredPanelId: panelId }),
  setDragging: (dragging) => set({ isDragging: dragging }),
  setResizing: (resizing) => set({ isResizing: resizing }),
}))
