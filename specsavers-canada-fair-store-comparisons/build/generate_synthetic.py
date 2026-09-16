"""
Synthetic dataset generator — Specsavers Canada outside-in case study (Phase 12).

ALL DATA IS SYNTHETIC. Store names, locations, dates and values are fictional and
are unrelated to actual Specsavers performance, stores, partners or patients.

Reproducible: fixed random seed. Output: data/synthetic_store_weekly.csv
"""
import csv, math, os, random
from datetime import date, timedelta

SEED = 20260913
rng = random.Random(SEED)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_CSV = os.path.join(OUT_DIR, "synthetic_store_weekly.csv")

WEEK1 = date(2026, 2, 23)          # Monday
N_WEEKS = 26
WEEKS = [WEEK1 + timedelta(days=7 * i) for i in range(N_WEEKS)]

# store_id, name, province, region, format, banner, opening_date, base_capacity
STORES = [
    ("SYN-001", "Aurora Point",      "BC", "West",     "Street-front",    "Standalone (no host)", date(2022, 3, 14), 190),
    ("SYN-002", "Birchwood Landing", "BC", "West",     "Shopping centre", "Standalone (no host)", date(2022, 6, 20), 210),
    ("SYN-003", "Cobalt Bay",        "BC", "West",     "Shopping centre", "Standalone (no host)", date(2023, 1, 16), 180),
    ("SYN-004", "Driftwood Row",     "BC", "West",     "Grocery-hosted",  "Host Banner A",        date(2025, 10, 6), 120),
    ("SYN-005", "Elmstone Commons",  "BC", "West",     "Shopping centre", "Standalone (no host)", date(2022, 9, 12), 200),
    ("SYN-006", "Fernhill Market",   "BC", "West",     "Street-front",    "Standalone (no host)", date(2024, 9, 9), 150),
    ("SYN-007", "Glacier Gate",      "AB", "Prairies", "Shopping centre", "Standalone (no host)", date(2023, 4, 17), 190),
    ("SYN-008", "Heronfield",        "AB", "Prairies", "Grocery-hosted",  "Host Banner A",        date(2025, 11, 3), 120),
    ("SYN-009", "Ironwood Plaza",    "AB", "Prairies", "Shopping centre", "Standalone (no host)", date(2023, 8, 21), 180),
    ("SYN-010", "Juniper Flats",     "AB", "Prairies", "Street-front",    "Standalone (no host)", date(2024, 5, 13), 150),
    ("SYN-011", "Kestrel Park",      "SK", "Prairies", "Grocery-hosted",  "Host Banner B",        date(2025, 9, 15), 110),
    ("SYN-012", "Lakeshore Vale",    "SK", "Prairies", "Shopping centre", "Standalone (no host)", date(2024, 11, 18), 140),
    ("SYN-013", "Marigold Square",   "MB", "Prairies", "Shopping centre", "Standalone (no host)", date(2024, 6, 17), 160),
    ("SYN-014", "Northstar Mews",    "MB", "Prairies", "Grocery-hosted",  "Host Banner B",        date(2026, 1, 12), 115),
    ("SYN-015", "Oakhaven Centre",   "ON", "Ontario",  "Shopping centre", "Standalone (no host)", date(2022, 1, 17), 220),
    ("SYN-016", "Pinecrest Terrace", "ON", "Ontario",  "Street-front",    "Standalone (no host)", date(2022, 11, 7), 180),
    ("SYN-017", "Quarry Lane",       "ON", "Ontario",  "Shopping centre", "Standalone (no host)", date(2023, 6, 5), 200),
    ("SYN-018", "Riverbend Commons", "ON", "Ontario",  "Grocery-hosted",  "Host Banner A",        date(2025, 10, 20), 120),
    ("SYN-019", "Sumac Hollow",      "ON", "Ontario",  "Shopping centre", "Standalone (no host)", date(2024, 3, 4), 170),
    ("SYN-020", "Tamarack Grove",    "ON", "Ontario",  "Grocery-hosted",  "Host Banner B",        date(2026, 4, 6), 110),
    ("SYN-021", "Upland Crossing",   "ON", "Ontario",  "Street-front",    "Standalone (no host)", date(2024, 8, 12), 150),
    ("SYN-022", "Violet Hill",       "ON", "Ontario",  "Shopping centre", "Standalone (no host)", date(2023, 2, 27), 200),
    ("SYN-023", "Willowmere",        "ON", "Ontario",  "Grocery-hosted",  "Host Banner A",        date(2026, 5, 4), 115),
    ("SYN-024", "Yarrow Heights",    "ON", "Ontario",  "Shopping centre", "Standalone (no host)", date(2025, 2, 24), 160),
    ("SYN-025", "Amberfield",        "NS", "Atlantic", "Grocery-hosted",  "Host Banner A",        date(2025, 9, 29), 110),
    ("SYN-026", "Bluewater Reach",   "NS", "Atlantic", "Shopping centre", "Standalone (no host)", date(2024, 10, 7), 150),
    ("SYN-027", "Copperleaf",        "NS", "Atlantic", "Grocery-hosted",  "Host Banner B",        date(2025, 11, 17), 110),
    ("SYN-028", "Dunmore Bend",      "NB", "Atlantic", "Grocery-hosted",  "Host Banner A",        date(2025, 10, 27), 110),
    ("SYN-029", "Evergreen Wharf",   "NB", "Atlantic", "Street-front",    "Standalone (no host)", date(2025, 4, 14), 140),
    ("SYN-030", "Foxglove Harbour",  "NL", "Atlantic", "Grocery-hosted",  "Host Banner B",        date(2026, 3, 16), 100),
]

