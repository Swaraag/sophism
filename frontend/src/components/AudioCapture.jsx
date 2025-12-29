import { useState, useRef } from 'react'

export default function AudioCapture({ websocketRef }) {
    const [ isRecording, toggleRecording ] = useState(false)
    const streamRef = useRef(null);
    const audioContextRef = useRef(null);
    const workletNodeRef = useRef(null);
    const micSourceRef = useRef(null);

    async function startDebate() {
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
        .getUserMedia({ video: false, audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false} })
        .then(async (stream) => {
            streamRef.current = stream;

            const audioContext = new AudioContext();
            audioContextRef.current = audioContext;

            await audioContext.audioWorklet.addModule("/audio-processor-worklet.js");
            
            const micSource = audioContext.createMediaStreamSource(stream);
            micSourceRef.current = micSource;

            const workletNode = new AudioWorkletNode(audioContext, "audio-processor-worklet");
            workletNodeRef.current = workletNode;

            workletNode.port.onmessage = (event) => {
                const ws = websocketRef.current
                if (ws.readyState === WebSocket.OPEN) {
                    const float32Data = event.data.audioData;
                    const int16Data = new Int16Array(float32Data.length);
                    for (let i = 0; i < float32Data.length; i++) {
                        int16Data[i] = Math.max(-32768, Math.min(32767, float32Data[i] * 32768));
                    }
                    
                    ws.send(int16Data.buffer);
                    //ws.send(event.data.audioData.buffer)
                }
                else {
                    console.error("The websocket isn't ready.")
                }
            }

            micSource.connect(workletNode);
            workletNode.connect(audioContext.destination);
            toggleRecording(true);
            console.log("Microphone is recording.")

        })
        .catch((err) => {
            console.error(err)
        });

    }

    // function for if the debate is paused by the user.
    async function pauseDebate() {
        if (isRecording) {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
            
            if (workletNodeRef.current) {
                workletNodeRef.current.disconnect();
            }
            if (micSourceRef.current) {
                micSourceRef.current.disconnect();
            }
            if (audioContextRef.current) {
                await audioContextRef.current.close();
            }
            
            toggleRecording(false);
            console.log("Debate paused. Microphone stopped.");
        }
        else {
            return;
        }

    }

    function endDebate() {

    }
    
    return (
        <div className="audio-controls">
            <button onClick={startDebate}>
                Start a debate
            </button>
            <button onClick={pauseDebate}>
                Pause debate
            </button>
            <button onClick={endDebate}>
                End debate
            </button>
        </div>
    )
}

            