import torch
from loguru import logger
from pyannote.audio.pipelines.speaker_diarization import DiarizeOutput
from tqdm import tqdm
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from transformers.utils import logging as hflogging

from transaud.utils import write_formatted_block

hflogging.set_verbosity_error()


def transcribe_speaker_audio_to_text(output_filename:str,
                                     waveform:torch.Tensor,
                                     sample_rate:float,
                                     diarizer_output:DiarizeOutput,
                                     line_length:int=120):
    """
    Transcribe speaker-segmented audio into a formatted, speaker-attributed 
    text file.

    This function takes a full audio waveform and the output of a speaker
    diarization pipeline, extracts per-speaker audio segments, transcribes
    each segment using the Whisper Turbo model, and writes a readable
    transcript to disk. Consecutive segments spoken by the same speaker
    are grouped into a single formatted block with timestamps and hanging
    indentation.

    GPU acceleration is used automatically when available.

    Args:
        output_filename (str): Path to the output text file where the 
            transcript will be written.
        waveform (torch.Tensor): Audio waveform tensor of shape
            ``(channels, samples)``. If multiple channels are present,
            they are averaged to mono before transcription.
        sample_rate (float): Sample rate of the waveform in Hz.
        diarizer_output (DiarizeOutput): Output object from a speaker
            diarization pipeline containing speaker labels and time
            boundaries.
        line_length (int, optional): Maximum number of characters per line
            in the output transcript. Defaults to 120.

    Returns:
        None. The transcript is written directly to ``filename``.

    Raises:
        RuntimeError: If model loading or transcription fails.
        IOError: If the output file cannot be written.
    """
    logger.info("Starting speaker transcription...")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    whisper_model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, dtype=torch_dtype, 
        low_cpu_mem_usage=True, use_safetensors=True
    )
    whisper_model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    asr_pipe = pipeline(
        "automatic-speech-recognition",
        model=whisper_model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        dtype=torch_dtype,
        device=device,
    )

    raw_segments = []
    for turn, speaker in tqdm(diarizer_output.speaker_diarization,
                              desc="Transcribing audio ...",position=0):
        start, end = int(turn.start*sample_rate), int(turn.end*sample_rate)
        segment_audio = waveform[:,start:end].mean(dim=0).flatten().numpy()
        transcription = asr_pipe(segment_audio, return_timestamps=True)
        
        raw_segments.append({
            "start": turn.start,
            "speaker": speaker,
            "text": transcription["text"].strip()
        }) 


    with open(output_filename, "w") as f:
        if not raw_segments:
            return

        current_time = raw_segments[0]["start"]
        current_speaker = raw_segments[0]["speaker"]
        speaker_buffer = []

        for seg in raw_segments:
            if seg["speaker"] == current_speaker:
                speaker_buffer.append(seg["text"])
            else:
                # Write the completed block for the previous speaker
                write_formatted_block(f, current_time, current_speaker, 
                                      speaker_buffer, line_length)
                
                # Reset for the new speaker
                current_speaker = seg["speaker"]
                current_time = seg["start"]
                speaker_buffer = [seg["text"]]

        # Write the final remaining block
        write_formatted_block(f, current_time, current_speaker, 
                              speaker_buffer, line_length)

    logger.info(f"Text transcript saved to {output_filename}")
