"""
Builds the film's soundtrack from scratch.

Origin of the audio: **every sample is synthesised here by arithmetic**. There
are no recordings, no samples, no loops and no third-party material, so there is
nothing to licence and nothing to clear. The file this writes is the only audio
in the film.

What it makes, and why:

  * a slow ambient bed - two quiet sine drones a fifth apart with a very slow
    tremolo, plus filtered noise. It gives the film a floor without carrying any
    melody that would compete with reading;
  * a soft click wherever the cursor presses a control, so the two real
    interactions read as interactions;
  * a short airy whoosh at each scene change, pitched down as it passes, which
    supports the camera move rather than announcing it;
  * two understated emphasis tones - one when the method comparison resolves,
    one when the priority event is named.

Nothing here is an alarm, a riser to a drop, or a disaster sting. The film has
to work muted, so the sound is support, never information.

Run from the video/ directory:
    python scripts/v2/make_audio.py
"""
from __future__ import annotations

import struct
import wave
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[2] / "src" / "v2" / "assets" / "audio"
RATE = 48_000
FPS = 30
FRAMES = 1260
DURATION = FRAMES / FPS            # 42.0 s

# Scene starts, in frames, mirroring SCENES in src/v2/Film40.tsx.
SCENE_STARTS = [0, 120, 300, 480, 720, 990, 1140]

# The two real cursor presses in the film, in frames.
CLICKS = [120 + 110]               # Data trust expander

# The two understated emphasis moments.
EMPHASIS = [480 + 58, 480 + 124, 720 + 70]

t = np.linspace(0, DURATION, int(RATE * DURATION), endpoint=False)


def seconds(frame: int) -> float:
    return frame / FPS


def fade(signal: np.ndarray, attack: float, release: float) -> np.ndarray:
    """Applies a raised-cosine attack and release so nothing clicks on or off."""
    out = signal.copy()
    a = int(attack * RATE)
    r = int(release * RATE)
    if a > 0:
        out[:a] *= (1 - np.cos(np.linspace(0, np.pi, a))) / 2
    if r > 0:
        out[-r:] *= (1 + np.cos(np.linspace(0, np.pi, r))) / 2
    return out


def place(bed: np.ndarray, signal: np.ndarray, at_seconds: float) -> None:
    """Mixes a short signal into the bed at a time, clipped to the bed's end."""
    start = int(at_seconds * RATE)
    end = min(start + len(signal), len(bed))
    if start < len(bed):
        bed[start:end] += signal[: end - start]


def one_pole_lowpass(signal: np.ndarray, cutoff: float) -> np.ndarray:
    """A gentle one-pole filter - enough to take the edge off noise."""
    alpha = np.exp(-2 * np.pi * cutoff / RATE)
    out = np.empty_like(signal)
    carry = 0.0
    for i, value in enumerate(signal):
        carry = alpha * carry + (1 - alpha) * value
        out[i] = carry
    return out


# --- the ambient bed -------------------------------------------------------

def ambient() -> np.ndarray:
    """Two quiet drones and a breath of filtered noise."""
    root = 55.0                                   # A1
    fifth = root * 1.5
    # A very slow tremolo keeps the bed from sounding like a held test tone.
    slow = 0.5 + 0.5 * np.sin(2 * np.pi * 0.045 * t)
    bed = (
        0.055 * np.sin(2 * np.pi * root * t) * (0.7 + 0.3 * slow)
        + 0.035 * np.sin(2 * np.pi * fifth * t) * (0.6 + 0.4 * (1 - slow))
        + 0.020 * np.sin(2 * np.pi * root * 2 * t) * slow
    )
    rng = np.random.default_rng(11)
    air = one_pole_lowpass(rng.normal(0, 1, len(t)), 900.0)
    air *= 0.018 / (np.max(np.abs(air)) or 1)
    bed += air
    # The film opens from darkness and resolves on the montage, so the bed
    # follows that shape rather than sitting flat.
    shape = np.interp(t, [0, 2.0, DURATION - 4.0, DURATION - 0.6, DURATION],
                      [0.0, 1.0, 1.0, 0.9, 0.0])
    return bed * shape


