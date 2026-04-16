import React from 'react'
import type { Panel } from '../../types/panel'

interface ImagePanelProps {
  panel: Panel
}

export function ImagePanel({ panel }: ImagePanelProps) {
  const imageUrl = panel.fields_data?.image_url as string | undefined

  if (!imageUrl) {
    return (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f0f0f0',
          border: '2px dashed #ccc',
          borderRadius: panel.border_radius || 0,
          fontSize: 14,
          color: '#999',
        }}
      >
        Click to add image
      </div>
    )
  }

  const maskStyle: React.CSSProperties = {}
  if (panel.masked_image === 'CIRCLE') {
    maskStyle.borderRadius = '50%'
    maskStyle.overflow = 'hidden'
  }

  return (
    <div style={{ width: '100%', height: '100%', ...maskStyle }}>
      <img
        src={imageUrl}
        alt=""
        draggable={false}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          borderRadius: panel.border_radius || 0,
          filter: panel.image_shadow !== 'initial'
            ? `drop-shadow(${panel.image_shadow})`
            : undefined,
        }}
      />
    </div>
  )
}
