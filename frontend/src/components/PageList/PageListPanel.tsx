import React, { useState } from 'react'
import { Plus, MoreHorizontal, ChevronLeft, ChevronRight } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import { PageContextMenu } from './PageContextMenu'
import type { Page } from '../../types/page'

interface PageListPanelProps {
  onAddPage?: () => void
  onDeletePage?: (pageId: string) => void
  onDuplicatePage?: (pageId: string) => void
}

export function PageListPanel({ onAddPage, onDeletePage, onDuplicatePage }: PageListPanelProps) {
  const { pages, activePageId, setActivePage, isPageListCollapsed, togglePageList, reorderPages } = useEditorStore()

  const handleMoveUp = (pageId: string) => {
    const idx = pages.findIndex((p) => p.id === pageId)
    if (idx <= 0) return
    const ids = pages.map((p) => p.id)
    ;[ids[idx - 1], ids[idx]] = [ids[idx], ids[idx - 1]]
    reorderPages(ids)
  }

  const handleMoveDown = (pageId: string) => {
    const idx = pages.findIndex((p) => p.id === pageId)
    if (idx < 0 || idx >= pages.length - 1) return
    const ids = pages.map((p) => p.id)
    ;[ids[idx], ids[idx + 1]] = [ids[idx + 1], ids[idx]]
    reorderPages(ids)
  }

  return (
    <div className={`bs-pagelist${isPageListCollapsed ? ' bs-pagelist--collapsed' : ''}`}>
      {!isPageListCollapsed && (
        <>
          <div className="bs-pagelist__header">
            <button className="bs-pagelist__add-btn" onClick={onAddPage}>
              <Plus size={14} />
              <span>새 페이지 추가</span>
            </button>
          </div>

          <div className="bs-pagelist__list">
            {pages.map((page, idx) => (
              <PageThumbnail
                key={page.id}
                page={page}
                index={idx}
                total={pages.length}
                isActive={page.id === activePageId}
                onClick={() => setActivePage(page.id)}
                onDelete={() => onDeletePage?.(page.id)}
                onDuplicate={() => onDuplicatePage?.(page.id)}
                onMoveUp={() => handleMoveUp(page.id)}
                onMoveDown={() => handleMoveDown(page.id)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function PageThumbnail({
  page, index, total, isActive, onClick, onDelete, onDuplicate, onMoveUp, onMoveDown,
}: {
  page: Page
  index: number
  total: number
  isActive: boolean
  onClick: () => void
  onDelete: () => void
  onDuplicate: () => void
  onMoveUp: () => void
  onMoveDown: () => void
}) {
  const [menu, setMenu] = useState<{ x: number; y: number } | null>(null)
  const className = `bs-page-thumb${isActive ? ' bs-page-thumb--active' : ''}`

  const handleMenuClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    const rect = (e.target as HTMLElement).getBoundingClientRect()
    setMenu({ x: rect.left, y: rect.bottom + 4 })
  }

  return (
    <div style={{ position: 'relative', paddingLeft: 28 }}>
      <span className="bs-page-thumb__number">{index + 1}</span>
      <div className={className} onClick={onClick}>
        <div
          className="bs-page-thumb__inner"
          style={{
            backgroundColor: page.background_color || '#fff',
            ...(page.background_type === 'WP' && page.wallpaper_image ? {
              backgroundImage: `url(${page.wallpaper_image})`,
              backgroundSize: 'cover',
              backgroundPosition: `${page.background_position_x}% ${page.background_position_y}%`,
            } : {}),
          }}
        >
          <button className="bs-page-thumb__menu-btn" onClick={handleMenuClick}>
            <MoreHorizontal size={14} />
          </button>
        </div>
      </div>

      {menu && (
        <PageContextMenu
          x={menu.x}
          y={menu.y}
          onClose={() => setMenu(null)}
          onDuplicate={onDuplicate}
          onDelete={onDelete}
          onMoveUp={onMoveUp}
          onMoveDown={onMoveDown}
          isFirst={index === 0}
          isLast={index === total - 1}
        />
      )}
    </div>
  )
}
