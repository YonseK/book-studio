import React, { useCallback, useState } from 'react'
import {
  Bold, Italic, Underline, AlignLeft, AlignCenter, AlignRight, AlignJustify,
  Pipette, ChevronDown, ChevronUp, Info, Type,
} from 'lucide-react'
import { useEditorStore } from '../../stores/editorStore'
import { useSelectionStore } from '../../stores/selectionStore'
import type { Panel } from '../../types/panel'

/** Font bank: display name → CSS font-family value */
const FONT_BANK: { label: string; family: string }[] = [
  // Korean fonts
  { label: '본고딕 보통', family: 'Noto Sans KR, sans-serif' },
  { label: '본고딕 굵게', family: 'Noto Sans KR, sans-serif' },
  { label: '서울한강 장체 보통', family: 'Seoul Hangang, sans-serif' },
  { label: '서울한강 장체 굵게', family: 'Seoul Hangang, sans-serif' },
  { label: '서울남산 장체 보통', family: 'Seoul Namsan, sans-serif' },
  { label: '서울남산 장체 굵게', family: 'Seoul Namsan, sans-serif' },
  { label: '나눔고딕 보통', family: 'NanumGothic, sans-serif' },
  { label: '나눔고딕 굵게', family: 'NanumGothic, sans-serif' },
  { label: '나눔 붓', family: 'Nanum Brush Script, cursive' },
  { label: '나눔 펜', family: 'Nanum Pen Script, cursive' },
  // Latin fonts
  { label: 'Roboto Thin', family: 'Roboto, sans-serif' },
  { label: 'Roboto Regular', family: 'Roboto, sans-serif' },
  { label: 'Roboto Bold', family: 'Roboto, sans-serif' },
  { label: 'Roboto Black', family: 'Roboto, sans-serif' },
  { label: 'Arial', family: 'Arial, sans-serif' },
  { label: 'Verdana', family: 'Verdana, sans-serif' },
  { label: 'Tahoma', family: 'Tahoma, sans-serif' },
  { label: 'Times New Roman', family: 'Times New Roman, serif' },
  { label: 'Georgia', family: 'Georgia, serif' },
  { label: 'Courier New', family: 'Courier New, monospace' },
  { label: 'Montserrat Thin', family: 'Montserrat, sans-serif' },
  { label: 'Montserrat Regular', family: 'Montserrat, sans-serif' },
  { label: 'Montserrat Black', family: 'Montserrat, sans-serif' },
  { label: 'Anton', family: 'Anton, sans-serif' },
  { label: 'Lobster', family: 'Lobster, cursive' },
  { label: 'Playball', family: 'Playball, cursive' },
  { label: 'Monoton', family: 'Monoton, cursive' },
]

/** Determine font-weight from label */
function getFontWeight(label: string): number | undefined {
  if (label.includes('Thin') || label.includes('가늘게') || label.includes('Extra Light')) return 100
  if (label.includes('Bold') || label.includes('굵게')) return 700
  if (label.includes('Black')) return 900
  return undefined
}

