import React from 'react'
import { useAIStore } from '../../stores/aiStore'
import { useEditorStore } from '../../stores/editorStore'
import { useAISession } from '../../hooks/useAISession'
import { AIPromptInput } from './AIPromptInput'
import { AIPlanReview } from './AIPlanReview'
import { AIGenerationProgress } from './AIGenerationProgress'
import type { BookStudioClient } from '../../api/restClient'

interface AIChatPanelProps {
  client: BookStudioClient
}

export function AIChatPanel({ client }: AIChatPanelProps) {
  const { phase, messages, plan, progress, errorMessage } = useAIStore()
  const { book, edition } = useEditorStore()
  const { startSession, approvePlan, cancelSession } = useAISession({ client })

  const handleSubmit = (prompt: string, options?: Record<string, unknown>) => {
    if (!book || !edition) return
    startSession(book.id, edition.id, prompt, options)
  }

  return (
    <div className="bs-ai">
      {/* 대화 히스토리 */}
      <div className="bs-ai__messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`bs-ai__message bs-ai__message--${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      {/* Phase별 UI */}
      <div className="bs-ai__content">
        {phase === 'idle' && (
          <AIPromptInput onSubmit={handleSubmit} />
        )}

        {phase === 'planning' && (
          <div className="bs-ai__loading">
            <div className="bs-ai__spinner" />
            <span>기획서를 작성하고 있습니다...</span>
          </div>
        )}

        {phase === 'reviewing' && plan && (
          <AIPlanReview
            plan={plan}
            onApprove={(editedPlan) => approvePlan(editedPlan)}
            onRegenerate={() => {
              if (!book || !edition) return
              const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user')
              startSession(book.id, edition.id, lastUserMsg?.content || '')
            }}
            onCancel={cancelSession}
          />
        )}

        {phase === 'generating' && (
          <AIGenerationProgress
            progress={progress}
            onCancel={cancelSession}
            onPageClick={(pageId) => {
              if (pageId) useEditorStore.getState().setActivePage(pageId)
            }}
          />
        )}

        {phase === 'complete' && (
          <div className="bs-ai__complete">
            <div className="bs-ai__complete-icon">{'\u2713'}</div>
            <p>생성 완료! 자유롭게 편집하세요.</p>
            <button
              className="bs-ai__btn bs-ai__btn--secondary"
              onClick={() => useAIStore.getState().reset()}
            >
              새로 만들기
            </button>
          </div>
        )}

        {phase === 'error' && (
          <div className="bs-ai__error">
            <p>{errorMessage}</p>
            <button
              className="bs-ai__btn bs-ai__btn--secondary"
              onClick={() => useAIStore.getState().reset()}
            >
              다시 시도
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
