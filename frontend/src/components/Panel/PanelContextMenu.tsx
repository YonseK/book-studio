import React, { useEffect, useRef } from 'react'
import { Copy, Trash2, ArrowUp, ArrowDown, Lock, Unlock } from 'lucide-react'

interface PanelContextMenuProps {
  x: number
  y: number
  onClose: () => void
  onDuplicate?: () => void
  onDelete?: () => void
  onBringForward?: () => void
  onSendBackward?: () => void
  onToggleLock?: () => void
  isLocked?: boolean
}

export function PanelContextMenu({
  x, y, onClose, onDuplicate, onDelete, onBringForward, onSendBackward, onToggleLock, isLocked,
}: PanelContextMenuProps) {
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
    <div ref={ref} className="bs-dropdown" style={{ position: 'fixed', left: x, top: y, zIndex: 9999 }}>
      <button className="bs-dropdown__item" onClick={() => { onDuplicate?.(); onClose(); }}>
        <Copy size={14} strokeWidth={1.5} />
        <span>복제</span>
      </button>
      <div className="bs-dropdown__separator" />
      <button className="bs-dropdown__item" onClick={() => { onBringForward?.(); onClose(); }}>
        <ArrowUp size={14} strokeWidth={1.5} />
        <span>앞으로 가져오기</span>
      </button>
      <button className="bs-dropdown__item" onClick={() => { onSendBackward?.(); onClose(); }}>
        <ArrowDown size={14} strokeWidth={1.5} />
        <span>뒤로 보내기</span>
      </button>
      <div className="bs-dropdown__separator" />
      <button className="bs-dropdown__item" onClick={() => { onToggleLock?.(); onClose(); }}>
        {isLocked ? <Unlock size={14} strokeWidth={1.5} /> : <Lock size={14} strokeWidth={1.5} />}
        <span>{isLocked ? '잠금 해제' : '잠금'}</span>
      </button>
      <div className="bs-dropdown__separator" />
      <button className="bs-dropdown__item bs-dropdown__item--danger" onClick={() => { onDelete?.(); onClose(); }}>
        <Trash2 size={14} strokeWidth={1.5} />
        <span>삭제</span>
      </button>
    </div>
  )
}
