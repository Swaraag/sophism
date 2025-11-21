# overlapping audio need to read this article: https://github.com/pyannote/pyannote-audio/discussions/1157
from services import pyannote_service
from services import whisper_service
from services import ollama_service
from services import transcript_service
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
import asyncio
import time

## LOGGING SETUP
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# loading startup services
@asynccontextmanager
async def lifespan(app: FastAPI):
    await pyannote_service.init_pyannote()
    await whisper_service.init_whisper()
    await ollama_service.init_ollama()
    # yield to distinguish between startup and shutdown
    yield

## FAST API SETUP
app = FastAPI(lifespan=lifespan)
# in order to allow requests between the frontend and backend
# allow_origins=["https://yourdomain.com"] for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (fine for development)
    allow_credentials=True, # allows cookies and auth
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# active websocket clients
connected_clients = set()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/debate/start")
async def start_debate():
    return {"status": "Debate started"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    # buffer of bytes that holds the incoming websocket information
    bytes_buffer = bytes()
    # transcript format is [{"diagID": 0, "speaker": Bob, "diag": "What's up?"}]
    transcript = []
    # fallacy format is [{"speaker": "Bob", "fallacy_type": "ad hominem", "diag": "You're just stupid", "explanation": "Attacks the person rather than their argument", "confidence": "high"}]
    fallacies = []
    # speaker format is ["speaker1", "speaker2"]
    speakers = []
    # current time
    last_processed_time = time.time()

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_bytes(), 
                    timeout=0.1
                )
                logger.info(f"Received {len(data)} bytes of audio")
                bytes_buffer += data
            except asyncio.TimeoutError:
                pass

            current_time = time.time()
            elapsed_time = current_time - last_processed_time

            if len(bytes_buffer) > 144000 or elapsed_time >= 15:
                if len(bytes_buffer) > 0:
                    transcript_seg = await transcript_service.audio_to_transcript(bytes_buffer)
                    transcript.extend(transcript_seg)
                    detected_fallacies = await ollama_service.detect_fallacies(transcript)
                    if len(detected_fallacies) > 0:
                        fallacies.extend(detected_fallacies)
                    await websocket.send_json({"transcript": transcript, "fallacies": fallacies})

                # reset the bytes array
                bytes_buffer = bytes()
                # reset the last processed time
                last_processed_time = current_time

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await websocket.close()

