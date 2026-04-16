import React from 'react'
import { Trash2, Image, Pipette, Check } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import colorPalette from '../../data/colorPalette.json'

interface WallpaperItem {
  id: string
  image_url: string
  image_view_url?: string
  image_thumb_url?: string
  title?: string
}

interface WallpaperBankProps {
  wallpapers: WallpaperItem[]
  onSelect?: (wallpaper: WallpaperItem) => void
}

/** Flatten spectrum rows into a single array */
const SPECTRUM_COLORS: string[] = colorPalette.spectrum.flat()

export function WallpaperBank({ wallpapers, onSelect }: WallpaperBankProps) {
  const { pages, activePageId, updatePage } = useEditorStore()
  const activePage = pages.find((p) => p.id === activePageId)

  const isWallpaperMode = activePage?.background_type !== 'CLR'

  const setBgColor = (color: string) => {
    if (!activePageId) return
    updatePage(activePageId, { background_color: color })
  }

  const setBgOpacity = (opacity: number) => {
    if (!activePageId) return
    updatePage(activePageId, { opacity })
  }

  return (
    <div>
      {/* Header */}
      <div className="bs-wallpaper__header">
        <div className="bs-wallpaper__header-title">
          <Image size={14} />
          <span>배경</span>
        </div>
      </div>

      {isWallpaperMode ? (
        /* ── Wallpaper Mode ── */
        <>
          {/* Opacity */}
          <div className="bs-wallpaper__section">
            <div className="bs-textbank__section-label">
              <span>배경색 투명도</span>
              <span className="bs-textbank__value">{activePage?.opacity ?? 1}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.05"
              value={activePage?.opacity ?? 1}
              onChange={(e) => setBgOpacity(Number(e.target.value))}
              className="bs-textbank__slider"
            />
          </div>

          {/* Wallpaper grid */}
          <div className="bs-wallpaper__bank-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 600 }}>
              <Image size={13} />
              <span>월페이퍼 뱅크</span>
            </div>
            <button
              style={{
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                width: 22, height: 22, borderRadius: 4,
                color: 'var(--bs-text-muted)', cursor: 'pointer',
              }}
              title="모두 삭제"
            >
              <Trash2 size={13} />
            </button>
          </div>
          <div className="bs-wallpaper__grid">
            {wallpapers.map((wp) => {
              const viewUrl = wp.image_view_url || wp.image_url
              const thumbUrl = wp.image_thumb_url || wp.image_url
              const isActive = activePage?.wallpaper_image === viewUrl
                || activePage?.wallpaper === viewUrl
              return (
                <div
                  key={wp.id}
                  onClick={() => onSelect?.(wp)}
                  className={`bs-wallpaper__item${isActive ? ' bs-wallpaper__item--active' : ''}`}
                >
                  <img
                    src={thumbUrl}
                    alt={wp.title || ''}
                    loading="lazy"
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                  />
                  {isActive && (
                    <div className="bs-wallpaper__item-check">
                      <Check size={24} strokeWidth={3} />
                    </div>
                  )}
                </div>
              )
            })}
            {wallpapers.length === 0 && (
              <div style={{
                gridColumn: '1 / -1', fontSize: 12, color: 'var(--bs-text-muted)',
                textAlign: 'center', padding: 20,
              }}>
                No wallpapers
              </div>
            )}
          </div>
        </>
      ) : (
        /* ── Color Mode ── */
        <>
          {/* Opacity */}
          <div className="bs-wallpaper__section">
            <div className="bs-textbank__section-label">
              <Pipette size={11} />
              <span>배경색 투명도</span>
              <span className="bs-textbank__value">{activePage?.opacity ?? 1}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.05"
              value={activePage?.opacity ?? 1}
              onChange={(e) => setBgOpacity(Number(e.target.value))}
              className="bs-textbank__slider"
            />
          </div>

          {/* Color label */}
          <div className="bs-wallpaper__section">
            <div className="bs-textbank__section-label">
              <Pipette size={11} />
              <span>배경 색상</span>
            </div>

            {/* Transparent button */}
            <button
              className="bs-wallpaper__transparent-btn"
              onClick={() => setBgColor('transparent')}
            >
              <span className="bs-wallpaper__transparent-checker" />
              <span>Transparent</span>
            </button>

            {/* Basic vivid colors (11 cells) */}
            <div className="bs-wallpaper__color-grid bs-wallpaper__color-grid--11col">
              {colorPalette.basic.slice(1).map((c, i) => (
                <button
                  key={`basic-${i}`}
                  className={`bs-wallpaper__color-cell${activePage?.background_color === c ? ' bs-wallpaper__color-cell--active' : ''}${c === '#ffffff' ? ' bs-wallpaper__color-cell--white' : ''}`}
                  style={{ backgroundColor: c }}
                  onClick={() => setBgColor(c)}
                  title={c}
                />
              ))}
            </div>

            {/* Pastel colors (11 cells) */}
            <div className="bs-wallpaper__color-grid bs-wallpaper__color-grid--11col">
              {colorPalette.pastel.map((c, i) => (
                <button
                  key={`pastel-${i}`}
                  className={`bs-wallpaper__color-cell${activePage?.background_color === c ? ' bs-wallpaper__color-cell--active' : ''}`}
                  style={{ backgroundColor: c }}
                  onClick={() => setBgColor(c)}
                  title={c}
                />
              ))}
            </div>

            {/* Gray scale (22 cells = 2 rows of 11) */}
            <div className="bs-wallpaper__color-grid bs-wallpaper__color-grid--11col">
              {colorPalette.grays.map((c, i) => (
                <button
                  key={`gray-${i}`}
                  className={`bs-wallpaper__color-cell${activePage?.background_color === c ? ' bs-wallpaper__color-cell--active' : ''}`}
                  style={{ backgroundColor: c }}
                  onClick={() => setBgColor(c)}
                  title={c}
                />
              ))}
            </div>

            {/* Full spectrum grid (65 rows x 11 cols) */}
            <div className="bs-wallpaper__color-grid bs-wallpaper__color-grid--spectrum">
              {SPECTRUM_COLORS.map((c, i) => (
                <button
                  key={`spec-${i}`}
                  className={`bs-wallpaper__color-cell${activePage?.background_color === c ? ' bs-wallpaper__color-cell--active' : ''}`}
                  style={{ backgroundColor: c }}
                  onClick={() => setBgColor(c)}
                />
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
