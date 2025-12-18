"""
Core implementation for the `miaudio` package.

This module provides a small set of high‑level, dependency‑free helpers for
playing WAV audio on Windows using only the Python standard library.

Design notes
------------

- Uses `winsound` on Windows only. On other platforms, calls that require
  playback will raise `PlatformNotSupportedError`.
- Supports WAV files only. Other extensions raise `UnsupportedFormatError`.
- Exposes simple primitives for:
  - blocking playback (`play_audio`)
  - background playback (`play_in_background`)
  - scheduled playback at an absolute time (`play_at_time`)
  - scheduled playback after a delay (`play_after_delay`)
  - explicitly stopping playback (`stop_audio`)
"""

from __future__ import annotations

import datetime as _dt
import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Optional, Sequence

try:  # pragma: no cover - import guarded for non‑Windows platforms
    import winsound as _winsound

    _HAS_WINSOUND = True
except Exception:  # pragma: no cover - non‑Windows platforms
    _winsound = None
    _HAS_WINSOUND = False


class PlatformNotSupportedError(RuntimeError):
    """Raised when attempting to use audio functionality on an unsupported platform."""


class AudioFileError(Exception):
    """Base class for all file‑related audio errors."""


class AudioFileNotFoundError(AudioFileError):
    """Audio file was not found at the specified path."""


class UnsupportedFormatError(AudioFileError):
    """Audio file format is not supported by this library (currently WAV only)."""


class PlaybackError(RuntimeError):
    """Raised for errors that occur during playback."""


# Backwards‑compatible alias; external code may have imported this earlier name.
FileNotFoundError = AudioFileNotFoundError


_STATE_LOCK = threading.Lock()
_STOP_EVENT = threading.Event()
_ACTIVE_THREAD: Optional[threading.Thread] = None


def is_supported_platform() -> bool:
    """
    Return True if the current environment supports audio playback.

    Currently this is equivalent to "running on Windows with `winsound` available".
    """

    return _HAS_WINSOUND


def _require_supported_platform() -> None:
    if not is_supported_platform():
        raise PlatformNotSupportedError(
            "miaudio currently supports only Windows via the standard-library "
            "`winsound` module. The current platform does not provide `winsound`."
        )


def _validate_audio_path(path: str | os.PathLike[str]) -> Path:
    """Validate that `path` points to an existing WAV file and return a Path."""

    p = Path(path)
    if not p.exists():
        raise AudioFileNotFoundError(f"Audio file not found: {p}")
    if not p.is_file():
        raise UnsupportedFormatError(f"Expected a file, got something else: {p}")
    if p.suffix.lower() != ".wav":
        raise UnsupportedFormatError(
            f"Unsupported audio format for {p.name!r}; only '.wav' is supported "
            "by the dependency‑free implementation."
        )
    return p


def _play_blocking(path: Path, loop: bool) -> None:
    """Internal helper to perform blocking playback using winsound."""

    assert _winsound is not None  # for type checkers
    flags = _winsound.SND_FILENAME
    if loop:
        flags |= _winsound.SND_LOOP | _winsound.SND_ASYNC
    # For non‑looping sounds, we prefer synchronous (blocking) playback.
    else:
        flags |= _winsound.SND_SYNC

    try:
        if loop:
            # For looped playback we start async and then wait until stop is signaled.
            _STOP_EVENT.clear()
            _winsound.PlaySound(str(path), flags)
            # Busy‑wait with a small sleep; winsound does not provide an event API.
            while not _STOP_EVENT.is_set():
                time.sleep(0.05)
        else:
            _winsound.PlaySound(str(path), flags)
    except Exception as exc:  # pragma: no cover - OS‑specific path
        raise PlaybackError(f"Playback failed for {path!s}: {exc}") from exc
    finally:
        if loop:
            # Always clear any remaining playback when exiting the loop.
            try:
                _winsound.PlaySound(None, 0)
            except Exception:
                pass


def play_audio(path: str | os.PathLike[str], *, loop: bool = False, block: bool = True) -> None:
    """
    Play a WAV audio file from the given path.

    Parameters
    ----------
    path:
        Filesystem path to a WAV file. The function verifies that the path exists,
        is a regular file, and has a `.wav` extension.
    loop:
        If True, repeatedly loop the sound until `stop_audio()` is called.
        Looping playback is implemented using asynchronous winsound playback and
        an internal stop event.
    block:
        If True (default), this function blocks until playback finishes (or until
        `stop_audio()` is called for looping playback). If False, the function
        returns immediately after starting playback in a background thread.

    Raises
    ------
    PlatformNotSupportedError
        If called on a platform where `winsound` is not available.
    FileNotFoundError
        If the specified file does not exist.
    UnsupportedFormatError
        If the specified file is not a `.wav` file.
    PlaybackError
        If playback fails due to an OS‑level error.
    """

    _require_supported_platform()
    audio_path = _validate_audio_path(path)

    if block:
        _play_blocking(audio_path, loop=loop)
        return

    # Non‑blocking mode: delegate to a background thread and return immediately.
    thread = play_in_background(audio_path, loop=loop)
    # We intentionally do not join the thread here.
    return None


