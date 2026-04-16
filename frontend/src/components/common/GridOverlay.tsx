import React from 'react'

interface GridOverlayProps {
  width: number
  height: number
  gridSize: number
  color?: string
}

export function GridOverlay({ width, height, gridSize, color = 'rgba(0,0,0,0.08)' }: GridOverlayProps) {
  return (
    <svg
      className="bs-grid-overlay"
      width={width}
      height={height}
      style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none', zIndex: 9999 }}
    >
      <defs>
        <pattern id="bs-grid" width={gridSize} height={gridSize} patternUnits="userSpaceOnUse">
          <path d={`M ${gridSize} 0 L 0 0 0 ${gridSize}`} fill="none" stroke={color} strokeWidth="0.5" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#bs-grid)" />
    </svg>
  )
}
