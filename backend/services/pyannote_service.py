from pyannote.audio import Pipeline
import torch
from dotenv import load_dotenv
import os
from pyannote.audio.pipelines.utils.hook import ProgressHook
import soundfile as sf
import librosa 
import numpy as np

load_dotenv()
pipeline = None

# init_pyannote() is called in main.py's lifespan() function
async def init_pyannote():
    '''Initializes the pyannote-audio model.'''
    global pipeline
    try:
        hf_token = os.getenv("HF_TOKEN")

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )

        # try:
        #     if hasattr(pipeline, '_segmentation'):
        #         pipeline._segmentation.threshold = 0.1 
        #         print("Modified VAD threshold to 0.1")
        # except Exception as threshold_error:
        #     print(f"Could not modify threshold: {threshold_error}")

        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))
            print("Using GPU")
        else:
            print("Using CPU (this will be slower)")
    except Exception as e:
        print(f"Error loading pyannote-audio: {e}")

# process_audio is called in transcript_service.py
async def process_audio(audio_bytes):
    '''Processes the audio bytes into segmented time stamps of each speaker's talking duration'''
    if pipeline is None:
        raise Exception("Pyannote-audio pipeline not initialized.")
    speaker_segs = []

    try:
        torch_tensor = torch.from_numpy(audio_bytes).float().unsqueeze(0)

        with ProgressHook() as hook:
            diarization = pipeline({"waveform": torch_tensor, "sample_rate": 16000}, hook=hook)
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segs.append({"speaker": speaker, "start": turn.start, "end": turn.end})
        print(f"Received {len(audio_bytes)} samples at an expected duration of {len(audio_bytes)/16000:.1f} seconds")
        
        return speaker_segs
    except Exception as e:
        print(f"Error processing audio: {e}")
        return []