import React, { useState, useMemo, useRef, useEffect } from 'react'
import { Folder, PenLine, SlidersHorizontal, Share2, X } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import { FileMenu } from './FileMenu'
import { BookInfoPanel } from './BookInfoPanel'
import { EditorOptions } from './EditorOptions'
import { SharePanel } from './SharePanel'
import { WallpaperBank } from './WallpaperBank'
import { TextBank } from './TextBank'
import { ImageBankPanel } from './ImageBankPanel'
import { ShapeBankPanel } from './ShapeBankPanel'

interface SidebarTabsProps {
  onNewBook?: () => void
  onOpenLibrary?: () => void
  onOpenShared?: () => void
  onPublish?: () => void
  onClone?: () => void
  onDelete?: () => void
}

import wallpaperMapping from '../../data/wallpaperMapping.json'

export function SidebarTabs(props: SidebarTabsProps) {
  const { sidebarContext, edition, activePageId, updatePage } = useEditorStore()
  const [openMenu, setOpenMenu] = useState<'file' | 'insert' | 'share' | null>(null)
  const [showOptions, setShowOptions] = useState(false)
  const [showBookInfo, setShowBookInfo] = useState(false)

  const menuRef = useRef<HTMLDivElement>(null)

  const wallpapers = useMemo(() =>
    wallpaperMapping.data.map((wp, i) => ({
      id: `wp-${i}`,
      image_url: wp.thumb,
      image_view_url: wp.view,
      image_thumb_url: wp.thumb,
    })),
    [],
  )

  // Close menus on outside click
  useEffect(() => {
    if (!openMenu) return
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpenMenu(null)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [openMenu])

  const handleMenuClick = (menu: 'file' | 'insert' | 'options' | 'share') => {
    if (menu === 'options') {
      setShowOptions(!showOptions)
      setOpenMenu(null)
    } else {
      setShowOptions(false)
      setOpenMenu(openMenu === menu ? null : menu)
    }
  }

  // Context bank header label
  const contextLabel = sidebarContext === 'text' ? '텍스트 편집'
    : sidebarContext === 'image' ? '이미지 편집'
    : sidebarContext === 'shape' ? '도형 편집'
    : sidebarContext === 'wallpaper' ? '배경'
    : null

  return (
    <>
      {/* ── Title ── */}
      <div className="bs-sidebar__header">
        <input
          className="bs-sidebar__title-input"
          value={edition?.title || ''}
          onChange={(e) => {
            if (edition) {
              useEditorStore.getState().setEdition({ ...edition, title: e.target.value })
            }
          }}
          placeholder="제목 없음"
        />
      </div>

      {/* ── Menu bar (원본 menus__menubox) ── */}
      <div className="bs-sidebar__menubox" ref={menuRef}>
        <button
          className={`bs-sidebar__menu-btn${openMenu === 'file' ? ' bs-sidebar__menu-btn--active' : ''}`}
          onClick={() => handleMenuClick('file')}
        >
          <Folder size={15} strokeWidth={1.5} />
          <span>파일</span>
        </button>
        <button
          className={`bs-sidebar__menu-btn${openMenu === 'insert' ? ' bs-sidebar__menu-btn--active' : ''}`}
          onClick={() => handleMenuClick('insert')}
        >
          <PenLine size={15} strokeWidth={1.5} />
          <span>입력</span>
        </button>
        <button
          className={`bs-sidebar__menu-btn${showOptions ? ' bs-sidebar__menu-btn--active' : ''}`}
          onClick={() => handleMenuClick('options')}
        >
          <SlidersHorizontal size={15} strokeWidth={1.5} />
          <span>옵션</span>
        </button>
        <button
          className={`bs-sidebar__menu-btn${openMenu === 'share' ? ' bs-sidebar__menu-btn--active' : ''}`}
          onClick={() => handleMenuClick('share')}
        >
          <Share2 size={15} strokeWidth={1.5} />
          <span>공유</span>
        </button>

        {/* ── Dropdown menus ── */}
        {openMenu === 'file' && (
          <div className="bs-sidebar__dropdown" style={{ left: '0.5em', top: '3.2em' }}>
            <FileMenu
              onClose={() => setOpenMenu(null)}
              onNewBook={props.onNewBook}
              onOpenLibrary={props.onOpenLibrary}
              onOpenShared={props.onOpenShared}
              onPublish={props.onPublish}
              onClone={props.onClone}
              onDelete={props.onDelete}
            />
          </div>
        )}

        {openMenu === 'insert' && (
          <div className="bs-sidebar__dropdown" style={{ left: '5em', top: '3.2em' }}>
            <InsertMenu onClose={() => setOpenMenu(null)} onBookInfo={() => { setShowBookInfo(true); setOpenMenu(null) }} />
          </div>
        )}

        {openMenu === 'share' && (
          <div className="bs-sidebar__dropdown" style={{ left: '10em', top: '3.2em' }}>
            <ShareMenu
              onClose={() => setOpenMenu(null)}
              onPublish={props.onPublish}
            />
          </div>
        )}
      </div>

      {/* ── Main content area ── */}
      <div className="bs-sidebar__content">
        {/* Options overlay panel (원본 FileOptions) */}
        {showOptions && (
          <div className="bs-sidebar__options-overlay">
            <div className="bs-sidebar__options-header">
              <span className="bs-sidebar__options-title">
                <SlidersHorizontal size={13} />
                <span>옵션</span>
              </span>
              <button
                className="bs-sidebar__options-close"
                onClick={() => setShowOptions(false)}
              >
                <X size={14} />
              </button>
            </div>
            <div className="bs-sidebar__options-body">
              <EditorOptions />
            </div>
          </div>
        )}

        {/* BookInfo overlay panel (원본 입력 → 책 정보) */}
        {showBookInfo && !showOptions && (
          <div className="bs-sidebar__options-overlay">
            <div className="bs-sidebar__options-header">
              <span className="bs-sidebar__options-title">
                <PenLine size={13} />
                <span>책 정보 입력</span>
              </span>
              <button
                className="bs-sidebar__options-close"
                onClick={() => setShowBookInfo(false)}
              >
                <X size={14} />
              </button>
            </div>
            <div className="bs-sidebar__options-body">
              <BookInfoPanel />
            </div>
          </div>
        )}

        {/* Context-sensitive controllers + banks */}
        {!showOptions && !showBookInfo && (
          <>
            {sidebarContext === 'text' ? (
              <>
                <div className="bs-sidebar__context-label">{contextLabel}</div>
                <TextBank />
              </>
            ) : sidebarContext === 'image' ? (
              <>
                <div className="bs-sidebar__context-label">{contextLabel}</div>
                <ImageBankPanel />
              </>
            ) : sidebarContext === 'shape' ? (
              <>
                <div className="bs-sidebar__context-label">{contextLabel}</div>
                <ShapeBankPanel />
              </>
            ) : (
              /* Default: wallpaper/color bank (원본 ItemBanks 기본) */
              <WallpaperBank wallpapers={wallpapers} onSelect={(wp) => {
                if (!activePageId) return
                const viewUrl = wp.image_view_url || wp.image_url
                updatePage(activePageId, {
                  background_type: 'WP',
                  wallpaper_image: viewUrl,
                  wallpaper: viewUrl,
                })
              }} />
            )}
          </>
        )}
      </div>
    </>
  )
}

/* ── Insert Menu (원본 GroupMenuInsert) ── */
function InsertMenu({ onClose, onBookInfo }: { onClose: () => void; onBookInfo: () => void }) {
  return (
    <div className="bs-dropdown" style={{ left: 0, top: 0 }}>
      <button
        className="bs-dropdown__item"
        onClick={onBookInfo}
      >
        <PenLine size={14} strokeWidth={1.5} />
        <span>책 정보 입력</span>
      </button>
    </div>
  )
}

/* ── Share Menu (원본 GroupMenuShare) ── */
function ShareMenu({ onClose, onPublish }: { onClose: () => void; onPublish?: () => void }) {
  const { book } = useEditorStore()
  const isPublished = book?.is_published

  return (
    <div className="bs-dropdown" style={{ left: 0, top: 0 }}>
      {!isPublished ? (
        <button
          className="bs-dropdown__item"
          onClick={() => { onPublish?.(); onClose() }}
        >
          <Share2 size={14} strokeWidth={1.5} />
          <span>내 컬렉션에 공유</span>
        </button>
      ) : (
        <button
          className="bs-dropdown__item"
          onClick={() => { onPublish?.(); onClose() }}
        >
          <Share2 size={14} strokeWidth={1.5} />
          <span>게시된 책 버전 업데이트</span>
        </button>
      )}
      <div className="bs-dropdown__separator" />
      <button
        className="bs-dropdown__item"
        onClick={onClose}
      >
        <PenLine size={14} strokeWidth={1.5} />
        <span>공개 범위 수정</span>
      </button>
    </div>
  )
}
