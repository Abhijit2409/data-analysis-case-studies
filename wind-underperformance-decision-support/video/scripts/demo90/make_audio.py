"""
Builds the demo film's soundtrack from scratch.

Origin of the audio: **every sample is synthesised here by arithmetic.** There
are no recordings, no samples, no loops and no third-party material, so there is
nothing to licence and nothing to clear. The file this writes is the only audio
in the film, and it can be rebuilt from this script at any time.

What it makes:

  * a slow ambient bed - two quiet drones a fifth apart, with filtered air;
  * a soft transition sound at each of the seven scene changes, placed slightly
    ahead of the cut so the sound leads the move;
  * a short mark where the data does something the viewer should notice: the
    method A leader, the method B leader, and the alert burden arriving;
  * a low settle under the closing title.

Nothing is an alarm or a riser to a drop. The film is built to be understood
with the sound off, so the sound only supports the motion.

Run from the video/ directory:
    python scripts/demo90/make_audio.py
"""
from __future__ import annotations

import json
import struct
import wave
from pathlib import Path

import numpy as np

VIDEO = Path(__file__).resolve().parents[2]
OUT = VIDEO / "src" / "demo90" / "assets" / "soundtrack.wav"
RATE = 48_000
FPS = 30

# Read the film's own timeline so the sound can never drift from the picture.
TIMELINE = (VIDEO / "src" / "demo90" / "timeline.ts").read_text(encoding="utf-8")


def read_number(name: str) -> int:
    """Pulls a single frame number out of the timeline module."""
    import re
    match = re.search(rf"{name}:\s*(\d+)", TIMELINE)
    if not match:
        raise KeyError(name)
    return int(match.group(1))


def read_pair(name: str) -> tuple[int, int]:
    import re
    match = re.search(rf"{name}:\s*\[(\d+),\s*(\d+)\]", TIMELINE)
    if not match:
        raise KeyError(name)
    return int(match.group(1)), int(match.group(2))


def read_scene(name: str) -> tuple[int, int]:
    """Scenes are written as {from, to}; copy windows as [in, out]."""
    import re
    match = re.search(rf"{name}:\s*\{{from:\s*(\d+),\s*to:\s*(\d+)\}}", TIMELINE)
    if not match:
        raise KeyError(name)
    return int(match.group(1)), int(match.group(2))


SCENE_STARTS = [read_scene(n)[0] for n in
                ("context", "dataTrust", "scope", "method", "model", "evidence", "decision")]
FILM_FRAMES = read_scene("decision")[1]
DURATION = FILM_FRAMES / FPS

# Moments the sound marks, read from the film's own copy timings.
METHOD_A = read_pair("methodALabel")[0]
METHOD_B = read_pair("methodBLabel")[0]
BURDEN = read_pair("burdenLabel")[0]
CLOSING = read_pair("closing")[0]

t = np.linspace(0, DURATION, int(RATE * DURATION), endpoint=False)


def fade(signal: np.ndarray, attack: float, release: float) -> np.ndarray:
    out = signal.copy()
    a, r = int(attack * RATE), int(release * RATE)
    if a > 0:
        out[:a] *= (1 - np.cos(np.linspace(0, np.pi, a))) / 2
    if r > 0:
        out[-r:] *= (1 + np.cos(np.linspace(0, np.pi, r))) / 2
    return out


def place(bed: np.ndarray, signal: np.ndarray, at_seconds: float) -> None:
    start = int(max(0.0, at_seconds) * RATE)
    end = min(start + len(signal), len(bed))
    if start < len(bed):
        bed[start:end] += signal[: end - start]


def lowpass(signal: np.ndarray, cutoff: float) -> np.ndarray:
    alpha = float(np.exp(-2 * np.pi * cutoff / RATE))
    out = np.empty_like(signal)
    carry = 0.0
    for i, value in enumerate(signal):
        carry = alpha * carry + (1 - alpha) * value
        out[i] = carry
    return out


