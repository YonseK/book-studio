import React, { useCallback } from 'react'
import { Plus, ChevronLeft, ChevronRight, Check, GripVertical } from 'lucide-react'
import {
  DndContext, closestCenter, PointerSensor, useSensor, useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  SortableContext, verticalListSortingStrategy, useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useEditorStore } from '../../stores/editorStore'
import { PageContextMenu } from './PageContextMenu'

interface PageListPanelProps {
  onAddPage?: () => void
  onDeletePage?: (pageId: string) => void
  onDuplicatePage?: (pageId: string) => void
}

export function PageListPanel({ onAddPage, onDeletePage, onDuplicatePage }: PageListPanelProps) {
  const {
    pages, panels, activePageId, setActivePage, layoutConfig,
    isPageListCollapsed, togglePageList, addPage, setPanels, reorderPages,
  } = useEditorStore()

  const sortedPages = [...pages].sort((a, b) => a.order - b.order)

  const handleDuplicate = useCallback((pageId: string) => {
    if (onDuplicatePage) {
      onDuplicatePage(pageId)
      return
    }
    // Local duplicate
    const page = pages.find((p) => p.id === pageId)
    if (!page) return
    const newId = `page-dup-${Date.now()}`
    const newPage = { ...page, id: newId, short_key: newId, order: pages.length }
    addPage(newPage)
    const srcPanels = panels[pageId] || []
    const newPanels = srcPanels.map((p, i) => ({
      ...p,
      id: `panel-dup-${Date.now()}-${i}`,
      page: newId,
    }))
    setPanels(newId, newPanels)
  }, [pages, panels, addPage, setPanels, onDuplicatePage])

  const handleMoveUp = useCallback((pageId: string) => {
    const idx = sortedPages.findIndex((p) => p.id === pageId)
    if (idx <= 0) return
    const ids = sortedPages.map((p) => p.id)
    ;[ids[idx - 1], ids[idx]] = [ids[idx], ids[idx - 1]]
    reorderPages(ids)
  }, [sortedPages, reorderPages])

  const handleMoveDown = useCallback((pageId: string) => {
    const idx = sortedPages.findIndex((p) => p.id === pageId)
    if (idx < 0 || idx >= sortedPages.length - 1) return
    const ids = sortedPages.map((p) => p.id)
    ;[ids[idx], ids[idx + 1]] = [ids[idx + 1], ids[idx]]
    reorderPages(ids)
  }, [sortedPages, reorderPages])

  const thumbWidth = 140
  const thumbScale = thumbWidth / layoutConfig.width
  const thumbHeight = layoutConfig.height * thumbScale

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
  )

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return
    const oldIndex = sortedPages.findIndex((p) => p.id === active.id)
    const newIndex = sortedPages.findIndex((p) => p.id === over.id)
    if (oldIndex < 0 || newIndex < 0) return
    const ids = sortedPages.map((p) => p.id)
    ids.splice(oldIndex, 1)
    ids.splice(newIndex, 0, active.id as string)
    reorderPages(ids)
  }, [sortedPages, reorderPages])

  return (
    <div className="bs-pagelist">
      {/* Header */}
      <div className="bs-pagelist__header">
        <button className="bs-pagelist__add" onClick={onAddPage}>
          <Plus size={13} />
          <span>새 페이지 추가</span>
        </button>
      </div>

      {/* Page list — drag sortable */}
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={sortedPages.map((p) => p.id)} strategy={verticalListSortingStrategy}>
          <div className="bs-pagelist__list">
            {sortedPages.map((page, idx) => {
              const isActive = page.id === activePageId
              const pagePanels = panels[page.id] || []

              return (
                <SortablePageThumbnail
                  key={page.id}
                  page={page}
                  index={idx}
                  total={sortedPages.length}
                  pagePanels={pagePanels}
                  isActive={isActive}
                  layoutConfig={layoutConfig}
                  thumbWidth={thumbWidth}
                  thumbHeight={thumbHeight}
                  thumbScale={thumbScale}
                  onClick={() => setActivePage(page.id)}
                  onDuplicate={() => handleDuplicate(page.id)}
                  onDelete={() => onDeletePage?.(page.id)}
                  onMoveUp={() => handleMoveUp(page.id)}
                  onMoveDown={() => handleMoveDown(page.id)}
                />
              )
            })}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  )
}

