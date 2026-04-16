import React from 'react'
import { useEditorStore } from '../../stores/editorStore'
import type { MediaType } from '../../types/panel'

interface ToolDef {
  type: MediaType
  label: string
  icon: string
}

const TOOLS: ToolDef[] = [
  { type: 'HL', label: 'Headline', icon: 'H' },
  { type: 'TXT', label: 'Text', icon: 'T' },
  { type: 'IMG', label: 'Image', icon: '🖼' },
  { type: 'SHA', label: 'Shape', icon: '◇' },
  { type: 'VOD', label: 'Video', icon: '▶' },
  { type: 'FILE', label: 'File', icon: '📎' },
]

interface ToolbarStripProps {
  onAddPanel?: (type: MediaType) => void
}

export function ToolbarStrip({ onAddPanel }: ToolbarStripProps) {
  return (
    <>
      {TOOLS.map((tool) => (
        <button
          key={tool.type}
          onClick={() => onAddPanel?.(tool.type)}
          title={tool.label}
          style={{
            width: 36,
            height: 36,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid #ddd',
            borderRadius: 6,
            backgroundColor: 'transparent',
            cursor: 'pointer',
            fontSize: 16,
          }}
        >
          {tool.icon}
        </button>
      ))}
    </>
  )
}
