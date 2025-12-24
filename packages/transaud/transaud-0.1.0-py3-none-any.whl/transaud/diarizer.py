import warnings
from typing import Tuple

# import torchaudio
from loguru import logger
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.speaker_diarization import DiarizeOutput
from pyannote.audio.pipelines.utils.hook import ProgressHook
from torch import Tensor

from transaud.env import HF_TOKEN
from transaud.audio_converter import load_audio_with_pydub

warnings.filterwarnings("ignore",category=UserWarning,
                        message="In 2.9, this function's implementation")
warnings.filterwarnings("ignore",category=UserWarning,
                        message=r"[Correction should be strictly less]")


def extract_speaker_segments(path_to_audio:str,num_speakers:int=None
                             )->Tuple[Tensor,float,DiarizeOutput]:
    """
    Performs speaker diarization on an audio file using a pre-trained Pyannote model.

    This function loads an audio file, initializes a speaker diarization pipeline 
    from Hugging Face, and identifies "who spoke when." It can optionally use a 
    provided number of speakers to improve accuracy.

    Args:
        path_to_audio (str): The file path to the audio file (e.g., .wav, .flac).
        num_speakers (int, optional): The known number of distinct speakers in the 
            audio. If None, the model will attempt to detect the number of 
            speakers automatically. Defaults to None.

    Returns:
        Tuple[Tensor, float, DiarizeOutput]: A tuple containing:
            - waveform (Tensor): The input waveform
            - sample_rate (float): The sampling rate of the processed audio.
            - diarized_output (DiarizeOutput): An object containing the 
              detected segments, timestamps, and speaker labels.

    Note:
        This function requires a valid `HF_TOKEN` to be defined in the environment 
        variables and access permissions to the `pyannote/speaker-diarization-community-1` 
        model on Hugging Face.
    """
    logger.info("Begin speaker detection....")
    # waveform, sample_rate = torchaudio.load(path_to_audio)
    waveform, sample_rate = load_audio_with_pydub(path_to_audio)

    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", 
                                        token=HF_TOKEN)
    
    if num_speakers:
        with ProgressHook() as hook:
            diarized_output = pipeline({"waveform": waveform, 
                                        "sample_rate": sample_rate},
                                        num_speakers=num_speakers,
                                        hook=hook)
    else:
        with ProgressHook() as hook:
            diarized_output = pipeline({"waveform": waveform,
                                        "sample_rate": sample_rate},
                                        hook=hook)
    
    logger.info("Speaker diarization completed.")

    return waveform, sample_rate, diarized_output