import React, { useEffect, useCallback } from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { useHistoryStore } from '../../stores/historyStore'
import { LAYOUT_PRESETS, type LayoutPreset } from '../../types/layout'
import type { BookStudioClient } from '../../api/restClient'
import type { MediaType } from '../../types/panel'
import { useAutoSave } from '../../hooks/useAutoSave'
import { ClientContext } from '../../contexts/ClientContext'
import { EditorLayout } from './EditorLayout'
import { EditorCanvas } from './EditorCanvas'
import { PositionBar } from './PositionBar'
import { SaveStatus } from './SaveStatus'
import { AppNav } from '../AppNav/AppNav'
import { ToolbarStrip } from '../Toolbar/ToolbarStrip'
import { PageListPanel } from '../PageList/PageListPanel'
import { SidebarTabs } from '../Sidebar/SidebarTabs'

export interface BookStudioEditorProps {
  client: BookStudioClient
  bookId: string
  defaultLayout?: LayoutPreset
  features?: {
    mediaBank?: boolean
    templates?: boolean
    htmlImport?: boolean
  }
}

export function BookStudioEditor({ client, bookId, defaultLayout = 'PPTX_WIDE', features }: BookStudioEditorProps) {
  const {
    setBook, setEdition, setPages, setPanels, setLayoutConfig,
    book, edition, pages, activePageId, addPage, addPanel, removePage,
  } = useEditorStore()
  const { push: pushHistory } = useHistoryStore()
  const { getManager } = useAutoSave({ client })

  // 초기 로드
  useEffect(() => {
    async function load() {
      const bookData = await client.books.get(bookId)
      setBook(bookData)

      const layout = LAYOUT_PRESETS[bookData.book_layout] ?? LAYOUT_PRESETS[defaultLayout]
      setLayoutConfig(layout)

      const editions = await client.editions.list(bookId)
      const latestEdition = editions.find((e) => e.latest) ?? editions[0]
      if (!latestEdition) return
      setEdition(latestEdition)

      const pagesData = await client.pages.list(bookId, latestEdition.id)
      setPages(pagesData)

      // 각 페이지의 패널 로드
      for (const page of pagesData) {
        const panels = await client.panels.list(page.id)
        setPanels(page.id, panels)
      }
    }
    load()
  }, [bookId, client, defaultLayout])

  // Font Awesome CDN (아이콘 패널 렌더링용)
  useEffect(() => {
    const FA_ID = 'bs-fontawesome-cdn'
    if (!document.getElementById(FA_ID)) {
      const link = document.createElement('link')
      link.id = FA_ID
      link.rel = 'stylesheet'
      link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
      document.head.appendChild(link)
    }
  }, [])

  // 키보드 단축키
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault()
        if (e.shiftKey) {
          useHistoryStore.getState().redo()
        } else {
          useHistoryStore.getState().undo()
        }
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const handleAddPage = useCallback(async () => {
    if (!book || !edition) return
    const page = await client.pages.create(book.id, edition.id, {
      book_edition: edition.id,
    })
    addPage(page)
  }, [book, edition, client, addPage])

  const handleDeletePage = useCallback(async (pageId: string) => {
    if (!book || !edition) return
    await client.pages.delete(book.id, edition.id, pageId)
    removePage(pageId)
  }, [book, edition, client, removePage])

  const handleAddPanel = useCallback(async (mediaType: MediaType) => {
    if (!activePageId) return

    // 패널 타입별 기본값
    const PANEL_DEFAULTS: Record<string, Record<string, unknown>> = {
      HL: {
        width: 700, height: 64, left: 130, top: 80,
        headline: '제목을 입력하세요',
        font_size: 36, font_bold: true, color: '#ffffff',
        line_height: 1.2, padding: 8,
      },
      TXT: {
        width: 500, height: 160, left: 130, top: 180,
        text: '텍스트를 입력하세요. 클릭하면 편집할 수 있습니다.',
        font_size: 18, color: '#e0e0e0',
        line_height: 1.6, padding: 12,
      },
      IMG: {
        width: 400, height: 300, left: 280, top: 120,
        background_color: 'rgba(255,255,255,0.05)',
        border_width: 1, border_color: 'rgba(255,255,255,0.15)', border_style: 'dashed',
      },
      SHA: {
        width: 200, height: 200, left: 380, top: 180,
        background_color: 'rgba(91,106,191,0.6)',
        border_radius: 8,
      },
      EV: {
        width: 560, height: 315, left: 200, top: 120,
        text: 'https://',
      },
      VOD: {
        width: 480, height: 270, left: 240, top: 140,
        background_color: 'rgba(0,0,0,0.3)',
      },
      FILE: {
        width: 300, height: 80, left: 330, top: 260,
        background_color: 'rgba(255,255,255,0.08)',
        border_width: 1, border_color: 'rgba(255,255,255,0.12)', border_radius: 8,
        text: '파일을 드래그하거나 클릭하세요',
        font_size: 13, color: '#999999', padding: 16,
      },
      DOC: {
        width: 600, height: 400, left: 180, top: 80,
        text: '문서 내용을 작성하세요.',
        font_size: 16, color: '#e0e0e0',
        line_height: 1.8, padding: 24,
        background_color: 'rgba(255,255,255,0.03)',
        border_width: 1, border_color: 'rgba(255,255,255,0.08)', border_radius: 4,
      },
    }

    const typeDefaults = PANEL_DEFAULTS[mediaType] || {}
    const defaults: Record<string, unknown> = {
      page: activePageId,
      media_type: mediaType,
      left: 100,
      top: 100,
      width: 300,
      height: 200,
      ...typeDefaults,
    }

    const panel = await client.panels.create(activePageId, defaults as any)
    addPanel(panel)
  }, [activePageId, client, addPanel])

  return (
    <ClientContext.Provider value={client}>
      <EditorLayout
        topbar={<><PositionBar /><SaveStatus getManager={getManager} /></>}
        iconMenu={
          <>
            <AppNav />
            <div className="bs-iconmenu__separator" />
            <ToolbarStrip onAddPanel={handleAddPanel} />
          </>
        }
        sidebar={<SidebarTabs client={client} />}
        canvas={<EditorCanvas />}
        pageList={
          <PageListPanel
            onAddPage={handleAddPage}
            onDeletePage={handleDeletePage}
          />
        }
      />
    </ClientContext.Provider>
  )
}
