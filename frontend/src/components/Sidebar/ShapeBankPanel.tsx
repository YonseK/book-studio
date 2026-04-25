import React, { useCallback } from 'react'
import { Pentagon } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import { SHAPE_IDS_ORDERED } from '../Panel/ShapePanel'
import type { Panel } from '../../types/panel'
import { ColorPalettePicker } from '../common/ColorPalettePicker'

// Mini SVG renderers for the bank grid (simplified versions)
const SHAPE_PREVIEWS: Record<number, React.ReactNode> = {
  1: <path d="M2,10 L2,14 L16,14 L16,19 L22,12 L16,5 L16,10 Z" />,
  2: <><path d="M6,5 L6,10 L2,10 L2,14 L6,14 L6,19 L12,12 Z" /><path d="M18,5 L18,10 L22,10 L22,14 L18,14 L18,19 L12,12 Z" /></>,
  3: <path d="M1,2 L18,2 L23,12 L18,22 L1,22 Z" />,
  4: <path d="M4,2 L18,2 L23,12 L18,22 L4,22 L9,12 Z" />,
  5: <path d="M4,2 L20,2 L23,12 L20,22 L4,22 L1,12 Z" />,
  6: <rect x="1" y="3" width="22" height="18" rx="9" />,
  7: <circle cx="12" cy="12" r="11" />,
  8: <polygon points="12,2 22,22 2,22" />,
  9: <rect x="1" y="4" width="22" height="16" />,
  10: <polygon points="12,1 23,9 19.5,22 4.5,22 1,9" />,
  11: <polygon points="12,1 22.5,6.5 22.5,17.5 12,23 1.5,17.5 1.5,6.5" />,
  12: <polygon points="7.5,1 16.5,1 23,7.5 23,16.5 16.5,23 7.5,23 1,16.5 1,7.5" />,
  13: <path d="M12,21.35 C5.4,15.36 1.5,11.28 1.5,7.5 C1.5,4.42 3.86,2 6.75,2 C8.51,2 10.11,2.93 12,4.34 C13.89,2.93 15.49,2 17.25,2 C20.14,2 22.5,4.42 22.5,7.5 C22.5,11.28 18.6,15.36 12,21.35 Z" />,
  14: <polygon points="12,1 14.7,8.3 22.5,9.1 16.7,14.2 18.5,22 12,18.1 5.5,22 7.3,14.2 1.5,9.1 9.3,8.3" />,
  15: <polygon points="12,1 14,5.5 19,2.5 17,7 22,7.5 18.5,10.5 23,12 18.5,13.5 22,16.5 17,17 19,21.5 14,18.5 12,23 10,18.5 5,21.5 7,17 2,16.5 5.5,13.5 1,12 5.5,10.5 2,7.5 7,7 5,2.5 10,5.5" />,
  16: <rect x="1" y="9" width="22" height="6" rx="0.5" />,
  17: <line x1="1" y1="12" x2="23" y2="12" strokeWidth="2" strokeLinecap="round" />,
  18: <><line x1="4" y1="12" x2="20" y2="12" strokeWidth="2" /><circle cx="3" cy="12" r="2.5" /><circle cx="21" cy="12" r="2.5" /></>,
  19: <><line x1="4" y1="12" x2="20" y2="12" strokeWidth="2" /><polygon points="1,12 6,8 6,16" /><circle cx="21" cy="12" r="2.5" /></>,
  20: <path d="M5,2 L23,2 L19,22 L1,22 Z" />,
  21: <rect x="1" y="1" width="22" height="22" rx="3.5" />,
  22: <path d="M3,2 L21,2 Q23,2 23,4 L23,16 Q23,18 21,18 L8,18 L3,22 L4,18 L3,18 Q1,18 1,16 L1,4 Q1,2 3,2 Z" />,
  23: <path d="M3,2 L21,2 Q23,2 23,4 L23,16 Q23,18 21,18 L14,18 L12,22 L10,18 L3,18 Q1,18 1,16 L1,4 Q1,2 3,2 Z" />,
  24: <path d="M3,2 L21,2 Q23,2 23,4 L23,16 Q23,18 21,18 L20,18 L21,22 L16,18 L3,18 Q1,18 1,16 L1,4 Q1,2 3,2 Z" />,
}

