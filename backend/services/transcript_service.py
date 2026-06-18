import logging
import numpy as np
from utils import audio_utils
from services import assemblyai_service

logger = logging.getLogger("main")

async def audio_to_transcript(pcm_bytes: bytes, total_time_processed: float) -> list:
    '''
    Converts raw Int16 48kHz PCM bytes to a list of transcript segments.
    Resamples to 16kHz, then sends to AssemblyAI for diarization + transcription.
    Returns [{speaker, start, end, transcript}] with timestamps offset by total_time_processed.
    '''
    # resample to 16kHz mono Int16 PCM for AssemblyAI
    audio_float = audio_utils.process_audio_bytes(pcm_bytes)          # Float32 16kHz numpy
    int16_bytes = (audio_float * 32767).astype(np.int16).tobytes()    # back to Int16 bytes

    segments = await assemblyai_service.transcribe_with_diarization(int16_bytes, total_time_processed)
    logger.info(f"transcript_service got {len(segments)} segments")
    return segments
