import React from 'react'
import { BookOpen, StickyNote, LayoutGrid, FilePlus, Library, Settings } from 'lucide-react'

interface AppNavProps {
  onMemo?: () => void
  onPageArrange?: () => void
  onNewBook?: () => void
  onBookshelf?: () => void
  onSettings?: () => void
}

export function AppNav({ onMemo, onPageArrange, onNewBook, onBookshelf, onSettings }: AppNavProps) {
  return (
    <>
      <button className="bs-iconmenu__btn bs-iconmenu__btn--active" title="Editor">
        <BookOpen size={18} strokeWidth={1.5} />
      </button>

      <button className="bs-iconmenu__btn" title="Memo" onClick={onMemo}>
        <StickyNote size={18} strokeWidth={1.5} />
      </button>

      <button className="bs-iconmenu__btn" title="Page arrange" onClick={onPageArrange}>
        <LayoutGrid size={18} strokeWidth={1.5} />
      </button>

      <button className="bs-iconmenu__btn" title="New book" onClick={onNewBook}>
        <FilePlus size={18} strokeWidth={1.5} />
      </button>

      <button className="bs-iconmenu__btn" title="Bookshelf" onClick={onBookshelf}>
        <Library size={18} strokeWidth={1.5} />
      </button>
    </>
  )
}
