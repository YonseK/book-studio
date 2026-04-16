import { useEffect, useRef, useCallback, useState } from 'react'
import { useEditorStore } from '../stores/editorStore'

interface CollaborationUser {
  user_id: string
  username: string
}

interface UseCollaborationOptions {
  wsUrl: string
  bookId: string
  enabled?: boolean
}

export function useCollaboration({ wsUrl, bookId, enabled = true }: UseCollaborationOptions) {
  const wsRef = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const [users, setUsers] = useState<CollaborationUser[]>([])
  const updatePanel = useEditorStore((s) => s.updatePanel)
  const updatePage = useEditorStore((s) => s.updatePage)

  useEffect(() => {
    if (!enabled) return

    const url = `${wsUrl}/ws/studio/${bookId}/`
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setConnected(true)
    ws.onclose = () => {
      setConnected(false)
      setUsers([])
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        switch (data.type) {
          case 'panel.update':
          case 'panel.move':
            if (data.panel_id && data.changes) {
              updatePanel(data.panel_id, data.changes)
            }
            break
          case 'page.update':
            if (data.page_id && data.changes) {
              updatePage(data.page_id, data.changes)
            }
            break
          case 'user.join':
            setUsers((prev) => [...prev.filter((u) => u.user_id !== data.user_id), { user_id: data.user_id, username: data.username }])
            break
          case 'user.leave':
            setUsers((prev) => prev.filter((u) => u.user_id !== data.user_id))
            break
        }
      } catch {}
    }

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [wsUrl, bookId, enabled, updatePanel, updatePage])

  const send = useCallback(
    (type: string, payload: Record<string, unknown>) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type, ...payload }))
      }
    },
    [],
  )

  const sendPanelMove = useCallback(
    (panelId: string, changes: { left?: number; top?: number; width?: number; height?: number }) => {
      send('panel.move', { panel_id: panelId, changes })
    },
    [send],
  )

  const sendPanelUpdate = useCallback(
    (panelId: string, changes: Record<string, unknown>) => {
      send('panel.update', { panel_id: panelId, changes })
    },
    [send],
  )

  return { connected, users, send, sendPanelMove, sendPanelUpdate }
}
