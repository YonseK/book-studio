// ── AI Session API 응답 타입 ──

export interface AISessionResponse {
  id: string
  book: string
  edition: string
  prompt: string
  options: Record<string, unknown>
  status: AISessionStatus
  error_message: string
  plan: AIPlan | null
  pattern_set: string | null
  total_pages: number
  completed_pages: number
  model_used: string
  total_input_tokens: number
  total_output_tokens: number
  created_at: string
  updated_at: string
  completed_at: string | null
}

export type AISessionStatus =
  | 'PLANNING'
  | 'REVIEW'
  | 'APPROVED'
  | 'GENERATING'
  | 'COMPLETE'
  | 'FAILED'
  | 'CANCELLED'

// ── 기획서 ──

export interface AIPlan {
  title: string
  total_pages: number
  tone: string
  target_audience: string
  color_mood: string
  pages: AIPagePlan[]
}

export interface AIPagePlan {
  index: number
  role: string
  purpose: string
  key_points: string[]
  suggested_pattern_category: string
  needs_image: boolean
}

// ── 디자인 패턴 ──

export interface DesignPatternListItem {
  id: string
  name: string
  category: string
  tags: string[]
  target_layout: string
  palette: ColorPalette
  source: 'LEGACY' | 'CURATED' | 'AI_GEN'
  is_active: boolean
  usage_count: number
  slot_count: number
}

export interface DesignPatternSet {
  id: string
  name: string
  description: string
  palette: ColorPalette
  target_layout: string
  is_active: boolean
  patterns: { pattern: DesignPatternListItem; priority: number }[]
  created_at: string
}

export interface ColorPalette {
  primary: string
  secondary: string
  accent: string
  text: string
  background: string
}
