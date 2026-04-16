import React, { useRef, useEffect } from 'react'
import type { Panel } from '../../types/panel'
import { useEditorStore } from '../../stores/editorStore'

interface TextPanelProps {
  panel: Panel
  isHeadline?: boolean
  isEditing?: boolean
}

export function TextPanel({ panel, isHeadline = false, isEditing = false }: TextPanelProps) {
  const updatePanel = useEditorStore((s) => s.updatePanel)
  const ref = useRef<HTMLDivElement>(null)
  const text = isHeadline ? panel.headline : panel.text

  // Auto-focus when entering edit mode
  useEffect(() => {
    if (isEditing && ref.current) {
      ref.current.focus()
      // Place cursor at end
      const sel = window.getSelection()
      if (sel && ref.current.childNodes.length > 0) {
        sel.selectAllChildren(ref.current)
        sel.collapseToEnd()
      }
    }
  }, [isEditing])

  const textStyle: React.CSSProperties = {
    width: '100%',
    height: '100%',
    fontSize: panel.font_size,
    fontFamily: panel.font_family !== 'initial' ? panel.font_family : undefined,
    fontWeight: panel.font_bold ? 'bold' : (panel.font_weight !== 'initial' ? panel.font_weight : undefined),
    fontStyle: panel.font_italic ? 'italic' : (panel.font_style !== 'initial' ? panel.font_style : undefined),
    textDecoration: panel.text_underline ? 'underline' : (panel.text_decoration !== 'initial' ? panel.text_decoration : undefined),
    color: panel.color,
    textAlign: (panel.text_align !== 'initial' ? panel.text_align : undefined) as React.CSSProperties['textAlign'],
    letterSpacing: panel.letter_spacing || undefined,
    lineHeight: panel.line_height || undefined,
    textShadow: panel.text_shadow !== 'initial' ? panel.text_shadow : undefined,
    overflow: 'hidden',
    outline: 'none',
    border: 'none',
    background: 'transparent',
    resize: 'none',
    padding: 0,
    margin: 0,
    cursor: isEditing ? 'text' : 'inherit',
    userSelect: isEditing ? 'text' : 'none',
    pointerEvents: isEditing ? 'auto' : 'none',
  }

  const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
    const content = e.currentTarget.innerHTML
    updatePanel(panel.id, isHeadline ? { headline: content } : { text: content })
  }

  return (
    <div
      ref={ref}
      className={`bs-text-panel ${isHeadline ? 'bs-headline' : 'bs-body-text'}`}
      contentEditable={isEditing}
      suppressContentEditableWarning
      onInput={handleInput}
      style={textStyle}
      dangerouslySetInnerHTML={{ __html: text }}
    />
  )
}