export function ShapeBankPanel() {
  const { panels, activePageId, updatePanel, selectedPanelIds } = useEditorStore()
  const activePanels = activePageId ? (panels[activePageId] ?? []) : []
  const panel = activePanels.find((p) => selectedPanelIds.includes(p.id))

  const update = useCallback((data: Partial<Panel>) => {
    if (panel) updatePanel(panel.id, data)
  }, [panel, updatePanel])

  if (!panel) return null

  return (
    <div className="bs-shapebank">
      {/* Header */}
      <div className="bs-textbank__header">
        <Pentagon size={14} />
        <span>도형</span>
      </div>

      {/* Controllers */}
      <div className="bs-textbank__options">
        {/* Opacity */}
        <div className="bs-textbank__section">
          <div className="bs-textbank__section-label">
            <span>도형 투명도</span>
            <span className="bs-textbank__value">{panel.opacity}</span>
          </div>
          <input
            type="range" min="0" max="1" step="0.05"
            value={panel.opacity}
            onChange={(e) => update({ opacity: Number(e.target.value) })}
            className="bs-textbank__slider"
          />
        </div>

        {/* Shape color */}
        <div className="bs-textbank__section">
          <div className="bs-textbank__section-label">
            <span>도형 색상</span>
          </div>
          <ColorPalettePicker
            value={panel.color === 'initial' ? '#000000' : panel.color}
            onChange={(c) => update({ color: c })}
            label="도형 색상"
          />
        </div>

        {/* Border width */}
        <div className="bs-textbank__section">
          <div className="bs-textbank__section-label">
            <span>테두리 두께</span>
            <span className="bs-textbank__value">{panel.stroke_width || panel.border_width}</span>
          </div>
          <input
            type="range" min="0" max="10" step="0.5"
            value={panel.stroke_width || panel.border_width}
            onChange={(e) => update({ stroke_width: Number(e.target.value), border_width: Number(e.target.value) })}
            className="bs-textbank__slider"
          />
        </div>

        {/* Border color */}
        <div className="bs-textbank__section">
          <div className="bs-textbank__section-label">
            <span>테두리 색상</span>
          </div>
          <ColorPalettePicker
            value={panel.border_color === 'initial' ? '#000000' : panel.border_color}
            onChange={(c) => update({ border_color: c })}
            label="테두리 색상"
          />
        </div>

        {/* Border opacity */}
        <div className="bs-textbank__section">
          <div className="bs-textbank__section-label">
            <span>테두리 투명도</span>
            <span className="bs-textbank__value">{panel.border_opacity}</span>
          </div>
          <input
            type="range" min="0" max="1" step="0.05"
            value={panel.border_opacity}
            onChange={(e) => update({ border_opacity: Number(e.target.value) })}
            className="bs-textbank__slider"
          />
        </div>

        {/* Drop shadow */}
        <div className="bs-textbank__section">
          <div className="bs-textbank__section-label">
            <span>그림자</span>
            <span className="bs-textbank__value">{panel.drop_shadow_px}</span>
          </div>
          <input
            type="range" min="0" max="20" step="1"
            value={panel.drop_shadow_px}
            onChange={(e) => {
              const px = Number(e.target.value)
              update({
                drop_shadow_px: px,
                box_shadow: px > 0 ? `0 ${px}px ${px * 2}px rgba(0,0,0,0.3)` : 'initial',
              })
            }}
            className="bs-textbank__slider"
          />
        </div>
      </div>

      {/* Shape Bank Grid */}
      <div className="bs-shapebank__grid-header">
        <Pentagon size={13} />
        <span>도형 뱅크</span>
      </div>
      <div className="bs-shapebank__grid">
        {SHAPE_IDS_ORDERED.map((shapeId) => {
          const isActive = panel.shape_type === shapeId
          return (
            <button
              key={shapeId}
              className={`bs-shapebank__item${isActive ? ' bs-shapebank__item--active' : ''}`}
              onClick={() => update({ shape_type: shapeId })}
            >
              <svg viewBox="0 0 24 24" className="bs-shapebank__svg">
                {SHAPE_PREVIEWS[shapeId]}
              </svg>
            </button>
          )
        })}
      </div>
    </div>
  )
}
