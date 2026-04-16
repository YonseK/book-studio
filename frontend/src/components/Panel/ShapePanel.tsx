import React from 'react'
import type { Panel } from '../../types/panel'

interface ShapePanelProps {
  panel: Panel
}

const SHAPES: Record<number, (w: number, h: number, color: string, stroke: string, strokeW: number) => React.ReactNode> = {
  0: (w, h, fill, stroke, sw) => <rect width={w} height={h} fill={fill} stroke={stroke} strokeWidth={sw} />,
  1: (w, h, fill, stroke, sw) => <ellipse cx={w/2} cy={h/2} rx={w/2} ry={h/2} fill={fill} stroke={stroke} strokeWidth={sw} />,
  2: (w, h, fill, stroke, sw) => <polygon points={`${w/2},0 ${w},${h} 0,${h}`} fill={fill} stroke={stroke} strokeWidth={sw} />,
  3: (w, h, fill, stroke, sw) => <polygon points={`${w/2},0 ${w},${h/2} ${w/2},${h} 0,${h/2}`} fill={fill} stroke={stroke} strokeWidth={sw} />,
  4: (w, h, fill, stroke, sw) => {
    const points = Array.from({ length: 5 }, (_, i) => {
      const angle = (i * 72 - 90) * Math.PI / 180
      const outerR = Math.min(w, h) / 2
      const innerR = outerR * 0.382
      const cx = w / 2, cy = h / 2
      const ox = cx + outerR * Math.cos(angle)
      const oy = cy + outerR * Math.sin(angle)
      const iAngle = angle + 36 * Math.PI / 180
      const ix = cx + innerR * Math.cos(iAngle)
      const iy = cy + innerR * Math.sin(iAngle)
      return `${ox},${oy} ${ix},${iy}`
    }).join(' ')
    return <polygon points={points} fill={fill} stroke={stroke} strokeWidth={sw} />
  },
}

export function ShapePanel({ panel }: ShapePanelProps) {
  const w = panel.width
  const h = panel.height
  const fill = panel.color !== '#ffffff' ? panel.color : panel.background_color
  const stroke = panel.border_color
  const strokeW = panel.stroke_width || panel.border_width

  const shapeRenderer = SHAPES[panel.shape_type] || SHAPES[0]

  return (
    <svg
      width="100%"
      height="100%"
      viewBox={`0 0 ${w} ${h}`}
      preserveAspectRatio="none"
    >
      {shapeRenderer(w, h, fill, stroke, strokeW)}
    </svg>
  )
}
