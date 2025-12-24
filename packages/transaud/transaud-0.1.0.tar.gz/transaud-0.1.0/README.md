### `transaud` Description
A command-line tool for speaker-attributed transcription using **pyannote** for speaker 
diarization and **Whisper Turbo** for speech-to-text. The tool produces readable, 
timestamped transcripts with speaker labels.<br>

### Overview
This tool performs the following steps:
1. Converts the input audio file to a temporary WAV format.
2. Runs speaker diarization to detect speaker turns.
3. Transcribes each speaker’s audio segment using Whisper Turbo.
4. Writes a formatted transcript grouped by speaker and timestamp.
GPU acceleration is automatically enabled when available, with a CPU fallback.

### Usage
```bash
poetry run transcribe -iaf /path/to/audio/file.ext
```
***Optional arguments***
- `--num-speakers`: Specify the number of speakers if known (improves diarization).
- `--line-length`: Set maximum line width for wrapped transcript text.
- `--output-text-file`: Specify a custom output file path.

### Output
The generated transcript:
- Groups consecutive speech from the same speaker
- Includes timestamps
- Uses hanging indentation for readability
If no output file is specified, a .txt file is created using the input audio filename.

### Dependencies
- `torch`
- `transformers`
- `pyannote.audio` (for diarization output)
- `tqdm`
- `ffmpeg` (system dependency)


### Environment variables.
***Hugging Face Authentication (Required)***<br>
This project uses pretrained models hosted on Hugging Face.
1. Generate a new huggingface token if you don't have one from 
    [hf tokens](https://huggingface.co/settings/tokens).
2. Approve access to the pyannote diarization model - 
    [link](https://huggingface.co/pyannote/speaker-diarization-community-1)
3. Create a .env file in the project root
    ```bash
    HF_TOKEN=your_token_here
    ```
4. Ensure environment variables are loaded into your shell:
    ```bash
    export HF_TOKEN=your_token_here
    ```

### Security Notice
> [!Caution]
> This module loads pretrained models from trusted Hugging Face repositories. 
    Ensure model sources are trusted when running in production environments.

### Known Issues
***Apple Silicon (macOS)***<br>

On Apple Silicon machines, you may encounter issues related to `torchcodec` or audio decoding. If so, update your `ffmpeg` library path:
```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
```

### Notes
- Converting audio to WAV internally ensures consistent behavior across systems.
- For best results, provide --num-speakers when the number of speakers is known.
- Long recordings may require significant memory when running on CPU.

### Model Licenses
This package does not ship any pretrained models.
Models are downloaded at runtime from Hugging Face and are subject
to their respective licenses:
- Whisper Turbo: OpenAI license
- pyannote speaker diarization: pyannote community license
Users are responsible for reviewing and complying with these licenses.