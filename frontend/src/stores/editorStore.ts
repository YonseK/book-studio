import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import type { Book, BookEdition } from '../types/book'
import type { Page } from '../types/page'
import type { Panel } from '../types/panel'
import type { LayoutConfig } from '../types/layout'
import { LAYOUT_PRESETS } from '../types/layout'

export interface EditorState {
  // 데이터
  book: Book | null
  edition: BookEdition | null
  pages: Page[]
  panels: Record<string, Panel[]> // pageId → panels
  // UI 상태
  activePageId: string | null
  selectedPanelIds: string[]
  zoom: number
  layoutConfig: LayoutConfig
  // 옵션
  showGrid: boolean
  showGuides: boolean
  snapToGrid: boolean
  gridSize: number
  theme: 'light' | 'dark'
  activeSidebarTab: 'file' | 'input' | 'options' | 'share'
  sidebarContext: 'default' | 'text' | 'image' | 'wallpaper'
  editingPanelId: string | null
  isPageListCollapsed: boolean

  // 액션
  setBook: (book: Book) => void
  setEdition: (edition: BookEdition) => void
  setPages: (pages: Page[]) => void
  setActivePage: (pageId: string) => void
  addPage: (page: Page) => void
  updatePage: (pageId: string, data: Partial<Page>) => void
  removePage: (pageId: string) => void
  reorderPages: (pageIds: string[]) => void
  setPanels: (pageId: string, panels: Panel[]) => void
  addPanel: (panel: Panel) => void
  updatePanel: (panelId: string, data: Partial<Panel>) => void
  removePanel: (panelId: string) => void
  selectPanel: (panelId: string | null) => void
  selectMultiplePanels: (panelIds: string[]) => void
  setZoom: (zoom: number) => void
  setLayoutConfig: (config: LayoutConfig) => void
  toggleGrid: () => void
  toggleGuides: () => void
  toggleSnap: () => void
  setGridSize: (size: number) => void
  setTheme: (theme: 'light' | 'dark') => void
  setActiveSidebarTab: (tab: 'file' | 'input' | 'options' | 'share') => void
  setSidebarContext: (ctx: 'default' | 'text' | 'image' | 'wallpaper') => void
  setEditingPanelId: (id: string | null) => void
  togglePageList: () => void
}

export const useEditorStore = create<EditorState>()(
  immer((set) => ({
    book: null,
    edition: null,
    pages: [],
    panels: {},
    activePageId: null,
    selectedPanelIds: [],
    zoom: 1,
    layoutConfig: LAYOUT_PRESETS.PPTX_WIDE,
    showGrid: false,
    showGuides: true,
    snapToGrid: false,
    gridSize: 20,
    theme: 'dark',
    activeSidebarTab: 'options',
    sidebarContext: 'wallpaper' as const,
    editingPanelId: null,
    isPageListCollapsed: false,

    setBook: (book) => set((s) => { s.book = book }),
    setEdition: (edition) => set((s) => { s.edition = edition }),

    setPages: (pages) => set((s) => {
      s.pages = pages
      if (pages.length > 0 && !s.activePageId) {
        s.activePageId = pages[0].id
      }
    }),

    setActivePage: (pageId) => set((s) => {
      s.activePageId = pageId
      s.selectedPanelIds = []
    }),

    addPage: (page) => set((s) => {
      s.pages.push(page)
      s.activePageId = page.id
    }),

    updatePage: (pageId, data) => set((s) => {
      const idx = s.pages.findIndex((p) => p.id === pageId)
      if (idx >= 0) Object.assign(s.pages[idx], data)
    }),

    removePage: (pageId) => set((s) => {
      s.pages = s.pages.filter((p) => p.id !== pageId)
      delete s.panels[pageId]
      if (s.activePageId === pageId) {
        s.activePageId = s.pages[0]?.id ?? null
      }
    }),

    reorderPages: (pageIds) => set((s) => {
      const map = new Map(s.pages.map((p) => [p.id, p]))
      s.pages = pageIds.map((id, i) => {
        const p = map.get(id)!
        p.order = i
        return p
      })
    }),

    setPanels: (pageId, panels) => set((s) => {
      s.panels[pageId] = panels
    }),

    addPanel: (panel) => set((s) => {
      const pageId = panel.page
      if (!s.panels[pageId]) s.panels[pageId] = []
      s.panels[pageId].push(panel)
      s.selectedPanelIds = [panel.id]
    }),

    updatePanel: (panelId, data) => set((s) => {
      for (const panels of Object.values(s.panels)) {
        const idx = panels.findIndex((p) => p.id === panelId)
        if (idx >= 0) {
          Object.assign(panels[idx], data)
          return
        }
      }
    }),

    removePanel: (panelId) => set((s) => {
      for (const [pageId, panels] of Object.entries(s.panels)) {
        s.panels[pageId] = panels.filter((p) => p.id !== panelId)
      }
      s.selectedPanelIds = s.selectedPanelIds.filter((id) => id !== panelId)
    }),

    selectPanel: (panelId) => set((s) => {
      s.selectedPanelIds = panelId ? [panelId] : []
    }),

    selectMultiplePanels: (panelIds) => set((s) => {
      s.selectedPanelIds = panelIds
    }),

    setZoom: (zoom) => set((s) => { s.zoom = Math.max(0.1, Math.min(5, zoom)) }),
    setLayoutConfig: (config) => set((s) => { s.layoutConfig = config }),
    toggleGrid: () => set((s) => { s.showGrid = !s.showGrid }),
    toggleGuides: () => set((s) => { s.showGuides = !s.showGuides }),
    toggleSnap: () => set((s) => { s.snapToGrid = !s.snapToGrid }),
    setGridSize: (size) => set((s) => { s.gridSize = size }),
    setTheme: (theme) => set((s) => { s.theme = theme }),
    setActiveSidebarTab: (tab) => set((s) => { s.activeSidebarTab = tab }),
    setSidebarContext: (ctx) => set((s) => { s.sidebarContext = ctx }),
    setEditingPanelId: (id) => set((s) => { s.editingPanelId = id }),
    togglePageList: () => set((s) => { s.isPageListCollapsed = !s.isPageListCollapsed }),
  })),
)
