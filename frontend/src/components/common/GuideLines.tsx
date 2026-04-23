import React, { useMemo } from 'react'
import { useEditorStore } from '../../stores/editorStore'

const SNAP_THRESHOLD = 5 // px

interface GuideLine {
  type: 'horizontal' | 'vertical'
  position: number
  isCenter: boolean // true = page center (red), false = panel align (blue)
}

export function GuideLines() {
  const { panels, activePageId, selectedPanelIds, layoutConfig, isDragging, showGuides } = useEditorStore()

  const activePanels = activePageId ? (panels[activePageId] ?? []) : []

  const guides = useMemo(() => {
    if (!isDragging || !showGuides || selectedPanelIds.length !== 1) return []

    const dragPanel = activePanels.find((p) => p.id === selectedPanelIds[0])
    if (!dragPanel) return []

    const result: GuideLine[] = []
    const pageCenterX = layoutConfig.width / 2
    const pageCenterY = layoutConfig.height / 2

    // Dragging panel edges and center
    const dLeft = dragPanel.left
    const dRight = dragPanel.left + dragPanel.width
    const dTop = dragPanel.top
    const dBottom = dragPanel.top + dragPanel.height
    const dCenterX = dragPanel.left + dragPanel.width / 2
    const dCenterY = dragPanel.top + dragPanel.height / 2

    // Page center guides
    if (Math.abs(dCenterX - pageCenterX) < SNAP_THRESHOLD) {
      result.push({ type: 'vertical', position: pageCenterX, isCenter: true })
    }
    if (Math.abs(dCenterY - pageCenterY) < SNAP_THRESHOLD) {
      result.push({ type: 'horizontal', position: pageCenterY, isCenter: true })
    }

    // Page edge guides
    if (Math.abs(dLeft) < SNAP_THRESHOLD) {
      result.push({ type: 'vertical', position: 0, isCenter: true })
    }
    if (Math.abs(dRight - layoutConfig.width) < SNAP_THRESHOLD) {
      result.push({ type: 'vertical', position: layoutConfig.width, isCenter: true })
    }
    if (Math.abs(dTop) < SNAP_THRESHOLD) {
      result.push({ type: 'horizontal', position: 0, isCenter: true })
    }
    if (Math.abs(dBottom - layoutConfig.height) < SNAP_THRESHOLD) {
      result.push({ type: 'horizontal', position: layoutConfig.height, isCenter: true })
    }

    // Other panel alignment guides
    const otherPanels = activePanels.filter(
      (p) => p.id !== dragPanel.id && p.is_active
    )

    for (const other of otherPanels) {
      const oLeft = other.left
      const oRight = other.left + other.width
      const oTop = other.top
      const oBottom = other.top + other.height
      const oCenterX = other.left + other.width / 2
      const oCenterY = other.top + other.height / 2

      // Vertical guides (x-axis alignment)
      const verticalChecks = [
        { drag: dLeft, other: oLeft },
        { drag: dLeft, other: oRight },
        { drag: dRight, other: oLeft },
        { drag: dRight, other: oRight },
        { drag: dCenterX, other: oCenterX },
        { drag: dLeft, other: oCenterX },
        { drag: dRight, other: oCenterX },
        { drag: dCenterX, other: oLeft },
        { drag: dCenterX, other: oRight },
      ]
      for (const check of verticalChecks) {
        if (Math.abs(check.drag - check.other) < SNAP_THRESHOLD) {
          result.push({ type: 'vertical', position: check.other, isCenter: false })
        }
      }

      // Horizontal guides (y-axis alignment)
      const horizontalChecks = [
        { drag: dTop, other: oTop },
        { drag: dTop, other: oBottom },
        { drag: dBottom, other: oTop },
        { drag: dBottom, other: oBottom },
        { drag: dCenterY, other: oCenterY },
        { drag: dTop, other: oCenterY },
        { drag: dBottom, other: oCenterY },
        { drag: dCenterY, other: oTop },
        { drag: dCenterY, other: oBottom },
      ]
      for (const check of horizontalChecks) {
        if (Math.abs(check.drag - check.other) < SNAP_THRESHOLD) {
          result.push({ type: 'horizontal', position: check.other, isCenter: false })
        }
      }
    }

    // Deduplicate by type+position
    const seen = new Set<string>()
    return result.filter((g) => {
      const key = `${g.type}-${Math.round(g.position)}`
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }, [isDragging, showGuides, selectedPanelIds, activePanels, layoutConfig])

  if (guides.length === 0) return null

  return (
    <svg
      className="bs-guidelines-overlay"
      width={layoutConfig.width}
      height={layoutConfig.height}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        pointerEvents: 'none',
        zIndex: 9998,
      }}
    >
      {guides.map((g, i) => {
        const color = g.isCenter ? '#e74c3c' : '#3498db'
        if (g.type === 'horizontal') {
          return (
            <line
              key={`h-${i}`}
              x1={0}
              y1={g.position}
              x2={layoutConfig.width}
              y2={g.position}
              stroke={color}
              strokeWidth={1}
              strokeDasharray="4 3"
            />
          )
        } else {
          return (
            <line
              key={`v-${i}`}
              x1={g.position}
              y1={0}
              x2={g.position}
              y2={layoutConfig.height}
              stroke={color}
              strokeWidth={1}
              strokeDasharray="4 3"
            />
          )
        }
      })}
    </svg>
  )
}