interface PageThumbnailProps {
  page: any
  index: number
  total: number
  pagePanels: any[]
  isActive: boolean
  layoutConfig: { width: number; height: number }
  thumbWidth: number
  thumbHeight: number
  thumbScale: number
  onClick: () => void
  onDuplicate: () => void
  onDelete: () => void
  onMoveUp: () => void
  onMoveDown: () => void
}

function SortablePageThumbnail(props: PageThumbnailProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: props.page.id,
  })

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 10 : undefined,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <PageThumbnail {...props} dragListeners={listeners} />
    </div>
  )
}

function PageThumbnail({
  page, index, total, pagePanels, isActive, layoutConfig, thumbWidth, thumbHeight, thumbScale,
  onClick, onDuplicate, onDelete, onMoveUp, onMoveDown, dragListeners,
}: PageThumbnailProps & { dragListeners?: any }) {
  const [menu, setMenu] = React.useState<{ x: number; y: number } | null>(null)

  const handleMenuClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    const rect = (e.target as HTMLElement).getBoundingClientRect()
    setMenu({ x: rect.left, y: rect.bottom + 4 })
  }

  return (
    <div
      className={`bs-pagelist__item${isActive ? ' bs-pagelist__item--active' : ''}`}
      onClick={onClick}
    >
      {/* Drag handle */}
      <div className="bs-pagelist__drag-handle" {...dragListeners}>
        <GripVertical size={12} />
      </div>
      {/* Active indicator */}
      {isActive && <div className="bs-pagelist__active-bar" />}

      {/* Thumbnail container */}
      <div
        className="bs-pagelist__thumb"
        style={{ width: thumbWidth, height: thumbHeight, overflow: 'hidden', position: 'relative' }}
      >
        {/* Scaled page content */}
        <div style={{
          width: layoutConfig.width,
          height: layoutConfig.height,
          transform: `scale(${thumbScale})`,
          transformOrigin: 'top left',
          position: 'absolute',
          top: 0,
          left: 0,
          backgroundColor: page.background_color || '#ffffff',
          opacity: page.opacity ?? 1,
          ...(page.background_type === 'WP' && page.wallpaper_image ? {
            backgroundImage: `url(${page.wallpaper_image})`,
            backgroundSize: 'cover',
            backgroundPosition: `${page.background_position_x || 50}% ${page.background_position_y || 50}%`,
          } : {}),
        }}>
          {/* Mini panel rendering */}
          {pagePanels
            .filter((p) => p.is_active)
            .sort((a, b) => a.z_index - b.z_index)
            .map((p) => (
              <div
                key={p.id}
                style={{
                  position: 'absolute',
                  left: p.left,
                  top: p.top,
                  width: p.width,
                  height: p.height,
                  fontSize: p.font_size,
                  fontWeight: p.font_bold ? 'bold' : undefined,
                  color: p.color,
                  textAlign: p.text_align !== 'initial' ? p.text_align as any : undefined,
                  overflow: 'hidden',
                  opacity: p.opacity,
                  transform: p.rotate ? `rotate(${p.rotate}deg)` : undefined,
                  backgroundColor: p.background_color !== 'transparent' ? p.background_color : undefined,
                  borderRadius: p.border_radius || undefined,
                }}
              >
                {(p.media_type === 'HL' || p.media_type === 'TXT' || p.media_type === 'DOC') && (
                  <div
                    style={{ pointerEvents: 'none', lineHeight: p.line_height || 1.4 }}
                    dangerouslySetInnerHTML={{ __html: p.media_type === 'HL' ? p.headline : p.text }}
                  />
                )}
                {p.media_type === 'SHA' && (
                  <div style={{
                    width: '100%', height: '100%',
                    backgroundColor: p.color !== '#ffffff' ? p.color : p.background_color,
                    borderRadius: p.shape_type === 7 ? '50%' : undefined,
                  }} />
                )}
                {p.media_type === 'IMG' && p.fields_data?.image_url && (
                  <img
                    src={p.fields_data.image_url as string}
                    alt=""
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                )}
              </div>
            ))}
        </div>
      </div>

      {/* Page number */}
      <div className="bs-pagelist__number">{page.order + 1}</div>

      {/* Active check */}
      {isActive && (
        <div className="bs-pagelist__check">
          <Check size={12} strokeWidth={3} />
        </div>
      )}

      {/* Menu button */}
      <button
        className="bs-pagelist__menu-btn"
        onClick={handleMenuClick}
      >
        ···
      </button>

      {/* Context menu */}
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
