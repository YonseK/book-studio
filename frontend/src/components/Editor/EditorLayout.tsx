import React, { useEffect, type ReactNode } from 'react'
import { useEditorStore, pushHistory } from '../../stores/editorStore'
import { useHistoryStore } from '../../stores/historyStore'
import { PanelLeft, PanelRight } from 'lucide-react'

interface EditorLayoutProps {
  topbar?: ReactNode
  iconMenu?: ReactNode
  sidebar?: ReactNode
  canvas: ReactNode
  collabBar?: ReactNode
  pageList?: ReactNode
}

export function EditorLayout({
  topbar,
  iconMenu,
  sidebar,
  canvas,
  collabBar,
  pageList,
}: EditorLayoutProps) {
  const theme = useEditorStore((s) => s.theme)
  const accentTheme = useEditorStore((s) => s.accentTheme)
  const isDesignerCollapsed = useEditorStore((s) => s.isDesignerCollapsed)
  const isPageListCollapsed = useEditorStore((s) => s.isPageListCollapsed)
  const toggleDesigner = useEditorStore((s) => s.toggleDesigner)
  const togglePageList = useEditorStore((s) => s.togglePageList)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement
      const isInput = target.isContentEditable || target.tagName === 'INPUT' || target.tagName === 'TEXTAREA'
      const { selectedPanelIds, updatePanel, copyToClipboard, pasteFromClipboard, deleteSelectedPanels } = useEditorStore.getState()

      // Arrow key nudging
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key) && selectedPanelIds.length > 0 && !isInput) {
        e.preventDefault()
        const step = e.shiftKey ? 10 : 1
        const delta: Record<string, number> = {}
        if (e.key === 'ArrowUp') delta.top = -step
        if (e.key === 'ArrowDown') delta.top = step
        if (e.key === 'ArrowLeft') delta.left = -step
        if (e.key === 'ArrowRight') delta.left = step
        selectedPanelIds.forEach((id) => updatePanel(id, delta))
      }

      // Copy
      if ((e.ctrlKey || e.metaKey) && e.key === 'c' && selectedPanelIds.length > 0 && !isInput) {
        copyToClipboard()
      }

      // Paste
      if ((e.ctrlKey || e.metaKey) && e.key === 'v' && !isInput) {
        pushHistory('paste panels')
        pasteFromClipboard()
      }

      // Delete
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedPanelIds.length > 0 && !isInput) {
        e.preventDefault()
        pushHistory('delete panels')
        deleteSelectedPanels()
      }

      // Undo/Redo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault()
        if (e.shiftKey) {
          const snapshot = useHistoryStore.getState().redo()
          if (snapshot) {
            const { pages, panels } = JSON.parse(snapshot.state)
            useEditorStore.setState({ pages, panels })
          }
        } else {
          const snapshot = useHistoryStore.getState().undo()
          if (snapshot) {
            const { pages, panels } = JSON.parse(snapshot.state)
            useEditorStore.setState({ pages, panels })
          }
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className={`bs-editor bs-theme-${theme} bs-poly-${accentTheme}`}>
      {topbar && <div className="bs-topbar">{topbar}</div>}
      <div className="bs-editor__body">
        {/* Left sidebar */}
        <div className={`bs-designer${isDesignerCollapsed ? ' bs-designer--collapsed' : ''}`}>
          <div className="bs-designer__content">
            {sidebar}
          </div>
          <div className="bs-designer__iconmenu">
            {iconMenu}
            <div className="bs-iconmenu__spacer" />
            <button
              className="bs-iconmenu__collapse-btn"
              onClick={toggleDesigner}
              title={isDesignerCollapsed ? '사이드바 펼치기' : '사이드바 접기'}
            >
              <PanelLeft size={16} strokeWidth={1.5} style={{
                transform: isDesignerCollapsed ? 'rotate(180deg)' : undefined,
                transition: 'transform 0.5s',
              }} />
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div className="bs-canvas-area">{canvas}</div>

        {/* Right sidebar */}
        <div className={`bs-pagelist-wrap${isPageListCollapsed ? ' bs-pagelist-wrap--collapsed' : ''}`}>
          <div className="bs-pagelist-wrap__collab">
            <button
              className="bs-collabbar__collapse-btn"
              onClick={togglePageList}
              title={isPageListCollapsed ? '페이지 목록 펼치기' : '페이지 목록 접기'}
            >
              <PanelRight size={16} strokeWidth={1.5} style={{
                transform: isPageListCollapsed ? 'rotate(180deg)' : undefined,
                transition: 'transform 0.5s',
              }} />
            </button>
            {collabBar}
          </div>
          <div className="bs-pagelist-wrap__list">
            {pageList}
          </div>
        </div>
      </div>
    </div>
  )
}
