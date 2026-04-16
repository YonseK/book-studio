import React from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { LAYOUT_PRESETS, type LayoutConfig, type LayoutPreset } from '../../types/layout'

export function AspectRatioSelector() {
  const { layoutConfig, setLayoutConfig } = useEditorStore()

  const presets = Object.values(LAYOUT_PRESETS).filter((p) => p.preset !== 'BANNER')

  return (
    <div style={{ padding: 12 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Layout</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {presets.map((preset) => (
          <button
            key={preset.preset}
            onClick={() => setLayoutConfig(preset)}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '6px 8px',
              fontSize: 12,
              border: preset.preset === layoutConfig.preset ? '2px solid #4a90d9' : '1px solid #ddd',
              borderRadius: 4,
              backgroundColor: preset.preset === layoutConfig.preset ? '#e8f0fe' : '#fff',
              cursor: 'pointer',
              textAlign: 'left',
            }}
          >
            <span>{preset.label}</span>
            <span style={{ color: '#999', fontSize: 11 }}>
              {preset.width}×{preset.height}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
