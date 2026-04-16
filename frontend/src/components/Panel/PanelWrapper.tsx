import React, { useRef, useCallback, useState, type MouseEvent } from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { useSelectionStore } from '../../stores/selectionStore'
import type { Panel } from '../../types/panel'
import { TextPanel } from './TextPanel'
import { ImagePanel } from './ImagePanel'
import { ShapePanel } from './ShapePanel'

interface PanelWrapperProps {
  panel: Panel
}

export function PanelWrapper({ panel }: PanelWrapperProps) {
  const updatePanel = useEditorStore((s) => s.updatePanel)
  const { selectedPanelIds, select, toggleSelect, setDragging, setResizing } = useSelectionStore()
  const isSelected = selectedPanelIds.includes(panel.id)
  const dragRef = useRef<{ startX: number; startY: number; origLeft: number; origTop: number } | null>(null)
  const resizeRef = useRef<{ startX: number; startY: number; origW: number; origH: number } | null>(null)

  const handleMouseDown = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation()
      if (e.shiftKey) {
        toggleSelect(panel.id)
      } else if (!isSelected) {
        select(panel.id)
      }
      // 드래그 시작
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

  const handleResizeMouseDown = useCallback(
    (e: MouseEvent) => {
      e.stopPropagation()
      resizeRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        origW: panel.width,
        origH: panel.height,
      }
      setResizing(true)

      const handleMouseMove = (ev: globalThis.MouseEvent) => {
        if (!resizeRef.current) return
        const dx = ev.clientX - resizeRef.current.startX
        const dy = ev.clientY - resizeRef.current.startY
        updatePanel(panel.id, {
          width: Math.max(20, resizeRef.current.origW + dx),
          height: Math.max(20, resizeRef.current.origH + dy),
        })
      }

      const handleMouseUp = () => {
        resizeRef.current = null
        setResizing(false)
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }

      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    },
    [panel.id, panel.width, panel.height, updatePanel, setResizing],
  )

  const renderContent = () => {
    switch (panel.media_type) {
      case 'TXT':
      case 'DOC':
        return <TextPanel panel={panel} />
      case 'HL':
        return <TextPanel panel={panel} isHeadline />
      case 'IMG':
        return <ImagePanel panel={panel} />
      case 'SHA':
        return <ShapePanel panel={panel} />
      default:
        return (
          <div style={{ padding: 8, fontSize: 12, color: '#999', textAlign: 'center' }}>
            {panel.media_type}
          </div>
        )
    }
  }

  return (
    <div
      className="bs-panel-wrapper"
      data-panel-id={panel.id}
      onMouseDown={handleMouseDown}
      style={{
        position: 'absolute',
        left: panel.left,
        top: panel.top,
        width: panel.width,
        height: panel.height,
        zIndex: panel.z_index,
        opacity: panel.opacity,
        transform: panel.rotate ? `rotate(${panel.rotate}deg)` : undefined,
        border: isSelected ? '2px solid #4a90d9' : '1px solid transparent',
        cursor: 'move',
        boxSizing: 'border-box',
        borderRadius: panel.border_radius || 0,
        backgroundColor: panel.background_color !== 'transparent' ? panel.background_color : undefined,
        padding: panel.padding,
        boxShadow: panel.box_shadow !== 'initial' ? panel.box_shadow : undefined,
      }}
    >
      {renderContent()}

      {/* 리사이즈 핸들 */}
      {isSelected && (
        <div
          onMouseDown={handleResizeMouseDown}
          style={{
            position: 'absolute',
            right: -4,
            bottom: -4,
            width: 8,
            height: 8,
            backgroundColor: '#4a90d9',
            cursor: 'se-resize',
            borderRadius: 2,
          }}
        />
      )}
    </div>
  )
}
