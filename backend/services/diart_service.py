from diart import SpeakerDiarization

pipeline = None

async def initialize_diart():
    global pipeline
    try:
        pipeline = SpeakerDiarization()
        print("Successfully loaded Diart model.")
    except Exception as e:
        print(f"Error loading Diart: {e}")

async def process_audio(audio_bytes):
    if pipeline is None:
        raise Exception("Diart pipeline not initialized.")
    # speaker_segs = [{"speaker": "speaker1", "start": 0:00, "end": 0:25}, ...]
    speaker_segs = []
    return speaker_segs