import React, { useState, useEffect, useCallback } from 'react'
import type { SaveManager, SaveStatus as SaveStatusType } from '../../services/saveManager'

interface SaveStatusProps {
  getManager: () => SaveManager | null
}

export function SaveStatus({ getManager }: SaveStatusProps) {
  const [status, setStatus] = useState<SaveStatusType>('idle')

  useEffect(() => {
    const manager = getManager()
    if (!manager) return
    setStatus(manager.getStatus())
    return manager.onStatusChange(setStatus)
  }, [getManager])

  const handleRetry = useCallback(() => {
    getManager()?.retryFailed()
  }, [getManager])

  if (status === 'idle') return null

  return (
    <div className="bs-save-status" data-status={status}>
      {status === 'saving' && <span className="bs-save-status__text">저장 중...</span>}
      {status === 'saved' && <span className="bs-save-status__text">저장됨</span>}
      {status === 'error' && (
        <button className="bs-save-status__retry" onClick={handleRetry}>
          저장 실패 — 재시도
        </button>
      )}
    </div>
  )
}
