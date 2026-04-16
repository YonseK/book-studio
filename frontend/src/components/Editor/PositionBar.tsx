import React from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { useSelectionStore } from '../../stores/selectionStore'
import { Search } from 'lucide-react'

export function PositionBar() {
  const { panels, activePageId } = useEditorStore()
  const { selectedPanelIds } = useSelectionStore()

  const activePanels = activePageId ? (panels[activePageId] ?? []) : []
  const selectedPanel = selectedPanelIds.length === 1
    ? activePanels.find((p) => p.id === selectedPanelIds[0])
    : null

  return (
    <>
      {selectedPanel ? (
        <div className="bs-topbar__position">
          <span>
            <span className="bs-topbar__label">TOP : </span>
            <span className="bs-topbar__value">{Math.round(selectedPanel.top)}px</span>
          </span>
          <span>
            <span className="bs-topbar__label">LEFT : </span>
            <span className="bs-topbar__value">{Math.round(selectedPanel.left)}px</span>
          </span>
          <span>
            <span className="bs-topbar__label">WIDTH : </span>
            <span className="bs-topbar__value">{Math.round(selectedPanel.width)}px</span>
          </span>
          <span>
            <span className="bs-topbar__label">HEIGHT : </span>
            <span className="bs-topbar__value">{Math.round(selectedPanel.height)}px</span>
          </span>
          <span>
            <span className="bs-topbar__label">ROTATE : </span>
            <span className="bs-topbar__value">{selectedPanel.rotate || 0}&deg;</span>
          </span>
        </div>
      ) : null}
      <div className="bs-topbar__search">
        <Search size={14} style={{ position: 'absolute', left: 8, top: '50%', transform: 'translateY(-50%)', color: 'var(--bs-text-muted)' }} />
        <input
          type="search"
          className="bs-topbar__search-input"
          placeholder="Search..."
        />
      </div>
    </>
  )
}
