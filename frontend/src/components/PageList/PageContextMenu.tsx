import React, { useEffect, useRef } from 'react'
import { Copy, Trash2, ChevronUp, ChevronDown } from 'lucide-react'

interface PageContextMenuProps {
  x: number
  y: number
  onClose: () => void
  onDuplicate?: () => void
  onDelete?: () => void
  onMoveUp?: () => void
  onMoveDown?: () => void
  isFirst?: boolean
  isLast?: boolean
}

export function PageContextMenu({
  x, y, onClose, onDuplicate, onDelete, onMoveUp, onMoveDown, isFirst, isLast,
}: PageContextMenuProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onClose])

  return (
    <div
      ref={ref}
      className="bs-dropdown"
      style={{ position: 'fixed', left: x, top: y }}
    >
      <button className="bs-dropdown__item" onClick={() => { onDuplicate?.(); onClose(); }}>
        <Copy size={14} strokeWidth={1.5} />
        <span>복제</span>
      </button>
      {!isFirst && (
        <button className="bs-dropdown__item" onClick={() => { onMoveUp?.(); onClose(); }}>
          <ChevronUp size={14} strokeWidth={1.5} />
          <span>위로 이동</span>
        </button>
      )}
      {!isLast && (
        <button className="bs-dropdown__item" onClick={() => { onMoveDown?.(); onClose(); }}>
          <ChevronDown size={14} strokeWidth={1.5} />
          <span>아래로 이동</span>
        </button>
      )}
      <div className="bs-dropdown__separator" />
      <button className="bs-dropdown__item bs-dropdown__item--danger" onClick={() => { onDelete?.(); onClose(); }}>
        <Trash2 size={14} strokeWidth={1.5} />
        <span>삭제</span>
      </button>
    </div>
  )
}
