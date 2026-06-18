import { useState } from 'react'

const CONFIDENCE_COLORS = (c) => {
  if (c >= 0.8) return '#dc2626'  // red — high confidence
  if (c >= 0.5) return '#d97706'  // amber — medium
  return '#6b7280'                // gray — low
}

export default function FallacyDisplay({ fallacies, speakerNames, onRename, speakerIds }) {
  const [expanded, setExpanded] = useState(new Set())
  const [editingId, setEditingId] = useState(null)
  const [draftName, setDraftName] = useState('')

  function toggleExpanded(index) {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(index) ? next.delete(index) : next.add(index)
      return next
    })
  }

  function startRename(speakerId) {
    setEditingId(speakerId)
    setDraftName(speakerNames[speakerId] ?? speakerId)
  }

  function commitRename(speakerId) {
    if (draftName.trim()) onRename(speakerId, draftName.trim())
    setEditingId(null)
  }

  return (
    <div className="panel-inner">
      <h2 className="panel-title">Fallacies</h2>

      {speakerIds.length > 0 && (
        <div className="speaker-names-section">
          <p className="speaker-names-label">Rename speakers</p>
          <div className="speaker-names-list">
            {speakerIds.map(id => (
              <div key={id} className="speaker-name-row">
                <span className="speaker-id-badge">{id}</span>
                {editingId === id ? (
                  <input
                    className="speaker-name-input"
                    value={draftName}
                    autoFocus
                    onChange={e => setDraftName(e.target.value)}
                    onBlur={() => commitRename(id)}
                    onKeyDown={e => { if (e.key === 'Enter') commitRename(id); if (e.key === 'Escape') setEditingId(null) }}
                  />
                ) : (
                  <button className="speaker-name-display" onClick={() => startRename(id)}>
                    {speakerNames[id] ?? id}
                    <EditIcon />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {fallacies.length === 0 ? (
        <p className="empty-state">No fallacies detected yet.</p>
      ) : (
        <ul className="fallacy-list">
          {fallacies.map((f, i) => {
            const isOpen = expanded.has(i)
            const confidence = typeof f.confidence === 'number' ? f.confidence : parseFloat(f.confidence) || 0
            const displayName = speakerNames[f.speaker] ?? f.speaker
            return (
              <li
                key={i}
                className={`fallacy-card ${isOpen ? 'fallacy-card--open' : ''}`}
                onClick={() => toggleExpanded(i)}
              >
                <div className="fallacy-card-header">
                  <div className="fallacy-card-title">
                    <span className="fallacy-type">{f.fallacy_type}</span>
                    <span className="fallacy-speaker">{displayName}</span>
                  </div>
                  <div className="fallacy-card-right">
                    <span
                      className="confidence-badge"
                      style={{ color: CONFIDENCE_COLORS(confidence) }}
                    >
                      {Math.round(confidence * 100)}%
                    </span>
                    <ChevronIcon open={isOpen} />
                  </div>
                </div>
                {isOpen && (
                  <div className="fallacy-card-body">
                    <blockquote className="fallacy-statement">"{f.statement}"</blockquote>
                    <p className="fallacy-explanation">{f.explanation}</p>
                  </div>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}

function EditIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style={{ marginLeft: 4, opacity: 0.5 }}>
      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
    </svg>
  )
}

function ChevronIcon({ open }) {
  return (
    <svg
      width="14" height="14" viewBox="0 0 24 24" fill="currentColor"
      style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s', opacity: 0.5 }}
    >
      <path d="M7 10l5 5 5-5H7z"/>
    </svg>
  )
}
