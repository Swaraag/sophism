import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [transcript, updateTranscript] = useState([])
  const [fallacies, updateFallacies] = useState([])
  const ws = useRef(null)

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws')

    ws.current.onopen = () => console.log('WebSocket Connected')

    ws.current.onclose = () => console.log('WebSocket Disconnected')

    ws.current.onerror = (error) => console.error('WebSocket Error:', error);

    // getting this from backend: await websocket.send_json({"transcript": transcript, "fallacies": fallacies})
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      updateTranscript(data.transcript)
      updateFallacies(data.fallacies)
      console.log("Transcript:", transcript)
      console.log("Fallacies:", fallacies)
    }

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    }
  }, [])

  return (
    <>
      <h1>Sophism</h1>
      <div className="card">
        <button>
          Start a debate!
        </button>
      </div>
    </>
  )
}

export default App
