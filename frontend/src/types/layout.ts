export type LayoutPreset =
  | 'PPTX_WIDE'
  | 'PPTX_WP'
  | 'BOOK'
  | 'A4_LAND'
  | 'CD'
  | 'BANNER'
  | 'CUSTOM'

export interface LayoutConfig {
  preset: LayoutPreset
  width: number
  height: number
  printWidth?: number
  printHeight?: number
  label: string
}

export const LAYOUT_PRESETS: Record<string, LayoutConfig> = {
  PPTX_WIDE: { preset: 'PPTX_WIDE', width: 1280, height: 720, printWidth: 338.7, printHeight: 190.5, label: 'PPTX Wide 16:9' },
  PPTX_WP: { preset: 'PPTX_WP', width: 720, height: 1280, printWidth: 190.5, printHeight: 338.7, label: 'PPTX Wide Portrait 9:16' },
  BOOK: { preset: 'BOOK', width: 768, height: 1086, printWidth: 203.2, printHeight: 287.34, label: 'A4 Portrait' },
  A4_LAND: { preset: 'A4_LAND', width: 1086, height: 768, printWidth: 287.34, printHeight: 203.2, label: 'A4 Landscape' },
  CD: { preset: 'CD', width: 768, height: 768, printWidth: 203.2, printHeight: 203.2, label: 'Square / CD' },
  BANNER: { preset: 'BANNER', width: 768, height: 0, label: 'Banner' },
}
