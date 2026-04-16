import React from 'react'
import type { Panel } from '../../types/panel'
import { useEditorStore } from '../../stores/editorStore'

interface TextPanelProps {
  panel: Panel
  isHeadline?: boolean
}

export function TextPanel({ panel, isHeadline = false }: TextPanelProps) {
  const updatePanel = useEditorStore((s) => s.updatePanel)
  const text = isHeadline ? panel.headline : panel.text

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
  }

  const handleInput = (e: React.FormEvent<HTMLDivElement>) => {
    const content = e.currentTarget.innerHTML
    updatePanel(panel.id, isHeadline ? { headline: content } : { text: content })
  }

  return (
    <div
      className={`bs-text-panel ${isHeadline ? 'bs-headline' : 'bs-body-text'}`}
      contentEditable
      suppressContentEditableWarning
      onInput={handleInput}
      style={textStyle}
      dangerouslySetInnerHTML={{ __html: text }}
    />
  )
}