def _background_worker(path: Path, loop: bool) -> None:
    """Target function for background playback threads."""

    try:
        _play_blocking(path, loop=loop)
    finally:
        global _ACTIVE_THREAD
        with _STATE_LOCK:
            if threading.current_thread() is _ACTIVE_THREAD:
                _ACTIVE_THREAD = None


def play_in_background(path: str | os.PathLike[str], *, loop: bool = False) -> threading.Thread:
    """
    Play a WAV file in a dedicated background thread.

    Parameters
    ----------
    path:
        Filesystem path to a WAV file (see `play_audio` for validation rules).
    loop:
        If True, the sound is played in a loop until `stop_audio()` is called.

    Returns
    -------
    threading.Thread
        The started background thread. In most cases you do not need to interact
        with this thread, but you may call `join()` on it if you want to wait for
        playback to finish.
    """

    _require_supported_platform()
    audio_path = _validate_audio_path(path)

    worker = threading.Thread(
        target=_background_worker,
        args=(audio_path, loop),
        daemon=True,
    )

    with _STATE_LOCK:
        global _ACTIVE_THREAD
        # Signal any existing playback to stop first.
        _STOP_EVENT.set()
        _ACTIVE_THREAD = worker
        _STOP_EVENT.clear()

    worker.start()
    return worker


def is_playing() -> bool:
    """
    Return True if there is an active background playback thread managed by `miaudio`.

    This does not detect sounds started by other code using `winsound` directly.
    """

    with _STATE_LOCK:
        return _ACTIVE_THREAD is not None and _ACTIVE_THREAD.is_alive()


def stop_audio() -> None:
    """
    Stop any audio currently playing via `miaudio`.

    This function is safe to call even if there is no active playback.
    """

    if not is_supported_platform():
        return

    assert _winsound is not None  # for type checkers

    with _STATE_LOCK:
        _STOP_EVENT.set()
        try:
            _winsound.PlaySound(None, 0)
        except Exception:
            # Stopping is best‑effort; we intentionally swallow errors here.
            pass


def play_after_delay(path: str | os.PathLike[str], delay_seconds: float) -> threading.Thread:
    """
    Schedule one‑shot playback after a relative delay.

    Parameters
    ----------
    path:
        Filesystem path to a WAV file.
    delay_seconds:
        Number of seconds to wait before starting playback. Negative values are
        treated as zero (play immediately).

    Returns
    -------
    threading.Thread
        Background thread that performs the wait and then plays the audio.
    """

    delay = max(0.0, float(delay_seconds))

    def _delayed() -> None:
        time.sleep(delay)
        try:
            play_audio(path, loop=False, block=True)
        except Exception:
            # For a scheduled fire‑and‑forget helper, we log nothing and simply exit.
            # Applications that need stronger guarantees can wrap this helper.
            return

    t = threading.Thread(target=_delayed, daemon=True)
    t.start()
    return t


def play_at_time(path: str | os.PathLike[str], when: _dt.datetime) -> threading.Thread:
    """
    Schedule one‑shot playback at the specified absolute time.

    Parameters
    ----------
    path:
        Filesystem path to a WAV file.
    when:
        A `datetime.datetime` representing the absolute time at which playback
        should start. Timezone‑aware datetimes are interpreted in their own
        timezone; naive datetimes are interpreted in the local timezone.

    Returns
    -------
    threading.Thread
        Background thread that waits until `when` and then plays the audio.
    """

    if not isinstance(when, _dt.datetime):
        raise TypeError("`when` must be a datetime.datetime instance")

    # Convert the target time to a POSIX timestamp, respecting tzinfo if present.
    target_ts = when.timestamp()
    now_ts = time.time()
    delay = max(0.0, target_ts - now_ts)
    return play_after_delay(path, delay)


def play_once(path: str | os.PathLike[str]) -> None:
    """
    Convenience wrapper for `play_audio(path, loop=False, block=True)`.

    This is the most common "fire and forget, but block until done" use case.
    """

    play_audio(path, loop=False, block=True)


def play_for(path: str | os.PathLike[str], seconds: float) -> None:
    """
    Play a WAV file but stop it automatically after the given duration.

    Parameters
    ----------
    path:
        Filesystem path to a WAV file.
    seconds:
        Maximum duration in seconds that playback is allowed to continue.
        Negative values are treated as zero (no playback).
    """

    max_duration = max(0.0, float(seconds))
    if max_duration == 0.0:
        return

    worker = play_in_background(path, loop=False)
    worker.join(timeout=max_duration)
    if worker.is_alive():
        stop_audio()