# --- one-shot elements -----------------------------------------------------

def click() -> np.ndarray:
    """A short, soft interface click. Deliberately dull - no snap."""
    length = int(0.055 * RATE)
    local = np.arange(length) / RATE
    body = (
        0.5 * np.sin(2 * np.pi * 1850 * local)
        + 0.3 * np.sin(2 * np.pi * 2700 * local)
    ) * np.exp(-local * 95)
    return fade(body * 0.10, 0.002, 0.03)


def whoosh(duration: float = 0.85) -> np.ndarray:
    """Filtered noise that sweeps downward - air moving past the camera."""
    length = int(duration * RATE)
    local = np.arange(length) / RATE
    rng = np.random.default_rng(int(duration * 1000))
    noise = one_pole_lowpass(rng.normal(0, 1, length), 1400.0)
    # A swell that peaks a third of the way through, then falls away.
    envelope = np.exp(-((local - duration * 0.34) ** 2) / (2 * (duration * 0.22) ** 2))
    sweep = np.sin(2 * np.pi * np.cumsum(np.linspace(420, 150, length)) / RATE)
    body = (noise * 0.75 + sweep * 0.25) * envelope
    body *= 0.085 / (np.max(np.abs(body)) or 1)
    return fade(body, 0.05, 0.3)


def emphasis(pitch: float = 392.0) -> np.ndarray:
    """A single soft tone with a long tail. Understated, never an alarm."""
    length = int(1.6 * RATE)
    local = np.arange(length) / RATE
    body = (
        0.6 * np.sin(2 * np.pi * pitch * local)
        + 0.25 * np.sin(2 * np.pi * pitch * 2 * local)
        + 0.12 * np.sin(2 * np.pi * pitch * 3 * local)
    ) * np.exp(-local * 2.6)
    return fade(body * 0.075, 0.01, 0.6)


# --- assembly ---------------------------------------------------------------

def build() -> np.ndarray:
    bed = ambient()

    for start in SCENE_STARTS[1:]:
        # The whoosh starts slightly before the cut so the sound leads the move.
        place(bed, whoosh(), max(0.0, seconds(start) - 0.28))

    for frame in CLICKS:
        place(bed, click(), seconds(frame))

    for i, frame in enumerate(EMPHASIS):
        place(bed, emphasis(392.0 if i % 2 == 0 else 294.0), seconds(frame))

    # Headroom: the film is background-quiet by design, and LinkedIn autoplays
    # muted, so a loud mix would only ever be an unpleasant surprise.
    peak = float(np.max(np.abs(bed)))
    if peak > 0:
        bed = bed * (10 ** (-14 / 20) / peak)
    return np.clip(bed, -1.0, 1.0)


def write_wav(mono: np.ndarray, path: Path) -> None:
    """Writes 16-bit stereo, the same signal in both channels."""
    samples = (mono * 32767).astype(np.int16)
    stereo = np.repeat(samples[:, None], 2, axis=1).ravel()
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(struct.pack(f"<{len(stereo)}h", *stereo))


if __name__ == "__main__":
    mix = build()
    target = OUT / "soundtrack.wav"
    write_wav(mix, target)
    peak_db = 20 * np.log10(max(float(np.max(np.abs(mix))), 1e-9))
    rms_db = 20 * np.log10(max(float(np.sqrt(np.mean(mix ** 2))), 1e-9))
    print(f"{target}")
    print(f"  {len(mix) / RATE:.2f} s  {RATE} Hz  stereo")
    print(f"  peak {peak_db:.1f} dBFS   rms {rms_db:.1f} dBFS")
    print(f"  {len(SCENE_STARTS) - 1} transitions, {len(CLICKS)} click(s), "
          f"{len(EMPHASIS)} emphasis tones")
    print("  origin: synthesised here; no recordings, samples or third-party audio")
