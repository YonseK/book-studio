import React from 'react'
import { ImageUp, Image, Pentagon, Code, Paperclip, Play, FileText } from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import type { MediaType } from '../../types/panel'

interface ToolbarStripProps {
  onAddPanel?: (type: MediaType) => void
}

export function ToolbarStrip({ onAddPanel }: ToolbarStripProps) {
  const { pages, activePageId, updatePage, setSidebarContext } = useEditorStore()
  const activePage = pages.find((p) => p.id === activePageId)
  const bgColor = activePage?.background_color || '#ffffff'

  const handleSwatchClick = () => {
    setSidebarContext('wallpaper')
    // Toggle background type between wallpaper and color
    if (activePageId && activePage) {
      updatePage(activePageId, {
        background_type: activePage.background_type === 'CLR' ? 'WP' : 'CLR',
      })
    }
  }

  return (
    <>
      {/* Background color swatches — click to toggle wallpaper/color mode */}
      <button
        className="bs-toolbar__swatch"
        title="배경 모드 전환"
        onClick={handleSwatchClick}
        style={{ cursor: 'pointer', border: 'none', background: 'none', padding: 0 }}
      >
        <div className="bs-toolbar__swatch-bg" style={{ backgroundColor: '#ffffff' }} />
        <div className="bs-toolbar__swatch-fg" style={{ backgroundColor: bgColor }} />
      </button>

      <div className="bs-toolbar__gap" />

      {/* Wallpaper upload */}
      <button className="bs-toolbar__btn" title="Upload wallpaper">
        <ImageUp size={18} strokeWidth={1.5} />
      </button>

      {/* Headline text */}
      <button
        className="bs-toolbar__btn"
        title="Headline text"
        onClick={() => onAddPanel?.('HL')}
      >
        <span style={{ fontSize: 18, fontWeight: 800, fontFamily: 'serif' }}>T</span>
      </button>

      {/* Body text */}
      <button
        className="bs-toolbar__btn"
        title="Body text"
        onClick={() => onAddPanel?.('TXT')}
      >
        <span style={{ fontSize: 15, fontWeight: 300 }}>T</span>
      </button>

      {/* Image */}
      <button
        className="bs-toolbar__btn"
        title="Image"
        onClick={() => onAddPanel?.('IMG')}
      >
        <Image size={18} strokeWidth={1.5} />
      </button>

      {/* Shape */}
      <button
        className="bs-toolbar__btn"
        title="Shape"
        onClick={() => onAddPanel?.('SHA')}
      >
        <Pentagon size={18} strokeWidth={1.5} />
      </button>

      {/* Embed */}
      <button
        className="bs-toolbar__btn"
        title="Web embed"
        onClick={() => onAddPanel?.('EV')}
      >
        <Code size={18} strokeWidth={1.5} />
      </button>

      {/* File */}
      <button
        className="bs-toolbar__btn"
        title="File upload"
        onClick={() => onAddPanel?.('FILE')}
      >
        <Paperclip size={18} strokeWidth={1.5} />
      </button>

      {/* Video */}
      <button
        className="bs-toolbar__btn"
        title="Video / Audio"
        onClick={() => onAddPanel?.('VOD')}
      >
        <Play size={18} strokeWidth={1.5} />
      </button>

      {/* Note */}
      <button
        className="bs-toolbar__btn"
        title="Note"
        onClick={() => onAddPanel?.('DOC')}
      >
        <FileText size={18} strokeWidth={1.5} />
      </button>
    </>
  )
}
