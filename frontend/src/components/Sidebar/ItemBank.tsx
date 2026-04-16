import React from 'react'

interface PubItemData {
  id: string
  title?: string
  image_url?: string
  width?: number
  height?: number
}

interface ItemBankProps {
  items: PubItemData[]
  onSelect?: (item: PubItemData) => void
}

export function ItemBank({ items, onSelect }: ItemBankProps) {
  return (
    <div style={{ padding: 12 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Item Bank</h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
        {items.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelect?.(item)}
            style={{
              borderRadius: 6,
              overflow: 'hidden',
              cursor: 'pointer',
              border: '1px solid #eee',
              backgroundColor: '#fff',
            }}
          >
            {item.image_url ? (
              <img
                src={item.image_url}
                alt={item.title || ''}
                style={{ width: '100%', aspectRatio: '1', objectFit: 'cover' }}
              />
            ) : (
              <div style={{ width: '100%', aspectRatio: '1', backgroundColor: '#f0f0f0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ fontSize: 10, color: '#999' }}>No image</span>
              </div>
            )}
            {item.title && (
              <div style={{ padding: '4px 6px', fontSize: 11, color: '#555', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {item.title}
              </div>
            )}
          </div>
        ))}
        {items.length === 0 && (
          <div style={{ gridColumn: '1 / -1', fontSize: 12, color: '#999', textAlign: 'center', padding: 20 }}>
            No items
          </div>
        )}
      </div>
    </div>
  )
}
