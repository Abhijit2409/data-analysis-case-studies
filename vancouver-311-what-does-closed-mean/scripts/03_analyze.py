"""Step 3 - Reference analysis. Every number used in the report, charts and the
workbook reconciliation comes from this script's outputs (build/results.json and
build/tables/*.csv). Also writes the cleaned row-level file used by Power Query.
"""
import json
import math
import pathlib
import numpy as np
import pandas as pd
from config import (TZ, GROUPS, SHORT, MAPPING, ADMIN_RE, ADMIN_RULE_TEXT, CANDIDATES,
                    FOCUS_FAMILY, PCTS, MIN_N_FOR_PERCENTILES, G1, G2, G3, G4, G5, G6)

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAWF = ROOT / "data" / "raw" / "311_requests_raw_window.csv"
PROC = ROOT / "data" / "processed"
BUILD = ROOT / "build"
TAB = BUILD / "tables"
TAB.mkdir(parents=True, exist_ok=True)

log = json.loads((ROOT / "data" / "raw" / "extraction_log.json").read_text())
EXTRACTED_UTC = pd.Timestamp(log["extracted_at_utc"])
EXTRACT_LOCAL_DATE = EXTRACTED_UTC.tz_convert(TZ).tz_localize(None).normalize()
R = {"extraction": log, "extraction_local_date": str(EXTRACT_LOCAL_DATE.date())}

# ---------------------------------------------------------------- load and derive
raw = pd.read_csv(RAWF, dtype=str, keep_default_na=False)
blank = lambda s: s.str.strip().eq("")
raw["open_utc"] = pd.to_datetime(raw["service_request_open_timestamp"], utc=True)
raw["open_local"] = raw["open_utc"].dt.tz_convert(TZ)
raw["open_date_local"] = raw["open_local"].dt.tz_localize(None).dt.normalize()
utc_year = raw["open_utc"].dt.year
loc_year = raw["open_date_local"].dt.year
R["cohort_reconciliation"] = {
    "raw_window_rows": int(len(raw)),
    "utc_year_2025_rows": int((utc_year == 2025).sum()),
    "local_2025_but_utc_2026": int(((loc_year == 2025) & (utc_year == 2026)).sum()),
    "utc_2025_but_local_2024": int(((loc_year == 2024) & (utc_year == 2025)).sum()),
}
df = raw[loc_year == 2025].copy().reset_index(drop=True)
N = len(df)
R["cohort_reconciliation"]["local_2025_rows"] = N
cr = R["cohort_reconciliation"]
assert cr["utc_year_2025_rows"] + cr["local_2025_but_utc_2026"] - cr["utc_2025_but_local_2024"] == N

df["close_date"] = pd.to_datetime(df["service_request_close_date"], format="%Y-%m-%d", errors="coerce")
df["modified_utc"] = pd.to_datetime(df["last_modified_timestamp"], utc=True)
df["open_month"] = df["open_date_local"].dt.month
df["is_closed"] = df["status"].eq("Close")
df["outcome_group"] = df["closure_reason"].map(lambda r: MAPPING.get(r, (G6,))[0])
df["outcome_subgroup"] = df["closure_reason"].map(lambda r: MAPPING.get(r, (G6, "UNMAPPED"))[1])
unmapped = sorted(set(df["closure_reason"]) - set(MAPPING))
R["unmapped_closure_reasons"] = unmapped
df["admin_sounding"] = df["service_request_type"].str.contains(ADMIN_RE)
df["zz_old"] = df["department"].str.upper().str.startswith("ZZ") | df["service_request_type"].str.upper().str.startswith("ZZ")
df["has_local_area"] = ~blank(df["local_area"])
df["has_coordinates"] = ~blank(df["latitude"])
df["has_address"] = ~blank(df["address"])
dup_key = [c for c in ["department", "service_request_type", "status", "closure_reason",
                       "service_request_open_timestamp", "service_request_close_date",
                       "address", "local_area", "channel", "latitude", "longitude"]]
df["duplicate_looking"] = df.duplicated(subset=dup_key, keep=False)
df["days_to_close"] = (df["close_date"] - df["open_date_local"]).dt.days
df["duration_exclusion"] = np.select(
    [~df["is_closed"], df["close_date"].isna(), df["days_to_close"] < 0],
    ["Open at extraction (no close date)", "Closed but close date missing", "Close date before local open date"],
    default="")
