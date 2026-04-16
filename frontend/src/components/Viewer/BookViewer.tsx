import React, { useState } from 'react'
import type { LayoutConfig } from '../../types/layout'

interface ViewerPage {
  id: string
  order: number
  html: string
}

interface BookViewerProps {
  pages: ViewerPage[]
  layout: LayoutConfig
  title?: string
}

export function BookViewer({ pages, layout, title }: BookViewerProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const total = pages.length

  if (total === 0) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#999' }}>
        No pages to display
      </div>
    )
  }

  const currentPage = pages[currentIndex]

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        height: '100%',
        backgroundColor: '#2c2c2c',
        color: '#fff',
      }}
    >
      {/* Header */}
      <div style={{ padding: '12px 20px', width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 14, fontWeight: 600 }}>{title || 'Book Viewer'}</span>
        <span style={{ fontSize: 12, color: '#aaa' }}>
          {currentIndex + 1} / {total}
        </span>
      </div>

      {/* Page */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 20,
          width: '100%',
        }}
      >
        <div
          style={{
            width: layout.width,
            height: layout.height,
            maxWidth: '100%',
            maxHeight: '100%',
            backgroundColor: '#fff',
            boxShadow: '0 4px 30px rgba(0,0,0,0.3)',
            overflow: 'hidden',
            borderRadius: 4,
          }}
          dangerouslySetInnerHTML={{ __html: currentPage.html }}
        />
      </div>

      {/* Navigation */}
      <div style={{ padding: '12px 20px', display: 'flex', gap: 12 }}>
        <button
          onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          disabled={currentIndex === 0}
          style={{ padding: '6px 16px', cursor: currentIndex > 0 ? 'pointer' : 'default', opacity: currentIndex > 0 ? 1 : 0.4 }}
        >
          ← Prev
        </button>
        <button
          onClick={() => setCurrentIndex((i) => Math.min(total - 1, i + 1))}
          disabled={currentIndex === total - 1}
          style={{ padding: '6px 16px', cursor: currentIndex < total - 1 ? 'pointer' : 'default', opacity: currentIndex < total - 1 ? 1 : 0.4 }}
        >
          Next →
        </button>
      </div>
    </div>
  )
}
