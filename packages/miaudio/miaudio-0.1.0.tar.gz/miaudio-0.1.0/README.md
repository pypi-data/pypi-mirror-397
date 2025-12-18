miaudio
=======

`miaudio` is a small, focused audio utility library designed for **pure Python on Windows**.
It aims to provide professional‑grade ergonomics while staying 100% dependency‑free.

It provides, among other things:

- **Simple audio playback** for WAV files using the Python standard library only.
- **Background playback** so your program can continue doing work while audio plays.
- **Scheduled playback** at a specific absolute time or after a delay.
- **Playlists and sequences** of files, with optional gaps and looping.
- **Scoped playback** with a context manager (`with play_while(...): ...`).
- **Timeout‑limited playback** (`play_for`).
- **Beep utilities** (`beep`, `beep_pattern`) and **system UI sounds**.
- **Introspectable state** (`is_playing`) so you can build richer UIs.
- **Explicit stop control** for stopping the currently playing sound.
- **Defensive error handling** with clear, documented exception types.

> **Important**
>
> `miaudio` is intentionally implemented with **no third‑party dependencies** and no
> external tools. It uses only the Python standard library and is currently
> supported on **Windows** via the built‑in `winsound` module. On unsupported
> platforms, the public APIs will raise `PlatformNotSupportedError`.

Quick start
-----------

```python
from miaudio import play_audio, play_in_background, stop_audio

# Play a WAV file and block until it finishes
play_audio("C:/sounds/notification.wav")

# Play in the background (non‑blocking)
thread = play_in_background("C:/sounds/loop.wav", loop=False)

# Stop whatever is currently playing (if any)
stop_audio()
```

Installation
------------

Once published on PyPI:

```bash
pip install miaudio
```

Until then, you can install from source:

```bash
pip install .
```

Core concepts
-------------

- **Windows‑only implementation**: Playback is implemented using `winsound`.
  On non‑Windows platforms, a `PlatformNotSupportedError` is raised.
- **WAV files only**: `winsound` supports uncompressed WAV files. Other
  formats (MP3, FLAC, etc.) are rejected with `UnsupportedFormatError`.
- **Thread‑safe control**: Background playback and scheduling use
  `threading.Thread` and `threading.Event`, with a small synchronization
  layer to ensure that stop/schedule operations interact safely.
- **Fire‑and‑forget vs. controlled playback**:
  `play_once`, `play_audio`, and `play_in_background` cover the common cases;
  additional helpers (`play_for`, `play_sequence`, `play_while`) handle
  longer‑running, structured use cases.

Public API (overview)
---------------------

The main functions and utilities exposed by `miaudio` are:

- **Basic playback**
  - **`play_audio(path: str, *, loop: bool = False, block: bool = True) -> None`**
  - **`play_once(path: str) -> None`**
  - **`play_for(path: str, seconds: float) -> None`**
  - **`stop_audio() -> None`**

- **Background & scheduling**
  - **`play_in_background(path: str, *, loop: bool = False) -> threading.Thread`**
  - **`play_sequence(paths, *, gap_seconds: float = 0.0, loop_sequence: bool = False, block: bool = True)`**
  - **`play_sequence_in_background(paths, *, gap_seconds: float = 0.0, loop_sequence: bool = False)`**
  - **`play_after_delay(path: str, delay_seconds: float) -> threading.Thread`**
  - **`play_at_time(path: str, when: datetime.datetime) -> threading.Thread`**
  - **`play_while(path: str, *, loop: bool = False)`** (context manager)

- **Status & platform**
  - **`is_supported_platform() -> bool`**
  - **`is_playing() -> bool`**

- **Beep & system sounds**
  - **`beep(frequency_hz: int = 800, duration_ms: int = 200) -> None`**
  - **`beep_pattern(pattern: Iterable[tuple[int, int, float]]) -> None`**
  - **`play_system_sound(kind: str = "asterisk") -> None`**

- **Exceptions**
  - **`miaudio.PlatformNotSupportedError`**
  - **`miaudio.AudioFileError`**
  - **`miaudio.AudioFileNotFoundError`**
  - **`miaudio.UnsupportedFormatError`**
  - **`miaudio.PlaybackError`**

