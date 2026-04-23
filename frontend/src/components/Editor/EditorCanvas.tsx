import React, { useRef, useCallback, type WheelEvent, type MouseEvent } from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { PanelWrapper } from '../Panel/PanelWrapper'
import { GridOverlay } from '../common/GridOverlay'
import { GuideLines } from '../common/GuideLines'

export function EditorCanvas() {
  const { layoutConfig, zoom, setZoom, activePageId, panels, pages, showGrid, gridSize } =
    useEditorStore()
  const clearSelection = useEditorStore((s) => s.clearSelection)
  const setSidebarContext = useEditorStore((s) => s.setSidebarContext)
  const setEditingPanelId = useEditorStore((s) => s.setEditingPanelId)
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
        setSidebarContext('wallpaper')
        setEditingPanelId(null)
      }
    },
    [clearSelection],
  )

  const { width, height } = layoutConfig

  const bgOpacity = activePage?.opacity ?? 1
  const isTransparent = activePage?.background_color === 'transparent'
  const showCheckerboard = isTransparent || bgOpacity < 1

  return (
    <div
      ref={containerRef}
      className="bs-canvas-container"
      onWheel={handleWheel}
      onClick={handleCanvasClick}
    >
      <div
        className="bs-canvas-page"
        style={{
          width,
          height,
          transform: `scale(${zoom})`,
          transformOrigin: 'center center',
          position: 'relative',
        }}
      >
        {/* Checkerboard layer for transparent background */}
        {showCheckerboard && (
          <div className="bs-canvas-checkerboard" style={{
            position: 'absolute',
            inset: 0,
            pointerEvents: 'none',
          }} />
        )}
        {/* Background layer with opacity — does not affect content */}
        <div style={{
          position: 'absolute',
          inset: 0,
          ...(isTransparent ? {} : { backgroundColor: activePage?.background_color || '#ffffff' }),
          opacity: bgOpacity,
          ...(activePage?.background_type === 'WP' && activePage.wallpaper_image ? {
            backgroundImage: `url(${activePage.wallpaper_image})`,
            backgroundSize: 'cover',
            backgroundPosition: `${activePage.background_position_x}% ${activePage.background_position_y}%`,
          } : {}),
          pointerEvents: 'none',
        }} />
        {showGrid && <GridOverlay width={width} height={height} gridSize={gridSize} />}
        <GuideLines />
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
