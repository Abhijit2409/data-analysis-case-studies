"""Step 1 - Download the public 3-1-1 extract and dataset metadata.

Pulls a buffered UTC window around calendar 2025 so the Vancouver-local 2025
filter can be applied locally in step 2 (no reliance on how the API interprets
time zones in its WHERE clause). The raw file is saved untouched.
"""
import json
import pathlib
import datetime as dt
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
BASE = "https://opendata.vancouver.ca/api/explore/v2.1/catalog/datasets/3-1-1-service-requests"

# Buffered window: 2024-12-31 00:00 UTC to 2026-01-02 00:00 UTC.
WHERE = ('service_request_open_timestamp >= "2024-12-31T00:00:00+00:00" and '
         'service_request_open_timestamp < "2026-01-02T00:00:00+00:00"')
PARAMS = {"where": WHERE, "timezone": "UTC", "delimiter": ",", "use_labels": "false"}

extracted_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)

meta = requests.get(BASE, timeout=60)
meta.raise_for_status()
(RAW / "dataset_metadata.json").write_text(json.dumps(meta.json(), indent=2), encoding="utf-8")

with requests.get(f"{BASE}/exports/csv", params=PARAMS, stream=True, timeout=600) as r:
    r.raise_for_status()
    out = RAW / "311_requests_raw_window.csv"
    with open(out, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
    export_url = r.url

log = {
    "extracted_at_utc": extracted_at.isoformat(),
    "dataset_page": "https://opendata.vancouver.ca/explore/dataset/3-1-1-service-requests/",
    "export_url": export_url,
    "api_where_clause": WHERE,
    "api_timezone_param": "UTC",
    "note": "Buffered UTC window; the 2025 cohort is filtered locally on the America/Vancouver opening date.",
    "dataset_modified": meta.json().get("metas", {}).get("default", {}).get("modified"),
    "dataset_records_count_all_years": meta.json().get("metas", {}).get("default", {}).get("records_count"),
}
(RAW / "extraction_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
print(json.dumps(log, indent=2))
print("bytes:", out.stat().st_size)
