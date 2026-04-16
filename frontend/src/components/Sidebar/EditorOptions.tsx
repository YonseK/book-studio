import React from 'react'
import { useEditorStore } from '../../stores/editorStore'

export function EditorOptions() {
  const {
    showGrid, toggleGrid,
    showGuides, toggleGuides,
    snapToGrid, toggleSnap,
    gridSize, setGridSize,
    theme, setTheme,
  } = useEditorStore()

  const checkboxStyle: React.CSSProperties = { marginRight: 8 }
  const rowStyle: React.CSSProperties = { display: 'flex', alignItems: 'center', padding: '6px 0', fontSize: 13 }

  return (
    <div style={{ padding: 12 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Options</h3>

      <div style={rowStyle}>
        <input type="checkbox" checked={showGrid} onChange={toggleGrid} style={checkboxStyle} />
        Show Grid
      </div>

      <div style={rowStyle}>
        <input type="checkbox" checked={showGuides} onChange={toggleGuides} style={checkboxStyle} />
        Show Guides
      </div>

      <div style={rowStyle}>
        <input type="checkbox" checked={snapToGrid} onChange={toggleSnap} style={checkboxStyle} />
        Snap to Grid
      </div>

      <div style={rowStyle}>
        <span style={{ marginRight: 8 }}>Grid size:</span>
        <select
          value={gridSize}
          onChange={(e) => setGridSize(Number(e.target.value))}
          style={{ fontSize: 12, padding: '2px 4px' }}
        >
          {[10, 20, 40, 80].map((s) => (
            <option key={s} value={s}>{s}px</option>
          ))}
        </select>
      </div>

      <div style={rowStyle}>
        <span style={{ marginRight: 8 }}>Theme:</span>
        <select
          value={theme}
          onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
          style={{ fontSize: 12, padding: '2px 4px' }}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </div>
    </div>
  )
}
