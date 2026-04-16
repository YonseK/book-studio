import React from 'react'
import { X, Check } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'

export function EditorOptions() {
  const {
    showGrid, toggleGrid,
    showGuides, toggleGuides,
    snapToGrid, toggleSnap,
    gridSize, setGridSize,
    theme, setTheme,
  } = useEditorStore()

  return (
    <div>
      <div className="bs-options__section">
        <div className="bs-options__label">그리드 보이기/감추기</div>
        <Toggle checked={showGrid} onChange={toggleGrid} />
      </div>

      <div className="bs-options__section">
        <div className="bs-options__label">그리드 색상 선택</div>
        <div className="bs-options__grid-icons">
          {[10, 20, 40, 80].map((size) => (
            <button
              key={size}
              className={`bs-options__grid-icon${gridSize === size ? ' bs-options__grid-icon--active' : ''}`}
              onClick={() => setGridSize(size)}
              title={`${size}px`}
            >
              <GridPattern size={size} />
            </button>
          ))}
        </div>
      </div>

      <div className="bs-options__section">
        <div className="bs-options__label">그리드에 자석</div>
        <Toggle checked={snapToGrid} onChange={toggleSnap} />
      </div>

      <div className="bs-options__divider" />

      <div className="bs-options__section">
        <div className="bs-options__label">가이드 라인 보이기/감추기</div>
        <div className="bs-options__row">
          <Toggle checked={showGuides} onChange={toggleGuides} />
          <span style={{ fontSize: 12, color: 'var(--bs-text-secondary)' }}>
            {showGuides ? 'ON' : 'OFF'}
          </span>
        </div>
      </div>

      <div className="bs-options__divider" />

      <div className="bs-options__section">
        <div className="bs-options__label">컬러 테마</div>
        <div className="bs-options__theme-cards">
          <button
            className={`bs-options__theme-card${theme === 'light' ? ' bs-options__theme-card--active' : ''}`}
            onClick={() => setTheme('light')}
          >
            <div style={{ width: '100%', height: '100%', backgroundColor: '#f5f5f5' }} />
            {theme === 'light' && (
              <div className="bs-options__theme-card-check">
                <Check size={20} />
              </div>
            )}
          </button>
          <button
            className={`bs-options__theme-card${theme === 'dark' ? ' bs-options__theme-card--active' : ''}`}
            onClick={() => setTheme('dark')}
          >
            <div style={{ width: '100%', height: '100%', backgroundColor: '#1e1e1e' }} />
            {theme === 'dark' && (
              <div className="bs-options__theme-card-check">
                <Check size={20} />
              </div>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button className={`bs-toggle${checked ? ' bs-toggle--on' : ''}`} onClick={onChange}>
      <div className="bs-toggle__track" />
      <div className="bs-toggle__thumb" />
    </button>
  )
}

function GridPattern({ size }: { size: number }) {
  const lines = size <= 20 ? 4 : size <= 40 ? 3 : 2
  const gap = 22 / (lines + 1)
  return (
    <svg width="22" height="22" viewBox="0 0 22 22">
      {Array.from({ length: lines }, (_, i) => {
        const pos = gap * (i + 1)
        return (
          <React.Fragment key={i}>
            <line x1={pos} y1="0" x2={pos} y2="22" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
            <line x1="0" y1={pos} x2="22" y2={pos} stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
          </React.Fragment>
        )
      })}
    </svg>
  )
}
