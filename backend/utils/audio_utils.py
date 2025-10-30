import numpy as np
import librosa

def bytes_to_audio_array(pcm_bytes):
    '''Takes the raw bytes, converts to a numpy array at 48khz'''
    if len(pcm_bytes) == 0:
        raise ValueError("Empty audio bytes received.")
    np_audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    return np_audio


def resample_audio(input_audio, orig_sr=48000, target_sr=16000):
    '''Takes the numpy array at 48khz and resamples down to 16khz'''
    resampled_audio = librosa.resample(y=input_audio, orig_sr=orig_sr, target_sr=target_sr)
    return resampled_audio

def process_audio_bytes(pcm_bytes):
    '''Combines both functions into one step that will be used in main.py'''
    audio_array = bytes_to_audio_array(pcm_bytes)
    resampled = resample_audio(audio_array, 48000, 16000)
    # returns 16000 khz numpy
    return resampled