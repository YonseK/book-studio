import React from 'react'
import { Check } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'

export function EditorOptions() {
  const {
    showGrid, toggleGrid,
    showGuides, toggleGuides,
    snapToGrid, toggleSnap,
    gridSize, setGridSize,
    theme, setTheme,
    accentTheme, setAccentTheme,
  } = useEditorStore()

  return (
    <div>
      {/* ── 그리드 ON/OFF ── */}
      <div className="bs-options__section">
        <div className="bs-options__label">그리드 보이기/감추기</div>
        <div className="bs-options__row">
          <Toggle checked={showGrid} onChange={toggleGrid} />
          <span className="bs-options__status">{showGrid ? 'ON' : 'OFF'}</span>
        </div>
      </div>

      {/* ── 그리드 크기 선택 ── */}
      <div className={`bs-options__section${!showGrid ? ' bs-options__section--disabled' : ''}`}>
        <div className="bs-options__label">그리드 크기 선택</div>
        <div className="bs-options__grid-icons">
          {[10, 20, 40, 80].map((size) => (
            <button
              key={size}
              className={`bs-options__grid-icon${gridSize === size ? ' bs-options__grid-icon--active' : ''}`}
              onClick={() => setGridSize(size)}
              title={`${size}px`}
              disabled={!showGrid}
            >
              <GridPattern size={size} />
            </button>
          ))}
        </div>
      </div>

      {/* ── 스냅 ── */}
      <div className={`bs-options__section${!showGrid ? ' bs-options__section--disabled' : ''}`}>
        <div className="bs-options__label">그리드에 자석</div>
        <div className="bs-options__row">
          <Toggle checked={snapToGrid} onChange={toggleSnap} />
          <span className="bs-options__status">{snapToGrid ? 'ON' : 'OFF'}</span>
        </div>
      </div>

      <div className="bs-options__divider" />

      {/* ── 가이드라인 ── */}
      <div className="bs-options__section">
        <div className="bs-options__label">가이드 라인 보이기/감추기</div>
        <div className="bs-options__row">
          <Toggle checked={showGuides} onChange={toggleGuides} />
          <span className="bs-options__status">{showGuides ? 'ON' : 'OFF'}</span>
        </div>
      </div>

      <div className="bs-options__divider" />

      {/* ── 컬러 테마 ── */}
      <div className="bs-options__section">
        <div className="bs-options__label">컬러 테마</div>
        <div className="bs-options__theme-cards">
          <button
            className={`bs-options__theme-card${theme === 'dark' ? ' bs-options__theme-card--active' : ''}`}
            onClick={() => setTheme('dark')}
            title="다크 테마"
          >
            <div className="bs-options__theme-card-preview bs-options__theme-card-preview--dark" />
            {theme === 'dark' && (
              <div className="bs-options__theme-card-check">
                <Check size={20} />
              </div>
            )}
          </button>
          <button
            className={`bs-options__theme-card${theme === 'light' ? ' bs-options__theme-card--active' : ''}`}
            onClick={() => setTheme('light')}
            title="라이트 테마"
          >
            <div className="bs-options__theme-card-preview bs-options__theme-card-preview--light" />
            {theme === 'light' && (
              <div className="bs-options__theme-card-check">
                <Check size={20} />
              </div>
            )}
          </button>
        </div>
      </div>

      <div className="bs-options__divider" />

      {/* ── 악센트 테마 ── */}
      <div className="bs-options__section">
        <div className="bs-options__label">악센트 컬러</div>
        <div className="bs-options__accent-cards">
          {ACCENT_THEMES.map((t) => (
            <button
              key={t.key}
              className={`bs-options__accent-btn${accentTheme === t.key ? ' bs-options__accent-btn--active' : ''}`}
              onClick={() => setAccentTheme(t.key)}
              title={t.label}
            >
              <div className="bs-options__accent-swatch" style={{ background: t.gradient }} />
              {accentTheme === t.key && (
                <div className="bs-options__accent-check">
                  <Check size={14} strokeWidth={3} />
                </div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

const ACCENT_THEMES: { key: 'a' | 'b' | 'c' | 'd'; label: string; gradient: string }[] = [
  { key: 'a', label: '바이올렛', gradient: 'linear-gradient(135deg, #f08c78, #b6259c)' },
  { key: 'b', label: '그린', gradient: 'linear-gradient(135deg, #82be64, #008278)' },
  { key: 'c', label: '레드', gradient: 'linear-gradient(135deg, #e6a050, #c81432)' },
  { key: 'd', label: '옐로', gradient: 'linear-gradient(135deg, #c8c832, #1abcdf)' },
]

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
