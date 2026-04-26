import React from 'react'
import type { AIPageProgress } from '../../stores/aiStore'

interface AIGenerationProgressProps {
  progress: AIPageProgress[]
  onCancel: () => void
  onPageClick: (pageId?: string) => void
}

export function AIGenerationProgress({ progress, onCancel, onPageClick }: AIGenerationProgressProps) {
  const completedCount = progress.filter((p) => p.status === 'complete').length
  const totalCount = progress.length
  const percentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

  return (
    <div className="bs-ai__progress">
      <div className="bs-ai__progress-bar">
        <div className="bs-ai__progress-fill" style={{ width: `${percentage}%` }} />
      </div>
      <div className="bs-ai__progress-label">
        {completedCount}/{totalCount} 페이지 완료
      </div>

      <div className="bs-ai__progress-list">
        {progress.map((p) => (
          <button
            key={p.index}
            className={`bs-ai__progress-item bs-ai__progress-item--${p.status}`}
            onClick={() => p.pageId && onPageClick(p.pageId)}
            disabled={p.status === 'pending'}
          >
            <span className="bs-ai__progress-icon">
              {p.status === 'complete' && '\u2713'}
              {p.status === 'generating' && '\u25CF'}
              {p.status === 'pending' && '\u25CB'}
              {p.status === 'error' && '\u2717'}
            </span>
            <span className="bs-ai__progress-text">
              {p.index + 1}. {p.role}
            </span>
          </button>
        ))}
      </div>

      <button className="bs-ai__btn bs-ai__btn--text bs-ai__btn--danger" onClick={onCancel}>
        생성 취소
      </button>
    </div>
  )
}
