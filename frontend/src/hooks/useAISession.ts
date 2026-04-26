import { useCallback, useRef, useEffect } from 'react'
import { useAIStore } from '../stores/aiStore'
import { useEditorStore, withRemoteUpdate } from '../stores/editorStore'
import type { BookStudioClient } from '../api/restClient'
import type { Page } from '../types/page'
import type { Panel } from '../types/panel'

interface UseAISessionOptions {
  client: BookStudioClient
}

export function useAISession({ client }: UseAISessionOptions) {
  const eventSourceRef = useRef<EventSource | null>(null)

  const {
    sessionId,
    setSession, setPhase, setPlan, updatePageProgress,
    setGeneratingPage, addMessage, setError, reset,
  } = useAIStore()

  const { addPage, setPanels, setActivePage } = useEditorStore()

  // ── SSE 연결 ──
  const connectStream = useCallback((sid: string) => {
    eventSourceRef.current?.close()

    const url = `${client.getBaseURL()}/ai/sessions/${sid}/stream/`
    const es = new EventSource(url, { withCredentials: true })
    eventSourceRef.current = es

    es.addEventListener('session_status', (e) => {
      const data = JSON.parse(e.data)
      if (data.plan) {
        setPlan(data.plan)
        if (data.completed_pages > 0) {
          for (let i = 0; i < data.completed_pages; i++) {
            updatePageProgress(i, { status: 'complete' })
          }
        }
      }
      if (data.status === 'REVIEW') setPhase('reviewing')
      else if (data.status === 'GENERATING') setPhase('generating')
      else if (data.status === 'COMPLETE') setPhase('complete')
      else if (data.status === 'FAILED') setError(data.error_message || 'Unknown error')
    })

    es.addEventListener('planning_complete', (e) => {
      const data = JSON.parse(e.data)
      setPlan(data.plan)
      setPhase('reviewing')
      addMessage({ role: 'assistant', content: '기획서를 작성했습니다. 검토해주세요.' })
    })

    es.addEventListener('page_start', (e) => {
      const data = JSON.parse(e.data)
      setGeneratingPage(data.page_index)
      updatePageProgress(data.page_index, { status: 'generating' })
    })

    es.addEventListener('page_complete', (e) => {
      const data = JSON.parse(e.data)
      const page: Page = data.page
      const panels: Panel[] = data.panels

      withRemoteUpdate(() => {
        addPage(page)
        setPanels(page.id, panels)
      })

      updatePageProgress(data.page_index, { status: 'complete', pageId: page.id })

      if (data.page_index === 0) {
        setActivePage(page.id)
      }
    })

    es.addEventListener('page_error', (e) => {
      const data = JSON.parse(e.data)
      updatePageProgress(data.page_index, { status: 'error', error: data.error })
    })

    es.addEventListener('generation_complete', () => {
      setPhase('complete')
      setGeneratingPage(null)
      addMessage({ role: 'assistant', content: '모든 페이지가 생성되었습니다. 자유롭게 편집하세요.' })
    })

    es.addEventListener('error', (e: any) => {
      const data = e.data ? JSON.parse(e.data) : {}
      setError(data.message || 'Connection error')
    })

    es.addEventListener('done', () => {
      es.close()
    })
  }, [client, setPlan, setPhase, updatePageProgress, setGeneratingPage, addMessage, setError, addPage, setPanels, setActivePage])

  // ── 세션 시작 ──
  const startSession = useCallback(async (
    bookId: string,
    editionId: string,
    prompt: string,
    options?: Record<string, unknown>,
  ) => {
    try {
      reset()
      setPhase('planning')
      addMessage({ role: 'user', content: prompt })

      const session = await client.ai.createSession({
        book: bookId,
        edition: editionId,
        prompt,
        options: options || {},
      })

      setSession(session.id)

      // 동기 모드에서는 planning이 이미 완료됨
      if (session.status === 'REVIEW' && session.plan) {
        setPlan(session.plan)
        setPhase('reviewing')
        addMessage({ role: 'assistant', content: '기획서를 작성했습니다. 검토해주세요.' })
      } else {
        connectStream(session.id)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to start session')
    }
  }, [client, reset, setPhase, addMessage, setSession, setPlan, connectStream, setError])

  // ── 기획서 승인 ──
  const approvePlan = useCallback(async (editedPlan?: unknown) => {
    if (!sessionId) return
    try {
      setPhase('generating')
      addMessage({ role: 'user', content: '이대로 진행합니다.' })

      const session = await client.ai.approveSession(sessionId, { plan: editedPlan })

      // 동기 모드에서 이미 완료되었을 수 있음
      if (session.status === 'COMPLETE') {
        setPhase('complete')
        addMessage({ role: 'assistant', content: '모든 페이지가 생성되었습니다.' })
      } else {
        // Celery 모드: SSE 연결
        if (!eventSourceRef.current || eventSourceRef.current.readyState === EventSource.CLOSED) {
          connectStream(sessionId)
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to approve plan')
    }
  }, [sessionId, client, setPhase, addMessage, connectStream, setError])

  // ── 세션 취소 ──
  const cancelSession = useCallback(async () => {
    if (!sessionId) return
    try {
      await client.ai.cancelSession(sessionId)
      eventSourceRef.current?.close()
      reset()
    } catch (err: any) {
      setError(err.message || 'Failed to cancel')
    }
  }, [sessionId, client, reset, setError])

  // ── Cleanup ──
  useEffect(() => {
    return () => { eventSourceRef.current?.close() }
  }, [])

  return { startSession, approvePlan, cancelSession }
}
