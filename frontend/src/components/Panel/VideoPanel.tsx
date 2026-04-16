import React from 'react'
import type { Panel } from '../../types/panel'

interface VideoPanelProps {
  panel: Panel
}

export function VideoPanel({ panel }: VideoPanelProps) {
  const videoUrl = panel.fields_data?.video_url as string | undefined
  const embedUrl = panel.fields_data?.embed_url as string | undefined

  if (embedUrl) {
    return (
      <iframe
        src={embedUrl}
        style={{ width: '100%', height: '100%', border: 'none' }}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      />
    )
  }

  if (videoUrl) {
    return (
      <video
        src={videoUrl}
        controls
        style={{ width: '100%', height: '100%', objectFit: 'contain', backgroundColor: '#000' }}
      />
    )
  }

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#1a1a1a',
        borderRadius: panel.border_radius || 0,
        color: '#888',
        fontSize: 14,
      }}
    >
      <span style={{ fontSize: 32, marginRight: 8 }}>▶</span>
      Video
    </div>
  )
}
