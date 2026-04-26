// ──── 스타일 (라이브러리 빌드 시 CSS로 추출됨) ────
import './styles/fonts.css'
import './styles/variables.css'
import './styles/editor.css'
import './styles/ai.css'

// ──── 메인 컴포넌트 ────
export { BookStudioEditor } from './components/Editor/BookStudioEditor'
export type { BookStudioEditorProps } from './components/Editor/BookStudioEditor'

// ──── 에디터 컴포넌트 ────
export { EditorLayout } from './components/Editor/EditorLayout'
export { EditorCanvas } from './components/Editor/EditorCanvas'
export { PositionBar } from './components/Editor/PositionBar'

// ──── 패널 컴포넌트 ────
export { PanelWrapper } from './components/Panel/PanelWrapper'
export { TextPanel } from './components/Panel/TextPanel'
export { ImagePanel } from './components/Panel/ImagePanel'
export { ShapePanel } from './components/Panel/ShapePanel'
export { VideoPanel } from './components/Panel/VideoPanel'
export { EmbedPanel } from './components/Panel/EmbedPanel'

// ──── 앱 네비게이션 ────
export { AppNav } from './components/AppNav/AppNav'

// ──── 도구 모음 ────
export { ToolbarStrip } from './components/Toolbar/ToolbarStrip'

// ──── 사이드바 ────
export { WallpaperBank } from './components/Sidebar/WallpaperBank'
export { EditorOptions } from './components/Sidebar/EditorOptions'
export { MediaBank } from './components/Sidebar/MediaBank'
export { ItemBank } from './components/Sidebar/ItemBank'
export { SharePanel } from './components/Sidebar/SharePanel'

// ──── 뷰어 ────
export { BookViewer } from './components/Viewer/BookViewer'

// ──── Hooks ────
export { useCollaboration } from './hooks/useCollaboration'

// ──── 페이지 목록 ────
export { PageListPanel } from './components/PageList/PageListPanel'

// ──── 공통 ────
export { GridOverlay } from './components/common/GridOverlay'
export { AspectRatioSelector } from './components/common/AspectRatioSelector'

// ──── AI ────
export { AIChatPanel } from './components/AI/AIChatPanel'
export { useAISession } from './hooks/useAISession'
export { useAIStore } from './stores/aiStore'
export type { AIPhase, AIPageProgress } from './stores/aiStore'

// ──── Context ────
export { ClientContext, useClient } from './contexts/ClientContext'

// ──── API ────
export { restClient } from './api/restClient'
export type { BookStudioClient, RestClientConfig } from './api/restClient'

// ──── 스토어 ────
export { useEditorStore } from './stores/editorStore'
export { useHistoryStore } from './stores/historyStore'

// ──── 타입 ────
export type { Book, BookEdition, BookCollaborator } from './types/book'
export type { Page, PageMemo, BackgroundType } from './types/page'
export type { Panel, MediaType } from './types/panel'
export type { LayoutPreset, LayoutConfig } from './types/layout'
export { LAYOUT_PRESETS } from './types/layout'
export type { AIPlan, AIPagePlan, AISessionResponse, DesignPatternListItem, DesignPatternSet, ColorPalette } from './types/ai'
