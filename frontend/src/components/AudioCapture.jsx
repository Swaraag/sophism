import { useState, useRef } from 'react'

export default function AudioCapture({ websocketRef }) {
    const [ isRecording, toggleRecording ] = useState(false)
    const recorderRef = useRef(null);
    const streamRef = useRef(null);

    function startDebate() {
        const websocket = websocketRef.current;
        console.log("websocket prop:", websocket);
        console.log("websocket readyState:", websocket?.readyState);
        console.log("WebSocket.OPEN constant:", WebSocket.OPEN);
        if (!websocket || websocket.readyState !== WebSocket.OPEN) {
            alert("Websocket isn't ready. Please try again soon.")
            return;
        }
        // this below section is for asking for microphone permission
        
        navigator.mediaDevices
        .getUserMedia({ video: false, audio: true })
        .then((stream) => {
            streamRef.current = stream;
            // this section is for capturing audio through the microphone
            recorderRef.current = new MediaRecorder(stream);
            
            recorderRef.current.ondataavailable = (event) => {
                const ws = websocketRef.current
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(event.data)
                }
                
                else {
                    console.error("The websocket isn't ready.")
                }
            }

            // sends info every 3000 miliseconds just to start
            recorderRef.current.start(3000);
            toggleRecording(true);
            console.log("Microphone is recording.");

        })
        .catch((err) => {
            console.error(err)
        });

    }

    // function for if the debate is paused by the user.
    function pauseDebate() {
        if (recorderRef.current.state == "recording") {
            recorderRef.current.stop()
            toggleRecording(false)
            streamRef.current.getTracks().forEach(track => track.stop())
        }
    }

    function endDebate() {

    }
    
    return (
        <>
            <button onClick={startDebate}>
                Start a debate
            </button>
            <button onClick={pauseDebate}>
                Pause debate
            </button>
            <button onClick={endDebate}>
                End debate
            </button>
        </>
    )
}

