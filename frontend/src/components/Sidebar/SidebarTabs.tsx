import React, { useState, useMemo } from 'react'
import { File, PenLine, Settings2, Share2 } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import { FileMenu } from './FileMenu'
import { BookInfoPanel } from './BookInfoPanel'
import { EditorOptions } from './EditorOptions'
import { SharePanel } from './SharePanel'
import { WallpaperBank } from './WallpaperBank'
import { TextBank } from './TextBank'
import { ImageBankPanel } from './ImageBankPanel'
import { ShapeBankPanel } from './ShapeBankPanel'

const TABS = [
  { key: 'file' as const, label: '파일', icon: File },
  { key: 'input' as const, label: '입력', icon: PenLine },
  { key: 'options' as const, label: '옵션', icon: Settings2 },
  { key: 'share' as const, label: '공유', icon: Share2 },
]

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
  const { activeSidebarTab, setActiveSidebarTab, sidebarContext, edition, activePageId, updatePage } = useEditorStore()
  const [showFileMenu, setShowFileMenu] = useState(false)

  const wallpapers = useMemo(() =>
    wallpaperMapping.data.map((wp, i) => ({
      id: `wp-${i}`,
      image_url: wp.thumb,
      image_view_url: wp.view,
      image_thumb_url: wp.thumb,
    })),
    [],
  )

  const handleTabClick = (key: typeof activeSidebarTab) => {
    if (key === 'file') {
      setShowFileMenu(!showFileMenu)
    } else {
      setShowFileMenu(false)
      setActiveSidebarTab(key)
    }
  }

  // Context bank header label
  const contextLabel = sidebarContext === 'text' ? '텍스트 편집'
    : sidebarContext === 'image' ? '이미지 편집'
    : sidebarContext === 'shape' ? '도형 편집'
    : sidebarContext === 'wallpaper' ? '월페이퍼 뱅크'
    : null

  return (
    <>
      {/* Title */}
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

      {/* Tab bar */}
      <div className="bs-sidebar__tabs">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`bs-sidebar__tab${activeSidebarTab === tab.key ? ' bs-sidebar__tab--active' : ''}`}
            onClick={() => handleTabClick(tab.key)}
          >
            <tab.icon size={13} strokeWidth={1.5} />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* File menu dropdown */}
      {showFileMenu && (
        <div style={{ position: 'relative' }}>
          <FileMenu
            onClose={() => setShowFileMenu(false)}
            onNewBook={props.onNewBook}
            onOpenLibrary={props.onOpenLibrary}
            onOpenShared={props.onOpenShared}
            onPublish={props.onPublish}
            onClone={props.onClone}
            onDelete={props.onDelete}
          />
        </div>
      )}

      {/* Context-sensitive bank or tab content */}
      <div className="bs-sidebar__content">
        {/* Context banks take priority when active */}
        {sidebarContext === 'text' ? (
          <>
            <div style={{
              fontSize: 12, fontWeight: 600, color: 'var(--bs-accent)',
              marginBottom: 12, paddingBottom: 8,
              borderBottom: '1px solid var(--bs-border)',
            }}>
              {contextLabel}
            </div>
            <TextBank />
          </>
        ) : sidebarContext === 'image' ? (
          <>
            <div style={{
              fontSize: 12, fontWeight: 600, color: 'var(--bs-accent)',
              marginBottom: 12, paddingBottom: 8,
              borderBottom: '1px solid var(--bs-border)',
            }}>
              {contextLabel}
            </div>
            <ImageBankPanel />
          </>
        ) : sidebarContext === 'shape' ? (
          <>
            <div style={{
              fontSize: 12, fontWeight: 600, color: 'var(--bs-accent)',
              marginBottom: 12, paddingBottom: 8,
              borderBottom: '1px solid var(--bs-border)',
            }}>
              {contextLabel}
            </div>
            <ShapeBankPanel />
          </>
        ) : sidebarContext === 'wallpaper' ? (
          <>
            <div style={{
              fontSize: 12, fontWeight: 600, color: 'var(--bs-text-secondary)',
              marginBottom: 12, paddingBottom: 8,
              borderBottom: '1px solid var(--bs-border)',
            }}>
              {contextLabel}
            </div>
            <WallpaperBank wallpapers={wallpapers} onSelect={(wp) => {
              if (!activePageId) return
              const viewUrl = wp.image_view_url || wp.image_url
              updatePage(activePageId, {
                background_type: 'WP',
                wallpaper_image: viewUrl,
                wallpaper: viewUrl,
              })
            }} />
          </>
        ) : (
          /* Default: show tab content */
          <>
            {activeSidebarTab === 'input' && <BookInfoPanel />}
            {activeSidebarTab === 'options' && <EditorOptions />}
            {activeSidebarTab === 'share' && <SharePanel />}
          </>
        )}
      </div>
    </>
  )
}