Threading model & stopping playback
-----------------------------------

Playback is coordinated via a module‑level lock and an internal stop event:

- At most one background playback thread is considered "active" at a time for
  higher‑level helpers like `play_in_background` and `play_sequence`.
- Calling `stop_audio()`:
  - Clears any `winsound` playback by issuing `winsound.PlaySound(None, 0)`.
  - Signals the internal event so cooperative background threads can stop.

While `winsound` itself is quite simple, `miaudio` wraps it to make:

- Parameter validation explicit and predictable.
- Exceptions strongly typed and well‑documented.
- Background, playlist, and scheduled playback easier to use reliably.

Usage examples
--------------

### Basic blocking playback

```python
from miaudio import play_audio

play_audio("C:/sounds/notification.wav")
```

### Non‑blocking background playback

```python
from miaudio import play_in_background, stop_audio
import time

thread = play_in_background("C:/sounds/music.wav", loop=True)

time.sleep(10)  # do other work, or just wait
stop_audio()    # stops the loop
thread.join()   # wait for the background thread to exit
```

### Play only for a limited time

```python
from miaudio import play_for

# Play for at most 3.5 seconds, then stop automatically
play_for("C:/sounds/long.wav", seconds=3.5)
```

### Playlist / sequence playback

```python
from miaudio import play_sequence

tracks = [
    "C:/sounds/intro.wav",
    "C:/sounds/loop.wav",
    "C:/sounds/outro.wav",
]

# Play all three, 0.25 seconds apart, then stop
play_sequence(tracks, gap_seconds=0.25, loop_sequence=False, block=True)
```

### Playlist in the background, looping

```python
from miaudio import play_sequence_in_background, stop_audio
import time

tracks = [
    "C:/sounds/a.wav",
    "C:/sounds/b.wav",
]

thread = play_sequence_in_background(tracks, gap_seconds=0.1, loop_sequence=True)
time.sleep(15)
stop_audio()
thread.join()
```

### Scoped playback with a context manager

```python
from miaudio import play_while

with play_while("C:/sounds/progress.wav", loop=True):
    # Do some long running work here
    do_expensive_work()
# Audio is now stopped, even if an exception was raised.
```

### Simple beeps and patterns

```python
from miaudio import beep, beep_pattern

beep()                      # quick default beep
beep(440, 500)              # A4, 500 ms

pattern = [
    (880, 150, 0.05),
    (660, 150, 0.05),
    (440, 250, 0.10),
]
beep_pattern(pattern)
```

### Play a Windows system sound

```python
from miaudio import play_system_sound

play_system_sound("exclamation")
play_system_sound("hand")
play_system_sound("question")
```

### Schedule a sound five seconds from now

```python
from miaudio import play_after_delay

play_after_delay("C:/sounds/alert.wav", delay_seconds=5.0)
```

### Schedule a sound at a specific time

```python
from datetime import datetime, timedelta
from miaudio import play_at_time

when = datetime.now() + timedelta(minutes=1)
play_at_time("C:/sounds/alert.wav", when=when)
```

Design goals
------------

- **Zero non‑stdlib dependencies**: Everything is implemented using only the
  Python standard library (`winsound`, `threading`, `pathlib`, `datetime`, etc.).
- **Clear, explicit failures**: The library fails fast with clear exception
  types when used on unsupported platforms or with unsupported formats.
- **Simple, focused API**: A small surface area that covers common use cases
  (play once, loop, background, schedule, playlists, stop).
- **Predictable behavior under load**: Helper functions are thread‑safe, and
  long‑running operations either block the caller or clearly document that they
  use background threads.

Limitations
-----------

- Currently supports **only Windows** via `winsound`.
- Currently supports **only WAV** files.
- Volume control, balance, and advanced audio processing are intentionally
  out of scope for this minimal, dependency‑free implementation.

Versioning
----------

`miaudio` follows [Semantic Versioning](https://semver.org) as closely as is
practical for a small utility library:

- **MAJOR**: incompatible API changes
- **MINOR**: backwards‑compatible feature additions
- **PATCH**: backwards‑compatible bug fixes and documentation updates