df["duration_eligible"] = df["duration_exclusion"].eq("")
fam_dept, fam_types = CANDIDATES[FOCUS_FAMILY]
df["focus_family"] = df["department"].eq(fam_dept) & df["service_request_type"].isin(fam_types)
df["open_age_days"] = np.where(~df["is_closed"], (EXTRACT_LOCAL_DATE - df["open_date_local"]).dt.days, np.nan)

closed = df[df["is_closed"]]
opn = df[~df["is_closed"]]
NC = len(closed)
excl = df[~df["admin_sounding"]]
closed_x = excl[excl["is_closed"]]

def pct(a, b):
    return float(a) / float(b) if b else None

def nearest_rank(values, p):
    v = np.sort(np.asarray(values))
    if len(v) == 0:
        return None
    return int(v[max(int(math.ceil(p * len(v))) - 1, 0)])

def dist(series_counts, denom):
    return [{"value": k, "count": int(v), "share": pct(v, denom)} for k, v in series_counts.items()]

# ---------------------------------------------------------------- A. profile / quality
fields = [c for c in raw.columns if c not in ("open_utc", "open_local", "open_date_local")]
missing = []
for c in fields:
    n = int(blank(df[c]).sum())
    missing.append({"field": c, "missing": n, "share": pct(n, N)})
R["profile"] = {
    "rows": N, "fields": fields, "missing": missing,
    "status_values": dist(df["status"].value_counts(), N),
    "closure_reason_values": dist(df["closure_reason"].value_counts(), N),
    "n_departments": int(df["department"].nunique()),
    "n_request_types": int(df["service_request_type"].nunique()),
    "channels": dist(df["channel"].value_counts(), N),
    "n_local_areas_named": int(df.loc[df["has_local_area"], "local_area"].nunique()),
    "months": [{"month": int(m), "count": int(c)} for m, c in df["open_month"].value_counts().sort_index().items()],
    "distinct_open_dates": int(df["open_date_local"].nunique()),
    "stable_case_identifier": "None published. No field uniquely identifies a case.",
}
hours_local = df["open_local"].dt.hour.value_counts(normalize=True).sort_index()
hours_utc = df["open_utc"].dt.hour.value_counts(normalize=True).sort_index()
auto = closed[closed["closure_reason"].eq("Closed automatically and sent to service group")]
eve = auto[auto["open_local"].dt.hour >= 17]
R["date_behaviour"] = {
    "open_timestamp_format": "ISO 8601 with +00:00 offset (UTC), e.g. " + df["service_request_open_timestamp"].iloc[0],
    "close_date_format": "Date only (YYYY-MM-DD), no time or offset",
    "last_modified_format": "ISO 8601 with +00:00 offset (UTC)",
    "peak_local_hours_share_9_to_16": float(hours_local.loc[9:16].sum()),
    "share_opened_0_to_6_local": float(hours_local.loc[0:6].sum()),
    "share_opened_14_to_23_utc": float(hours_utc.loc[14:23].sum()),
    "evening_auto_closed_n": int(len(eve)),
    "evening_auto_closed_close_eq_local_open_date": float((eve["close_date"] == eve["open_date_local"]).mean()),
    "evening_auto_closed_close_eq_utc_open_date": float((eve["close_date"] == eve["open_utc"].dt.tz_localize(None).dt.normalize()).mean()),
    "timestamps_with_zero_seconds_share": float((df["service_request_open_timestamp"].str[17:19] == "00").mean()),
}
open_nonNA = opn[opn["closure_reason"].ne("N/A")]
R["quality"] = {
    "closed_without_close_date": int((df["is_closed"] & df["close_date"].isna()).sum()),
    "open_with_close_date": int((~df["is_closed"] & df["close_date"].notna()).sum()),
    "open_with_non_na_reason": int(len(open_nonNA)),
    "open_with_non_na_reason_by_reason": open_nonNA["closure_reason"].value_counts().to_dict(),
    "closed_with_na_reason": int((df["is_closed"] & df["closure_reason"].eq("N/A")).sum()),
    "open_na_reason": int((~df["is_closed"] & df["closure_reason"].eq("N/A")).sum()),
    "negative_days": int((df["days_to_close"] < 0).sum()),
    "negative_days_values": df.loc[df["days_to_close"] < 0, "days_to_close"].value_counts().to_dict(),
    "negative_days_reasons": df.loc[df["days_to_close"] < 0, "closure_reason"].value_counts().to_dict(),
    "negative_days_local_hours": df.loc[df["days_to_close"] < 0, "open_local"].dt.hour.value_counts().sort_index().to_dict(),
    "modified_before_open": int((df["modified_utc"] < df["open_utc"]).sum()),
    "close_after_extraction": int((df["close_date"] > EXTRACT_LOCAL_DATE).sum()),
    "max_close_date": str(df["close_date"].max().date()),
    "missing_local_area": int((~df["has_local_area"]).sum()),
    "missing_coordinates": int((~df["has_coordinates"]).sum()),
    "missing_address": int((~df["has_address"]).sum()),
    "zz_old_rows": int(df["zz_old"].sum()),
    "zz_old_types": df.loc[df["zz_old"], "service_request_type"].value_counts().to_dict(),
    "exact_duplicate_rows_all_columns": int(raw.loc[loc_year == 2025].duplicated(
        subset=[c for c in raw.columns if c not in ("open_utc", "open_local", "open_date_local")], keep=False).sum()),
    "duplicate_looking_rows": int(df["duplicate_looking"].sum()),
    "duplicate_looking_groups": int(df[df["duplicate_looking"]].groupby(dup_key).ngroups),
    "duplicate_looking_top_types": df[df["duplicate_looking"]]["service_request_type"].value_counts().head(5).to_dict(),
    "duplicate_looking_key": "All published fields identical except last-modified timestamp",
}
# local-area missingness by department (top by volume) - explains where location is blank
la = df.groupby("department").agg(records=("department", "size"), missing_area=("has_local_area", lambda s: int((~s).sum())))
la["share"] = la["missing_area"] / la["records"]
R["quality"]["missing_area_top_departments"] = (la.sort_values("missing_area", ascending=False).head(6)
    .reset_index().to_dict(orient="records"))

