import type { LayoutPreset } from './layout'

export interface Book {
  id: string
  short_key: string
  user: string
  book_mode: string
  book_layout: LayoutPreset
  privacy: 'PUBLIC' | 'FRIENDS' | 'PRIVATE'
  license: string
  custom_width?: number | null
  custom_height?: number | null
  is_active: boolean
  is_published: boolean
  allow_clone: boolean
  created_at: string
  updated_at: string
  latest_title?: string
  edition_count?: number
}

export interface BookEdition {
  id: string
  book: string
  title: string
  description: string
  is_published: boolean
  is_active: boolean
  version: number
  latest: boolean
  created_at: string
  updated_at: string
  published_at?: string | null
  fields_data?: Record<string, unknown> | null
  page_count?: number
}

export interface BookCollaborator {
  id: string
  user: string | null
  book: string
  role: 'VIEWER' | 'COMMENTER' | 'EDITOR' | 'CM' | 'MANAGER'
  invitation_email?: string | null
  accepted: boolean
  rejected: boolean
  deleted: boolean
  is_active: boolean
  created_at: string
}
