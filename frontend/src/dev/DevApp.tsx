import React, { useEffect } from 'react'
import { useEditorStore } from '../stores/editorStore'
import { LAYOUT_PRESETS } from '../types/layout'
import { EditorLayout } from '../components/Editor/EditorLayout'
import { EditorCanvas } from '../components/Editor/EditorCanvas'
import { PositionBar } from '../components/Editor/PositionBar'
import { AppNav } from '../components/AppNav/AppNav'
import { ToolbarStrip } from '../components/Toolbar/ToolbarStrip'
import { PageListPanel } from '../components/PageList/PageListPanel'
import { SidebarTabs } from '../components/Sidebar/SidebarTabs'
import { Copy, Scissors, ClipboardPaste } from 'lucide-react'
import type { MediaType, Panel } from '../types/panel'
import type { Page } from '../types/page'

export function DevApp() {
  const {
    setBook, setEdition, setPages, setPanels, setLayoutConfig,
    pages, activePageId, addPage, addPanel, removePage, edition,
  } = useEditorStore()

  useEffect(() => {
    const bookId = 'demo-book'
    const editionId = 'demo-edition'

    setBook({
      id: bookId,
      short_key: 'demo',
      user: 'dev',
      book_mode: 'BOOK',
      book_layout: 'PPTX_WIDE',
      privacy: 'PRIVATE',
      license: 'MIT',
      is_active: true,
      is_published: false,
      allow_clone: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })

    setEdition({
      id: editionId,
      book: bookId,
      title: 'BookStudio Demo',
      description: '',
      is_published: false,
      is_active: true,
      version: 1,
      latest: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })

    setLayoutConfig(LAYOUT_PRESETS.PPTX_WIDE)

    const page1: Page = {
      id: 'page-1', short_key: 'p1', user: 'dev', book_edition: editionId,
      order: 0, background_type: 'CLR', background_position_x: 50, background_position_y: 50,
      background_color: '#f5c842', opacity: 1, description: 'Cover',
      is_active: true, is_locked: false, prevent_deletion: false, show_page_memo: true,
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    }
    const page2: Page = {
      ...page1, id: 'page-2', short_key: 'p2', order: 1,
      background_color: '#f0f4f8', description: 'Content',
    }
    const page3: Page = {
      ...page1, id: 'page-3', short_key: 'p3', order: 2,
      background_color: '#1a1a2e', description: 'Dark Page',
    }

    setPages([page1, page2, page3])

    const makePanel = (overrides: Partial<Panel>): Panel => ({
      id: '', user: 'dev', page: 'page-1', media_type: 'TXT',
      text: '', headline: '', link_url: '',
      background_color: 'transparent', background_opacity: 1,
      left: 0, top: 0, width: 300, height: 200,
      z_index: 0, padding: 0,
      font_size: 16, font_family: 'initial', font_style: 'initial', font_weight: 'initial',
      color: '#333333', text_align: 'initial', opacity: 1,
      letter_spacing: 0, line_height: 1.4, text_decoration: 'initial',
      border_width: 0, border_radius: 0, border_color: '#ffffff', border_style: 'solid', border_opacity: 1, stroke_width: 0,
      text_shadow: 'initial', box_shadow: 'initial', image_shadow: 'initial',
      text_shadow_px: 0, box_shadow_px: 0, image_shadow_px: 0, drop_shadow_px: 0,
      angle: 0, translate_x: 0, translate_y: 0, scale_x: 1, scale_y: 1, rotate: 0,
      font_bold: false, font_italic: false, text_underline: false,
      order: 0, is_active: true, fixed: false, shape_type: 0,
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
      ...overrides,
    })

    setPanels('page-1', [
      makePanel({
        id: 'panel-1', page: 'page-1', media_type: 'HL',
        headline: 'BookStudio', left: 340, top: 250, width: 600, height: 80,
        font_size: 56, font_bold: true, color: '#ffffff', text_align: 'center',
        order: 0,
      }),
      makePanel({
        id: 'panel-2', page: 'page-1', media_type: 'TXT',
        text: 'HTML 기반 프레젠테이션 에디터', left: 340, top: 350, width: 600, height: 50,
        font_size: 20, color: '#ffffff', text_align: 'center', opacity: 0.8,
        order: 1,
      }),
      makePanel({
        id: 'panel-3', page: 'page-1', media_type: 'SHA',
        left: 490, top: 100, width: 300, height: 300,
        shape_type: 1, color: '#ffffff', stroke_width: 2, opacity: 0.15,
        order: 2, z_index: -1,
      }),
    ])

    setPanels('page-2', [
      makePanel({
        id: 'panel-4', page: 'page-2', media_type: 'HL',
        headline: 'Features', left: 80, top: 60, width: 400, height: 60,
        font_size: 36, font_bold: true, color: '#1a1a2e', order: 0,
      }),
      makePanel({
        id: 'panel-5', page: 'page-2', media_type: 'TXT',
        text: '• Drag & Resize panels<br>• Rich text editing<br>• Shapes (circle, rect, triangle, star)<br>• Layout presets<br>• Grid & Guidelines<br>• Undo / Redo<br>• Page management',
        left: 80, top: 140, width: 500, height: 280,
        font_size: 18, color: '#444', line_height: 1.8, order: 1,
      }),
    ])

    setPanels('page-3', [
      makePanel({
        id: 'panel-6', page: 'page-3', media_type: 'HL',
        headline: 'Dark Theme', left: 400, top: 300, width: 480, height: 80,
        font_size: 48, font_bold: true, color: '#7cc576', text_align: 'center', order: 0,
      }),
    ])
  }, [])

  // Keyboard shortcuts
  const { selectedPanelIds } = useEditorStore.getState()
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const { selectedPanelIds, removePanel, panels, activePageId, addPanel } = useEditorStore.getState()

      // Delete selected panels
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedPanelIds.length > 0) {
        const target = e.target as HTMLElement
        if (target.isContentEditable || target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return
        e.preventDefault()
        selectedPanelIds.forEach((id) => removePanel(id))
      }

      // Ctrl+C — copy panels
      if ((e.ctrlKey || e.metaKey) && e.key === 'c' && selectedPanelIds.length > 0) {
        const allPanels = activePageId ? (panels[activePageId] ?? []) : []
        const copied = allPanels.filter((p) => selectedPanelIds.includes(p.id))
        if (copied.length > 0) {
          clipboardRef.current = copied.map((p) => ({ ...p }))
        }
      }

      // Ctrl+V — paste panels
      if ((e.ctrlKey || e.metaKey) && e.key === 'v' && clipboardRef.current.length > 0 && activePageId) {
        clipboardRef.current.forEach((p) => {
          const id = `panel-${panelCounter++}`
          addPanel({ ...p, id, page: activePageId, left: p.left + 20, top: p.top + 20 })
        })
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const clipboardRef = React.useRef<Panel[]>([])

  let pageCounter = 4
  const handleAddPage = () => {
    const id = `page-${pageCounter++}`
    const newPage: Page = {
      id, short_key: id, user: 'dev', book_edition: 'demo-edition',
      order: pages.length, background_type: 'CLR',
      background_position_x: 50, background_position_y: 50,
      background_color: '#ffffff', opacity: 1, description: '',
      is_active: true, is_locked: false, prevent_deletion: false, show_page_memo: true,
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    }
    addPage(newPage)
    setPanels(id, [])
  }

  let panelCounter = 100
  const handleAddPanel = (mediaType: MediaType) => {
    if (!activePageId) return
    const id = `panel-${panelCounter++}`
    const panel: Panel = {
      id, user: 'dev', page: activePageId, media_type: mediaType,
      text: mediaType === 'TXT' ? 'New text' : '',
      headline: mediaType === 'HL' ? 'Heading' : '',
      link_url: '', background_color: 'transparent', background_opacity: 1,
      left: 100 + Math.random() * 200, top: 100 + Math.random() * 200,
      width: mediaType === 'HL' ? 500 : 300, height: mediaType === 'HL' ? 60 : 200,
      z_index: panelCounter, padding: 0,
      font_size: mediaType === 'HL' ? 32 : 16,
      font_family: 'initial', font_style: 'initial', font_weight: 'initial',
      color: '#333', text_align: 'initial', opacity: 1,
      letter_spacing: 0, line_height: 1.4, text_decoration: 'initial',
      border_width: 0, border_radius: 0, border_color: '#ffffff', border_style: 'solid',
      border_opacity: 1, stroke_width: 0,
      text_shadow: 'initial', box_shadow: 'initial', image_shadow: 'initial',
      text_shadow_px: 0, box_shadow_px: 0, image_shadow_px: 0, drop_shadow_px: 0,
      angle: 0, translate_x: 0, translate_y: 0, scale_x: 1, scale_y: 1, rotate: 0,
      font_bold: mediaType === 'HL', font_italic: false, text_underline: false,
      order: 0, is_active: true, fixed: false, shape_type: mediaType === 'SHA' ? 0 : 0,
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
    }
    addPanel(panel)
  }

  return (
    <EditorLayout
      topbar={<PositionBar />}
      appNav={<AppNav />}
      sidebar={<SidebarTabs />}
      toolbar={<ToolbarStrip onAddPanel={handleAddPanel} />}
      canvas={<EditorCanvas />}
      minibar={
        <>
          <button className="bs-minibar__btn" title="Copy page">
            <Copy size={15} strokeWidth={1.5} />
          </button>
          <button className="bs-minibar__btn" title="Cut page">
            <Scissors size={15} strokeWidth={1.5} />
          </button>
          <button className="bs-minibar__btn" title="Paste page">
            <ClipboardPaste size={15} strokeWidth={1.5} />
          </button>
        </>
      }
      pageList={
        <PageListPanel
          onAddPage={handleAddPage}
          onDeletePage={(id) => removePage(id)}
        />
      }
    />
  )
}
