export type BackgroundType = 'CLR' | 'WP' | 'VOD'

export interface Page {
  id: string
  short_key: string
  user: string
  book_edition: string
  order: number
  background_type: BackgroundType
  wallpaper?: string | null
  wallpaper_image?: string | null
  background_position_x: number
  background_position_y: number
  background_color: string
  opacity: number
  description: string
  is_active: boolean
  is_locked: boolean
  prevent_deletion: boolean
  show_page_memo: boolean
  created_at: string
  updated_at: string
  fields_data?: Record<string, unknown> | null
  panel_count?: number
  has_document?: boolean
}

export interface PageMemo {
  id: string
  user: string
  page: string
  text: string
  theme: number
  arrow?: string | null
  decimal_width: number
  decimal_height: number
  translate_x: number
  translate_y: number
  private: boolean
  is_secret: boolean
  new_memo: boolean
  created_at: string
  updated_at: string
}
