import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from textwrap import TextWrapper
from typing import List


def get_lib_dir():
    """
    Trace the path to the repo's root

    Returns:
        str
    """
    file_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    repo_dir = file_dir.parents[1]
    return repo_dir


def format_timedelta(time_seconds:float)->str:
    """
    Format time delta from audio transcription
    """
    td = timedelta(seconds=time_seconds)
    fmt = (datetime(1970, 1, 1, tzinfo=timezone.utc) + td).strftime("%H:%M:%S.%f")
    return fmt[:-3]


def write_formatted_block(writer, start_time:float, 
                          speaker:str, text_list:List[str], 
                          line_length:int):
    """
    Write a formatted, wrapped transcript block to an output writer.

    This function formats a speaker-attributed transcription segment with
    a timestamp header and wraps the associated text to a fixed line width
    using hanging indentation. The first line includes the timestamp and
    speaker label, while subsequent lines are indented to align with the
    start of the spoken text.

    Args:
        writer: A file-like object with a ``write(str)`` method (e.g. an open
            file handle or ``io.StringIO``).
        start_time (float): Start time of the segment in seconds. This will be
            converted to a human-readable timestamp.
        speaker (str): Speaker label to display (e.g. ``"Speaker 1"``).
        text_list (List[str]): List of text fragments to be concatenated into
            a single transcription block.
        line_length (int): Maximum line width (in characters) for text wrapping.

    Returns:
        None. The formatted block is written directly to ``writer``.
    """
    full_text = " ".join(text_list)
    timestamp = format_timedelta(start_time)
    
    # Define the prefix (header)
    prefix = f"[{timestamp}] {speaker}: "

    # Calculate indentation size
    indent_space = " " * len(prefix)
    
    # Wrap text to char limit with hanging indentation
    wrapper = TextWrapper(
        width=line_length,
        initial_indent=prefix,
        subsequent_indent=indent_space,
        break_long_words=False
    )
    writer.write(wrapper.fill(full_text) + "\n\n")