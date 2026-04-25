import { useEffect, useRef, useCallback } from 'react'
import { useEditorStore, onDirtyChange } from '../stores/editorStore'
import { SaveManager, type SaveStatus } from '../services/saveManager'
import type { BookStudioClient } from '../api/restClient'

interface UseAutoSaveOptions {
  client: BookStudioClient
  enabled?: boolean
}

export function useAutoSave({ client, enabled = true }: UseAutoSaveOptions) {
  const managerRef = useRef<SaveManager | null>(null)
  const statusRef = useRef<SaveStatus>('idle')

  // Stable getters that read from store at call time
  const getBookId = useCallback(() => useEditorStore.getState().book?.id ?? null, [])
  const getEditionId = useCallback(() => useEditorStore.getState().edition?.id ?? null, [])
  const getPageIdForPanel = useCallback((panelId: string) => {
    const { panels } = useEditorStore.getState()
    for (const [pageId, pagePanels] of Object.entries(panels)) {
      if (pagePanels.some((p) => p.id === panelId)) return pageId
    }
    return null
  }, [])

  // Initialize SaveManager
  useEffect(() => {
    if (!enabled) return

    const manager = new SaveManager({
      client,
      getBookId,
      getEditionId,
      getPageIdForPanel,
      isNewUnsaved: () => false, // TODO: 빈 북 생성 방지 플래그 연동
    })
    managerRef.current = manager

    // Subscribe to dirty changes from the store
    const unsubDirty = onDirtyChange((event) => {
      manager.enqueue(event.entityType, event.entityId, event.changes, event.category)
    })

    // Flush on page navigation (beforeunload)
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (manager.hasPendingChanges()) {
        manager.flush()
        e.preventDefault()
      }
    }
    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      unsubDirty()
      window.removeEventListener('beforeunload', handleBeforeUnload)
      manager.flush()
      manager.dispose()
      managerRef.current = null
    }
  }, [client, enabled, getBookId, getEditionId, getPageIdForPanel])

  // Flush on active page change (빠른 페이지 전환 보호)
  useEffect(() => {
    if (!enabled) return
    let prevPageId = useEditorStore.getState().activePageId
    return useEditorStore.subscribe((state) => {
      if (state.activePageId !== prevPageId) {
        if (prevPageId) managerRef.current?.flush()
        prevPageId = state.activePageId
      }
    })
  }, [enabled])

  const flush = useCallback(() => managerRef.current?.flush(), [])
  const getStatus = useCallback(() => managerRef.current?.getStatus() ?? 'idle', [])
  const retryFailed = useCallback(() => managerRef.current?.retryFailed(), [])
  const getManager = useCallback(() => managerRef.current, [])

  return { flush, getStatus, retryFailed, getManager }
}
