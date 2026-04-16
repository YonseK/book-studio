import React, { type ReactNode } from 'react'
import { useEditorStore } from '../../stores/editorStore'

interface EditorLayoutProps {
  sidebar?: ReactNode
  canvas: ReactNode
  pageList?: ReactNode
  header?: ReactNode
  toolbar?: ReactNode
}

export function EditorLayout({ sidebar, canvas, pageList, header, toolbar }: EditorLayoutProps) {
  const theme = useEditorStore((s) => s.theme)

  return (
    <div
      className={`bs-editor bs-theme-${theme}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        backgroundColor: theme === 'dark' ? '#1a1a2e' : '#f5f5f5',
        color: theme === 'dark' ? '#e0e0e0' : '#333',
      }}
    >
      {header && (
        <div className="bs-editor-header" style={{ flexShrink: 0, borderBottom: '1px solid #ddd' }}>
          {header}
        </div>
      )}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {toolbar && (
          <div
            className="bs-editor-toolbar"
            style={{
              width: 48,
              flexShrink: 0,
              borderRight: '1px solid #ddd',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              padding: '8px 0',
              gap: 4,
              backgroundColor: theme === 'dark' ? '#16213e' : '#fff',
            }}
          >
            {toolbar}
          </div>
        )}
        {sidebar && (
          <div
            className="bs-editor-sidebar"
            style={{
              width: 280,
              flexShrink: 0,
              borderRight: '1px solid #ddd',
              overflow: 'auto',
              backgroundColor: theme === 'dark' ? '#16213e' : '#fff',
            }}
          >
            {sidebar}
          </div>
        )}
        <div
          className="bs-editor-canvas-area"
          style={{
            flex: 1,
            overflow: 'auto',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: theme === 'dark' ? '#0f3460' : '#e8e8e8',
          }}
        >
          {canvas}
        </div>
        {pageList && (
          <div
            className="bs-editor-pagelist"
            style={{
              width: 200,
              flexShrink: 0,
              borderLeft: '1px solid #ddd',
              overflow: 'auto',
              backgroundColor: theme === 'dark' ? '#16213e' : '#fff',
            }}
          >
            {pageList}
          </div>
        )}
      </div>
    </div>
  )
}
