from diart import SpeakerDiarization

pipeline = None

async def init_diart():
    '''Initializes the diart model.'''
    global pipeline
    try:
        pipeline = SpeakerDiarization()
        print("Successfully loaded Diart model.")
    except Exception as e:
        print(f"Error loading Diart: {e}")

async def process_audio(audio_bytes):
    '''Processes the audio bytes into segmented time stamps of each speaker's talking duration'''
    if pipeline is None:
        raise Exception("Diart pipeline not initialized.")
    # speaker_segs = [{"speaker": "speaker1", "start": 0:00, "end": 0:25}, ...]
    speaker_segs = []
    return speaker_segs