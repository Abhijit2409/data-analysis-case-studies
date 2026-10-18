"""
Checks the rendered demo film, frame by frame.

This is the companion to verify_demo_claims.py. That one checks the data and the
source; this one checks what actually came out of the renderer, because some
defects only exist in pixels.

It includes a label-collision check that the earlier verification did not have.
Measuring text positions from the source would only prove the intent; measuring
ink in the rendered frame proves what a viewer sees. Adjacent category labels
are required to keep a clear horizontal gap in every frame of both bar scenes,
during the morph as well as at rest.

Run from the video/ directory:
    python scripts/demo90/verify_render.py [path/to/film.mp4]
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

VIDEO = Path(__file__).resolve().parents[2]
DEFAULT = VIDEO / "out" / "demo90" / "wind-underperformance-demo90.mp4"
FFMPEG = next(VIDEO.glob("node_modules/@remotion/compositor-*/ffmpeg.exe"), None) or Path("ffmpeg")

# The band just under the baseline where category labels are drawn. The scan
# starts at the plot's left edge so the y-axis tick in the gutter, which shares
# this band, is not mistaken for a category label.
LABEL_BAND = (860, 910)
PLOT_LEFT = 230
# Scenes that draw category labels, as frame ranges.
BAR_SCENES = [("method comparison", 1470, 1890), ("detection benchmark", 1890, 2190)]
# Adjacent labels must keep at least this much clear space between them.
MIN_LABEL_GAP = 40
# Word spaces inside one label are narrower than this, so fragments closer than
# this are treated as one label rather than as two that have collided.
WORD_GAP = 30
# A real category label is at least this wide. Narrower ink is a stray
# antialiased fragment of a label still fading in, not a label of its own, and
# measuring gaps against it would report collisions that do not exist.
MIN_LABEL_WIDTH = 25

results: list[tuple[str, bool, str]] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    results.append((label, bool(ok), detail))


def decode(path: Path, into: Path) -> list[Path]:
    subprocess.run(
        [str(FFMPEG), "-nostdin", "-v", "error", "-i", str(path),
         "-y", str(into / "f_%05d.png")],
        check=True,
    )
    return sorted(into.glob("f_*.png"))


def label_runs(grey: np.ndarray) -> list[tuple[int, int]]:
    """Groups ink in the label band into labels, merging word spaces."""
    band = grey[LABEL_BAND[0]:LABEL_BAND[1], PLOT_LEFT:]
    columns = (band > 42).any(axis=0)
    runs: list[tuple[int, int]] = []
    start = None
    for x, on in enumerate(columns):
        if on and start is None:
            start = x
        elif not on and start is not None:
            runs.append((start + PLOT_LEFT, x - 1 + PLOT_LEFT))
            start = None
    if start is not None:
        runs.append((start + PLOT_LEFT, len(columns) - 1 + PLOT_LEFT))

    merged: list[tuple[int, int]] = []
    for run in runs:
        if merged and run[0] - merged[-1][1] - 1 <= WORD_GAP:
            merged[-1] = (merged[-1][0], run[1])
        else:
            merged.append(run)
    return [run for run in merged if run[1] - run[0] + 1 >= MIN_LABEL_WIDTH]


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    if not source.exists():
        print(f"no such file: {source}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp:
        frames = decode(source, Path(tmp))

        # Frames are processed one at a time. Holding 2,670 full-resolution
        # frames in memory at once is about 11 GB and simply fails.
        ink: list[float] = []
        sig: list[int] = []
        edge: list[float] = []
        clipped: list[int] = []
        tightest = {name: (None, None) for name, _, _ in BAR_SCENES}
        settled: dict[str, tuple[int, list[int], list[int]]] = {}
        SETTLED_AT = {"method A settled": 1620, "method B settled": 1820}
        width = height = 0

        for index, path in enumerate(frames):
            grey = np.asarray(Image.open(path).convert("L")).astype(np.int16)
            if index == 0:
                height, width = grey.shape
            ink.append(float((grey > 55).mean()))
            sig.append(hash((grey > 40).astype(np.uint8).tobytes()))
            edge.append(float(np.abs(np.diff(grey.astype(np.float32), axis=1)).mean()))

            ys, xs = np.nonzero(grey > 90)
            if len(xs) and (xs.min() <= 0 or xs.max() >= width - 1
                            or ys.min() <= 0 or ys.max() >= height - 1):
                clipped.append(index)

            for name, begin, finish in BAR_SCENES:
                if begin <= index < finish:
                    runs = label_runs(grey)
                    if len(runs) >= 2:
                        gaps = [runs[j + 1][0] - runs[j][1] - 1 for j in range(len(runs) - 1)]
                        smallest = min(gaps)
                        best = tightest[name][0]
                        if best is None or smallest < best:
                            tightest[name] = (smallest, (index, len(runs), gaps))
            for label, at in SETTLED_AT.items():
                if index == at:
                    runs = label_runs(grey)
                    settled[label] = (
                        len(runs),
                        [b - a + 1 for a, b in runs],
                        [runs[j + 1][0] - runs[j][1] - 1 for j in range(len(runs) - 1)],
                    )

        check(f"{len(frames)} frames at 1920x1080",
              len(frames) == 2670 and (width, height) == (1920, 1080),
              f"{len(frames)} frames, {width}x{height}")

        # --- label collisions, every frame of every bar scene ---------------
        for name, _, _ in BAR_SCENES:
            smallest, offender = tightest[name]
            if smallest is None:
                check(f"{name}: labels measured", False, "no labels found in the band")
                continue
            check(f"{name}: adjacent labels keep a clear gap",
                  smallest >= MIN_LABEL_GAP,
                  f"tightest {smallest}px at frame {offender[0]} "
                  f"({offender[0] / 30:.1f}s), {offender[1]} labels, gaps {offender[2]}")

        for label, (count, widths, gaps) in settled.items():
            check(f"{label}: four separate turbine labels",
                  count == 4 and (not gaps or min(gaps) >= MIN_LABEL_GAP),
                  f"{count} labels, widths {widths}, gaps {gaps}")

        # --- the frame checks ----------------------------------------------
        blank = [i for i, v in enumerate(ink) if v < 0.0005]
        check("no blank frame", not blank, f"{blank[:8]}")

        still, start_run = [], 0
        for i in range(1, len(frames) + 1):
            if i == len(frames) or sig[i] != sig[start_run]:
                if i - start_run >= 60:
                    still.append((start_run, i - 1, round((i - start_run) / 30, 1)))
                start_run = i
        check("no frozen stretch of 2s or more", not still, f"{still}")

        edges = np.array(edge)
        collapsed = [i for i in range(1, len(edges) - 1)
                     if edges[i] < 0.70 * min(edges[i - 1], edges[i + 1])
                     and min(edges[i - 1], edges[i + 1]) > 0.5]
        check("no frame renders before its content is ready", not collapsed, f"{collapsed[:8]}")
        check("nothing touches the frame edge", not clipped, f"{clipped[:8]}")
        check("first frame carries data marks", ink[0] > 0.0008, f"{ink[0]:.3%}")

    width_col = max(len(label) for label, _, _ in results) + 2
    for label, ok, detail in results:
        print(f"  [{'OK  ' if ok else 'FAIL'}] {label:<{width_col}} {detail}")
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} render checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