admin_types = (df[df["admin_sounding"]].groupby(["department", "service_request_type"]).size()
               .rename("records").reset_index().sort_values("records", ascending=False))
R["admin"] = {"rule": ADMIN_RULE_TEXT, "rows": int(df["admin_sounding"].sum()),
              "share": pct(df["admin_sounding"].sum(), N), "types": admin_types.to_dict(orient="records"),
              "false_positive_example": "Disposal Facility - Transfer Station Inquiry Case (not flagged: 'Transfer' names a facility)",
              "reviewed_not_flagged": ["Preventative Maintenance Program Case", "Hot Topic Case", "Employee Feedback Case"]}
admin_types.to_csv(TAB / "admin_sounding_types.csv", index=False)

# ---------------------------------------------------------------- B. demand
by_month = df.groupby("open_month").size()
by_dept = df["department"].value_counts()
by_type = df.groupby(["department", "service_request_type"]).size().sort_values(ascending=False)
by_channel = df["channel"].value_counts()
by_area = df["local_area"].replace("", "(Not recorded)").value_counts()
R["demand"] = {
    "total": N,
    "by_month": [{"month": int(m), "count": int(c)} for m, c in by_month.items()],
    "month_min": {"month": int(by_month.idxmin()), "count": int(by_month.min())},
    "month_max": {"month": int(by_month.idxmax()), "count": int(by_month.max())},
    "by_department_top10": [{"department": k, "count": int(v), "share": pct(v, N)} for k, v in by_dept.head(10).items()],
    "top_types": [{"department": d, "type": t, "count": int(v), "share": pct(v, N)} for (d, t), v in by_type.head(10).items()],
    "top5_types_share": pct(by_type.head(5).sum(), N), "top10_types_share": pct(by_type.head(10).sum(), N),
    "top5_types_count": int(by_type.head(5).sum()), "top10_types_count": int(by_type.head(10).sum()),
    "top5_depts_share": pct(by_dept.head(5).sum(), N), "top5_depts_count": int(by_dept.head(5).sum()),
    "by_channel": dist(by_channel, N),
    "by_local_area": dist(by_area, N),
    "sanitation_share": pct(by_dept.get("ENG - Sanitation Services", 0), N),
}
pd.DataFrame(R["demand"]["by_month"]).to_csv(TAB / "demand_by_month.csv", index=False)
by_dept.rename("records").to_csv(TAB / "demand_by_department.csv")
by_type.rename("records").to_csv(TAB / "demand_by_type.csv")

