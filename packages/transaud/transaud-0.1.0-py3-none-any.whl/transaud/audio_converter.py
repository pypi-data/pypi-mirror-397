import os
from tempfile import NamedTemporaryFile

import numpy as np
import pydub
import torch
from loguru import logger
from pydub import AudioSegment
from pydub.playback import play


def convert_audio_to_wav(audio_file_path, wav_output_path):
    """
    Converts an M4A audio file to an wav file using pydub and ffmpeg.
    """
    try:
        ext = os.path.basename(audio_file_path).split(".")[1]

        audio = AudioSegment.from_file(audio_file_path, format=ext)
        audio.export(wav_output_path, format="wav")# bitrate="192k"

        logger.info(f"Successfully converted '{audio_file_path}' to .wav")

        return audio
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.info("Please ensure FFmpeg is installed and added to your system's PATH.")


def load_audio_with_pydub(path_to_audio: str, target_sr: int = 16000):
    """Bypasses torchcodec by using pydub to load and normalize audio."""
    # Load and force to mono + target sample rate
    audio = AudioSegment.from_file(path_to_audio)
    audio = audio.set_frame_rate(target_sr).set_channels(1)
    
    # Convert to numpy array
    samples = np.array(audio.get_array_of_samples())
    
    # Normalize integer PCM to float32 [-1.0, 1.0]
    # (pydub usually loads 16-bit PCM)
    fp_samples = samples.astype(np.float32) / 32768.0
    
    # Convert to torch tensor with shape [channels, samples]
    waveform = torch.from_numpy(fp_samples).unsqueeze(0)
    
    return waveform, target_sr