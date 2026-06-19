# Sophism

An AI-powered real-time debate analyzer that detects logical fallacies as people speak.

![Python](https://img.shields.io/badge/python-3.12-blue)
![React](https://img.shields.io/badge/react-19-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> **You're on the `cloud-deploy` branch** — this version uses AssemblyAI + Groq APIs and is deployed to Render + Vercel at zero cost.
> For the local/offline version (Pyannote + Whisper + Ollama, no external APIs), switch to the [`main`](../../tree/main) branch.

---

## Live Demo

**[sophism.vercel.app](https://sophism.vercel.app)** *(frontend on Vercel, backend on Render)*

---

## Overview

Sophism captures live audio from a debate, identifies who is speaking, transcribes their words, and uses AI to detect logical fallacies in real-time. This branch replaces all local ML models with cloud APIs so it can run on free hosting with near-zero RAM.

**Key Features:**
- Real-time audio capture and streaming
- Speaker diarization via AssemblyAI
- Speech-to-text transcription via AssemblyAI
- Fallacy detection via Groq (Llama 3.1 8B Instant)
- ~15 second end-to-end latency
- Fully hosted — no local setup required for users

---

## Running Locally (development)

### Prerequisites

- Python 3.12
- Node.js 18+
- FFmpeg (`brew install ffmpeg` on macOS)
- A Groq API key (free at [console.groq.com](https://console.groq.com))
- An AssemblyAI API key (free at [assemblyai.com](https://www.assemblyai.com))

### Setup

```bash
git clone https://github.com/Swaraag/sophism.git
cd sophism
git checkout cloud-deploy
```

**Backend:**
```bash
cd backend
python3.12 -m venv sophism-backend-venv
sophism-backend-venv/bin/pip install -r requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_key_here
ASSEMBLYAI_API_KEY=your_key_here
```

**Frontend:**
```bash
cd frontend
npm install
```

### Running

**Terminal 1 — Backend** (from `backend/`):
```bash
sophism-backend-venv/bin/uvicorn main:app --reload
```
Starts in ~2 seconds (no local model loading).

**Terminal 2 — Frontend** (from `frontend/`):
```bash
npm run dev
```
Open `http://localhost:5173`.

---

## Usage

1. Open the app and wait for "Connected" status
2. Click **Start Debate** and grant microphone permissions
3. Speak — audio is processed in ~5 second chunks, results appear in ~15 seconds
4. Click **End Debate** to stop recording while keeping results visible
5. Click **Continue** to resume recording on the same session
6. Click **Reset** to clear everything and start fresh

---

## Architecture

```
Browser mic (48kHz Float32)
  → AudioWorkletNode buffers 240,000 samples (~5 sec)
  → Convert Float32 → Int16 (50% bandwidth reduction)
  → Binary WebSocket → wss://sophism.onrender.com/ws

FastAPI backend (Render free tier):
  → Accumulates until >144,000 bytes OR 15 seconds elapsed
  → audio_utils: Int16 → Float32, resample 48kHz → 16kHz
  → assemblyai_service: wraps in WAV header, sends to AssemblyAI API
      → returns [{speaker, start, end, transcript}]
  → ollama_service (Groq): sends transcript to llama-3.1-8b-instant
      → returns [{speaker, fallacy_type, statement, explanation, confidence}]
  → deduplicates fallacies by statement string
  → WebSocket response: {type: "update", transcript, fallacies, new_segments, new_fallacies}

React frontend (Vercel):
  → Transcript panel: speaker-colored entries with timestamps, auto-scrolls
  → Fallacy panel: collapsible cards with confidence scores, inline speaker rename
```

---

## Tech Stack

**Backend:** FastAPI, AssemblyAI SDK, Groq SDK, Librosa, NumPy

**Frontend:** React 19, Vite, Web Audio API (AudioWorkletNode), WebSocket

---

## Deployment

### Backend → Render (free)

1. render.com → New Web Service → connect `Swaraag/sophism` → branch: `cloud-deploy`
2. Root directory: `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Instance type: Free
6. Environment variables (set in Render dashboard):
   - `GROQ_API_KEY`
   - `ASSEMBLYAI_API_KEY`

### Frontend → Vercel (free)

1. vercel.com → New Project → `Swaraag/sophism` → Root directory: `frontend`
2. Environment variable: `VITE_WS_URL=wss://sophism.onrender.com/ws`
3. Deploy

### Keep-warm → UptimeRobot (free)

Render free tier spins down after ~15 min of inactivity (cold start takes ~30s). UptimeRobot pings every 5 min to prevent this.

1. uptimerobot.com → Add Monitor → HTTP/website monitoring
2. URL: `https://sophism.onrender.com/`
3. Interval: 5 minutes

---

## Project Structure

```
sophism/
├── render.yaml                          # Render deployment config
├── backend/
│   ├── main.py                          # FastAPI WebSocket server
│   ├── requirements.txt                 # fastapi, groq, assemblyai, librosa, numpy
│   ├── .env                             # gitignored — API keys
│   ├── services/
│   │   ├── assemblyai_service.py        # diarization + transcription via AssemblyAI
│   │   ├── ollama_service.py            # fallacy detection via Groq
│   │   ├── transcript_service.py        # pipeline orchestration
│   │   └── ollama_instructions.txt      # LLM system prompt
│   └── utils/
│       └── audio_utils.py               # audio format conversion + resampling
└── frontend/
    ├── public/
    │   └── audio-processor-worklet.js   # AudioWorklet: buffers + converts audio
    └── src/
        ├── App.jsx                      # WebSocket logic, state management
        ├── components/
        │   ├── AudioCapture.jsx         # mic controls (start/pause/end/continue/reset)
        │   ├── TranscriptDisplay.jsx    # transcript panel with speaker colors
        │   └── FallacyDisplay.jsx       # fallacy cards + speaker rename
        └── App.css                      # dark theme design system
```

---

## Free Tier Limits

| Service | Free limit |
|---|---|
| AssemblyAI | 100 hours/month transcription |
| Groq | 14,400 req/day, 500k tokens/day |
| Render | 750 hours/month |
| Vercel | 100GB bandwidth/month |
| UptimeRobot | 50 monitors, 5-min interval |

---

## License

MIT
