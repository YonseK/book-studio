import React, { useEffect, useRef } from 'react'
import { FilePlus, FolderOpen, FolderHeart, Upload, Copy, Trash2 } from 'lucide-react'

interface FileMenuProps {
  onClose: () => void
  onNewBook?: () => void
  onOpenLibrary?: () => void
  onOpenShared?: () => void
  onPublish?: () => void
  onClone?: () => void
  onDelete?: () => void
}

export function FileMenu({
  onClose, onNewBook, onOpenLibrary, onOpenShared, onPublish, onClone, onDelete,
}: FileMenuProps) {
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

  const items = [
    { icon: FilePlus, label: '새 책 만들기', onClick: onNewBook },
    { icon: FolderOpen, label: '작업중인 책 보관함', onClick: onOpenLibrary },
    { icon: FolderHeart, label: '공유된 책 보관함', onClick: onOpenShared },
    null, // separator
    { icon: Upload, label: '게시된 책 버전 업데이트', onClick: onPublish },
    { icon: Copy, label: '복제', onClick: onClone },
    null, // separator
    { icon: Trash2, label: '삭제', onClick: onDelete, danger: true },
  ]

  return (
    <div ref={ref} className="bs-dropdown" style={{ left: 0, top: 0 }}>
      {items.map((item, i) =>
        item === null ? (
          <div key={`sep-${i}`} className="bs-dropdown__separator" />
        ) : (
          <button
            key={item.label}
            className={`bs-dropdown__item${item.danger ? ' bs-dropdown__item--danger' : ''}`}
            onClick={() => { item.onClick?.(); onClose(); }}
          >
            <item.icon size={14} strokeWidth={1.5} />
            <span>{item.label}</span>
          </button>
        ),
      )}
    </div>
  )
}
