import React, { useState } from 'react'
import type { Panel } from '../../types/panel'
import { useEditorStore } from '../../stores/editorStore'

interface EmbedPanelProps {
  panel: Panel
}

export function EmbedPanel({ panel }: EmbedPanelProps) {
  const updatePanel = useEditorStore((s) => s.updatePanel)
  const url = panel.link_url || (panel.fields_data?.embed_url as string) || ''
  const [editing, setEditing] = useState(!url)
  const [inputUrl, setInputUrl] = useState(url)

  if (!url || editing) {
    return (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f8f8f8',
          border: '2px dashed #ccc',
          borderRadius: panel.border_radius || 0,
          padding: 16,
          gap: 8,
        }}
      >
        <span style={{ fontSize: 12, color: '#666' }}>Embed URL</span>
        <input
          type="url"
          value={inputUrl}
          onChange={(e) => setInputUrl(e.target.value)}
          placeholder="https://..."
          style={{
            width: '80%',
            padding: '6px 8px',
            fontSize: 12,
            border: '1px solid #ccc',
            borderRadius: 4,
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && inputUrl) {
              updatePanel(panel.id, { link_url: inputUrl })
              setEditing(false)
            }
          }}
        />
        <button
          onClick={() => {
            if (inputUrl) {
              updatePanel(panel.id, { link_url: inputUrl })
              setEditing(false)
            }
          }}
          style={{ padding: '4px 12px', fontSize: 11, cursor: 'pointer' }}
        >
          Embed
        </button>
      </div>
    )
  }

  return (
    <iframe
      src={url}
      style={{ width: '100%', height: '100%', border: 'none', borderRadius: panel.border_radius || 0 }}
      sandbox="allow-scripts allow-same-origin allow-popups"
      onDoubleClick={() => setEditing(true)}
    />
  )
}
