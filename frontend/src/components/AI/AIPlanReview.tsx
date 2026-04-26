import React, { useState } from 'react'
import type { AIPlan } from '../../types/ai'

interface AIPlanReviewProps {
  plan: AIPlan
  onApprove: (editedPlan?: AIPlan) => void
  onRegenerate: () => void
  onCancel: () => void
}

export function AIPlanReview({ plan, onApprove, onRegenerate, onCancel }: AIPlanReviewProps) {
  const [editedPlan, setEditedPlan] = useState<AIPlan>(plan)
  const [isEditing, setIsEditing] = useState(false)

  return (
    <div className="bs-ai__plan">
      <div className="bs-ai__plan-header">
        <h4>{editedPlan.title}</h4>
        <span className="bs-ai__plan-meta">
          {editedPlan.total_pages}페이지 / {editedPlan.tone}
        </span>
      </div>

      <div className="bs-ai__plan-pages">
        {editedPlan.pages.map((page, i) => (
          <div key={i} className="bs-ai__plan-page">
            <span className="bs-ai__plan-page-num">{i + 1}</span>
            <div className="bs-ai__plan-page-info">
              <span className="bs-ai__plan-page-role">{page.role}</span>
              {isEditing ? (
                <input
                  className="bs-ai__plan-page-edit"
                  value={page.purpose}
                  onChange={(e) => {
                    const updated = { ...editedPlan, pages: [...editedPlan.pages] }
                    updated.pages[i] = { ...updated.pages[i], purpose: e.target.value }
                    setEditedPlan(updated)
                  }}
                />
              ) : (
                <span className="bs-ai__plan-page-purpose">{page.purpose}</span>
              )}
            </div>
            {page.needs_image && (
              <span className="bs-ai__plan-page-badge">IMG</span>
            )}
          </div>
        ))}
      </div>

      <div className="bs-ai__plan-actions">
        <button
          className="bs-ai__btn bs-ai__btn--text"
          onClick={() => setIsEditing(!isEditing)}
        >
          {isEditing ? '편집 완료' : '수정'}
        </button>
        <button className="bs-ai__btn bs-ai__btn--text" onClick={onRegenerate}>
          다시 만들기
        </button>
        <button className="bs-ai__btn bs-ai__btn--text" onClick={onCancel}>
          취소
        </button>
        <button
          className="bs-ai__btn bs-ai__btn--primary"
          onClick={() => onApprove(isEditing ? editedPlan : undefined)}
        >
          이대로 진행
        </button>
      </div>
    </div>
  )
}
