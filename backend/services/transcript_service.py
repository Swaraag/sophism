from utils import audio_utils
from services import whisper_service
from services import pyannote_service

async def audio_to_transcript(pcm_bytes):
    '''Takes the speaker segment information and the transcribed audio and merges them'''

    # transcribed_audio is a numpy array of 16000 khz
    processed_bytes = audio_utils.process_audio_bytes(pcm_bytes)

    # speaker_seg = [{"speaker": "speaker1", "start": 0:00, "end": 0:25}, ...]
    speaker_segs = await pyannote_service.process_audio(processed_bytes)

    print(f"Pyannote found {len(speaker_segs)} speaker segments")  # ← Add this
    print(f"Segments: {speaker_segs}")  # ← Add this

    # returns whisper_model.transcribe(audio_bytes)
    #transcribed_audio = whisper_service.transcribe_audio(processed_bytes)

    # format the speaker_segs and transcribed audio
    # desired format: final_transcript = [{"speaker": "speaker1", "start": 0:00, "end": 0:25, "transcript": "Hi my name is..."}, ...]

    # given the start and end stamps in segment, slice the audio in processed_bytes, and run transcribe_audio() on it
    final_transcript = []
    for segment in speaker_segs:
        # starting/ending point as indices in the numpy array
        start = int(segment["start"]*16000)
        end = int(segment["end"]*16000)
        segment["transcript"] = await whisper_service.transcribe_audio(processed_bytes[start:end])
        final_transcript.append(segment)
    return final_transcript