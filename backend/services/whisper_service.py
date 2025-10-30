import whisper
from utils import audio_utils

model = None

async def init_model():
    global model
    model = whisper.load_model("base")

async def transcribe_audio(audio_bytes) -> str:
    if model is None:
            raise Exception("Whisper model is not initialized")
    
    # call function within audio_utils.py that converts the audio_bytes into the right format for whisper
    transcribed_audio = model.transcribe(audio_bytes)
    return transcribed_audio["text"]