# Deliberate patterns (documented in phase-12-synthetic-dataset.md)
P3_HIGH_DEMAND_LOW_ATTENDANCE = {"SYN-012", "SYN-019"}
P4_DECLINING_CONVERSION = "SYN-005"
P2_ELEVATED_TURNAROUND_REGION = "Atlantic"
P2_EXEMPT = {"SYN-029"}             # one Atlantic store near network norm ("5 of 6")
# P5 data-quality warnings: (store, week_no) -> (completeness_pct, refresh_status, unresolved_share, volume_factor)
P5_DQ = {
    ("SYN-013", 5):  (95.5, "Current", 0.0, 1.0),     # Amber: completeness
    ("SYN-009", 9):  (93.5, "Current", 0.09, 1.0),    # Amber: unresolved appointment statuses
    ("SYN-009", 10): (92.0, "Current", 0.11, 1.0),    # Amber: unresolved appointment statuses
    ("SYN-022", 14): (84.0, "Delayed", 0.0, 0.84),    # Red: completeness < 90
    ("SYN-022", 15): (78.5, "Stale", 0.0, 0.785),     # Red: completeness + stale
    ("SYN-022", 16): (88.0, "Delayed", 0.0, 0.88),    # Red: completeness < 90
    ("SYN-027", 20): (91.0, "Stale", 0.0, 0.91),      # Red: stale
    ("SYN-003", 26): (96.0, "Delayed", 0.0, 0.96),    # Amber: latest week delayed
    ("SYN-016", 26): (96.0, "Delayed", 0.0, 0.96),    # Amber: latest week delayed
}

COHORT_BANDS = [("New", 0, 26), ("Developing", 27, 104), ("Mature", 105, 10**6)]


def cohort_for(weeks_since_opening):
    for name, lo, hi in COHORT_BANDS:
        if lo <= weeks_since_opening <= hi:
            return name
    return "Unclassified"


def noise(sd):
    return rng.gauss(0, sd)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def ramp(age):
    """Demand ramp 0..1 by weeks since opening (synthetic assumption)."""
    return 1 - math.exp(-age / 16.0)


