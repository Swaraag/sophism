import logging
from utils import audio_utils
from services import whisper_service
from services import pyannote_service

logger = logging.getLogger("main")

async def audio_to_transcript(pcm_bytes, total_time_processed):
    '''Takes raw PCM bytes, runs diarization + transcription, returns merged segments.'''

    processed_bytes = audio_utils.process_audio_bytes(pcm_bytes)

    speaker_segs = await pyannote_service.process_audio(processed_bytes)
    logger.info(f"Pyannote found {len(speaker_segs)} speaker segments: {speaker_segs}")

    final_transcript = []
    for segment in speaker_segs:
        start = int(segment["start"] * 16000)
        end = int(segment["end"] * 16000)
        segment["transcript"] = await whisper_service.transcribe_audio(processed_bytes[start:end])
        segment["start"] += total_time_processed
        segment["end"] += total_time_processed
        final_transcript.append(segment)

    return final_transcript
