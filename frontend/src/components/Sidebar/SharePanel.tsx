import React, { useState, useCallback } from 'react'
import type { BookStudioClient } from '../../api/restClient'
import { useEditorStore } from '../../stores/editorStore'

interface SharePanelProps {
  client: BookStudioClient
}

export function SharePanel({ client }: SharePanelProps) {
  const { book, edition } = useEditorStore()
  const [exporting, setExporting] = useState(false)
  const [message, setMessage] = useState('')

  const handlePublish = useCallback(async () => {
    if (!book) return
    setExporting(true)
    setMessage('')
    try {
      await client.books.publish(book.id)
      setMessage('Published successfully!')
    } catch (e) {
      setMessage('Publish failed.')
    } finally {
      setExporting(false)
    }
  }, [book, client])

  const handleExportHTML = useCallback(async () => {
    if (!edition) return
    setExporting(true)
    try {
      const data = await client.export.htmlBook(edition.id)
      const blob = new Blob(
        [JSON.stringify(data.pages, null, 2)],
        { type: 'application/json' },
      )
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${edition.title || 'book'}_html.json`
      a.click()
      URL.revokeObjectURL(url)
    } finally {
      setExporting(false)
    }
  }, [edition, client])

  const handleImportHTML = useCallback(async () => {
    if (!edition) return
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.html,.htm'
    input.onchange = async () => {
      const file = input.files?.[0]
      if (!file) return
      const html = await file.text()
      setExporting(true)
      try {
        await client.import.html(edition.id, html)
        setMessage('Import successful! Reload to see pages.')
      } catch {
        setMessage('Import failed.')
      } finally {
        setExporting(false)
      }
    }
    input.click()
  }, [edition, client])

  return (
    <div style={{ padding: 12 }}>
      <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 12 }}>Share & Export</h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        <button onClick={handlePublish} disabled={exporting} style={btnStyle}>
          Publish
        </button>
        <button onClick={handleExportHTML} disabled={exporting} style={btnStyle}>
          Export as HTML
        </button>
        <button onClick={handleImportHTML} disabled={exporting} style={btnStyle}>
          Import HTML
        </button>
      </div>

      {message && (
        <div style={{ marginTop: 8, fontSize: 12, color: '#4a90d9' }}>{message}</div>
      )}
    </div>
  )
}

const btnStyle: React.CSSProperties = {
  padding: '8px 12px',
  fontSize: 12,
  border: '1px solid #ddd',
  borderRadius: 4,
  backgroundColor: '#fff',
  cursor: 'pointer',
  textAlign: 'left',
}
