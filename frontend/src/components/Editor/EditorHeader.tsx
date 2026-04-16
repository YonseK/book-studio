import React from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { useHistoryStore } from '../../stores/historyStore'

export function EditorHeader() {
  const { edition, zoom, setZoom, theme } = useEditorStore()
  const { canUndo, canRedo, undo, redo } = useHistoryStore()

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 16px',
        height: 48,
        backgroundColor: theme === 'dark' ? '#16213e' : '#fff',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontWeight: 600, fontSize: 14 }}>
          {edition?.title || 'Untitled'}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <button
          onClick={() => undo()}
          disabled={!canUndo()}
          style={{ padding: '4px 8px', fontSize: 12, cursor: canUndo() ? 'pointer' : 'default', opacity: canUndo() ? 1 : 0.4 }}
          title="Undo (Ctrl+Z)"
        >
          ↩ Undo
        </button>
        <button
          onClick={() => redo()}
          disabled={!canRedo()}
          style={{ padding: '4px 8px', fontSize: 12, cursor: canRedo() ? 'pointer' : 'default', opacity: canRedo() ? 1 : 0.4 }}
          title="Redo (Ctrl+Shift+Z)"
        >
          ↪ Redo
        </button>

        <span style={{ margin: '0 8px', fontSize: 12, color: '#888' }}>|</span>

        <button onClick={() => setZoom(zoom - 0.1)} style={{ padding: '4px 8px', fontSize: 12 }}>−</button>
        <span style={{ fontSize: 12, minWidth: 40, textAlign: 'center' }}>{Math.round(zoom * 100)}%</span>
        <button onClick={() => setZoom(zoom + 0.1)} style={{ padding: '4px 8px', fontSize: 12 }}>+</button>
      </div>
    </div>
  )
}
