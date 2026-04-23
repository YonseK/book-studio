import React from 'react'
import { useEditorStore } from '../../stores/editorStore'
import { AspectRatioSelector } from '../common/AspectRatioSelector'

export function BookInfoPanel() {
  const { edition, book, setEdition, setBook } = useEditorStore()

  return (
    <div>
      <div className="bs-options__section">
        <div className="bs-options__label">제목</div>
        <input
          type="text"
          value={edition?.title || ''}
          onChange={(e) => {
            if (edition) {
              setEdition({ ...edition, title: e.target.value })
            }
          }}
          placeholder="제목 없음"
          style={{
            width: '100%',
            height: 32,
            padding: '0 8px',
            backgroundColor: 'var(--bs-bg-tertiary)',
            borderRadius: 4,
            fontSize: 13,
          }}
        />
      </div>

      <div className="bs-options__section">
        <div className="bs-options__label">설명</div>
        <textarea
          value={edition?.description || ''}
          onChange={(e) => {
            if (edition) {
              setEdition({ ...edition, description: e.target.value })
            }
          }}
          placeholder="설명을 입력하세요"
          rows={3}
          style={{
            width: '100%',
            padding: 8,
            backgroundColor: 'var(--bs-bg-tertiary)',
            borderRadius: 4,
            fontSize: 13,
            resize: 'vertical',
          }}
        />
      </div>

      <div className="bs-options__section">
        <div className="bs-options__label">레이아웃</div>
        <AspectRatioSelector />
      </div>

      <div className="bs-options__section">
        <div className="bs-options__label">공개 설정</div>
        <select
          value={book?.privacy || 'PRIVATE'}
          onChange={(e) => {
            if (book) {
              setBook({ ...book, privacy: e.target.value as 'PRIVATE' | 'PUBLIC' | 'FRIENDS' })
            }
          }}
          style={{
            width: '100%',
            height: 32,
            padding: '0 8px',
            backgroundColor: 'var(--bs-bg-tertiary)',
            borderRadius: 4,
            fontSize: 13,
            color: 'var(--bs-text-primary)',
          }}
        >
          <option value="PRIVATE">비공개</option>
          <option value="PUBLIC">공개</option>
          <option value="FRIENDS">친구 공개</option>
        </select>
      </div>
    </div>
  )
}