# ---------------------------------------------------------------- C. closure outcomes
def outcome_block(closed_df, open_df):
    nc = len(closed_df)
    g = closed_df["outcome_group"].value_counts().reindex(GROUPS, fill_value=0)
    return {"closed": nc, "open": int(len(open_df)), "total": nc + int(len(open_df)),
            "open_share_of_total": pct(len(open_df), nc + len(open_df)),
            "groups": [{"group": k, "short": SHORT[k], "count": int(v), "share": pct(v, nc)} for k, v in g.items()],
            "reasons": dist(closed_df["closure_reason"].value_counts(), nc)}
R["outcomes_all"] = outcome_block(closed, opn)
R["outcomes_excl_admin"] = outcome_block(closed_x, excl[~excl["is_closed"]])
assert sum(x["count"] for x in R["outcomes_all"]["groups"]) == NC

# Unknown concentration
unk = closed[closed["closure_reason"].eq("Unknown")]
unk_types = unk["service_request_type"].value_counts()
R["unknown"] = {
    "total": int(len(unk)), "share_of_closed": pct(len(unk), NC),
    "top_types": [{"type": t, "count": int(c), "type_closed": int((closed["service_request_type"] == t).sum()),
                   "rate_within_type": pct(c, (closed["service_request_type"] == t).sum())}
                  for t, c in unk_types.head(4).items()],
    "top2_count": int(unk_types.head(2).sum()), "top2_share": pct(unk_types.head(2).sum(), len(unk)),
    "admin_sounding_count": int(unk["admin_sounding"].sum()),
    "by_channel": dist(unk["channel"].value_counts(), len(unk)),
}
autoc = closed[closed["closure_reason"].eq("Closed automatically and sent to service group")]
R["auto_closed"] = {"total": int(len(autoc)), "admin_sounding_count": int(autoc["admin_sounding"].sum()),
                    "admin_sounding_share": pct(autoc["admin_sounding"].sum(), len(autoc))}
R["admin_share_of_unknown"] = pct(unk["admin_sounding"].sum(), len(unk))

def group_share_table(frame, key, min_closed=0, top=None):
    t = pd.crosstab(frame[key], frame["outcome_group"]).reindex(columns=GROUPS, fill_value=0)
    t["closed"] = t[GROUPS].sum(axis=1)
    t = t[t["closed"] >= min_closed].sort_values("closed", ascending=False)
    if top:
        t = t.head(top)
    for gname in GROUPS:
        t[SHORT[gname] + " %"] = t[gname] / t["closed"]
    return t

dept_tab = group_share_table(closed, "department", min_closed=1000)
dept_tab.to_csv(TAB / "outcomes_by_department.csv")
dom_reason = (closed.groupby("department")["closure_reason"].agg(lambda s: s.value_counts().index[0]).rename("top_reason"))
dom_share = (closed.groupby("department")["closure_reason"].agg(lambda s: s.value_counts(normalize=True).iloc[0]).rename("top_reason_share"))
sp = dept_tab["Service provided %"]
R["dept_variation"] = {
    "n_departments_min1000_closed": int(len(dept_tab)),
    "min1000_closed_records": int(dept_tab["closed"].sum()),
    "service_provided_min": {"department": sp.idxmin(), "share": float(sp.min()), "closed": int(dept_tab.loc[sp.idxmin(), "closed"])},
    "service_provided_max": {"department": sp.idxmax(), "share": float(sp.max()), "closed": int(dept_tab.loc[sp.idxmax(), "closed"])},
    "rows": [{"department": d, "closed": int(r["closed"]),
              **{SHORT[g]: float(r[SHORT[g] + " %"]) for g in GROUPS},
              **{SHORT[g] + " n": int(r[g]) for g in GROUPS},
              "top_reason": dom_reason[d], "top_reason_share": float(dom_share[d])}
             for d, r in dept_tab.iterrows()],
}
chan_tab = group_share_table(closed, "channel", min_closed=1000)
chan_tab.to_csv(TAB / "outcomes_by_channel.csv")
R["by_channel"] = [{"channel": c, "closed": int(r["closed"]), **{SHORT[g]: float(r[SHORT[g] + " %"]) for g in GROUPS}}
                   for c, r in chan_tab.iterrows()]
