from pyannote.audio import Pipeline
import torch
from dotenv import load_dotenv
import os
from pyannote.audio.pipelines.utils.hook import ProgressHook

load_dotenv()
pipeline = None

async def init_pyannote():
    '''Initializes the pyannote-audio model.'''
    global pipeline
    try:
        hf_token = os.getenv("HF_TOKEN")

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )
        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))
            print("Using GPU")
        else:
            print("Using CPU (this will be slower)")
    except Exception as e:
        print(f"Error loading pyannote-audio: {e}")

async def process_audio(audio_bytes):
    '''Processes the audio bytes into segmented time stamps of each speaker's talking duration'''
    if pipeline is None:
        raise Exception("Pyannote-audio pipeline not initialized.")
    speaker_segs = []
    try:
        torch_tensor = torch.from_numpy(audio_bytes).float()
        torch_tensor = torch_tensor.unsqueeze(0)

        print(f"Torch tensor shape: {torch_tensor.shape}")
        print(f"Torch tensor min/max: {torch_tensor.min()}, {torch_tensor.max()}")
        print(f"Torch tensor first 20 values: {torch_tensor[0, :20]}")

        with ProgressHook() as hook:
            diarization = pipeline({"waveform": torch_tensor, "sample_rate": 16000}, hook=hook)

        print(f"Raw diarization output: {list(diarization.itertracks(yield_label=True))}")
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_segs.append({"speaker": speaker, "start": turn.start, "end": turn.end})

        # speaker_segs = [{"speaker": "speaker1", "start": 0:00, "end": 0:25}, ...]
        
        return speaker_segs
    except Exception as e:
        print(f"Error processing audio: {e}")
        return []