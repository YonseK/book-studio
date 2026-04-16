import React, { useRef, useCallback, type WheelEvent, type MouseEvent } from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { useSelectionStore } from '../../stores/selectionStore'
import { PanelWrapper } from '../Panel/PanelWrapper'
import { GridOverlay } from '../common/GridOverlay'

export function EditorCanvas() {
  const { layoutConfig, zoom, setZoom, activePageId, panels, pages, showGrid, gridSize, showGuides } =
    useEditorStore()
  const clearSelection = useSelectionStore((s) => s.clearSelection)
  const containerRef = useRef<HTMLDivElement>(null)

  const activePage = pages.find((p) => p.id === activePageId)
  const activePanels = activePageId ? (panels[activePageId] ?? []) : []

  const handleWheel = useCallback(
    (e: WheelEvent) => {
      if (e.ctrlKey || e.metaKey) {
        e.preventDefault()
        const delta = e.deltaY > 0 ? -0.05 : 0.05
        setZoom(zoom + delta)
      }
    },
    [zoom, setZoom],
  )

  const handleCanvasClick = useCallback(
    (e: MouseEvent) => {
      if (e.target === e.currentTarget || (e.target as HTMLElement).classList.contains('bs-canvas-page')) {
        clearSelection()
      }
    },
    [clearSelection],
  )

  const { width, height } = layoutConfig

  const bgStyle: React.CSSProperties = activePage
    ? {
        backgroundColor: activePage.background_color,
        opacity: activePage.opacity,
      }
    : { backgroundColor: '#ffffff' }

  return (
    <div
      ref={containerRef}
      className="bs-canvas-container"
      onWheel={handleWheel}
      onClick={handleCanvasClick}
      style={{
        position: 'relative',
        padding: 40,
        cursor: 'default',
      }}
    >
      <div
        className="bs-canvas-page"
        style={{
          position: 'relative',
          width,
          height,
          transform: `scale(${zoom})`,
          transformOrigin: 'center center',
          boxShadow: '0 2px 20px rgba(0,0,0,0.15)',
          borderRadius: 2,
          overflow: 'hidden',
          ...bgStyle,
        }}
      >
        {showGrid && <GridOverlay width={width} height={height} gridSize={gridSize} />}
        {activePanels
          .filter((p) => p.is_active && !p.fields_data?.deleted)
          .sort((a, b) => a.z_index - b.z_index)
          .map((panel) => (
            <PanelWrapper key={panel.id} panel={panel} />
          ))}
      </div>
    </div>
  )
}
