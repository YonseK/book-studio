import React, { useRef, useCallback, useState, type MouseEvent } from 'react'
import { useEditorStore, pushHistory } from '../../stores/editorStore'
import { useClient } from '../../contexts/ClientContext'
import type { Panel } from '../../types/panel'
import { TextPanel } from './TextPanel'
import { ImagePanel } from './ImagePanel'
import { ShapePanel } from './ShapePanel'
import { VideoPanel } from './VideoPanel'
import { EmbedPanel } from './EmbedPanel'
import { PanelContextMenu } from './PanelContextMenu'

interface PanelWrapperProps {
  panel: Panel
}

export function PanelWrapper({ panel }: PanelWrapperProps) {
  const updatePanel = useEditorStore((s) => s.updatePanel)
  const selectedPanelIds = useEditorStore((s) => s.selectedPanelIds)
  const selectPanel = useEditorStore((s) => s.selectPanel)
  const toggleSelectPanel = useEditorStore((s) => s.toggleSelectPanel)
  const setDragging = useEditorStore((s) => s.setDragging)
  const setResizing = useEditorStore((s) => s.setResizing)
  const zoom = useEditorStore((s) => s.zoom)
  const snapToGrid = useEditorStore((s) => s.snapToGrid)
  const gridSize = useEditorStore((s) => s.gridSize)
  const isSelected = selectedPanelIds.includes(panel.id)
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number } | null>(null)
  const dragRef = useRef<{ startX: number; startY: number; origLeft: number; origTop: number } | null>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)

  const setSidebarContext = useEditorStore((s) => s.setSidebarContext)
  const setEditingPanelId = useEditorStore((s) => s.setEditingPanelId)
  const editingPanelId = useEditorStore((s) => s.editingPanelId)
  const isEditing = editingPanelId === panel.id

  const snap = (value: number) => snapToGrid ? Math.round(value / gridSize) * gridSize : value

  const handleMouseDown = useCallback(
    (e: MouseEvent) => {
      if (isEditing) return // don't drag while editing text
      pushHistory('move panel')
      e.stopPropagation()
      if (e.shiftKey) {
        toggleSelectPanel(panel.id)
      } else if (!isSelected) {
        selectPanel(panel.id)
      }
      // Switch sidebar context based on media type
      const type = panel.media_type
      if (type === 'TXT' || type === 'HL' || type === 'DOC') {
        setSidebarContext('text')
      } else if (type === 'IMG') {
        setSidebarContext('image')
      } else if (type === 'SHA') {
        setSidebarContext('shape')
      } else if (type === 'EV' || type === 'WS') {
        setSidebarContext('embed')
      } else if (type === 'VOD' || type === 'AUDIO') {
        setSidebarContext('video')
      } else {
        setSidebarContext('default')
      }
      dragRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        origLeft: panel.left,
        origTop: panel.top,
      }
      setDragging(true)

      const handleMouseMove = (ev: globalThis.MouseEvent) => {
        if (!dragRef.current) return
        const dx = ev.clientX - dragRef.current.startX
        const dy = ev.clientY - dragRef.current.startY
        const currentZoom = useEditorStore.getState().zoom
        const currentSnapToGrid = useEditorStore.getState().snapToGrid
        const currentGridSize = useEditorStore.getState().gridSize
        const snapVal = (value: number) => currentSnapToGrid ? Math.round(value / currentGridSize) * currentGridSize : value
        const layoutConfig = useEditorStore.getState().layoutConfig
        const newLeft = snapVal(dragRef.current.origLeft + dx / currentZoom)
        const newTop = snapVal(dragRef.current.origTop + dy / currentZoom)
        const clampedLeft = Math.max(-panel.width + 20, Math.min(layoutConfig.width - 20, newLeft))
        const clampedTop = Math.max(-panel.height + 20, Math.min(layoutConfig.height - 20, newTop))
        updatePanel(panel.id, { left: clampedLeft, top: clampedTop })
      }

      const handleMouseUp = () => {
        dragRef.current = null
        setDragging(false)
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }

      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    },
    [panel.id, panel.left, panel.top, panel.width, panel.height, panel.media_type, isSelected, isEditing, selectPanel, toggleSelectPanel, updatePanel, setDragging, setSidebarContext, zoom],
  )

  const handleResize = useCallback(
    (e: MouseEvent, direction: string) => {
      pushHistory('resize panel')
      e.stopPropagation()
      e.preventDefault()
      const startX = e.clientX
      const startY = e.clientY
      const origW = panel.width
      const origH = panel.height
      const origLeft = panel.left
      const origTop = panel.top
      setResizing(true)

      const handleMouseMove = (ev: globalThis.MouseEvent) => {
        const currentZoom = useEditorStore.getState().zoom
        const currentSnapToGrid = useEditorStore.getState().snapToGrid
        const currentGridSize = useEditorStore.getState().gridSize
        const snapVal = (value: number) => currentSnapToGrid ? Math.round(value / currentGridSize) * currentGridSize : value
        const dx = (ev.clientX - startX) / currentZoom
        const dy = (ev.clientY - startY) / currentZoom
        const updates: Partial<Panel> = {}

        if (direction.includes('r')) updates.width = snapVal(Math.max(20, origW + dx))
        if (direction.includes('l')) {
          updates.width = snapVal(Math.max(20, origW - dx))
          updates.left = snapVal(origLeft + (origW - (updates.width ?? origW)))
        }
        if (direction.includes('b')) updates.height = snapVal(Math.max(20, origH + dy))
        if (direction.includes('t')) {
          updates.height = snapVal(Math.max(20, origH - dy))
          updates.top = snapVal(origTop + (origH - (updates.height ?? origH)))
        }

        updatePanel(panel.id, updates)
      }

      const handleMouseUp = () => {
        setResizing(false)
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }

      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    },
    [panel.id, panel.width, panel.height, panel.left, panel.top, updatePanel, setResizing, zoom],
  )

  const handleRotateStart = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation()
      e.preventDefault()
      const el = wrapperRef.current
      if (!el) return
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 2
      const startAngle = Math.atan2(e.clientY - cy, e.clientX - cx) * 180 / Math.PI
      const origRotate = panel.rotate || 0

      const handleMouseMove = (ev: globalThis.MouseEvent) => {
        const currentAngle = Math.atan2(ev.clientY - cy, ev.clientX - cx) * 180 / Math.PI
        const delta = currentAngle - startAngle
        updatePanel(panel.id, { rotate: Math.round(origRotate + delta) })
      }

      const handleMouseUp = () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }

      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    },
    [panel.id, panel.rotate, updatePanel],
  )

  const renderContent = () => {
    switch (panel.media_type) {
      case 'TXT':
      case 'DOC':
        return <TextPanel panel={panel} isEditing={isEditing} />
      case 'HL':
        return <TextPanel panel={panel} isHeadline isEditing={isEditing} />
      case 'IMG':
        return <ImagePanel panel={panel} />
      case 'SHA':
        return <ShapePanel panel={panel} />
      case 'VOD':
      case 'AUDIO':
        return <VideoPanel panel={panel} />
      case 'EV':
      case 'WS':
        return <EmbedPanel panel={panel} />
      default:
        return (
          <div style={{ padding: 8, fontSize: 12, color: '#999', textAlign: 'center' }}>
            {panel.media_type}
          </div>
        )
    }
  }

  const handleDoubleClick = useCallback((e: MouseEvent) => {
    e.stopPropagation()
    const type = panel.media_type
    if (type === 'TXT' || type === 'HL' || type === 'DOC') {
      setEditingPanelId(panel.id)
      setSidebarContext('text')
    }
  }, [panel.id, panel.media_type, setEditingPanelId, setSidebarContext])

  const handleContextMenu = useCallback((e: MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (!isSelected) selectPanel(panel.id)
    setContextMenu({ x: e.clientX, y: e.clientY })
  }, [isSelected, selectPanel, panel.id])

  const removePanel = useEditorStore((s) => s.removePanel)
  const addPanel = useEditorStore((s) => s.addPanel)
  const client = useClient()

  const className = `bs-panel${isSelected ? ' bs-panel--selected' : ''}`

  return (
    <div
      ref={wrapperRef}
      className={className}
      data-panel-id={panel.id}
      onMouseDown={handleMouseDown}
      onDoubleClick={handleDoubleClick}
      onContextMenu={handleContextMenu}
      style={{
        left: panel.left,
        top: panel.top,
        width: panel.width,
        height: panel.height,
        zIndex: panel.z_index,
        opacity: panel.opacity,
        transform: panel.rotate ? `rotate(${panel.rotate}deg)` : undefined,
        borderRadius: panel.border_radius || 0,
        backgroundColor: panel.background_color !== 'transparent' ? panel.background_color : undefined,
        padding: panel.padding,
        boxShadow: panel.box_shadow !== 'initial' ? panel.box_shadow : undefined,
      }}
    >
      {renderContent()}

      {isSelected && (
        <>
          <div className="bs-handle--rotate" onMouseDown={handleRotateStart}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4a4a4a" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 4v6h6" />
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
            </svg>
          </div>
          <div className="bs-handle bs-handle--tr" onMouseDown={(e) => handleResize(e, 'tr')} />
          <div className="bs-handle bs-handle--bl" onMouseDown={(e) => handleResize(e, 'bl')} />
          <div className="bs-handle bs-handle--br" onMouseDown={(e) => handleResize(e, 'br')} />
          <div className="bs-handle bs-handle--mt" onMouseDown={(e) => handleResize(e, 't')} />
          <div className="bs-handle bs-handle--mb" onMouseDown={(e) => handleResize(e, 'b')} />
          <div className="bs-handle bs-handle--ml" onMouseDown={(e) => handleResize(e, 'l')} />
          <div className="bs-handle bs-handle--mr" onMouseDown={(e) => handleResize(e, 'r')} />
        </>
      )}

      {contextMenu && (
        <PanelContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          onClose={() => setContextMenu(null)}
          onDuplicate={async () => {
            try {
              const cloned = await client.panels.clone(panel.page, panel.id)
              addPanel({ ...cloned, left: cloned.left + 20, top: cloned.top + 20 })
            } catch {
              // fallback: 로컬 복제
              const id = `panel-dup-${Date.now()}`
              addPanel({ ...panel, id, left: panel.left + 20, top: panel.top + 20 })
            }
          }}
          onDelete={async () => {
            try {
              await client.panels.delete(panel.page, panel.id)
            } catch (e) {
              console.error('Failed to delete panel:', e)
            }
            removePanel(panel.id)
          }}
          onBringForward={() => updatePanel(panel.id, { z_index: panel.z_index + 1 })}
          onSendBackward={() => updatePanel(panel.id, { z_index: Math.max(0, panel.z_index - 1) })}
          onToggleLock={() => updatePanel(panel.id, { fixed: !panel.fixed })}
          isLocked={panel.fixed}
        />
      )}
    </div>
  )
}
