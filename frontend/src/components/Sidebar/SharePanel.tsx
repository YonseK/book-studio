import React, { useState, useCallback } from 'react'
import { Upload, FileDown, FileUp } from 'lucide-react'
import type { BookStudioClient } from '../../api/restClient'
import { useEditorStore } from '../../stores/editorStore'

interface SharePanelProps {
  client?: BookStudioClient
}

export function SharePanel({ client }: SharePanelProps) {
  const { book, edition } = useEditorStore()
  const [message, setMessage] = useState('')

  const handlePublish = useCallback(async () => {
    if (!book || !client) {
      setMessage('API client not available')
      return
    }
    try {
      await client.books.publish(book.id)
      setMessage('출판 완료!')
    } catch {
      setMessage('출판 실패.')
    }
  }, [book, client])

  return (
    <div>
      <div className="bs-options__section">
        <div className="bs-options__label">출판</div>
        <button
          className="bs-dropdown__item"
          onClick={handlePublish}
          style={{ width: '100%', borderRadius: 4, backgroundColor: 'var(--bs-bg-tertiary)' }}
        >
          <Upload size={14} strokeWidth={1.5} />
          <span>게시된 책 버전 업데이트</span>
        </button>
      </div>

      <div className="bs-options__section">
        <div className="bs-options__label">내보내기 / 가져오기</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <button
            className="bs-dropdown__item"
            style={{ width: '100%', borderRadius: 4, backgroundColor: 'var(--bs-bg-tertiary)' }}
          >
            <FileDown size={14} strokeWidth={1.5} />
            <span>HTML로 내보내기</span>
          </button>
          <button
            className="bs-dropdown__item"
            style={{ width: '100%', borderRadius: 4, backgroundColor: 'var(--bs-bg-tertiary)' }}
          >
            <FileUp size={14} strokeWidth={1.5} />
            <span>HTML 가져오기</span>
          </button>
        </div>
      </div>

      {message && (
        <div style={{ marginTop: 8, fontSize: 12, color: 'var(--bs-accent)' }}>{message}</div>
      )}
    </div>
  )
}
