export type LayoutPreset =
  | 'PPTX_WIDE'
  | 'PPTX_STD'
  | 'PPTX_WP'
  | 'PPTX_SP'
  | 'BOOK'
  | 'A4_LAND'
  | 'MBOOK'
  | 'CD'
  | 'CARD'
  | 'CINEMA'
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
  PPTX_STD: { preset: 'PPTX_STD', width: 960, height: 720, printWidth: 254, printHeight: 190.5, label: 'PPTX Standard 4:3' },
  PPTX_WP: { preset: 'PPTX_WP', width: 720, height: 1280, printWidth: 190.5, printHeight: 338.7, label: 'PPTX Wide Portrait 9:16' },
  PPTX_SP: { preset: 'PPTX_SP', width: 720, height: 960, printWidth: 190.5, printHeight: 254, label: 'PPTX Standard Portrait 3:4' },
  BOOK: { preset: 'BOOK', width: 768, height: 1086, printWidth: 203.2, printHeight: 287.34, label: 'A4 Portrait' },
  A4_LAND: { preset: 'A4_LAND', width: 1086, height: 768, printWidth: 287.34, printHeight: 203.2, label: 'A4 Landscape' },
  MBOOK: { preset: 'MBOOK', width: 768, height: 960, printWidth: 203.2, printHeight: 254, label: 'Mini Book' },
  CD: { preset: 'CD', width: 768, height: 768, printWidth: 203.2, printHeight: 203.2, label: 'Square / CD' },
  CARD: { preset: 'CARD', width: 768, height: 552, printWidth: 203.2, printHeight: 146.05, label: 'Card' },
  CINEMA: { preset: 'CINEMA', width: 768, height: 432, printWidth: 203.2, printHeight: 114.3, label: 'Cinema 16:9' },
  BANNER: { preset: 'BANNER', width: 768, height: 0, label: 'Banner' },
}
