import { useState, useRef } from 'react'

export default function AudioCapture({ websocketRef, wsStatus, onEndDebate, onReset }) {
  const [isRecording, setIsRecording] = useState(false)
  const [isEnded, setIsEnded] = useState(false)
  const streamRef = useRef(null)
  const audioContextRef = useRef(null)
  const workletNodeRef = useRef(null)
  const micSourceRef = useRef(null)

  async function toggleDebate() {
    if (isRecording) {
      await pauseDebate()
    } else {
      await startDebate()
    }
  }

  async function startDebate() {
    const websocket = websocketRef.current
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      alert('Backend not connected. Please wait and try again.')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: false,
        audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false },
      })
      streamRef.current = stream

      const audioContext = new AudioContext()
      audioContextRef.current = audioContext

      await audioContext.audioWorklet.addModule('/audio-processor-worklet.js')

      const micSource = audioContext.createMediaStreamSource(stream)
      micSourceRef.current = micSource

      const workletNode = new AudioWorkletNode(audioContext, 'audio-processor-worklet')
      workletNodeRef.current = workletNode

      workletNode.port.onmessage = (event) => {
        const ws = websocketRef.current
        if (ws?.readyState === WebSocket.OPEN) {
          const float32Data = event.data.audioData
          const int16Data = new Int16Array(float32Data.length)
          for (let i = 0; i < float32Data.length; i++) {
            int16Data[i] = Math.max(-32768, Math.min(32767, float32Data[i] * 32768))
          }
          ws.send(int16Data.buffer)
        }
      }

      micSource.connect(workletNode)
      workletNode.connect(audioContext.destination)
      setIsRecording(true)
    } catch (err) {
      console.error('Failed to start recording:', err)
      alert('Could not access microphone: ' + err.message)
    }
  }

  async function pauseDebate() {
    streamRef.current?.getTracks().forEach(t => t.stop())
    workletNodeRef.current?.disconnect()
    micSourceRef.current?.disconnect()
    if (audioContextRef.current) {
      await audioContextRef.current.close()
      audioContextRef.current = null
    }
    setIsRecording(false)
  }

  async function endDebate() {
    await pauseDebate()
    setIsEnded(true)
    onEndDebate()
  }

  function continueDebate() {
    setIsEnded(false)
  }

  function resetDebate() {
    setIsEnded(false)
    onReset()
  }

  const canStart = wsStatus === 'connected'

  if (isEnded) {
    return (
      <div className="controls">
        <button className="btn btn-primary btn-start" onClick={continueDebate}>
          <MicIcon /> Continue
        </button>
        <button className="btn btn-danger" onClick={resetDebate}>
          <StopIcon /> Reset
        </button>
      </div>
    )
  }

  return (
    <div className="controls">
      <button
        className={`btn btn-primary ${isRecording ? 'btn-pause' : 'btn-start'}`}
        onClick={toggleDebate}
        disabled={!canStart}
        title={!canStart ? 'Waiting for backend connection…' : ''}
      >
        {isRecording ? (
          <><PauseIcon /> Pause</>
        ) : (
          <><MicIcon /> Start Debate</>
        )}
      </button>
      <button className="btn btn-danger" onClick={endDebate}>
        <StopIcon /> End Debate
      </button>
    </div>
  )
}

function MicIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm0 2a2 2 0 0 0-2 2v7a2 2 0 0 0 4 0V5a2 2 0 0 0-2-2zm-7 9a7 7 0 0 0 14 0h2a9 9 0 0 1-8 8.94V23h-2v-2.06A9 9 0 0 1 3 12H5z"/>
    </svg>
  )
}

function PauseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
    </svg>
  )
}

function StopIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M6 6h12v12H6z"/>
    </svg>
  )
}
