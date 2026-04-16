import React, { useCallback } from 'react'
import { Upload, Circle, Square, RotateCw } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import { useSelectionStore } from '../../stores/selectionStore'
import type { Panel } from '../../types/panel'

export function ImageBankPanel() {
  const { panels, activePageId, updatePanel } = useEditorStore()
  const { selectedPanelIds } = useSelectionStore()
  const activePanels = activePageId ? (panels[activePageId] ?? []) : []
  const panel = activePanels.find((p) => selectedPanelIds.includes(p.id))

  const update = useCallback((data: Partial<Panel>) => {
    if (panel) updatePanel(panel.id, data)
  }, [panel, updatePanel])

  if (!panel) return null

  const imageUrl: string = (panel.fields_data as any)?.image_url || ''

  return (
    <div>
      {/* Image URL / Upload */}
      <div className="bs-options__section">
        <div className="bs-options__label">이미지</div>
        {imageUrl ? (
          <div style={{
            width: '100%', aspectRatio: '16/9', borderRadius: 4,
            overflow: 'hidden', backgroundColor: 'var(--bs-bg-tertiary)',
            marginBottom: 8,
          }}>
            <img src={imageUrl} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
        ) : (
          <div style={{
            width: '100%', height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center',
            backgroundColor: 'var(--bs-bg-tertiary)', borderRadius: 4, marginBottom: 8,
            color: 'var(--bs-text-muted)', fontSize: 12,
          }}>
            이미지 없음
          </div>
        )}
        <button
          style={{
            width: '100%', height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: 6, backgroundColor: 'var(--bs-bg-tertiary)', borderRadius: 4,
            color: 'var(--bs-text-secondary)', fontSize: 12, cursor: 'pointer',
          }}
        >
          <Upload size={14} />
          이미지 업로드
        </button>
      </div>

      {/* Image URL input */}
      <div className="bs-options__section">
        <div className="bs-options__label">이미지 URL</div>
        <input
          type="text"
          value={imageUrl}
          onChange={(e) => update({ fields_data: { ...panel.fields_data, image_url: e.target.value } })}
          placeholder="https://..."
          style={{
            width: '100%', height: 32, padding: '0 8px',
            backgroundColor: 'var(--bs-bg-tertiary)', borderRadius: 4,
            fontSize: 12, color: 'var(--bs-text-primary)',
          }}
        />
      </div>

      {/* Border Radius */}
      <div className="bs-options__section">
        <div className="bs-options__label">모서리 둥글기</div>
        <input
          type="range" min="0" max="50" step="1"
          value={panel.border_radius}
          onChange={(e) => update({ border_radius: Number(e.target.value) })}
          style={{ width: '100%', accentColor: 'var(--bs-accent)' }}
        />
        <span style={{ fontSize: 11, color: 'var(--bs-text-secondary)' }}>{panel.border_radius}px</span>
      </div>

      {/* Opacity */}
      <div className="bs-options__section">
        <div className="bs-options__label">투명도</div>
        <input
          type="range" min="0" max="1" step="0.05"
          value={panel.opacity}
          onChange={(e) => update({ opacity: Number(e.target.value) })}
          style={{ width: '100%', accentColor: 'var(--bs-accent)' }}
        />
        <span style={{ fontSize: 11, color: 'var(--bs-text-secondary)' }}>{Math.round(panel.opacity * 100)}%</span>
      </div>

      {/* Rotation */}
      <div className="bs-options__section">
        <div className="bs-options__label">회전</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input
            type="range" min="0" max="360" step="1"
            value={panel.rotate || 0}
            onChange={(e) => update({ rotate: Number(e.target.value) })}
            style={{ flex: 1, accentColor: 'var(--bs-accent)' }}
          />
          <span style={{ fontSize: 11, color: 'var(--bs-text-secondary)', minWidth: 36 }}>{panel.rotate || 0}&deg;</span>
        </div>
      </div>

      {/* Shadow */}
      <div className="bs-options__section">
        <div className="bs-options__label">그림자</div>
        <input
          type="range" min="0" max="30" step="1"
          value={panel.drop_shadow_px}
          onChange={(e) => {
            const px = Number(e.target.value)
            update({
              drop_shadow_px: px,
              box_shadow: px > 0 ? `0 ${px}px ${px * 2}px rgba(0,0,0,0.3)` : 'initial',
            })
          }}
          style={{ width: '100%', accentColor: 'var(--bs-accent)' }}
        />
        <span style={{ fontSize: 11, color: 'var(--bs-text-secondary)' }}>{panel.drop_shadow_px}px</span>
      </div>
    </div>
  )
}