export function TextBank() {
  const { panels, activePageId, updatePanel } = useEditorStore()
  const { selectedPanelIds } = useSelectionStore()
  const activePanels = activePageId ? (panels[activePageId] ?? []) : []
  const panel = activePanels.find((p) => selectedPanelIds.includes(p.id))

  const [moreOptions, setMoreOptions] = useState(false)

  const update = useCallback((data: Partial<Panel>) => {
    if (panel) updatePanel(panel.id, data)
  }, [panel, updatePanel])

  if (!panel) return null

  const isHeadline = panel.media_type === 'HL'
  const currentFamily = panel.font_family === 'initial' ? 'inherit' : panel.font_family

  return (
    <div className="bs-textbank">
      {/* Header */}
      <div className="bs-textbank__header">
        <Type size={14} />
        <span>{isHeadline ? '헤드라인 텍스트' : '텍스트'}</span>
      </div>

      {/* ── Options area (scrollable when expanded) ── */}
      <div className="bs-textbank__options">

      {/* Font Family & Color */}
      <div className="bs-textbank__section">
        <div className="bs-textbank__section-label">
          <Type size={11} />
          <span>폰트 패밀리 & 폰트 색상</span>
        </div>
        <div className="bs-textbank__family-row">
          <div className="bs-textbank__family-name">
            {currentFamily === 'inherit' ? '기본' : currentFamily.split(',')[0]}
          </div>
          <label className="bs-textbank__color-btn" title="폰트 색상">
            <Pipette size={16} />
            <input
              type="color"
              value={panel.color === 'initial' ? '#ffffff' : panel.color}
              onChange={(e) => update({ color: e.target.value })}
              style={{ position: 'absolute', opacity: 0, width: 0, height: 0 }}
            />
          </label>
        </div>
      </div>

      {/* Font Size */}
      <div className="bs-textbank__section">
        <div className="bs-textbank__section-label">
          <span style={{ fontWeight: 600, fontSize: 12 }}>A.</span>
          <span>폰트 사이즈</span>
          <span className="bs-textbank__value">{panel.font_size}</span>
        </div>
        <input
          type="range" min="8" max="200" step="1"
          value={panel.font_size}
          onChange={(e) => update({ font_size: Number(e.target.value) })}
          className="bs-textbank__slider"
        />
      </div>

      {/* Font Opacity */}
      <div className="bs-textbank__section">
        <div className="bs-textbank__section-label">
          <Type size={11} />
          <span>폰트 투명도</span>
          <span className="bs-textbank__value">{panel.opacity}</span>
        </div>
        <input
          type="range" min="0" max="1" step="0.05"
          value={panel.opacity}
          onChange={(e) => update({ opacity: Number(e.target.value) })}
          className="bs-textbank__slider"
        />
      </div>

      {/* Expanded Options (font style + box controls) */}
      {moreOptions && (
        <>
          {/* Font Style (B/I/U + Alignment) */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>三</span>
              <span>폰트 스타일</span>
            </div>
            <div className="bs-textbank__style-row">
              <StyleBtn active={panel.font_bold} onClick={() => update({ font_bold: !panel.font_bold })} title="굵게">
                <Bold size={14} strokeWidth={panel.font_bold ? 3 : 1.5} />
              </StyleBtn>
              <StyleBtn active={panel.font_italic} onClick={() => update({ font_italic: !panel.font_italic })} title="기울임">
                <Italic size={14} strokeWidth={1.5} />
              </StyleBtn>
              <StyleBtn active={panel.text_underline} onClick={() => update({ text_underline: !panel.text_underline })} title="밑줄">
                <Underline size={14} strokeWidth={1.5} />
              </StyleBtn>
              <div className="bs-textbank__style-sep" />
              {(['left', 'center', 'right', 'justify'] as const).map((align) => {
                const Icon = align === 'left' ? AlignLeft : align === 'center' ? AlignCenter : align === 'right' ? AlignRight : AlignJustify
                return (
                  <StyleBtn
                    key={align}
                    active={panel.text_align === align}
                    onClick={() => update({ text_align: align })}
                    title={align}
                  >
                    <Icon size={14} strokeWidth={1.5} />
                  </StyleBtn>
                )
              })}
            </div>
          </div>

          {/* Letter Spacing */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>씌</span>
              <span>글자 간격</span>
              <span className="bs-textbank__value">{panel.letter_spacing}</span>
            </div>
            <input
              type="range" min="-2" max="20" step="0.5"
              value={panel.letter_spacing}
              onChange={(e) => update({ letter_spacing: Number(e.target.value) })}
              className="bs-textbank__slider"
            />
          </div>

          {/* Line Height */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>三</span>
              <span>문장 줄 높이</span>
              <span className="bs-textbank__value">{panel.line_height}</span>
            </div>
            <input
              type="range" min="0.5" max="4" step="0.1"
              value={panel.line_height}
              onChange={(e) => update({ line_height: Number(e.target.value) })}
              className="bs-textbank__slider"
            />
          </div>

          {/* Padding */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>▢</span>
              <span>전체 여백</span>
              <span className="bs-textbank__value">{panel.padding}</span>
            </div>
            <input
              type="range" min="0" max="60" step="1"
              value={panel.padding}
              onChange={(e) => update({ padding: Number(e.target.value) })}
              className="bs-textbank__slider"
            />
          </div>

          {/* Text Shadow */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>A.</span>
              <span>폰트 그림자</span>
              <span className="bs-textbank__value">{panel.text_shadow_px}</span>
            </div>
            <input
              type="range" min="0" max="20" step="1"
              value={panel.text_shadow_px}
              onChange={(e) => {
                const px = Number(e.target.value)
                update({
                  text_shadow_px: px,
                  text_shadow: px > 0 ? `${px}px ${px}px ${px * 2}px rgba(0,0,0,0.5)` : 'initial',
                })
              }}
              className="bs-textbank__slider"
            />
          </div>

          {/* ── Box Controls ── */}

          {/* Background Color */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>■</span>
              <span>상자 배경 색상</span>
            </div>
            <label className="bs-textbank__color-btn" title="배경 색상">
              <Pipette size={16} />
              <input
                type="color"
                value={panel.background_color === 'transparent' ? '#000000' : panel.background_color}
                onChange={(e) => update({ background_color: e.target.value })}
                style={{ position: 'absolute', opacity: 0, width: 0, height: 0 }}
              />
            </label>
          </div>

          {/* Background Opacity */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>■</span>
              <span>상자 배경 색상 투명도</span>
              <span className="bs-textbank__value">{panel.background_opacity}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.05"
              value={panel.background_opacity}
              onChange={(e) => update({ background_opacity: Number(e.target.value) })}
              className="bs-textbank__slider"
            />
          </div>

          {/* Border Width */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>▢</span>
              <span>상자 테두리 두께</span>
              <span className="bs-textbank__value">{panel.border_width}</span>
            </div>
            <input
              type="range" min="0" max="20" step="1"
              value={panel.border_width}
              onChange={(e) => update({ border_width: Number(e.target.value) })}
              className="bs-textbank__slider"
            />
          </div>

          {/* Border Radius */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>◻</span>
              <span>상자 모서리 둥글게</span>
              <span className="bs-textbank__value">{panel.border_radius}</span>
            </div>
            <input
              type="range" min="0" max="100" step="1"
              value={panel.border_radius}
              onChange={(e) => update({ border_radius: Number(e.target.value) })}
              className="bs-textbank__slider"
            />
          </div>

          {/* Border Color */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>▢</span>
              <span>상자 테두리 색상</span>
            </div>
            <label className="bs-textbank__color-btn" title="테두리 색상">
              <Pipette size={16} />
              <input
                type="color"
                value={panel.border_color === 'initial' ? '#000000' : panel.border_color}
                onChange={(e) => update({ border_color: e.target.value })}
                style={{ position: 'absolute', opacity: 0, width: 0, height: 0 }}
              />
            </label>
          </div>

          {/* Border Opacity */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>▢</span>
              <span>상자 테두리 색상 투명도</span>
              <span className="bs-textbank__value">{panel.border_opacity}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.05"
              value={panel.border_opacity}
              onChange={(e) => update({ border_opacity: Number(e.target.value) })}
              className="bs-textbank__slider"
            />
          </div>

          {/* Border Style */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>▢</span>
              <span>상자 테두리 스타일</span>
            </div>
            <div className="bs-textbank__style-row">
              {(['solid', 'dashed', 'dotted'] as const).map((style) => (
                <StyleBtn
                  key={style}
                  active={panel.border_style === style}
                  onClick={() => update({ border_style: style })}
                  title={style}
                >
                  <div className={`bs-textbank__border-preview bs-textbank__border-preview--${style}`} />
                </StyleBtn>
              ))}
            </div>
          </div>

          {/* Box Shadow */}
          <div className="bs-textbank__section">
            <div className="bs-textbank__section-label">
              <span style={{ fontSize: 12 }}>▢</span>
              <span>상자 그림자</span>
              <span className="bs-textbank__value">{panel.drop_shadow_px}</span>
            </div>
            <input
              type="range" min="0" max="30" step="1"
              value={panel.drop_shadow_px}
              onChange={(e) => {
                const px = Number(e.target.value)
                update({
                  drop_shadow_px: px,
                  box_shadow: px > 0 ? `0 ${px}px ${px * 2}px rgba(0,0,0,0.3)` : 'initial',
                })
              }}
              className="bs-textbank__slider"
            />
          </div>
        </>
      )}

      </div>{/* end options */}

      {/* More Options Toggle — fixed between options and font bank */}
      <button
        className="bs-textbank__more-btn"
        onClick={() => setMoreOptions(!moreOptions)}
      >
        {moreOptions ? (
          <>
            <ChevronUp size={14} className="bs-textbank__more-icon" />
            <span>옵션 간략히</span>
          </>
        ) : (
          <>
            <ChevronDown size={14} className="bs-textbank__more-icon" />
            <span>옵션 더 보기</span>
          </>
        )}
      </button>

      {/* Font Bank */}
      <div className="bs-textbank__fontbank">
        <div className="bs-textbank__fontbank-header">
          <Type size={13} />
          <span>폰트 뱅크</span>
        </div>
        <div className="bs-textbank__fontbank-list">
          {FONT_BANK.map((font) => {
            const isActive = currentFamily.includes(font.family.split(',')[0])
            const weight = getFontWeight(font.label)
            return (
              <button
                key={font.label}
                className={`bs-textbank__font-item${isActive ? ' bs-textbank__font-item--active' : ''}`}
                onClick={() => {
                  const updates: Partial<Panel> = { font_family: font.family }
                  if (weight !== undefined) {
                    updates.font_bold = weight >= 700
                  }
                  update(updates)
                }}
              >
                <span
                  className="bs-textbank__font-preview"
                  style={{ fontFamily: font.family, fontWeight: weight }}
                >
                  {font.label}
                </span>
                <Info size={13} className="bs-textbank__font-info" />
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function StyleBtn({
  active, onClick, title, children,
}: {
  active: boolean; onClick: () => void; title: string; children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      title={title}
      className={`bs-textbank__style-btn${active ? ' bs-textbank__style-btn--active' : ''}`}
    >
      {children}
    </button>
  )
}