def play_sequence(
    paths: Sequence[str | os.PathLike[str]],
    *,
    gap_seconds: float = 0.0,
    loop_sequence: bool = False,
    block: bool = True,
) -> Optional[threading.Thread]:
    """
    Play a sequence (playlist) of WAV files in order.

    Parameters
    ----------
    paths:
        Iterable of filesystem paths to WAV files. All paths are validated up front.
    gap_seconds:
        Number of seconds to wait between each track (default: 0).
    loop_sequence:
        If True, repeat the entire sequence until `stop_audio()` is called.
    block:
        If True, block the calling thread until playback has finished (or until
        `stop_audio()` is called when looping). If False, playback occurs in a
        background thread and this function returns that thread.

    Returns
    -------
    Optional[threading.Thread]
        The background thread, if `block=False`; otherwise `None`.
    """

    _require_supported_platform()
    tracks = [Path(_validate_audio_path(p)) for p in paths]
    gap = max(0.0, float(gap_seconds))

    def _run_sequence() -> None:
        while True:
            for track in tracks:
                if _STOP_EVENT.is_set():
                    return
                _play_blocking(track, loop=False)
                if _STOP_EVENT.is_set():
                    return
                if gap > 0:
                    end_time = time.time() + gap
                    while time.time() < end_time:
                        if _STOP_EVENT.is_set():
                            return
                        time.sleep(0.01)
            if not loop_sequence:
                break

    if block:
        _run_sequence()
        return None

    worker = threading.Thread(target=_run_sequence, daemon=True)
    with _STATE_LOCK:
        global _ACTIVE_THREAD
        _STOP_EVENT.set()
        _ACTIVE_THREAD = worker
        _STOP_EVENT.clear()
    worker.start()
    return worker


def play_sequence_in_background(
    paths: Sequence[str | os.PathLike[str]],
    *,
    gap_seconds: float = 0.0,
    loop_sequence: bool = False,
) -> threading.Thread:
    """
    Background variant of `play_sequence` with `block=False`.

    Returns the started background thread for optional joining.
    """

    return play_sequence(
        paths,
        gap_seconds=gap_seconds,
        loop_sequence=loop_sequence,
        block=False,
    )


def beep(frequency_hz: int = 800, duration_ms: int = 200) -> None:
    """
    Emit a simple beep using the system speaker, if supported.

    Parameters
    ----------
    frequency_hz:
        Frequency in hertz. On many systems this must be between 37 and 32767.
    duration_ms:
        Duration in milliseconds.
    """

    _require_supported_platform()
    assert _winsound is not None  # for type checkers
    freq = max(37, min(int(frequency_hz), 32767))
    dur = max(1, int(duration_ms))
    try:
        _winsound.Beep(freq, dur)
    except Exception as exc:  # pragma: no cover - system specific
        raise PlaybackError(f"Beep failed: {exc}") from exc


def beep_pattern(pattern: Iterable[tuple[int, int, float]]) -> None:
    """
    Play a pattern of beeps.

    Parameters
    ----------
    pattern:
        Iterable of triples `(frequency_hz, duration_ms, gap_seconds)`. Each
        entry describes a single beep and the gap after it.
    """

    for frequency_hz, duration_ms, gap_seconds in pattern:
        beep(frequency_hz, duration_ms)
        if gap_seconds > 0:
            time.sleep(gap_seconds)


def play_system_sound(kind: str = "asterisk") -> None:
    """
    Play a standard Windows UI sound via `winsound.MessageBeep`.

    Parameters
    ----------
    kind:
        One of: ``"asterisk"``, ``"exclamation"``, ``"hand"``, ``"question"``,
        ``"ok"``. Any other value falls back to the default sound.
    """

    _require_supported_platform()
    assert _winsound is not None  # for type checkers

    mapping = {
        "asterisk": 0x00000040,    # MB_ICONASTERISK
        "exclamation": 0x00000030,  # MB_ICONEXCLAMATION
        "hand": 0x00000010,        # MB_ICONHAND
        "question": 0x00000020,    # MB_ICONQUESTION
        "ok": 0x00000000,          # MB_OK
    }
    type_flag = mapping.get(kind.lower(), 0xFFFFFFFF)  # -1: simple beep

    try:
        _winsound.MessageBeep(type_flag)
    except Exception as exc:  # pragma: no cover - system specific
        raise PlaybackError(f"System sound failed: {exc}") from exc


@contextmanager
def play_while(path: str | os.PathLike[str], *, loop: bool = False):
    """
    Context manager that plays audio while the context body executes.

    Example
    -------
    >>> with play_while("progress.wav", loop=True):
    ...     do_long_running_task()
    """

    worker = play_in_background(path, loop=loop)
    try:
        yield
    finally:
        stop_audio()
        # Give the worker a brief opportunity to exit cleanly.
        worker.join(timeout=1.0)