chan_x = group_share_table(closed_x, "channel", min_closed=1000)
R["by_channel_excl_admin"] = [{"channel": c, "closed": int(r["closed"]), **{SHORT[g]: float(r[SHORT[g] + " %"]) for g in GROUPS}}
                              for c, r in chan_x.iterrows()]
mon_tab = group_share_table(closed, "open_month")
mon_tab = mon_tab.sort_index()
mon_tab.to_csv(TAB / "outcomes_by_month.csv")
R["by_month"] = [{"month": int(m), "closed": int(r["closed"]), **{SHORT[g]: float(r[SHORT[g] + " %"]) for g in GROUPS}}
                 for m, r in mon_tab.iterrows()]
spm = mon_tab["Service provided %"]
R["by_month_range"] = {"service_provided_min": float(spm.min()), "min_month": int(spm.idxmin()),
                       "service_provided_max": float(spm.max()), "max_month": int(spm.idxmax())}
type_tab = group_share_table(closed, "service_request_type", top=15)
type_tab.to_csv(TAB / "outcomes_top_types.csv")

# ---------------------------------------------------------------- D. durations
elig = df[df["duration_eligible"]]
def pstats(values):
    v = np.asarray(values)
    out = {"n": int(len(v))}
    for p in PCTS:
        out[f"p{int(p*100)}"] = nearest_rank(v, p) if len(v) >= MIN_N_FOR_PERCENTILES else None
    out["same_day_share"] = float((v == 0).mean()) if len(v) else None
    return out
R["duration_exclusions"] = df["duration_exclusion"].replace("", "Eligible").value_counts().to_dict()
R["duration_all_mixed"] = pstats(elig["days_to_close"])
R["duration_by_group"] = [{"group": g, "short": SHORT[g], **pstats(elig.loc[elig["outcome_group"] == g, "days_to_close"])} for g in GROUPS]
ex = elig[~elig["admin_sounding"]]
R["duration_all_mixed_excl_admin"] = pstats(ex["days_to_close"])
R["duration_by_group_excl_admin"] = [{"group": g, "short": SHORT[g], **pstats(ex.loc[ex["outcome_group"] == g, "days_to_close"])} for g in GROUPS]

