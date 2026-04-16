import React, { useRef, useCallback, useState, type MouseEvent } from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { useSelectionStore } from '../../stores/selectionStore'
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
  const { selectedPanelIds, select, toggleSelect, setDragging, setResizing } = useSelectionStore()
  const isSelected = selectedPanelIds.includes(panel.id)
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number } | null>(null)
  const dragRef = useRef<{ startX: number; startY: number; origLeft: number; origTop: number } | null>(null)

  const setSidebarContext = useEditorStore((s) => s.setSidebarContext)
  const setEditingPanelId = useEditorStore((s) => s.setEditingPanelId)
  const editingPanelId = useEditorStore((s) => s.editingPanelId)
  const isEditing = editingPanelId === panel.id

  const handleMouseDown = useCallback(
    (e: MouseEvent) => {
      if (isEditing) return // don't drag while editing text
      e.stopPropagation()
      if (e.shiftKey) {
        toggleSelect(panel.id)
      } else if (!isSelected) {
        select(panel.id)
      }
      // Switch sidebar context based on media type
      const type = panel.media_type
      if (type === 'TXT' || type === 'HL' || type === 'DOC') {
        setSidebarContext('text')
      } else if (type === 'IMG') {
        setSidebarContext('image')
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
        updatePanel(panel.id, {
          left: dragRef.current.origLeft + dx,
          top: dragRef.current.origTop + dy,
        })
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
    [panel.id, panel.left, panel.top, isSelected, select, toggleSelect, updatePanel, setDragging],
  )

  const handleResize = useCallback(
    (e: MouseEvent, direction: string) => {
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
        const dx = ev.clientX - startX
        const dy = ev.clientY - startY
        const updates: Partial<Panel> = {}

        if (direction.includes('r')) updates.width = Math.max(20, origW + dx)
        if (direction.includes('l')) {
          updates.width = Math.max(20, origW - dx)
          updates.left = origLeft + (origW - (updates.width ?? origW))
        }
        if (direction.includes('b')) updates.height = Math.max(20, origH + dy)
        if (direction.includes('t')) {
          updates.height = Math.max(20, origH - dy)
          updates.top = origTop + (origH - (updates.height ?? origH))
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
    [panel.id, panel.width, panel.height, panel.left, panel.top, updatePanel, setResizing],
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
    if (!isSelected) select(panel.id)
    setContextMenu({ x: e.clientX, y: e.clientY })
  }, [isSelected, select, panel.id])

  const removePanel = useEditorStore((s) => s.removePanel)
  const addPanel = useEditorStore((s) => s.addPanel)

  const className = `bs-panel${isSelected ? ' bs-panel--selected' : ''}`

  return (
    <div
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
          <div className="bs-handle bs-handle--corner bs-handle--tl" onMouseDown={(e) => handleResize(e, 'tl')} />
          <div className="bs-handle bs-handle--corner bs-handle--tr" onMouseDown={(e) => handleResize(e, 'tr')} />
          <div className="bs-handle bs-handle--corner bs-handle--bl" onMouseDown={(e) => handleResize(e, 'bl')} />
          <div className="bs-handle bs-handle--corner bs-handle--br" onMouseDown={(e) => handleResize(e, 'br')} />
          <div className="bs-handle bs-handle--edge-h bs-handle--mt" onMouseDown={(e) => handleResize(e, 't')} />
          <div className="bs-handle bs-handle--edge-h bs-handle--mb" onMouseDown={(e) => handleResize(e, 'b')} />
          <div className="bs-handle bs-handle--edge-v bs-handle--ml" onMouseDown={(e) => handleResize(e, 'l')} />
          <div className="bs-handle bs-handle--edge-v bs-handle--mr" onMouseDown={(e) => handleResize(e, 'r')} />
        </>
      )}

      {contextMenu && (
        <PanelContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          onClose={() => setContextMenu(null)}
          onDuplicate={() => {
            const id = `panel-dup-${Date.now()}`
            addPanel({ ...panel, id, left: panel.left + 20, top: panel.top + 20 })
          }}
          onDelete={() => removePanel(panel.id)}
          onBringForward={() => updatePanel(panel.id, { z_index: panel.z_index + 1 })}
          onSendBackward={() => updatePanel(panel.id, { z_index: Math.max(0, panel.z_index - 1) })}
          onToggleLock={() => updatePanel(panel.id, { fixed: !panel.fixed })}
          isLocked={panel.fixed}
        />
      )}
    </div>
  )
}