def ambient() -> np.ndarray:
    root, fifth = 55.0, 82.5
    slow = 0.5 + 0.5 * np.sin(2 * np.pi * 0.035 * t)
    bed = (
        0.055 * np.sin(2 * np.pi * root * t) * (0.7 + 0.3 * slow)
        + 0.032 * np.sin(2 * np.pi * fifth * t) * (0.6 + 0.4 * (1 - slow))
        + 0.018 * np.sin(2 * np.pi * root * 2 * t) * slow
    )
    rng = np.random.default_rng(7)
    air = lowpass(rng.normal(0, 1, len(t)), 850.0)
    air *= 0.016 / (np.max(np.abs(air)) or 1)
    bed += air
    shape = np.interp(t, [0, 2.5, DURATION - 5.0, DURATION - 0.8, DURATION],
                      [0.0, 1.0, 1.0, 0.85, 0.0])
    return bed * shape


def transition(duration: float = 0.9) -> np.ndarray:
    """Filtered air moving past, sweeping down. One per scene change."""
    length = int(duration * RATE)
    local = np.arange(length) / RATE
    rng = np.random.default_rng(int(duration * 977))
    noise = lowpass(rng.normal(0, 1, length), 1300.0)
    envelope = np.exp(-((local - duration * 0.32) ** 2) / (2 * (duration * 0.21) ** 2))
    sweep = np.sin(2 * np.pi * np.cumsum(np.linspace(400, 140, length)) / RATE)
    body = (noise * 0.78 + sweep * 0.22) * envelope
    body *= 0.08 / (np.max(np.abs(body)) or 1)
    return fade(body, 0.05, 0.32)


def mark(pitch: float = 392.0, level: float = 0.07) -> np.ndarray:
    """A single soft tone with a long tail. Understated, never an alarm."""
    length = int(1.5 * RATE)
    local = np.arange(length) / RATE
    body = (
        0.6 * np.sin(2 * np.pi * pitch * local)
        + 0.24 * np.sin(2 * np.pi * pitch * 2 * local)
        + 0.10 * np.sin(2 * np.pi * pitch * 3 * local)
    ) * np.exp(-local * 2.4)
    return fade(body * level, 0.012, 0.55)


def settle() -> np.ndarray:
    """A low, slow arrival under the closing title."""
    length = int(3.2 * RATE)
    local = np.arange(length) / RATE
    body = (
        0.5 * np.sin(2 * np.pi * 110 * local)
        + 0.3 * np.sin(2 * np.pi * 165 * local)
    ) * np.exp(-local * 0.8)
    return fade(body * 0.065, 0.4, 1.6)


def build() -> np.ndarray:
    bed = ambient()
    for start in SCENE_STARTS:
        place(bed, transition(), start / FPS - 0.3)
    place(bed, mark(392.0), METHOD_A / FPS)
    place(bed, mark(330.0), METHOD_B / FPS)
    place(bed, mark(262.0, 0.075), BURDEN / FPS)
    place(bed, settle(), CLOSING / FPS - 0.5)

    peak = float(np.max(np.abs(bed)))
    if peak > 0:
        bed *= 10 ** (-14 / 20) / peak
    return np.clip(bed, -1.0, 1.0)


def write_wav(mono: np.ndarray, path: Path) -> None:
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
    write_wav(mix, OUT)
    print(f"{OUT}")
    print(f"  {len(mix) / RATE:.3f} s  {RATE} Hz  stereo "
          f"(film is {FILM_FRAMES} frames = {DURATION:.3f} s)")
    print(f"  peak {20 * np.log10(np.max(np.abs(mix))):.1f} dBFS   "
          f"rms {20 * np.log10(np.sqrt(np.mean(mix ** 2))):.1f} dBFS")
    print(f"  {len(SCENE_STARTS)} scene transitions, 3 data marks, 1 closing settle")
    print("  origin: synthesised here; no recordings, samples or third-party audio")
