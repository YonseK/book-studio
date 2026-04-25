import React, { useState } from 'react'
import { Pipette, ChevronDown, ChevronUp } from 'lucide-react'
import colorPalette from '../../data/colorPalette.json'

const SPECTRUM_COLORS: string[] = colorPalette.spectrum.flat()

interface ColorPalettePickerProps {
  value: string
  onChange: (color: string) => void
  label?: string
  /** 아이콘 앞에 보여줄 커스텀 아이콘 */
  icon?: React.ReactNode
}

export function ColorPalettePicker({ value, onChange, label, icon }: ColorPalettePickerProps) {
  const [open, setOpen] = useState(false)

  const displayColor = !value || value === 'initial' || value === 'transparent'
    ? '#000000'
    : value

  return (
    <div className="bs-colorpicker">
      {/* Color button — shows current color + toggles palette */}
      <button
        className="bs-colorpicker__btn"
        onClick={() => setOpen(!open)}
        title={label}
      >
        <span className="bs-colorpicker__swatch" style={{ backgroundColor: displayColor }} />
        {icon || <Pipette size={13} />}
        {label && <span className="bs-colorpicker__label">{label}</span>}
        {open ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
      </button>

      {/* Palette dropdown */}
      {open && (
        <div className="bs-colorpicker__palette">
          {/* Transparent */}
          <button
            className={`bs-colorpicker__transparent${value === 'transparent' ? ' bs-colorpicker__cell--active' : ''}`}
            onClick={() => { onChange('transparent'); setOpen(false) }}
          >
            <span className="bs-wallpaper__transparent-checker" />
            <span>투명</span>
          </button>

          {/* Basic vivid (11 colors, skip transparent) */}
          <div className="bs-colorpicker__row">
            {colorPalette.basic.slice(1).map((c, i) => (
              <button
                key={`b-${i}`}
                className={`bs-colorpicker__cell${value === c ? ' bs-colorpicker__cell--active' : ''}${c === '#ffffff' ? ' bs-colorpicker__cell--white' : ''}`}
                style={{ backgroundColor: c }}
                onClick={() => { onChange(c); setOpen(false) }}
              />
            ))}
          </div>

          {/* Pastel */}
          <div className="bs-colorpicker__row">
            {colorPalette.pastel.map((c, i) => (
              <button
                key={`p-${i}`}
                className={`bs-colorpicker__cell${value === c ? ' bs-colorpicker__cell--active' : ''}`}
                style={{ backgroundColor: c }}
                onClick={() => { onChange(c); setOpen(false) }}
              />
            ))}
          </div>

          {/* Gray scale */}
          <div className="bs-colorpicker__row">
            {colorPalette.grays.map((c, i) => (
              <button
                key={`g-${i}`}
                className={`bs-colorpicker__cell${value === c ? ' bs-colorpicker__cell--active' : ''}${c === 'transparent' ? ' bs-colorpicker__cell--checker' : ''}`}
                style={c !== 'transparent' ? { backgroundColor: c } : undefined}
                onClick={() => { onChange(c); setOpen(false) }}
              />
            ))}
          </div>

          {/* Spectrum grid */}
          <div className="bs-colorpicker__spectrum">
            {SPECTRUM_COLORS.map((c, i) => (
              <button
                key={`s-${i}`}
                className={`bs-colorpicker__cell${value === c ? ' bs-colorpicker__cell--active' : ''}`}
                style={{ backgroundColor: c }}
                onClick={() => { onChange(c); setOpen(false) }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
