from services import ollama_service
from services import assemblyai_service
from services import transcript_service
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
import asyncio
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # no local models to load — just validate API keys are present and reachable
    assemblyai_service.init_assemblyai()
    ollama_service.init_ollama()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = set()

async def send_heartbeats(websocket):
    try:
        while True:
            await asyncio.sleep(5)
            await websocket.send_json({"type": "ping"})
    except asyncio.CancelledError:
        pass
    except Exception:
        pass

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Sophism backend is running."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    heartbeat_task = asyncio.create_task(send_heartbeats(websocket))
    connected_clients.add(websocket)

    bytes_buffer = bytes()
    transcript = []
    fallacies = []
    seen_fallacy_statements = set()
    last_processed_time = time.time()
    total_time_processed = 0

    try:
        await websocket.send_json({"type": "init", "transcript": transcript, "fallacies": fallacies})
    except Exception as e:
        logger.error(f"Error sending initial state: {e}")

    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=0.1)
                logger.info(f"Received {len(data)} bytes of audio")
                bytes_buffer += data
            except asyncio.TimeoutError:
                pass

            current_time = time.time()
            elapsed_time = current_time - last_processed_time

            if len(bytes_buffer) > 144000 or elapsed_time >= 15:
                if len(bytes_buffer) > 0:
                    try:
                        await websocket.send_json({"type": "processing"})

                        process_start = time.time()
                        new_segments = await transcript_service.audio_to_transcript(bytes_buffer, total_time_processed)
                        logger.info(f"Transcription: {time.time() - process_start:.2f}s — {len(new_segments)} segments")

                        transcript.extend(new_segments)

                        raw_fallacies = await ollama_service.detect_fallacies(transcript, new_segments)

                        new_fallacies = []
                        for f in raw_fallacies:
                            key = f.get("statement", "").strip()
                            if key and key not in seen_fallacy_statements:
                                seen_fallacy_statements.add(key)
                                new_fallacies.append(f)
                                fallacies.append(f)

                        logger.info(f"Total processing: {time.time() - process_start:.2f}s")

                        await websocket.send_json({
                            "type": "update",
                            "new_segments": new_segments,
                            "new_fallacies": new_fallacies,
                            "transcript": transcript,
                            "fallacies": fallacies,
                        })

                    except Exception as e:
                        logger.error(f"Processing error: {e}", exc_info=True)
                        try:
                            await websocket.send_json({"type": "error", "message": str(e)})
                        except Exception:
                            pass

                total_time_processed += (len(bytes_buffer) / 2) / 48000
                bytes_buffer = bytes()
                last_processed_time = current_time

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        if websocket.client_state.name == 1:
            await websocket.close()
        connected_clients.discard(websocket)
