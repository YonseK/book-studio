import React from 'react'
import { useEditorStore } from '../../stores/editorStore'

interface WallpaperItem {
  id: string
  image_url: string
  title?: string
}

interface WallpaperBankProps {
  wallpapers: WallpaperItem[]
  onSelect?: (wallpaper: WallpaperItem) => void
}

export function WallpaperBank({ wallpapers, onSelect }: WallpaperBankProps) {
  return (
    <div style={{ padding: 12 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Wallpapers</h3>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 6,
        }}
      >
        {wallpapers.map((wp) => (
          <div
            key={wp.id}
            onClick={() => onSelect?.(wp)}
            style={{
              aspectRatio: '16 / 9',
              borderRadius: 4,
              overflow: 'hidden',
              cursor: 'pointer',
              border: '2px solid transparent',
            }}
          >
            <img
              src={wp.image_url}
              alt={wp.title || ''}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </div>
        ))}
        {wallpapers.length === 0 && (
          <div style={{ gridColumn: '1 / -1', fontSize: 12, color: '#999', textAlign: 'center', padding: 20 }}>
            No wallpapers
          </div>
        )}
      </div>
    </div>
  )
}
