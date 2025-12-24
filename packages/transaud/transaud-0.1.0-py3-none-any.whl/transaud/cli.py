import os
from tempfile import NamedTemporaryFile

import click
from loguru import logger

from transaud.audio_converter import convert_audio_to_wav
from transaud.diarizer import extract_speaker_segments
from transaud.utils import get_lib_dir
from transaud.whisper import transcribe_speaker_audio_to_text


@click.command()
@click.option("-iaf","--input_audio_file", type=click.Path(exists=True, readable=True), 
              nargs=1, required=True, help="Path to input audio file.")
@click.option("-ns","--num_speakers", nargs=1, required=False, type=click.INT,  
              default=None, help="Number of speakers in input audio file if known.")
@click.option("-ll","--line_length", nargs=1, required=False, type=click.INT,  
              default=120, help="Line length for transcribed text in output file.")
@click.option("-otf","--output_text_file", nargs=1, required=False, default=None, 
              type=click.Path(exists=False, readable=False), 
              help="Path to output audio file. File will be overwritten with each run.")
def main(input_audio_file:str,
         num_speakers:int|None,
         line_length:int,
         output_text_file:str|None):
    """
    Run speaker diarization and transcription on an input audio file.

    This command-line entry point converts the input audio to a temporary
    WAV file, performs speaker diarization to identify speaker turns, and
    transcribes each speaker segment using a speech-to-text model. The final
    output is a formatted, speaker-attributed transcript written to a text
    file.

    If an output file path is not provided, the transcript is written to a
    ``.txt`` file derived from the input audio filename.

    Args:
        input_audio_file (str): Path to the input audio file. The file must
            exist and be readable. Supported formats depend on the audio
            conversion backend.
        num_speakers (int | None): Optional number of speakers in the audio.
            Providing this value can improve diarization accuracy. If ``None``,
            the number of speakers is inferred automatically.
        line_length (int): Maximum number of characters per line in the output
            transcript. Used for text wrapping and formatting.
        output_text_file (str | None): Optional path to the output transcript
            file. If provided, the file will be overwritten. If ``None``, a
            filename is generated from the input audio name.

    Returns:
        None. This function writes the transcript to disk and exits.

    Side Effects:
        - Creates a temporary WAV file during processing.
        - Writes (or overwrites) the output transcript file.
        - Deletes the temporary WAV file after completion.

    Raises:
        click.ClickException: If argument validation fails.
        RuntimeError: If audio processing, diarization, or transcription fails.
        IOError: If the output file cannot be written.
    """
    
    logger.info("Loading audio and converting file format....")
    
    wav = NamedTemporaryFile(delete=False,suffix=".wav")
    convert_audio_to_wav(input_audio_file,wav.name)

    # Extract the output filename
    audio_name = os.path.basename(input_audio_file).split(".")[0]
    filename = output_text_file if output_text_file else f"{audio_name}.txt"

    audio, smpr, diarized = extract_speaker_segments(wav.name,num_speakers)
    transcribe_speaker_audio_to_text(filename,audio, smpr, diarized,line_length)
    
    os.remove(wav.name)
