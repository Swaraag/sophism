import assemblyai as aai
import io
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("main")

def init_assemblyai():
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise Exception("ASSEMBLYAI_API_KEY not set in environment.")
    aai.settings.api_key = api_key
    logger.info("AssemblyAI service ready.")

async def transcribe_with_diarization(pcm_bytes_16khz: bytes, total_time_offset: float) -> list:
    '''
    Sends 16kHz mono Int16 PCM bytes to AssemblyAI.
    Returns segments: [{speaker, start, end, transcript}]
    start/end are in seconds, offset by total_time_offset for continuity across chunks.
    '''
    # AssemblyAI expects a file-like object or URL; wrap bytes in a WAV container
    wav_bytes = _pcm_to_wav(pcm_bytes_16khz, sample_rate=16000, channels=1, sampwidth=2)

    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_code="en",
        speech_model=aai.SpeechModel.nano,  # fastest + cheapest tier
    )

    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(io.BytesIO(wav_bytes))

    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"AssemblyAI transcription error: {transcript.error}")

    if not transcript.utterances:
        logger.info("AssemblyAI returned no utterances.")
        return []

    segments = []
    for utt in transcript.utterances:
        segments.append({
            "speaker": utt.speaker,
            "start": round(utt.start / 1000.0 + total_time_offset, 3),
            "end":   round(utt.end   / 1000.0 + total_time_offset, 3),
            "transcript": utt.text,
        })

    logger.info(f"AssemblyAI returned {len(segments)} utterances.")
    return segments


def _pcm_to_wav(pcm_bytes: bytes, sample_rate: int, channels: int, sampwidth: int) -> bytes:
    '''Wraps raw PCM bytes in a minimal WAV header so AssemblyAI can parse the format.'''
    import struct
    data_size = len(pcm_bytes)
    byte_rate = sample_rate * channels * sampwidth
    block_align = channels * sampwidth

    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,
        b'WAVE',
        b'fmt ',
        16,             # subchunk1 size
        1,              # PCM format
        channels,
        sample_rate,
        byte_rate,
        block_align,
        sampwidth * 8,  # bits per sample
        b'data',
        data_size,
    )
    return header + pcm_bytes
