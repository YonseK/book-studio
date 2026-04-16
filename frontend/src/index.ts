// ──── 메인 컴포넌트 ────
export { BookStudioEditor } from './components/Editor/BookStudioEditor'
export type { BookStudioEditorProps } from './components/Editor/BookStudioEditor'

// ──── 에디터 컴포넌트 ────
export { EditorLayout } from './components/Editor/EditorLayout'
export { EditorCanvas } from './components/Editor/EditorCanvas'
export { EditorHeader } from './components/Editor/EditorHeader'

// ──── 패널 컴포넌트 ────
export { PanelWrapper } from './components/Panel/PanelWrapper'
export { TextPanel } from './components/Panel/TextPanel'
export { ImagePanel } from './components/Panel/ImagePanel'
export { ShapePanel } from './components/Panel/ShapePanel'

// ──── 도구 모음 ────
export { ToolbarStrip } from './components/Toolbar/ToolbarStrip'

// ──── 사이드바 ────
export { WallpaperBank } from './components/Sidebar/WallpaperBank'
export { EditorOptions } from './components/Sidebar/EditorOptions'

// ──── 페이지 목록 ────
export { PageListPanel } from './components/PageList/PageListPanel'

// ──── 공통 ────
export { GridOverlay } from './components/common/GridOverlay'
export { AspectRatioSelector } from './components/common/AspectRatioSelector'

// ──── API ────
export { restClient } from './api/restClient'
export type { BookStudioClient, RestClientConfig } from './api/restClient'

// ──── 스토어 ────
export { useEditorStore } from './stores/editorStore'
export { useHistoryStore } from './stores/historyStore'
export { useSelectionStore } from './stores/selectionStore'

// ──── 타입 ────
export type { Book, BookEdition, BookCollaborator } from './types/book'
export type { Page, PageMemo, BackgroundType } from './types/page'
export type { Panel, MediaType } from './types/panel'
export type { LayoutPreset, LayoutConfig } from './types/layout'
export { LAYOUT_PRESETS } from './types/layout'
