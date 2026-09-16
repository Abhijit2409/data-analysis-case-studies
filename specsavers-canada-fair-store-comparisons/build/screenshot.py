"""Capture headless Microsoft Edge screenshots of a local HTML page (used for the 'before' evidence set).
Rendered-page tests and 'after' screenshots use the DevTools-protocol tools in tests/cdp.js.

Usage:
  python build/screenshot.py <html-path> <out.png> [width] [height] [hash]

The optional hash (e.g. "page=p3&store=SYN-014&role=ROL") is appended to the file URL; the dashboard reads it
to restore state. Requires Microsoft Edge (Chromium) at the default Windows install path, or set EDGE_PATH.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

EDGE = os.environ.get("EDGE_PATH", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def _profile():
    # A fresh profile per call: a shared profile makes a second Edge call hand off to the first and exit early.
    return tempfile.mkdtemp(prefix="edge-headless-casestudy-")


def capture(html, out, width=1440, height=1100, hash_=""):
    url = Path(html).resolve().as_uri() + (("#" + hash_) if hash_ else "")
    out = str(Path(out).resolve())
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    if os.path.exists(out):
        os.remove(out)
    prof = _profile()
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={prof}",
           f"--window-size={width},{height}", "--virtual-time-budget=6000", f"--screenshot={out}", url]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        for _ in range(60):
            if os.path.exists(out) and os.path.getsize(out) > 0:
                return out
            time.sleep(0.5)
        raise RuntimeError("Screenshot not written: " + out)
    finally:
        for _ in range(20):  # temporary profiles are 10-120 MB; always remove them
            shutil.rmtree(prof, ignore_errors=True)
            if not os.path.exists(prof):
                break
            time.sleep(0.5)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    print(capture(a[0], a[1], int(a[2]) if len(a) > 2 else 1440, int(a[3]) if len(a) > 3 else 1100, a[4] if len(a) > 4 else ""))
