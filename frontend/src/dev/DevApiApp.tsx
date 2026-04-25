import React, { useEffect, useState } from 'react'
import { restClient } from '../api/restClient'
import { BookStudioEditor } from '../components/Editor/BookStudioEditor'

const client = restClient({ baseURL: '/api/studio' })

export function DevApiApp() {
  const [bookId, setBookId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function setup() {
      try {
        const res = await fetch('/api/dev-setup/', { credentials: 'same-origin' })
        if (!res.ok) throw new Error(`Setup failed: ${res.status}`)
        const data = await res.json()
        // CSRF 쿠키가 자동 설정됨 (Django get_token)
        setBookId(data.book_id)
      } catch (e) {
        setError(e instanceof Error ? e.message : String(e))
      }
    }
    setup()
  }, [])

  if (error) {
    return (
      <div style={{ padding: 40, color: '#ff5050', fontFamily: 'monospace' }}>
        <h2>Backend connection failed</h2>
        <p>{error}</p>
        <p style={{ color: '#999', marginTop: 12 }}>
          백엔드가 실행 중인지 확인하세요:<br />
          <code>cd backend && DJANGO_SETTINGS_MODULE=tests.settings python -m django migrate && DJANGO_SETTINGS_MODULE=tests.settings python -m django runserver</code>
        </p>
      </div>
    )
  }

  if (!bookId) {
    return <div style={{ padding: 40, color: '#999' }}>Loading...</div>
  }

  return <BookStudioEditor client={client} bookId={bookId} />
}
