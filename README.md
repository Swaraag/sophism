# Sophism

An AI-powered real-time debate analyzer that detects logical fallacies as people speak.

![Project Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.12-blue)
![React](https://img.shields.io/badge/react-19.2-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

Sophism captures audio from a live debate, identifies who is speaking, transcribes their words, and uses AI to detect logical fallacies in real-time. The system processes everything locally with no external API costs, making it ideal for educational settings, debate practice, or critical thinking exercises.

**Key Features:**
- Real-time audio capture and processing
- Speaker diarization (distinguishes between speakers)
- Speech-to-text transcription
- AI-powered fallacy detection
- Sub-10 second latency
- Completely local processing (privacy-first)

## Demo

[Live Demo] *(Coming soon)*

**Example Output:**
```json
{
  "transcript": [
    {
      "speaker": "SPEAKER_00",
      "start": 0.0,
      "end": 5.0,
      "transcript": "You can't trust anything John says because he's not even a scientist."
    }
  ],
  "fallacies": [
    {
      "speaker": "SPEAKER_00",
      "fallacy_type": "ad hominem",
      "statement": "You can't trust anything John says because he's not even a scientist.",
      "explanation": "Attacks the person's credentials rather than addressing the argument itself.",
      "confidence": 0.92
    }
  ]
}
```

## Installation

### Prerequisites

- Python 3.12
- Node.js 18+
- FFmpeg
- Ollama
- HuggingFace account (free)

### Backend Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Swaraag/sophism.git
cd sophism
```

2. **Install Python dependencies:**
```bash
cd backend
# Ensure you're using Python 3.12
pip install -r requirements.txt
```

3. **Install system dependencies:**
```bash
# macOS
brew install ffmpeg portaudio libsndfile

# Ubuntu/Debian
sudo apt-get install ffmpeg portaudio19-dev libsndfile1
```

4. **Install and configure Ollama:**
```bash
# macOS
brew install ollama

# Other platforms: https://ollama.com

# Pull the Llama 3.1 model
ollama pull llama3.1:8b
```

5. **Configure HuggingFace authentication:**
```bash
# Create a .env file in the backend directory
echo "HF_TOKEN=your_token_here" > .env
```

Get your token from [HuggingFace Settings](https://huggingface.co/settings/tokens) and accept the [Pyannote terms](https://huggingface.co/pyannote/speaker-diarization-3.1).


7. **Start the backend:**
```bash
uvicorn main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node dependencies:**
```bash
cd frontend
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Usage

1. **Start both servers** (backend and frontend)
2. **Open the frontend** in your browser
3. **Click "Start a debate!"** to begin audio capture
4. **Grant microphone permissions** when prompted
5. **Speak naturally** - the system processes 5-second chunks
6. **View results** in real-time as transcript and detected fallacies appear

**Tips for best results:**
- Speak clearly with distinct pauses between speakers
- Minimize background noise
- Allow 5-10 seconds for processing lag
- Use headphones to prevent audio feedback


## Architecture

### High-Level Flow

```
Microphone → Browser Capture (48kHz Float32)
                    ↓
          AudioWorklet Buffering (5 sec chunks)
                    ↓
          Format Conversion (Float32 → Int16)
                    ↓
          WebSocket Transmission (480KB/5sec)
                    ↓
          FastAPI Backend Processing
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
Speaker         Speech          Fallacy
Diarization     Transcription   Detection
(Pyannote)      (Whisper)       (Llama 3.1)
    ↓               ↓               ↓
    └───────────────┴───────────────┘
                    ↓
          Merged Results (JSON)
                    ↓
          WebSocket Response
                    ↓
          React UI Display
```

### Tech Stack

**Backend:**
- **FastAPI** - WebSocket server with async support
- **Pyannote-audio 3.1** - Neural speaker diarization
- **OpenAI Whisper** - Speech recognition (local inference)
- **Ollama + Llama 3.1** - Logical fallacy detection
- **PyTorch 2.3** - Deep learning framework
- **Librosa** - Audio processing and resampling

**Frontend:**
- **React 19** - UI framework with hooks
- **Vite** - Modern build tool
- **Web Audio API** - Raw PCM audio capture
- **AudioWorkletNode** - High-performance audio processing
- **WebSocket** - Real-time bidirectional communication

### Audio Pipeline Details

The system uses a sophisticated buffered processing approach optimized for both quality and bandwidth:

| Stage | Format | Sample Rate | Samples | Bytes | Duration |
|-------|--------|-------------|---------|-------|----------|
| Browser Capture | Float32 | 48 kHz | 240,000 | 960,000 | 5 sec |
| After Conversion | Int16 | 48 kHz | 240,000 | 480,000 | 5 sec |
| WebSocket Send | Int16 | - | - | **480,000** | - |
| Backend Receive | Int16 | - | - | 480,000 | - |
| Conversion | Float32 | 48 kHz | 240,000 | 960,000 | 5 sec |
| After Resample | Float32 | 16 kHz | 80,000 | 320,000 | 5 sec |
| AI Processing | Float32 | 16 kHz | 80,000 | 320,000 | 5 sec |

**Key Optimizations:**
- **50% bandwidth reduction:** Float32 → Int16 conversion before transmission
- **Industry-standard format:** Int16 PCM is used by Opus, WebRTC, telephony
- **Minimal quality loss:** 16-bit precision sufficient for speech
- **Production-ready:** Scalable architecture for deployment

## Project Structure

```
sophism/
├── backend/
│   ├── services/
│   │   ├── pyannote_service.py      # Speaker diarization
│   │   ├── whisper_service.py       # Speech transcription
│   │   ├── ollama_service.py        # Fallacy detection
│   │   ├── transcript_service.py    # Service orchestration
│   │   └── ollama_instructions.txt  # LLM prompt engineering
│   ├── utils/
│   │   └── audio_utils.py           # Audio format conversion
│   ├── main.py                      # FastAPI WebSocket server
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── audio-processor-worklet.js  # AudioWorklet processor
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioCapture.jsx     # Mic capture & streaming
│   │   │   ├── TranscriptDisplay.jsx
│   │   │   └── FallacyDisplay.jsx
│   │   ├── App.jsx                  # Main component
│   │   └── main.jsx
│   └── package.json
└── README.md
```

## Technical Deep Dive

### Why Buffered Processing?

Unlike true streaming, Sophism processes audio in 5-second chunks. This approach:

- **Improves accuracy:** Pyannote performs better with complete audio segments
- **Provides context:** Speaker transitions are clearer in full chunks
- **Simplifies architecture:** Easier than continuous streaming
- **Acceptable latency:** 5-10 seconds is fine for educational use

### Audio Format Conversion Pipeline

**Frontend (AudioWorkletNode):**
```javascript
// Capture Float32 audio (native browser format)
const float32Data = inputBuffer.getChannelData(0);

// Convert to Int16 for transmission (50% bandwidth savings)
const int16Data = new Int16Array(float32Data.length);
for (let i = 0; i < float32Data.length; i++) {
    int16Data[i] = Math.max(-32768, Math.min(32767, float32Data[i] * 32768));
}

// Send via WebSocket
websocket.send(int16Data.buffer);
```

**Backend (audio_utils.py):**
```python
def bytes_to_audio_array(pcm_bytes):
    # Convert Int16 bytes to Float32 numpy array
    np_audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    return np_audio

def resample_audio(input_audio, orig_sr=48000, target_sr=16000):
    # Downsample for AI models (16kHz is standard for speech)
    resampled_audio = librosa.resample(y=input_audio, orig_sr=orig_sr, target_sr=target_sr)
    return resampled_audio
```

### Speaker Diarization

Pyannote-audio uses neural networks trained on the VoxCeleb dataset to:

1. **Detect speech activity** - Where is someone speaking?
2. **Segment speakers** - When do speaker changes occur?
3. **Cluster voices** - Which segments belong to the same person?
4. **Label speakers** - Assign consistent speaker IDs

**Model:** `pyannote/speaker-diarization-3.1`
- **Architecture:** Segmentation + Embedding + Clustering
- **Runtime:** ~1-2 seconds for 5 seconds of audio (CPU)
- **Accuracy:** ~90% on VoxCeleb test set

### Fallacy Detection

The system uses Llama 3.1 (8B parameters) via Ollama with a carefully engineered prompt:

**Prompt Strategy:**
- Temperature 0 for consistency
- Explicit JSON format requirements
- Focus on recent statements (last 15-20 seconds)
- Strict criteria for fallacy identification
- Confidence scoring for transparency

**Detected Fallacies:**
- Ad hominem (personal attacks)
- Straw man (misrepresentation)
- False dichotomy (false choice)
- Slippery slope (unjustified extrapolation)
- Appeal to authority (irrelevant expertise)
- Hasty generalization (insufficient evidence)

Using a bigger model would improve fallacy accuracy significantly, can be done easily by downloading a bigger model and adding the name in `backend/services/ollama_service.py`

## API Reference

### WebSocket Endpoint

**URL:** `ws://localhost:8000/ws`

**Client → Server (Audio Data):**
```
Binary message: Int16 PCM audio (480,000 bytes per 5 seconds)
```

**Server → Client (Results):**
```json
{
  "transcript": [
    {
      "speaker": "SPEAKER_00",
      "start": 1.043,
      "end": 5.110,
      "transcript": "The text of what was said..."
    }
  ],
  "fallacies": [
    {
      "speaker": "SPEAKER_00",
      "fallacy_type": "ad hominem",
      "statement": "The fallacious statement...",
      "explanation": "Why it's a fallacy...",
      "confidence": 0.85
    }
  ]
}
```

## Current Limitations & Future Work

### Current Limitations
- **Single microphone only** - Cannot handle separate audio sources yet
- **Two speakers optimized** - Best results with two-person debates
- **CPU-only inference** - GPU support would improve speed
- **English-only** - Whisper and Llama training bias toward English

### Planned Improvements
- [ ] GPU acceleration for faster processing
- [ ] Multi-microphone support
- [ ] Real-time confidence visualization
- [ ] Historical debate review interface
- [ ] Export transcripts as PDF/JSON
- [ ] Custom fallacy definitions
- [ ] Speaker name customization
- [ ] Production deployment with WSS (secure WebSocket)

## Performance Metrics

**Latency Breakdown:**
- Audio buffering: ~5 seconds
- Speaker diarization: ~1-2 seconds
- Transcription: ~1-2 seconds
- Fallacy detection: ~2-3 seconds
- **Total:** 9-12 seconds from speech to result

**Resource Usage:**
- RAM: ~4GB (model loading)
- CPU: ~50% during processing (MacBook Pro M1)
- Bandwidth: ~96 KB/sec (Int16 streaming)
- Disk: ~10GB (models + dependencies)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

**Areas for contribution:**
- UI/UX improvements
- Additional fallacy types
- Performance optimization
- Multi-language support
- Testing and documentation

## License

MIT License - see LICENSE file for details

## Acknowledgments

- **Pyannote-audio** - Neural speaker diarization
- **OpenAI Whisper** - Speech recognition
- **Ollama** - Local LLM inference
- **FastAPI** - Modern Python web framework
- **React** - UI framework

## Contact

For questions, suggestions, or collaboration:
- GitHub Issues: [sophism/issues](https://github.com/Swaraag/sophism/issues)
- Email: swaraag.sistla@gmail.com

---
