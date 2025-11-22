import numpy as np
import librosa

# bytes_to_audio_array() is called in process_audio_bytes() below
def bytes_to_audio_array(pcm_bytes):
    '''Takes the raw bytes, converts to a numpy array at 48khz'''
    if len(pcm_bytes) == 0:
        raise ValueError("Empty audio bytes received.")
    np_audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    return np_audio

# resample_audio() is called in process_audio_bytes() below
def resample_audio(input_audio, orig_sr=48000, target_sr=16000):
    '''Takes the numpy array at 48khz and resamples down to 16khz'''
    resampled_audio = librosa.resample(y=input_audio, orig_sr=orig_sr, target_sr=target_sr)
    return resampled_audio

# process_audio_bytes() is called in transcript_service.py's audio_to_transcript() function
def process_audio_bytes(pcm_bytes):
    '''Combines both functions into one step that will be used in main.py'''

    audio_array = bytes_to_audio_array(pcm_bytes)

    max_val = np.max(np.abs(audio_array))
    if max_val > 0:
        audio_array = audio_array / max_val  # Scale to -1.0 to 1.0

    resampled = resample_audio(audio_array, 48000, 16000)

    energy = np.mean(np.abs(resampled))
    print(f"Audio energy level: {energy}")
    
    if energy < 0.01:
        print("WARNING: Audio is very quiet or silent!")
    
    # returns 16000 khz numpy
    return resampled