from pyannote.audio import Pipeline
import torch
from dotenv import load_dotenv
import os
from pyannote.audio.pipelines.utils.hook import ProgressHook

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

        try:
            # This attempts to lower the VAD activation threshold
            if hasattr(pipeline, '_segmentation'):
                pipeline._segmentation.threshold = 0.1  # Much lower than default
                print("Modified VAD threshold to 0.1")
        except Exception as threshold_error:
            print(f"Could not modify threshold: {threshold_error}")

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
    
async def test_pyannote_with_file():
    """Test pyannote with a known audio file to verify it works"""
    import librosa
    
    current_dir = os.path.dirname(__file__)  # This is services/
    backend_dir = os.path.dirname(current_dir)  # This is backend/
    test_file = os.path.join(backend_dir, "speech_test.wav")
    
    try:
        print(f"Loading test audio from {test_file}...")
        
        # Load and process the audio
        audio, sr = librosa.load(test_file, sr=16000, mono=True)
        print(f"Loaded test audio: {len(audio)} samples at {sr}Hz ({len(audio)/sr:.1f} seconds)")
        print(f"Audio energy: {abs(audio).mean():.4f}")
        print(f"Audio range: {audio.min():.4f} to {audio.max():.4f}")
        
        # Convert to tensor
        torch_tensor = torch.from_numpy(audio).float().unsqueeze(0)
        print(f"Tensor shape: {torch_tensor.shape}")
        
        # Run through pyannote
        print("Running pyannote on test audio...")
        with ProgressHook() as hook:
            diarization = pipeline({"waveform": torch_tensor, "sample_rate": 16000}, hook=hook)
        
        # Extract results
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({"speaker": speaker, "start": turn.start, "end": turn.end})
        
        print(f"\n*** TEST RESULTS ***")
        print(f"Pyannote detected {len(segments)} speaker segments in test file")
        for seg in segments:
            print(f"  {seg['speaker']}: {seg['start']:.2f}s - {seg['end']:.2f}s")
        
        return segments
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return []