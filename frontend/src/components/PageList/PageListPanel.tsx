import React from 'react'
import { useEditorStore } from '../../stores/editorStore'
import type { Page } from '../../types/page'

interface PageListPanelProps {
  onAddPage?: () => void
  onDeletePage?: (pageId: string) => void
}

export function PageListPanel({ onAddPage, onDeletePage }: PageListPanelProps) {
  const { pages, activePageId, setActivePage } = useEditorStore()

  return (
    <div style={{ padding: 8, display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 12, fontWeight: 600 }}>Pages</span>
        <button
          onClick={onAddPage}
          style={{
            fontSize: 11,
            padding: '3px 8px',
            border: '1px solid #ddd',
            borderRadius: 4,
            backgroundColor: '#fff',
            cursor: 'pointer',
          }}
        >
          + Add
        </button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {pages.map((page, idx) => (
          <PageThumbnail
            key={page.id}
            page={page}
            index={idx}
            isActive={page.id === activePageId}
            onClick={() => setActivePage(page.id)}
            onDelete={() => onDeletePage?.(page.id)}
          />
        ))}
      </div>
    </div>
  )
}

function PageThumbnail({
  page,
  index,
  isActive,
  onClick,
  onDelete,
}: {
  page: Page
  index: number
  isActive: boolean
  onClick: () => void
  onDelete: () => void
}) {
  return (
    <div
      onClick={onClick}
      style={{
        position: 'relative',
        aspectRatio: '16 / 9',
        borderRadius: 4,
        border: isActive ? '2px solid #4a90d9' : '1px solid #ddd',
        backgroundColor: page.background_color || '#fff',
        cursor: 'pointer',
        overflow: 'hidden',
        flexShrink: 0,
      }}
    >
      <span
        style={{
          position: 'absolute',
          bottom: 4,
          left: 6,
          fontSize: 10,
          color: '#666',
          backgroundColor: 'rgba(255,255,255,0.8)',
          padding: '1px 4px',
          borderRadius: 2,
        }}
      >
        {index + 1}
      </span>
    </div>
  )
}
