"""Step 2 - Profile the raw extract and build the 2025 local-date cohort.

Prints a feasibility profile and saves the cohort (address/coordinates removed,
presence flags kept) for the analysis step.
"""
import json
import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "311_requests_raw_window.csv"
PROC = ROOT / "data" / "processed"
TZ = "America/Vancouver"
pd.set_option("display.width", 250, "display.max_rows", 500, "display.max_colwidth", 90)

raw = pd.read_csv(RAW, dtype=str, keep_default_na=False)
print("RAW WINDOW ROWS:", len(raw))
print("COLUMNS:", list(raw.columns))
print("\nSAMPLE RAW VALUES")
for c in ["service_request_open_timestamp", "service_request_close_date", "last_modified_timestamp"]:
    print(c, raw[c].head(3).tolist(), "| distinct lengths:", raw[c].str.len().value_counts().to_dict())

df = raw.copy()
blank = lambda s: s.str.strip().eq("")
df["open_utc"] = pd.to_datetime(df["service_request_open_timestamp"], utc=True, errors="coerce")
df["open_local"] = df["open_utc"].dt.tz_convert(TZ)
df["open_date_local"] = df["open_local"].dt.tz_localize(None).dt.normalize()
df["close_date"] = pd.to_datetime(df["service_request_close_date"], errors="coerce", format="%Y-%m-%d")
df["modified_utc"] = pd.to_datetime(df["last_modified_timestamp"], utc=True, errors="coerce")
print("\nUNPARSEABLE open ts:", df["open_utc"].isna().sum(),
      "| unparseable non-blank close:", (df["close_date"].isna() & ~blank(df["service_request_close_date"])).sum())

coh = df[df["open_date_local"].dt.year == 2025].copy()
print("\n2025 LOCAL-DATE COHORT ROWS:", len(coh))
print("Rows in window whose UTC year is 2025 (for comparison):", (df["open_utc"].dt.year == 2025).sum())
print("Rows whose local date is 2025 but UTC date is 2026:", ((coh["open_utc"].dt.year == 2026)).sum())

print("\nMISSING / BLANK RATE (2025 cohort)")
for c in raw.columns:
    n = blank(coh[c]).sum()
    print(f"  {c:32s} {n:8d}  {n/len(coh):6.2%}")

print("\nOPEN HOUR DISTRIBUTION  UTC vs LOCAL (share of rows)")
h = pd.DataFrame({"utc": coh["open_utc"].dt.hour.value_counts(normalize=True).sort_index(),
                  "local": coh["open_local"].dt.hour.value_counts(normalize=True).sort_index()})
print((h * 100).round(1).T.to_string())

print("\nMONTH COVERAGE (local open month)")
print(coh["open_date_local"].dt.month.value_counts().sort_index().to_string())
print("Distinct local open dates:", coh["open_date_local"].nunique())

print("\nSTATUS\n", coh["status"].value_counts(dropna=False).to_string())
print("\nCLOSURE REASON\n", coh["closure_reason"].replace("", "<blank>").value_counts().to_string())
print("\nSTATUS x CLOSURE REASON")
print(pd.crosstab(coh["closure_reason"].replace("", "<blank>"), coh["status"]).to_string())
print("\nSTATUS x CLOSE DATE PRESENT")
print(pd.crosstab(coh["status"], coh["close_date"].notna()).to_string())

print("\nCHANNEL\n", coh["channel"].replace("", "<blank>").value_counts().to_string())
print("\nLOCAL AREA\n", coh["local_area"].replace("", "<blank>").value_counts().to_string())
print("\nDEPARTMENTS:", coh["department"].nunique())
print(coh["department"].value_counts().to_string())
print("\nREQUEST TYPES:", coh["service_request_type"].nunique())

