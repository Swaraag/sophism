import { useState, useEffect, useRef, useCallback } from 'react'
import './App.css'
import AudioCapture from './components/AudioCapture'
import TranscriptDisplay from './components/TranscriptDisplay'
import FallacyDisplay from './components/FallacyDisplay'

// 'connecting' | 'connected' | 'disconnected' | 'retrying' | 'failed'
const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/ws'
const MAX_RETRIES = 7

function App() {
  const [transcript, setTranscript] = useState([])
  const [fallacies, setFallacies] = useState([])
  const [wsStatus, setWsStatus] = useState('connecting')
  const [isProcessing, setIsProcessing] = useState(false)
  const [errorMessage, setErrorMessage] = useState(null)
  const [speakerNames, setSpeakerNames] = useState({}) // { SPEAKER_00: 'Alice', ... }

  const ws = useRef(null)
  const shouldRetry = useRef(true)
  const retryCount = useRef(0)
  const retryTimeout = useRef(null)

  function onEndDebate() {
    // Stop recording but keep transcript/fallacies visible
    setIsProcessing(false)
    setErrorMessage(null)
  }

  function onReset() {
    shouldRetry.current = false
    ws.current?.close()
    setTranscript([])
    setFallacies([])
    setSpeakerNames({})
    setErrorMessage(null)
    setIsProcessing(false)
    setTimeout(() => {
      shouldRetry.current = true
      retryCount.current = 0
      setWsStatus('connecting')
      createWS()
    }, 500)
  }

  const createWS = useCallback(() => {
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
    setWsStatus('connecting')
    ws.current = new WebSocket(WS_URL)

    ws.current.onopen = () => {
      console.log('WebSocket connected')
      setWsStatus('connected')
      setErrorMessage(null)
      retryCount.current = 0
    }

    ws.current.onclose = () => {
      console.log('WebSocket disconnected')
      setIsProcessing(false)

      if (!shouldRetry.current) return

      retryCount.current += 1
      if (retryCount.current >= MAX_RETRIES) {
        setWsStatus('failed')
        return
      }

      // exponential backoff: 2s, 4s, 8s, 16s... capped at 30s
      const delay = Math.min(2000 * Math.pow(2, retryCount.current - 1), 30000)
      setWsStatus('retrying')
      console.log(`Retrying WebSocket (#${retryCount.current}) in ${delay}ms`)
      retryTimeout.current = setTimeout(createWS, delay)
    }

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'ping') return

      if (data.type === 'processing') {
        setIsProcessing(true)
        return
      }

      if (data.type === 'error') {
        setIsProcessing(false)
        setErrorMessage(data.message)
        return
      }

      if (data.type === 'init') {
        // On reconnect the backend sends a fresh empty init — don't wipe existing state
        setIsProcessing(false)
        setErrorMessage(null)
        return
      }

      if (data.type === 'update') {
        setIsProcessing(false)
        setErrorMessage(null)
        setTranscript(data.transcript)
        setFallacies(data.fallacies)

        // auto-discover speaker IDs and assign default names
        if (data.transcript) {
          setSpeakerNames(prev => {
            const next = { ...prev }
            data.transcript.forEach(seg => {
              if (seg.speaker && !(seg.speaker in next)) {
                const n = Object.keys(next).length
                next[seg.speaker] = `Speaker ${n + 1}`
              }
            })
            return next
          })
        }
      }
    }
  }, [])

  useEffect(() => {
    createWS()
    return () => {
      shouldRetry.current = false
      ws.current?.close()
      if (retryTimeout.current) clearTimeout(retryTimeout.current)
    }
  }, [createWS])

  function renameSpeaker(speakerId, name) {
    setSpeakerNames(prev => ({ ...prev, [speakerId]: name }))
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Sophism</h1>
        <p className="app-subtitle">Real-time logical fallacy detection</p>
      </header>

      <div className="status-bar">
        <ConnectionStatus status={wsStatus} />
        {isProcessing && <span className="processing-pill">Analyzing…</span>}
        {errorMessage && <span className="error-pill" title={errorMessage}>Processing error</span>}
      </div>

      <main className="app-main">
        <AudioCapture
          websocketRef={ws}
          wsStatus={wsStatus}
          onEndDebate={onEndDebate}
          onReset={onReset}
        />

        <div className="content-grid">
          <section className="panel transcript-panel">
            <TranscriptDisplay
              transcript={transcript}
              speakerNames={speakerNames}
            />
          </section>
          <section className="panel fallacy-panel">
            <FallacyDisplay
              fallacies={fallacies}
              speakerNames={speakerNames}
              onRename={renameSpeaker}
              speakerIds={Object.keys(speakerNames)}
            />
          </section>
        </div>
      </main>
    </div>
  )
}

function ConnectionStatus({ status }) {
  const config = {
    connecting: { dot: 'dot dot--yellow', label: 'Connecting…' },
    connected:  { dot: 'dot dot--green',  label: 'Connected' },
    retrying:   { dot: 'dot dot--yellow', label: 'Reconnecting…' },
    disconnected:{ dot: 'dot dot--red',   label: 'Disconnected' },
    failed:     { dot: 'dot dot--red',    label: 'Connection failed — is the backend running?' },
  }
  const { dot, label } = config[status] ?? config.disconnected
  return (
    <span className="connection-status">
      <span className={dot} />
      {label}
    </span>
  )
}

export default App
