from utils import audio_utils
from services import whisper_service
from services import diart_service

def audio_to_transcript(pcm_bytes):
    processed_bytes = audio_utils.process_audio_bytes(pcm_bytes)

    speaker_segs = diart_service.process_audio(processed_bytes)

