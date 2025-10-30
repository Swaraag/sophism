# overlapping audio need to read this article: https://github.com/pyannote/pyannote-audio/discussions/1157
from services import diart_service
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

## LOGGING SETUP
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")


## FAST API SETUP
app = FastAPI()
# in order to allow requests between the frontend and backend
# allow_origins=["https://yourdomain.com"] for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (fine for development)
    allow_credentials=True, # allows cookies and auth
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

## GLOBAL VARIABLES
# transcript format is [{"diagID": 0, "speaker": Bob, "diag": "What's up?"}]
transcript = []
# fallacy format is [{"speaker": "Bob", "fallacy_type": "ad hominem", "diag": "You're just stupid", "explanation": "Attacks the person rather than their argument", "confidence": "high"}]
fallacies = []
# speaker format is ["speaker1", "speaker2"]
speakers = []
# active websocket clients
connected_clients = set()

# broadcasts when transcript or fallacies is updated
async def broadcast(transcript, fallacies):
    for client in connected_clients:
        try:
            await client.send_json({"transcript": transcript, "fallacies": fallacies})
        except WebSocketDisconnect:
            connected_clients.discard(client)
            logger.info("Client disconnected.")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/debate/start")
async def start_debate():
    transcript = []
    fallacies = []
    return {"status": "Debate started"}

@app.get("/api/debate/state")
async def debate_state():
    # maybe need to add more 
    return {"transcript": transcript, "fallacies": fallacies}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            # Process audio data here
            logger.info(f"Received {len(data)} bytes of audio")
            # Send response back
            await websocket.send_json({"status": "audio received"})
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"Error: {e}")

### DIART WORK
@app.on_event("startup")
async def startup():
    await diart_service.initialize_diart()
