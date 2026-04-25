import React from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { LAYOUT_PRESETS } from '../../types/layout'

export function AspectRatioSelector() {
  const { layoutConfig, setLayoutConfig } = useEditorStore()

  const presets = Object.values(LAYOUT_PRESETS).filter((p) => p.preset !== 'BANNER')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {presets.map((preset) => {
        const isActive = preset.preset === layoutConfig.preset
        // 미니 프리뷰: 최대 28px 기준으로 비율 계산
        const maxDim = 28
        const ratio = preset.width / preset.height
        const pw = ratio >= 1 ? maxDim : Math.round(maxDim * ratio)
        const ph = ratio >= 1 ? Math.round(maxDim / ratio) : maxDim

        return (
          <button
            key={preset.preset}
            onClick={() => setLayoutConfig(preset)}
            className={`bs-layout-btn${isActive ? ' bs-layout-btn--active' : ''}`}
          >
            <div className="bs-layout-btn__preview" style={{ width: pw, height: ph }} />
            <span className="bs-layout-btn__label">{preset.label}</span>
            <span className="bs-layout-btn__size">
              {preset.width}×{preset.height}
            </span>
          </button>
        )
      })}
    </div>
  )
}