rows = []
for (sid, name, prov, region, fmt, banner, opened, base_cap) in STORES:
    # store-level persistent effects
    store_util_eff = noise(0.02)
    store_conv_eff = noise(0.025)
    store_aov = {"Street-front": 345, "Shopping centre": 335, "Grocery-hosted": 305}[fmt] + noise(12)
    for wk_no, wk in enumerate(WEEKS, start=1):
        if wk < opened:
            continue  # store not yet open: no row
        age = (wk - opened).days // 7
        cohort = cohort_for(age)
        r = ramp(age)

        # ---- capacity ----
        cap_ramp = 0.78 + 0.22 * min(1.0, age / 20.0)
        available = int(round(base_cap * cap_ramp * (1 + noise(0.03))))

        # ---- utilization (held / available) ----
        if age >= 105:
            util = 0.84
        else:
            util = 0.44 + 0.38 * r
        util += store_util_eff + noise(0.02)
        if sid in P3_HIGH_DEMAND_LOW_ATTENDANCE:
            util = 0.935 + noise(0.012)
        util = clamp(util, 0.30, 0.97)
        held = int(round(available * util))

        cancel_share = clamp(0.08 + noise(0.012), 0.03, 0.15)
        booked = min(available, int(round(held / (1 - cancel_share))))
        cancelled = booked - held

        no_show_rate = clamp(0.06 + noise(0.01), 0.02, 0.12)
        if sid in P3_HIGH_DEMAND_LOW_ATTENDANCE:
            no_show_rate = clamp(0.165 + noise(0.012), 0.13, 0.21)
        no_show = int(round(held * no_show_rate))

        dq = P5_DQ.get((sid, wk_no))
        unresolved = int(round(booked * dq[2])) if dq else 0
        completed = held - no_show - unresolved

        # ---- conversion (exam-linked distinct purchasing customers / completed) ----
        if age >= 105:
            conv = 0.60
        else:
            conv = 0.43 + 0.15 * r
        if fmt == "Grocery-hosted":
            conv -= 0.02
        conv += store_conv_eff + noise(0.02)
        if sid == P4_DECLINING_CONVERSION:
            # decline deliberately placed in Mar-May 2026, well before any real-world event
            if wk_no <= 6:
                conv = 0.63 + noise(0.012)
            elif wk_no <= 10:
                conv = 0.63 - (wk_no - 6) * 0.04 + noise(0.008)     # step down to ~0.47
            else:
                conv = 0.47 - (wk_no - 10) * 0.003 + noise(0.008)   # slow drift to ~0.42
        conv = clamp(conv, 0.25, 0.80)
        purchasing = int(round(completed * conv))

        aov = store_aov * (0.93 + 0.07 * r) * (1 + noise(0.04))
        revenue = round(purchasing * aov * (1 - clamp(0.02 + noise(0.01), 0, 0.06)), 2)

        # ---- fulfilment ----
        orders = int(round(purchasing * (1.12 + noise(0.03)) + completed * 0.05))
        if region == P2_ELEVATED_TURNAROUND_REGION and sid not in P2_EXEMPT:
            ontime_rate = clamp(0.74 + noise(0.035), 0.55, 0.88)
            turnaround = clamp(9.6 + noise(0.7), 7.8, 12.5)
        elif sid in P2_EXEMPT:
            ontime_rate = clamp(0.94 + noise(0.02), 0.86, 0.99)
            turnaround = clamp(5.5 + noise(0.4), 4.6, 6.8)
        else:
            ontime_rate = clamp(0.925 + noise(0.02), 0.84, 0.99)
            turnaround = clamp(6.0 + noise(0.45), 4.6, 7.6)
        if age < 13:
            turnaround += 0.6
            ontime_rate -= 0.03
        on_time = int(round(orders * clamp(ontime_rate, 0, 1)))
        turnaround = round(turnaround, 1)

        # ---- recall ----
        if age < 12:
            recall_contacts = None       # recall programme not yet active: NULL (not applicable)
            recall_bookings = None
        else:
            if age >= 105:
                base_contacts = 110
            else:
                base_contacts = 8 + 95 * min(1.0, (age - 12) / 90.0)
            recall_contacts = max(0, int(round(base_contacts * (base_cap / 180) * (1 + noise(0.12)))))
            rate = 0.18 if age >= 105 else (0.15 if age >= 27 else 0.12)
            recall_bookings = int(round(recall_contacts * clamp(rate + noise(0.015), 0.03, 0.35)))

        # ---- data quality ----
        completeness = round(clamp(99.3 + noise(0.35), 98.2, 100.0), 1)
        status = "Current"
        if dq:
            completeness, status, _, factor = dq
            if factor < 1.0:
                # records missing: received volumes understated proportionally
                def scale(v):
                    return None if v is None else int(math.floor(v * factor))
                available = scale(available)
                booked = scale(booked)
                cancelled = scale(cancelled)
                no_show = scale(no_show)
                completed = scale(completed)
                # keep invariants after scaling
                completed = min(completed, booked - cancelled - no_show)
                purchasing = min(scale(purchasing), completed)
                revenue = round(revenue * factor, 2)
                orders = scale(orders)
                on_time = min(scale(on_time), orders)
                recall_contacts = scale(recall_contacts)
                recall_bookings = None if recall_contacts is None else min(scale(recall_bookings), recall_contacts)

        rows.append({
            "week_start": wk.isoformat(),
            "store_id": sid,
            "store_name": f"Synthetic - {name}",
            "province": prov,
            "region": region,
            "retail_banner": banner,
            "store_format": fmt,
            "opening_date": opened.isoformat(),
            "maturity_cohort": cohort,
            "weeks_since_opening": age,
            "available_appointment_slots": available,
            "booked_appointments": booked,
            "completed_exams": completed,
            "cancelled_appointments": cancelled,
            "no_show_appointments": no_show,
            "purchasing_customers": purchasing,
            "eyewear_revenue": f"{revenue:.2f}",
            "orders_placed": orders,
            "orders_ready_on_time": on_time,
            "average_turnaround_days": f"{turnaround:.1f}",
            "recall_contacts": "" if recall_contacts is None else recall_contacts,
            "recall_bookings": "" if recall_bookings is None else recall_bookings,
            "data_completeness_pct": f"{completeness:.1f}",
            "data_refresh_status": status,
        })

os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {len(rows)} rows to {os.path.abspath(OUT_CSV)}")
