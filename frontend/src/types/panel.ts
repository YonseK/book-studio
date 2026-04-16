export type MediaType =
  | 'TXT' | 'HL' | 'IMG' | 'WS' | 'VOD' | 'AUDIO'
  | 'EV' | 'SHA' | 'WGT' | 'PDF' | 'FILE' | 'DOC' | 'PT' | 'BC'

export interface Panel {
  id: string
  user: string
  page: string
  media_type: MediaType
  text: string
  headline: string
  link_url: string
  image?: string | null
  masked_image?: string | null
  // style
  background_color: string
  background_opacity: number
  left: number
  top: number
  width: number
  height: number
  z_index: number
  padding: number
  font_size: number
  font_family: string
  font_style: string
  font_weight: string
  color: string
  text_align: string
  opacity: number
  letter_spacing: number
  line_height: number
  text_decoration: string
  border_width: number
  border_radius: number
  border_color: string
  border_style: string
  border_opacity: number
  stroke_width: number
  text_shadow: string
  box_shadow: string
  image_shadow: string
  text_shadow_px: number
  box_shadow_px: number
  image_shadow_px: number
  drop_shadow_px: number
  angle: number
  translate_x: number
  translate_y: number
  scale_x: number
  scale_y: number
  rotate: number
  font_bold: boolean
  font_italic: boolean
  text_underline: boolean
  // state
  order: number
  is_active: boolean
  fixed: boolean
  shape_type: number
  created_at: string
  updated_at: string
  fields_data?: Record<string, unknown> | null
}