# Close date vs local open date
closed = coh[coh["close_date"].notna()].copy()
closed["days_local"] = (closed["close_date"] - closed["open_date_local"]).dt.days
closed["days_utcdate"] = (closed["close_date"] - closed["open_utc"].dt.tz_localize(None).dt.normalize()).dt.days
print("\nDAYS TO CLOSE (local open date basis) - negative / zero / positive:",
      (closed["days_local"] < 0).sum(), (closed["days_local"] == 0).sum(), (closed["days_local"] > 0).sum())
print("DAYS TO CLOSE (UTC open date basis)   - negative / zero / positive:",
      (closed["days_utcdate"] < 0).sum(), (closed["days_utcdate"] == 0).sum(), (closed["days_utcdate"] > 0).sum())
print("Negative (local) value counts:", closed.loc[closed["days_local"] < 0, "days_local"].value_counts().sort_index().to_dict())
neg = closed[closed["days_local"] < 0]
print("Negative local by local open hour:", neg["open_local"].dt.hour.value_counts().sort_index().to_dict())
print("Negative local by closure reason:", neg["closure_reason"].value_counts().to_dict())

# Which calendar is the close date on? Compare to last-modified date for instant auto-closures.
auto = closed[closed["closure_reason"].eq("Closed automatically and sent to service group")]
mod_local = auto["modified_utc"].dt.tz_convert(TZ).dt.tz_localize(None).dt.normalize()
mod_utc = auto["modified_utc"].dt.tz_localize(None).dt.normalize()
print("\nAUTO-CLOSED rows:", len(auto),
      "| close_date == local modified date:", (auto["close_date"] == mod_local).mean().round(4),
      "| == UTC modified date:", (auto["close_date"] == mod_utc).mean().round(4))
ev = auto[auto["open_local"].dt.hour >= 17]
print("  evening (local >=17h) auto-closed:", len(ev),
      "| close==local open date:", (ev["close_date"] == ev["open_date_local"]).mean().round(4),
      "| close==UTC open date:", (ev["close_date"] == ev["open_utc"].dt.tz_localize(None).dt.normalize()).mean().round(4))
allev = closed[closed["open_local"].dt.hour >= 17]
print("  all evening closed rows: close==local open date share", (allev["close_date"] == allev["open_date_local"]).mean().round(4),
      "| close == local date + 1 share", (allev["days_local"] == 1).mean().round(4))

print("\nLAST MODIFIED before OPEN:", (coh["modified_utc"] < coh["open_utc"]).sum())
print("CLOSE DATE after extraction date:", (coh["close_date"] > pd.Timestamp("2026-09-11")).sum())
print("Max close date:", coh["close_date"].max(), "| Max open local:", coh["open_local"].max())

# Identifier and duplicate-looking rows
keycols = [c for c in raw.columns]
print("\nEXACT DUPLICATE ROWS (all published columns):", coh.duplicated(subset=keycols, keep=False).sum(),
      "rows in", coh[coh.duplicated(subset=keycols, keep=False)].groupby(keycols).ngroups, "groups")
print("Candidate ID-like columns: none published" if not any("id" in c.lower() for c in raw.columns) else "ID col present")

zz = coh["department"].str.upper().str.startswith("ZZ") | coh["service_request_type"].str.upper().str.startswith("ZZ")
print("\nZZ OLD labels:", zz.sum())
print(coh.loc[zz, ["department", "service_request_type"]].value_counts().head(30).to_string())

print("\nMISSING local area:", blank(coh["local_area"]).sum(), "| missing lat:", blank(coh["latitude"]).sum(),
      "| missing address:", blank(coh["address"]).sum())

# Full request type list for manual review
rt = coh.groupby(["department", "service_request_type"]).size().rename("n").reset_index().sort_values("n", ascending=False)
rt.to_csv(PROC / "request_type_inventory.csv", index=False)

# Save cohort without address/coordinates (privacy); keep presence flags.
out = coh.drop(columns=["address", "latitude", "longitude", "geom"]).copy()
out["has_address"] = ~blank(coh["address"])
out["has_coordinates"] = ~blank(coh["latitude"])
out.to_parquet(PROC / "cohort_2025.parquet", index=False)
print("\nSaved cohort:", len(out))
