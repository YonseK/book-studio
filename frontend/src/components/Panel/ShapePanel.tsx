import React from 'react'
import type { Panel } from '../../types/panel'

type ShapeRenderer = (fill: string, stroke: string, sw: number) => React.ReactNode

const SHAPES: Record<number, ShapeRenderer> = {
  // Arrows
  1: (f, s, sw) => <path d="M2,10 L2,14 L16,14 L16,19 L22,12 L16,5 L16,10 Z" fill={f} stroke={s} strokeWidth={sw} />,
  2: (f, s, sw) => <path d="M6,5 L6,10 L2,10 L2,14 L6,14 L6,19 L12,12 Z M18,5 L18,10 L22,10 L22,14 L18,14 L18,19 L12,12 Z" fill={f} stroke={s} strokeWidth={sw} fillRule="evenodd" />,
  16: (f, s, sw) => <rect x="1" y="9" width="22" height="6" rx="0.5" fill={f} stroke={s} strokeWidth={sw} />,

  // Lines
  17: (f, s, sw) => <line x1="1" y1="12" x2="23" y2="12" stroke={s || f} strokeWidth={sw || 2} strokeLinecap="round" />,
  18: (f, s, sw) => <><line x1="4" y1="12" x2="20" y2="12" stroke={s || f} strokeWidth={sw || 2} /><circle cx="3" cy="12" r="2.5" fill={f} stroke={s} strokeWidth={sw || 0.5} /><circle cx="21" cy="12" r="2.5" fill={f} stroke={s} strokeWidth={sw || 0.5} /></>,
  19: (f, s, sw) => <><line x1="4" y1="12" x2="20" y2="12" stroke={s || f} strokeWidth={sw || 2} /><polygon points="1,12 6,8 6,16" fill={f} stroke={s} strokeWidth={sw || 0.5} /><circle cx="21" cy="12" r="2.5" fill={f} stroke={s} strokeWidth={sw || 0.5} /></>,

  // Title boxes
  3: (f, s, sw) => <path d="M1,2 L18,2 L23,12 L18,22 L1,22 Z" fill={f} stroke={s} strokeWidth={sw} />,
  4: (f, s, sw) => <path d="M4,2 L18,2 L23,12 L18,22 L4,22 L9,12 Z" fill={f} stroke={s} strokeWidth={sw} />,
  5: (f, s, sw) => <path d="M4,2 L20,2 L23,12 L20,22 L4,22 L1,12 Z" fill={f} stroke={s} strokeWidth={sw} />,
  6: (f, s, sw) => <rect x="1" y="3" width="22" height="18" rx="9" fill={f} stroke={s} strokeWidth={sw} />,
  20: (f, s, sw) => <path d="M5,2 L23,2 L19,22 L1,22 Z" fill={f} stroke={s} strokeWidth={sw} />,
  21: (f, s, sw) => <rect x="1" y="1" width="22" height="22" rx="3.5" fill={f} stroke={s} strokeWidth={sw} />,

  // Basic shapes
  7: (f, s, sw) => <circle cx="12" cy="12" r="11" fill={f} stroke={s} strokeWidth={sw} />,
  8: (f, s, sw) => <polygon points="12,2 22,22 2,22" fill={f} stroke={s} strokeWidth={sw} />,
  9: (f, s, sw) => <rect x="1" y="4" width="22" height="16" fill={f} stroke={s} strokeWidth={sw} />,
  10: (f, s, sw) => {
    // Regular pentagon
    const pts = Array.from({length: 5}, (_, i) => {
      const a = (i * 72 - 90) * Math.PI / 180
      return `${12 + 11 * Math.cos(a)},${12 + 11 * Math.sin(a)}`
    }).join(' ')
    return <polygon points={pts} fill={f} stroke={s} strokeWidth={sw} />
  },
  11: (f, s, sw) => {
    // Regular hexagon
    const pts = Array.from({length: 6}, (_, i) => {
      const a = (i * 60 - 90) * Math.PI / 180
      return `${12 + 11 * Math.cos(a)},${12 + 11 * Math.sin(a)}`
    }).join(' ')
    return <polygon points={pts} fill={f} stroke={s} strokeWidth={sw} />
  },
  12: (f, s, sw) => {
    // Regular octagon
    const pts = Array.from({length: 8}, (_, i) => {
      const a = (i * 45 - 90) * Math.PI / 180
      return `${12 + 11 * Math.cos(a)},${12 + 11 * Math.sin(a)}`
    }).join(' ')
    return <polygon points={pts} fill={f} stroke={s} strokeWidth={sw} />
  },
  13: (f, s, sw) => <path d="M12,21.35 C5.4,15.36 1.5,11.28 1.5,7.5 C1.5,4.42 3.86,2 6.75,2 C8.51,2 10.11,2.93 12,4.34 C13.89,2.93 15.49,2 17.25,2 C20.14,2 22.5,4.42 22.5,7.5 C22.5,11.28 18.6,15.36 12,21.35 Z" fill={f} stroke={s} strokeWidth={sw} />,
  14: (f, s, sw) => {
    // 5-pointed star
    const pts = Array.from({length: 5}, (_, i) => {
      const outerA = (i * 72 - 90) * Math.PI / 180
      const innerA = outerA + 36 * Math.PI / 180
      const ox = 12 + 11 * Math.cos(outerA)
      const oy = 12 + 11 * Math.sin(outerA)
      const ix = 12 + 4.5 * Math.cos(innerA)
      const iy = 12 + 4.5 * Math.sin(innerA)
      return `${ox},${oy} ${ix},${iy}`
    }).join(' ')
    return <polygon points={pts} fill={f} stroke={s} strokeWidth={sw} />
  },
  15: (f, s, sw) => {
    // Badge/sun with 12 points
    const pts = Array.from({length: 12}, (_, i) => {
      const outerA = (i * 30 - 90) * Math.PI / 180
      const innerA = outerA + 15 * Math.PI / 180
      const ox = 12 + 11 * Math.cos(outerA)
      const oy = 12 + 11 * Math.sin(outerA)
      const ix = 12 + 7.5 * Math.cos(innerA)
      const iy = 12 + 7.5 * Math.sin(innerA)
      return `${ox},${oy} ${ix},${iy}`
    }).join(' ')
    return <polygon points={pts} fill={f} stroke={s} strokeWidth={sw} />
  },

  // Speech bubbles
  22: (f, s, sw) => <path d="M3,2 L21,2 Q23,2 23,4 L23,16 Q23,18 21,18 L8,18 L3,22 L4,18 L3,18 Q1,18 1,16 L1,4 Q1,2 3,2 Z" fill={f} stroke={s} strokeWidth={sw} />,
  23: (f, s, sw) => <path d="M3,2 L21,2 Q23,2 23,4 L23,16 Q23,18 21,18 L14,18 L12,22 L10,18 L3,18 Q1,18 1,16 L1,4 Q1,2 3,2 Z" fill={f} stroke={s} strokeWidth={sw} />,
  24: (f, s, sw) => <path d="M3,2 L21,2 Q23,2 23,4 L23,16 Q23,18 21,18 L20,18 L21,22 L16,18 L3,18 Q1,18 1,16 L1,4 Q1,2 3,2 Z" fill={f} stroke={s} strokeWidth={sw} />,
}

// Ordered list for the shape bank grid display
export const SHAPE_IDS_ORDERED = [
  1, 2, 16, 17, 18, 19,  // arrows & lines
  3, 4, 5, 6, 20, 21,    // title boxes
  7, 8, 9, 10, 11, 12,   // basic shapes
  13, 14, 15,             // heart, star, badge
  22, 23, 24,             // speech bubbles
]

interface ShapePanelProps {
  panel: Panel
}

export function ShapePanel({ panel }: ShapePanelProps) {
  const fill = panel.color !== '#ffffff' ? panel.color : panel.background_color
  const stroke = panel.border_color
  const strokeW = panel.stroke_width || panel.border_width

  const renderer = SHAPES[panel.shape_type] || SHAPES[9] // default to square

  return (
    <svg
      width="100%"
      height="100%"
      viewBox="0 0 24 24"
      preserveAspectRatio="none"
      style={{ opacity: panel.opacity }}
    >
      {renderer(fill, stroke, strokeW)}
    </svg>
  )
}
