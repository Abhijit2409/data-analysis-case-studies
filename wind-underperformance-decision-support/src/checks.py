"""
A small validation recorder.

The point: a script must not be able to say a check passed unless the check
actually ran. Every call to `require` or `record` is written to a table, with its
result, so the claim and the evidence stay together.

Two levels:
    require(...)  a check that must pass. Failure stops the script.
    record(...)   a check whose result is reported either way, used where a
                  failure changes the conclusion rather than invalidating the run.
"""

from pathlib import Path

import pandas as pd


class CheckRecorder:
    """Collects check results and writes them to a CSV."""

    def __init__(self, stage):
        self.stage = stage
        self.results = []

    def record(self, name, passed, detail=""):
        """Run-of-the-mill check. Reports the result and carries on."""
        passed = bool(passed)
        self.results.append({
            "stage": self.stage,
            "check": name,
            "result": "PASS" if passed else "FAIL",
            "detail": str(detail),
        })
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))
        return passed

    def require(self, name, passed, detail=""):
        """A check the rest of the work depends on. Stops the script if it fails."""
        if not self.record(name, passed, detail):
            raise AssertionError(f"Required check failed: {name}. {detail}")
        return True

    @property
    def all_passed(self):
        return all(r["result"] == "PASS" for r in self.results)

    def failures(self):
        return [r["check"] for r in self.results if r["result"] == "FAIL"]

    def to_frame(self):
        return pd.DataFrame(self.results)

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        frame = self.to_frame()
        frame.to_csv(path, index=False)
        passed = (frame["result"] == "PASS").sum()
        print(f"\n  {passed}/{len(frame)} checks passed -> {path.name}")
        return frame


# Checksums recorded during the Phase 1 audit. Used to prove the raw files have
# not been edited since they were audited.
RAW_FILE_CHECKSUMS = {
    "la_haute_borne.zip":
        "be5ea66a3355286e491f5618250dc83e85252a8cb337748d7ba19edc50df6138",
}

EXPECTED_RAW_SCADA_ROWS = 420_480
RATED_POWER_KW = 2050