# Open cases
R["open_cases"] = {
    "count": int(len(opn)), "share": pct(len(opn), N),
    "age_p50": nearest_rank(opn["open_age_days"], 0.5), "age_p90": nearest_rank(opn["open_age_days"], 0.9),
    "age_min": int(opn["open_age_days"].min()), "age_max": int(opn["open_age_days"].max()),
    "top_departments": [{"department": d, "count": int(c), "dept_total": int((df["department"] == d).sum()),
                         "rate": pct(c, (df["department"] == d).sum())} for d, c in opn["department"].value_counts().head(5).items()],
    "by_open_quarter": {f"Q{q}": int(c) for q, c in ((opn["open_month"] - 1) // 3 + 1).value_counts().sort_index().items()},
}

# ---------------------------------------------------------------- E. focus family selection
rows = []
for name, (dept, types) in CANDIDATES.items():
    f = df[df["department"].eq(dept) & df["service_request_type"].isin(types)]
    fc = f[f["is_closed"]]
    gs = fc["outcome_group"].value_counts(normalize=True).reindex(GROUPS, fill_value=0)
    rows.append({"family": name, "department": dept, "types": len(types), "records": len(f), "closed": len(fc),
                 "groups_ge5pct": int((gs >= 0.05).sum()), "service_provided": gs[G1], "continuing": gs[G2],
                 "no_action": gs[G3], "unclear": gs[G5], "admin_sounding_rows": int(f["admin_sounding"].sum()),
                 "missing_local_area": pct((~f["has_local_area"]).sum(), len(f)),
                 "top_reason": fc["closure_reason"].value_counts().index[0],
                 "top_reason_share": float(fc["closure_reason"].value_counts(normalize=True).iloc[0])})
sel = pd.DataFrame(rows)
sel["meets_volume"] = sel["records"] >= 5000
sel["meets_outcome_variety"] = sel["groups_ge5pct"] >= 3
sel["meets_interpretability"] = sel["unclear"] <= 0.05
sel["meets_scope"] = sel["types"].between(2, 5)
sel["criteria_met"] = sel[["meets_volume", "meets_outcome_variety", "meets_interpretability", "meets_scope"]].sum(axis=1)
sel = sel.sort_values(["criteria_met", "groups_ge5pct", "records"], ascending=False)
sel.to_csv(TAB / "focus_family_selection.csv", index=False)
R["focus_selection"] = sel.to_dict(orient="records")
R["focus_selected"] = FOCUS_FAMILY

# ---------------------------------------------------------------- focus family detail
F = df[df["focus_family"]]
FC = F[F["is_closed"]]
FE = F[F["duration_eligible"]]
fam = {"name": FOCUS_FAMILY, "department": fam_dept, "types": fam_types, "records": int(len(F)),
       "closed": int(len(FC)), "open": int((~F["is_closed"]).sum()), "share_of_cohort": pct(len(F), N),
       "dept_records": int((df["department"] == fam_dept).sum()),
       "groups": [{"group": g, "short": SHORT[g], "count": int(c), "share": pct(c, len(FC))}
                  for g, c in FC["outcome_group"].value_counts().reindex(GROUPS, fill_value=0).items()],
       "reasons": dist(FC["closure_reason"].value_counts(), len(FC))}
by_t = []
for t in fam_types:
    ft = F[F["service_request_type"] == t]
    ftc = ft[ft["is_closed"]]
    gs = ftc["outcome_group"].value_counts().reindex(GROUPS, fill_value=0)
    rs = ftc["closure_reason"].value_counts()
    by_t.append({"type": t, "records": int(len(ft)), "closed": int(len(ftc)), "open": int((~ft["is_closed"]).sum()),
                 **{SHORT[g] + " n": int(gs[g]) for g in GROUPS},
                 **{SHORT[g]: pct(gs[g], len(ftc)) for g in GROUPS},
                 "reasons": {k: int(v) for k, v in rs.items()}})
fam["by_type"] = by_t
dur = []
for t in fam_types + ["All three types"]:
    sub = FE if t == "All three types" else FE[FE["service_request_type"] == t]
    dur.append({"type": t, "group": "All outcomes (mixed)", **pstats(sub["days_to_close"])})
    for g in [G1, G2, G3]:
        dur.append({"type": t, "group": SHORT[g], **pstats(sub.loc[sub["outcome_group"] == g, "days_to_close"])})
    for r in ["Further action has been planned", "Referred to another service group"]:
        dur.append({"type": t, "group": "  of which: " + r, **pstats(sub.loc[sub["closure_reason"] == r, "days_to_close"])})
fam["durations"] = dur
pd.DataFrame(dur).to_csv(TAB / "focus_durations.csv", index=False)
fam["duration_excluded"] = F["duration_exclusion"].replace("", "Eligible").value_counts().to_dict()
fam["channels"] = dist(F["channel"].value_counts(), len(F))
fc_chan = group_share_table(FC, "channel", min_closed=200)
fam["channel_outcomes"] = [{"channel": c, "closed": int(r["closed"]), **{SHORT[g]: float(r[SHORT[g] + " %"]) for g in GROUPS}}
                           for c, r in fc_chan.iterrows()]
fam["local_area_missing"] = int((~F["has_local_area"]).sum())
fam["local_area_missing_share"] = pct((~F["has_local_area"]).sum(), len(F))
fa = F[F["has_local_area"]]
area_tab = group_share_table(fa[fa["is_closed"]], "local_area")
fam["local_area_top5"] = [{"area": a, "records": int((fa["local_area"] == a).sum())} for a in fa["local_area"].value_counts().head(5).index]
fam["local_area_continuing_range"] = {"min": float(area_tab["Assigned / referred / continuing %"].min()),
                                      "max": float(area_tab["Assigned / referred / continuing %"].max()),
                                      "areas": int(len(area_tab)), "min_closed_per_area": int(area_tab["closed"].min())}
area_tab.to_csv(TAB / "focus_outcomes_by_local_area.csv")
fam_month = F.groupby("open_month").size()
fam["by_month"] = [{"month": int(m), "count": int(c)} for m, c in fam_month.items()]
fm = group_share_table(FC, "open_month").sort_index()
fam["continuing_by_month"] = [{"month": int(m), "share": float(r["Assigned / referred / continuing %"]), "closed": int(r["closed"])}
                              for m, r in fm.iterrows()]
fam["open_age_p50"] = nearest_rank(F.loc[~F["is_closed"], "open_age_days"], 0.5) if (~F["is_closed"]).sum() else None
R["focus"] = fam

# ---------------------------------------------------------------- mapping table with counts
map_rows = []
for reason, (g, sg, why, q) in MAPPING.items():
    map_rows.append({"closure_reason_original": reason, "outcome_group": g, "outcome_subgroup": sg,
                     "closed_2025": int((closed["closure_reason"] == reason).sum()),
                     "open_2025": int((opn["closure_reason"] == reason).sum()),
                     "rationale": why, "validation_question": q})
pd.DataFrame(map_rows).to_csv(PROC / "closure_outcome_mapping.csv", index=False)
R["mapping"] = map_rows

# ---------------------------------------------------------------- cleaned row-level file for Power Query
clean = pd.DataFrame({
    "extract_row": np.arange(1, N + 1),
    "department": df["department"], "service_request_type": df["service_request_type"],
    "status": df["status"], "closure_reason": df["closure_reason"],
    "open_timestamp_utc": df["service_request_open_timestamp"],
    "open_datetime_local": df["open_local"].dt.strftime("%Y-%m-%d %H:%M:%S"),
    "open_date_local": df["open_date_local"].dt.strftime("%Y-%m-%d"),
    "open_month": df["open_month"],
    "close_date": df["service_request_close_date"],
    "days_to_close": df["days_to_close"].astype("Int64"),
    "duration_eligible": np.where(df["duration_eligible"], "Yes", "No"),
    "duration_exclusion_reason": df["duration_exclusion"],
    "local_area": df["local_area"].replace("", "(Not recorded)"),
    "channel": df["channel"],
    "has_address": np.where(df["has_address"], "Yes", "No"),
    "has_coordinates": np.where(df["has_coordinates"], "Yes", "No"),
    "admin_sounding": np.where(df["admin_sounding"], "Yes", "No"),
    "zz_old_label": np.where(df["zz_old"], "Yes", "No"),
    "duplicate_looking": np.where(df["duplicate_looking"], "Yes", "No"),
    "focus_family": np.where(df["focus_family"], "Yes", "No"),
})
clean.to_csv(PROC / "cohort_2025_clean.csv", index=False, encoding="utf-8")
R["clean_file"] = {"rows": int(len(clean)), "columns": list(clean.columns),
                   "note": "Address, latitude, longitude and geom removed for privacy; presence flags retained."}

(BUILD / "results.json").write_text(json.dumps(R, indent=2, default=str), encoding="utf-8")

# ---------------------------------------------------------------- console summary
print("cohort", N, "closed", NC, "open", len(opn), "unmapped", unmapped)
print(json.dumps(R["cohort_reconciliation"]))
for x in R["outcomes_all"]["groups"]:
    print(f'  {x["group"]:50s} {x["count"]:8d} {x["share"]:.2%}')
print("EXCL ADMIN closed", R["outcomes_excl_admin"]["closed"])
for x in R["outcomes_excl_admin"]["groups"]:
    print(f'  {x["group"]:50s} {x["count"]:8d} {x["share"]:.2%}')
print("unknown", json.dumps(R["unknown"]["top_types"]), R["unknown"]["top2_share"])
print("dept variation", json.dumps(R["dept_variation"]["service_provided_min"]), json.dumps(R["dept_variation"]["service_provided_max"]), R["dept_variation"]["n_departments_min1000_closed"])
print("duration mixed", R["duration_all_mixed"])
for x in R["duration_by_group"]:
    print("  ", x)
print("exclusions", R["duration_exclusions"])
print("open", json.dumps(R["open_cases"], default=str))
print(sel[["family", "records", "closed", "groups_ge5pct", "service_provided", "continuing", "no_action", "unclear", "criteria_met"]].to_string())
print("focus", FOCUS_FAMILY, fam["records"], fam["closed"], fam["open"])
for x in fam["groups"]:
    print("  ", x)
print(pd.DataFrame(dur).to_string())
print("quality", json.dumps({k: v for k, v in R["quality"].items() if not isinstance(v, (list,))}, default=str))
print("date", json.dumps(R["date_behaviour"]))
print("demand top5/top10 types", R["demand"]["top5_types_share"], R["demand"]["top10_types_share"], "top5 depts", R["demand"]["top5_depts_share"])
print("month range", R["by_month_range"])
print("area continuing range", fam["local_area_continuing_range"])
print(pd.DataFrame(fam["channel_outcomes"]).to_string())
