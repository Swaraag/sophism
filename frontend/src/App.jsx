import { useState, useEffect, useRef } from 'react'
import './App.css'
import AudioCapture from './components/AudioCapture'
import TranscriptDisplay from './components/TranscriptDisplay'
import FallacyDisplay from './components/FallacyDisplay'

function App() {
  const [transcript, updateTranscript] = useState([])
  const [fallacies, updateFallacies] = useState([])
  const ws = useRef(null)

  const shouldRetry = useRef(true)
  const wsRetryCount = useRef(0)
  const wsRetryDelay = useRef(5000)
  const wsRetryTimeout = useRef(null)

  function createWS() {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    ws.current = new WebSocket('ws://localhost:8000/ws')

    ws.current.onopen = () => {
      console.log('WebSocket Connected');
      // reset values if the socket connects successfully
      wsRetryDelay.current = 5000
      wsRetryCount.current = 0
    }

    ws.current.onclose = () => {
      console.log('WebSocket Disconnected')
      // update retry delay and the count
      wsRetryDelay.current *= 2
      wsRetryCount.current += 1

      if (wsRetryCount.current < 7 && shouldRetry.current) {
        console.log("Retrying WebSocket connection (#" + wsRetryCount.current + "): " + wsRetryDelay.current + "ms")
        wsRetryTimeout.current = setTimeout(() => {
          createWS()
        }, wsRetryDelay.current)
      }
    }

    ws.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
    }

    // getting this from backend: await websocket.send_json({"transcript": transcript, "fallacies": fallacies})
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      updateTranscript(data.transcript)
      updateFallacies(data.fallacies)
      console.log("Transcript:", data.transcript)
      console.log("Fallacies:", data.fallacies)
    }

  }

  useEffect(() => {

    createWS()

    return () => {
      if (ws.current) {
        shouldRetry.current = false
        ws.current.close();
      }
      if (wsRetryTimeout.current) {
        clearTimeout(wsRetryTimeout.current)
      }
    }
  }, [])

  return (
    <>
      <h1>Sophism</h1>
      <AudioCapture websocketRef={ws}/>

      <div className="content-flex">
        <div className="transcript-panel"><TranscriptDisplay transcript={transcript}/></div>
        <div className="fallacy-panel"><FallacyDisplay fallacies={fallacies}/></div>
      </div>

      
    </>
  )
}

export default App
