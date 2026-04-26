import React, { useState } from 'react'

interface AIPromptInputProps {
  onSubmit: (prompt: string, options?: Record<string, unknown>) => void
}

export function AIPromptInput({ onSubmit }: AIPromptInputProps) {
  const [prompt, setPrompt] = useState('')
  const [showOptions, setShowOptions] = useState(false)
  const [pageCount, setPageCount] = useState<number | ''>('')
  const [tone, setTone] = useState('')

  const handleSubmit = () => {
    if (!prompt.trim()) return
    const options: Record<string, unknown> = {}
    if (pageCount) options.page_count = pageCount
    if (tone) options.tone = tone
    onSubmit(prompt.trim(), options)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="bs-ai__prompt">
      <div className="bs-ai__prompt-header">
        무엇을 만들어 드릴까요?
      </div>

      <textarea
        className="bs-ai__prompt-input"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="예: 친환경 에너지 사업 제안서, 10페이지, 투자자 대상"
        rows={3}
      />

      <button
        className="bs-ai__options-toggle"
        onClick={() => setShowOptions(!showOptions)}
      >
        {showOptions ? '옵션 숨기기' : '옵션 설정'}
      </button>

      {showOptions && (
        <div className="bs-ai__options">
          <label className="bs-ai__option-label">
            <span>페이지 수</span>
            <input
              type="number"
              min={3}
              max={30}
              value={pageCount}
              onChange={(e) => setPageCount(e.target.value ? Number(e.target.value) : '')}
              placeholder="자동"
              className="bs-ai__option-input"
            />
          </label>
          <label className="bs-ai__option-label">
            <span>톤</span>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="bs-ai__option-select"
            >
              <option value="">자동</option>
              <option value="professional">전문적</option>
              <option value="casual">캐주얼</option>
              <option value="creative">창의적</option>
              <option value="academic">학술적</option>
            </select>
          </label>
        </div>
      )}

      <button
        className="bs-ai__btn bs-ai__btn--primary"
        onClick={handleSubmit}
        disabled={!prompt.trim()}
      >
        생성 시작
      </button>
    </div>
  )
}
