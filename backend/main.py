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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pyannote_service.init_pyannote()
    await whisper_service.init_whisper()
    await ollama_service.init_ollama()
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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    heartbeat_task = asyncio.create_task(send_heartbeats(websocket))
    connected_clients.add(websocket)

    bytes_buffer = bytes()
    transcript = []
    fallacies = []
    # tracks which statement strings have already been flagged to prevent duplicate fallacies
    seen_fallacy_statements = set()
    last_processed_time = time.time()
    total_time_processed = 0

    try:
        await websocket.send_json({"type": "init", "transcript": transcript, "fallacies": fallacies})
        logger.info("Sent initial state to frontend")
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
                        # notify frontend that processing has started
                        await websocket.send_json({"type": "processing"})

                        process_start = time.time()
                        new_segments = await transcript_service.audio_to_transcript(bytes_buffer, total_time_processed)

                        transcript_time = time.time() - process_start
                        logger.info(f"Transcript processing: {transcript_time:.2f}s — {len(new_segments)} new segments")

                        transcript.extend(new_segments)

                        # only run fallacy detection on new segments, using full transcript for context
                        fallacy_start = time.time()
                        raw_fallacies = await ollama_service.detect_fallacies(transcript, new_segments)
                        fallacy_time = time.time() - fallacy_start
                        logger.info(f"Fallacy detection: {fallacy_time:.2f}s")

                        # deduplicate by statement text — same statement can't be flagged twice
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
                        logger.info("Sent update to frontend")

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
