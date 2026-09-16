"""Build dashboard-mockup.html from the template, the presentation logic module and the synthetic analysis JSON (Phase 13)."""
import json
import os
import sys

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
with open(os.path.join(BASE, "data", "analysis_summary.json"), encoding="utf-8") as fh:
    data = json.load(fh)
with open(os.path.join(BASE, "build", "mockup_template.html"), encoding="utf-8") as fh:
    tpl = fh.read()
with open(os.path.join(BASE, "build", "dashboard_logic.js"), encoding="utf-8") as fh:
    logic = fh.read()

for placeholder in ("/*__DATA__*/null", "/*__LOGIC__*/"):
    if tpl.count(placeholder) != 1:
        sys.exit(f"Template must contain exactly one {placeholder}")
payload = json.dumps(data, separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
out = tpl.replace("/*__LOGIC__*/", logic.replace("</script", "<\\/script")).replace("/*__DATA__*/null", payload)
path = os.path.join(BASE, "dashboard-mockup.html")
with open(path, "w", encoding="utf-8") as fh:
    fh.write(out)
print("Wrote", os.path.abspath(path), f"({len(out) / 1024:.0f} KB)")
