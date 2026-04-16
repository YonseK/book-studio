import React, { useEffect, useCallback } from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { useHistoryStore } from '../../stores/historyStore'
import { LAYOUT_PRESETS, type LayoutPreset } from '../../types/layout'
import type { BookStudioClient } from '../../api/restClient'
import type { MediaType } from '../../types/panel'
import { EditorLayout } from './EditorLayout'
import { EditorCanvas } from './EditorCanvas'
import { PositionBar } from './PositionBar'
import { AppNav } from '../AppNav/AppNav'
import { ToolbarStrip } from '../Toolbar/ToolbarStrip'
import { PageListPanel } from '../PageList/PageListPanel'
import { EditorOptions } from '../Sidebar/EditorOptions'
import { AspectRatioSelector } from '../common/AspectRatioSelector'

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
    const defaults: Record<string, unknown> = {
      page: activePageId,
      media_type: mediaType,
      left: 100,
      top: 100,
      width: mediaType === 'HL' ? 600 : 300,
      height: mediaType === 'HL' ? 60 : 200,
    }
    if (mediaType === 'HL') {
      defaults.font_size = 32
      defaults.font_bold = true
    }
    const panel = await client.panels.create(activePageId, defaults as any)
    addPanel(panel)
  }, [activePageId, client, addPanel])

  return (
    <EditorLayout
      topbar={<PositionBar />}
      appNav={<AppNav />}
      toolbar={<ToolbarStrip onAddPanel={handleAddPanel} />}
      sidebar={
        <>
          <div className="bs-sidebar__header">
            <span style={{ fontSize: 13, fontWeight: 600 }}>{edition?.title || 'Untitled'}</span>
          </div>
          <div className="bs-sidebar__content">
            <AspectRatioSelector />
            <EditorOptions />
          </div>
        </>
      }
      canvas={<EditorCanvas />}
      pageList={
        <PageListPanel
          onAddPage={handleAddPage}
          onDeletePage={handleDeletePage}
        />
      }
    />
  )
}
