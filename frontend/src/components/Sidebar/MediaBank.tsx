import React, { useState } from 'react'

type BankTab = 'IMAGE' | 'WALLPAPER' | 'WIDGET' | 'EFFECT' | 'VIDEO'

interface MediaItem {
  id: string
  title?: string
  image_url?: string
  bank_type: string
}

interface MediaBankProps {
  items: MediaItem[]
  onSelect?: (item: MediaItem) => void
  onUpload?: (file: File) => void
}

const TABS: { key: BankTab; label: string }[] = [
  { key: 'IMAGE', label: 'Images' },
  { key: 'WALLPAPER', label: 'Wallpapers' },
  { key: 'WIDGET', label: 'Widgets' },
  { key: 'EFFECT', label: 'Effects' },
  { key: 'VIDEO', label: 'Videos' },
]

export function MediaBank({ items, onSelect, onUpload }: MediaBankProps) {
  const [activeTab, setActiveTab] = useState<BankTab>('IMAGE')

  const bankTypeMap: Record<BankTab, string> = {
    IMAGE: 'IMG',
    WALLPAPER: 'WP',
    WIDGET: 'WGT',
    EFFECT: 'FX',
    VIDEO: 'VOD',
  }

  const filtered = items.filter((i) => i.bank_type === bankTypeMap[activeTab])

  return (
    <div style={{ padding: 12 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Media Bank</h3>

      <div style={{ display: 'flex', gap: 4, marginBottom: 8, flexWrap: 'wrap' }}>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '3px 8px',
              fontSize: 11,
              border: activeTab === tab.key ? '1px solid #4a90d9' : '1px solid #ddd',
              borderRadius: 4,
              backgroundColor: activeTab === tab.key ? '#e8f0fe' : '#fff',
              cursor: 'pointer',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {onUpload && (
        <label
          style={{
            display: 'block',
            marginBottom: 8,
            padding: '8px 0',
            textAlign: 'center',
            border: '1px dashed #ccc',
            borderRadius: 4,
            cursor: 'pointer',
            fontSize: 12,
            color: '#666',
          }}
        >
          + Upload
          <input
            type="file"
            accept="image/*,video/*"
            style={{ display: 'none' }}
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) onUpload(file)
            }}
          />
        </label>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 6 }}>
        {filtered.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelect?.(item)}
            style={{
              aspectRatio: '1',
              borderRadius: 4,
              overflow: 'hidden',
              cursor: 'pointer',
              border: '1px solid #eee',
              backgroundColor: '#f8f8f8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {item.image_url ? (
              <img src={item.image_url} alt={item.title || ''} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <span style={{ fontSize: 10, color: '#999' }}>{item.title || item.id.slice(0, 6)}</span>
            )}
          </div>
        ))}
        {filtered.length === 0 && (
          <div style={{ gridColumn: '1 / -1', fontSize: 12, color: '#999', textAlign: 'center', padding: 20 }}>
            No items
          </div>
        )}
      </div>
    </div>
  )
}
