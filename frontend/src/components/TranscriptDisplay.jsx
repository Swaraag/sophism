import { useEffect, useRef } from 'react'

function formatTime(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${String(s).padStart(2, '0')}`
}

// stable color per speaker index so SPEAKER_00 is always the same hue
const SPEAKER_COLORS = ['#7c3aed', '#0891b2', '#059669', '#d97706', '#dc2626']

export default function TranscriptDisplay({ transcript, speakerNames }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [transcript])

  const speakerIds = [...new Set(transcript.map(s => s.speaker))]
  const colorMap = Object.fromEntries(
    speakerIds.map((id, i) => [id, SPEAKER_COLORS[i % SPEAKER_COLORS.length]])
  )

  return (
    <div className="panel-inner">
      <h2 className="panel-title">Transcript</h2>
      {transcript.length === 0 ? (
        <p className="empty-state">Transcript will appear here once the debate starts.</p>
      ) : (
        <ul className="transcript-list">
          {transcript.map((seg, i) => {
            const displayName = speakerNames[seg.speaker] ?? seg.speaker
            const color = colorMap[seg.speaker] ?? '#888'
            return (
              <li key={i} className="transcript-entry">
                <div className="transcript-meta">
                  <span className="speaker-tag" style={{ color }}>
                    {displayName}
                  </span>
                  <span className="timestamp">
                    {formatTime(seg.start)}–{formatTime(seg.end)}
                  </span>
                </div>
                <p className="transcript-text">{seg.transcript}</p>
              </li>
            )
          })}
          <div ref={bottomRef} />
        </ul>
      )}
    </div>
  )
}
