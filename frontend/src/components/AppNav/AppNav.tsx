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
    <nav className="bs-appnav">
      <button className="bs-appnav__btn bs-appnav__btn--active" title="Editor">
        <BookOpen size={18} strokeWidth={1.5} />
      </button>

      <button className="bs-appnav__btn" title="Memo" onClick={onMemo}>
        <StickyNote size={18} strokeWidth={1.5} />
      </button>

      <button className="bs-appnav__btn" title="Page arrange" onClick={onPageArrange}>
        <LayoutGrid size={18} strokeWidth={1.5} />
      </button>

      <div className="bs-appnav__separator" />

      <button className="bs-appnav__btn" title="New book" onClick={onNewBook}>
        <FilePlus size={18} strokeWidth={1.5} />
      </button>

      <button className="bs-appnav__btn" title="Bookshelf" onClick={onBookshelf}>
        <Library size={18} strokeWidth={1.5} />
      </button>

      <div className="bs-appnav__spacer" />

      <button className="bs-appnav__btn" title="Settings" onClick={onSettings}>
        <Settings size={18} strokeWidth={1.5} />
      </button>
    </nav>
  )
}
