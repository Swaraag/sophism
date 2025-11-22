import whisper

whisper_model = None

# init_whisper() is called in main.py's lifespan() function
async def init_whisper():
    '''Initializes the whisper model.'''
    global whisper_model
    whisper_model = whisper.load_model("base")

# transcribe_audio() is called in transcript_service.py's audio_to_transcript() function
async def transcribe_audio(audio_bytes) -> str:
    '''Transcribes the audio, attaching different speakers to each section'''
    if whisper_model is None:
            raise Exception("Whisper model is not initialized")
    
    # call function within audio_utils.py that converts the audio_bytes into the right format for whisper
    transcribed_audio = whisper_model.transcribe(audio_bytes)
    return transcribed_audio["text"]

