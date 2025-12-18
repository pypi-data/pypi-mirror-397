"""
miaudio
=======

A small, dependency‑free audio helper library for Windows, implemented purely
with the Python standard library.

High‑level functions:

- play_audio
- play_in_background
- play_at_time
- play_after_delay
- stop_audio
- is_supported_platform

All functions are documented in their respective docstrings.
"""

from .core import (
    AudioFileError,
    AudioFileNotFoundError,
    PlaybackError,
    PlatformNotSupportedError,
    UnsupportedFormatError,
    beep,
    beep_pattern,
    is_playing,
    is_supported_platform,
    play_after_delay,
    play_at_time,
    play_audio,
    play_for,
    play_in_background,
    play_once,
    play_sequence,
    play_sequence_in_background,
    play_system_sound,
    play_while,
)

__all__ = [
    "play_audio",
    "play_once",
    "play_for",
    "play_in_background",
    "play_sequence",
    "play_sequence_in_background",
    "play_at_time",
    "play_after_delay",
    "play_while",
    "stop_audio",
    "is_playing",
    "is_supported_platform",
    "beep",
    "beep_pattern",
    "play_system_sound",
    "PlatformNotSupportedError",
    "AudioFileError",
    "AudioFileNotFoundError",
    "UnsupportedFormatError",
    "PlaybackError",
]


