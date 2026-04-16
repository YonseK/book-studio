import React, { type ReactNode } from 'react'
import { useEditorStore } from '../../stores/editorStore'

interface EditorLayoutProps {
  topbar?: ReactNode
  appNav?: ReactNode
  sidebar?: ReactNode
  toolbar?: ReactNode
  canvas: ReactNode
  minibar?: ReactNode
  pageList?: ReactNode
}

export function EditorLayout({
  topbar,
  appNav,
  sidebar,
  toolbar,
  canvas,
  minibar,
  pageList,
}: EditorLayoutProps) {
  const theme = useEditorStore((s) => s.theme)

  return (
    <div className={`bs-editor bs-theme-${theme}`}>
      {topbar && <div className="bs-topbar">{topbar}</div>}
      <div className="bs-editor__body">
        {appNav}
        {sidebar && <div className="bs-sidebar">{sidebar}</div>}
        {toolbar && <div className="bs-toolbar">{toolbar}</div>}
        <div className="bs-canvas-area">{canvas}</div>
        {minibar && <div className="bs-minibar">{minibar}</div>}
        {pageList}
      </div>
    </div>
  )
}
