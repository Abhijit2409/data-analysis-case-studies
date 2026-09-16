"""
Calculation regression tests for build/kpi_engine.py (Phase E). SYNTHETIC data only.

Run:  python -m unittest discover -s tests -v
IDs in test names match issue-register.md (PY-*).
"""
import json
import math
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "build"))
import kpi_engine as E  # noqa: E402

DATA, SW = None, None


def setUpModule():
    global DATA, SW
    DATA = E.derive(E.load(os.path.join(ROOT, "data", "synthetic_store_weekly.csv")))
    SW, _ = E.compute(DATA)


def week(sw, w):
    return sw[sw["week_start"] == pd.Timestamp(w)]


def row(sid, w, sw=None):
    return E.get_row(SW if sw is None else sw, sid, w)


# ---------------------------------------------------------------------------------------------- unit-frame builder
BASE_ROW = dict(province="ON", region="Ontario", retail_banner="Standalone (no host)", store_format="Shopping centre",
                available_appointment_slots=100, booked_appointments=90, cancelled_appointments=10, no_show_appointments=5,
                completed_exams=75, purchasing_customers=45, eyewear_revenue=9000.0, orders_placed=50, orders_ready_on_time=45,
                average_turnaround_days=6.0, recall_contacts=60.0, recall_bookings=10.0, data_completeness_pct=99.0,
                data_refresh_status="Current")


def build(specs, n_weeks, week1="2026-01-05"):
    """specs: list of dicts {id, opened, fmt?, region?, rows: callable(i, age) -> overrides dict or None to drop the week}."""
    rows = []
    for sp in specs:
        opened = pd.Timestamp(sp["opened"])
        for i in range(n_weeks):
            wk = pd.Timestamp(week1) + pd.Timedelta(weeks=i)
            if wk < opened:
                continue
            age = (wk - opened).days // 7
            over = sp.get("rows", lambda i, a: {})(i, age)
            if over is None:
                continue
            r = dict(BASE_ROW, week_start=wk, store_id=sp["id"], store_name="Synthetic - " + sp["id"], opening_date=opened,
                     weeks_since_opening=age, maturity_cohort=E.cohort_for(age))
            r["store_format"] = sp.get("fmt", r["store_format"])
            r["region"] = sp.get("region", r["region"])
            r.update(over)
            rows.append(r)
    df = pd.DataFrame(rows).sort_values(["store_id", "week_start"]).reset_index(drop=True)
    sw, weeks = E.compute(E.derive(df))
    return sw, weeks


def wk(i, week1="2026-01-05"):
    return pd.Timestamp(week1) + pd.Timedelta(weeks=i)


# ---------------------------------------------------------------------------------------------- baselines
class Baselines(unittest.TestCase):
    def test_PY_BASE_01_network_latest_week(self):
        lw = week(SW, "2026-08-17")
        p = E.pooled(lw)
        self.assertEqual(p["stores"], 30)
        self.assertEqual(p["completed_exams"], 3496)
        self.assertEqual(sorted(lw.loc[lw["dq_status"] == "Amber", "store_id"]), ["SYN-003", "SYN-016"])
        self.assertEqual(int((lw["dq_status"] == "Red").sum()), 0)

    def test_PY_BASE_02_atlantic_latest_week(self):
        lw = week(SW, "2026-08-17")
        at = lw[lw["region"] == "Atlantic"]
        p = E.pooled(at)
        self.assertEqual(p["stores"], 6)
        self.assertEqual(p["completed_exams"], 545)
        self.assertEqual(round(p["utilization"] * 100, 1), 81.0)
        self.assertEqual(round(p["attendance"] * 100, 1), 94.6)
        self.assertEqual(round(p["conversion"] * 100, 1), 55.8)
        self.assertEqual(round(p["on_time"] * 100, 1), 77.3)
        self.assertEqual(round(p["turnaround"], 1), 9.1)
        self.assertTrue((at["dq_status"] == "Green").all())

    def test_PY_FUN_01_syn014_funnel_window(self):
        r = row("SYN-014", "2026-08-17")
        self.assertEqual((r["utilization_d4"], r["utilization_n4"], r["conversion_d4"], r["conversion_n4"]), (460, 350, 326, 187))
        self.assertEqual(r["utilization_weeks"], 4)


# ---------------------------------------------------------------------------------------------- data-quality withholding
class RedWithholding(unittest.TestCase):
    def test_PY_RED_01_red_selected_week_is_unavailable(self):
        for sid, w in [("SYN-022", "2026-05-25"), ("SYN-022", "2026-06-01"), ("SYN-022", "2026-06-08"), ("SYN-027", "2026-07-06")]:
            r = row(sid, w)
            self.assertEqual(r["dq_status"], "Red")
            for k in E.PEER_KPIS:
                self.assertTrue(pd.isna(r[f"{k}_r4"]), f"{sid} {w} {k} should be withheld")
                self.assertEqual(r[f"{k}_state"], "red")
            for k in E.EXCEPTION_KPIS:
                self.assertFalse(r[f"{k}_flag"])
        r = row("SYN-027", "2026-07-06")
        self.assertEqual(r["ramp_state"], "red")
        self.assertTrue(pd.isna(r["ramp_index"]))

    def test_PY_RED_02_history_preserved_and_recovery(self):
        self.assertEqual(row("SYN-022", "2026-05-18")["conversion_state"], "ok")
        self.assertAlmostEqual(row("SYN-022", "2026-05-18")["conversion_r4"], 0.6040688575899843, places=9)
        self.assertEqual(row("SYN-022", "2026-06-15")["conversion_state"], "insufficient_history")  # 1 usable week
        self.assertEqual(row("SYN-022", "2026-06-22")["conversion_state"], "insufficient_history")  # 2 usable weeks
        self.assertEqual(row("SYN-022", "2026-06-29")["conversion_state"], "ok")                    # 3 usable weeks

    def test_PY_RED_03_red_rows_excluded_from_peer_pools(self):
        w = "2026-05-25"
        focal = row("SYN-002", w)
        wk_rows = week(SW, w)
        pool = wk_rows[(wk_rows["store_id"] != "SYN-002") & (wk_rows["maturity_cohort"] == focal["maturity_cohort"])
                       & (wk_rows["store_format"] == focal["store_format"]) & wk_rows["conversion_r4"].notna()]
        self.assertNotIn("SYN-022", set(pool["store_id"]))
        self.assertEqual(int(focal["conversion_peer_n"]), len(pool))
        self.assertAlmostEqual(focal["conversion_peer_median"], pool["conversion_r4"].median(), places=12)
        # ramp peers at SYN-027's age exclude its Red week
        self.assertTrue(all(pd.isna(x) for x in SW.loc[SW["dq_status"] == "Red", "exams_r4"]))

    def test_PY_RED_04_unit_red_week_with_three_prior_usable_weeks(self):
        sw, _ = build([{"id": "T1", "opened": "2020-01-06", "rows": lambda i, a: {"data_refresh_status": "Stale"} if i == 4 else {}}], 6)
        r = E.get_row(sw, "T1", wk(4))
        self.assertEqual(r["conversion_state"], "red")
        self.assertTrue(pd.isna(r["conversion_r4"]))
        self.assertEqual(E.get_row(sw, "T1", wk(3))["conversion_state"], "ok")

    def test_PY_AMBER_01_provisional_marker(self):
        self.assertTrue(row("SYN-003", "2026-08-17")["provisional"])
        self.assertTrue(row("SYN-009", "2026-05-18")["provisional"])   # window 04-27..05-18 contains Amber 04-27
        self.assertFalse(row("SYN-009", "2026-05-25")["provisional"])
        self.assertFalse(row("SYN-014", "2026-08-17")["provisional"])


# ---------------------------------------------------------------------------------------------- windows and cohorts
class Windows(unittest.TestCase):
    def test_PY_WIN_01_calendar_window_with_missing_rows(self):
        sw, _ = build([{"id": "T1", "opened": "2020-01-06", "rows": lambda i, a: None if i in (4,) else {}},
                       {"id": "T2", "opened": "2020-01-06", "rows": lambda i, a: None if i in (4, 5) else {}}], 8)
        r1 = E.get_row(sw, "T1", wk(6))  # window weeks 3..6, week 4 missing -> 3 usable
        self.assertEqual(r1["conversion_state"], "ok")
        self.assertEqual(r1["conversion_weeks"], 3)
        self.assertEqual(r1["conversion_d4"], 225)
        r2 = E.get_row(sw, "T2", wk(6))  # weeks 4 and 5 missing -> 2 usable
        self.assertEqual(r2["conversion_state"], "insufficient_history")

    def test_PY_WIN_02_minimum_history_and_ratio_of_sums(self):
        vals = {0: (20, 10), 1: (100, 90), 2: (100, 50)}
        sw, _ = build([{"id": "N1", "opened": "2026-01-05",
                        "rows": lambda i, a: {"completed_exams": vals[i][0], "purchasing_customers": vals[i][1], "no_show_appointments": 80 - vals[i][0] if vals[i][0] < 80 else 0,
                                              "booked_appointments": 110, "available_appointment_slots": 120} if i in vals else {}}], 3)
        self.assertEqual(E.get_row(sw, "N1", wk(1))["conversion_state"], "insufficient_history")
        r = E.get_row(sw, "N1", wk(2))
        self.assertEqual(r["conversion_state"], "ok")
        self.assertAlmostEqual(r["conversion_r4"], 150 / 220, places=12)
        self.assertNotAlmostEqual(r["conversion_r4"], (0.5 + 0.9 + 0.5) / 3, places=3)

    def test_PY_COH_01_cohort_boundaries(self):
        self.assertEqual([E.cohort_for(x) for x in (0, 26, 27, 104, 105, None)], ["New", "New", "Developing", "Developing", "Mature", "Unclassified"])
        s = SW[SW["store_id"] == "SYN-014"].set_index("week_start")["maturity_cohort"]
        self.assertEqual(s[pd.Timestamp("2026-07-13")], "New")
        self.assertEqual(s[pd.Timestamp("2026-07-20")], "Developing")


# ---------------------------------------------------------------------------------------------- peers
class Peers(unittest.TestCase):
    def pool(self, spec):
        return [(f"S{i}", 0.5, c, f) for i, (c, f) in enumerate(spec)]

    def test_PY_PEER_01_fallback(self):
        pool = self.pool([("Developing", "Street-front")] * 3 + [("Developing", "Grocery-hosted")] * 3)
        basis, peers, nf, nc = E.choose_peers("X", "Developing", "Street-front", pool)
        self.assertEqual((basis, len(peers), nf, nc), ("cohort (fallback)", 6, 3, 6))
        basis, peers, nf, nc = E.choose_peers("X", "Developing", "Street-front", self.pool([("Developing", "Street-front")] * 5))
        self.assertEqual((basis, len(peers)), ("cohort x format", 5))

    def test_PY_PEER_02_suppression_below_floor_and_self_excluded(self):
        pool = self.pool([("New", "Grocery-hosted")] * 4) + [("X", 0.9, "New", "Grocery-hosted")]
        basis, peers, nf, nc = E.choose_peers("X", "New", "Grocery-hosted", pool)
        self.assertEqual((basis, peers, nc), ("suppressed", [], 4))
        self.assertEqual(E.choose_peers("X", "Unclassified", "Grocery-hosted", pool)[0], "suppressed")

    def test_PY_PEER_03_dataset_cases(self):
        self.assertEqual(row("SYN-029", "2026-08-17")["conversion_peer_basis"], "cohort (fallback)")
        self.assertEqual(row("SYN-030", "2026-08-17")["conversion_peer_basis"], "suppressed")
        self.assertEqual(row("SYN-014", "2026-08-17")["conversion_peer_basis"], "cohort x format")
        self.assertEqual(int(row("SYN-014", "2026-08-17")["conversion_peer_n"]), 7)

    def test_PY_PEER_04_quantile_matches_pandas(self):
        vals = [0.61, 0.52, 0.58, 0.49, 0.55, 0.63, 0.57]
        s = pd.Series(vals)
        for q in (0.25, 0.5, 0.75):
            self.assertAlmostEqual(E.quantile_linear(vals, q), s.quantile(q), places=12)


# ---------------------------------------------------------------------------------------------- suppression
class Suppression(unittest.TestCase):
    def test_PY_SUP_01_count_display_states(self):
        self.assertEqual(E.count_display(None), ("not_applicable", None))
        self.assertEqual(E.count_display(0), ("zero", 0))
        self.assertEqual(E.count_display(1), ("suppressed", "<5"))
        self.assertEqual(E.count_display(4), ("suppressed", "<5"))
        self.assertEqual(E.count_display(5), ("value", 5))
        rb = DATA["recall_bookings"]
        self.assertEqual(int(((rb >= 1) & (rb <= 4)).sum()), 216)
        self.assertEqual(row("SYN-014", "2026-08-17")["recall_bookings"], 3)

    def test_PY_SUP_02_rate_rule(self):
        self.assertEqual(E.rate_state(3, 40), "suppressed")          # visible denominator would reveal the numerator
        self.assertEqual(E.rate_state(0, 40), "ok")                  # genuine zero is shown
        self.assertEqual(E.rate_state(10, 4), "low_volume")
        self.assertEqual(E.rate_state(3, 4), "low_volume")
        self.assertEqual(E.rate_state(3, 40, count_based=False), "ok")  # e.g., turnaround day-sums
        self.assertEqual(E.rate_state(None, None), "not_applicable")

    def test_PY_SUP_03_engine_states(self):
        sw, _ = build([{"id": "R1", "opened": "2020-01-06", "rows": lambda i, a: {"recall_contacts": 10.0, "recall_bookings": 1.0}},
                       {"id": "R2", "opened": "2020-01-06", "rows": lambda i, a: {"recall_contacts": 10.0, "recall_bookings": 0.0}},
                       {"id": "R3", "opened": "2020-01-06", "rows": lambda i, a: {"recall_contacts": None, "recall_bookings": None} if i == 3 else {}},
                       {"id": "R4", "opened": "2020-01-06", "rows": lambda i, a: {"recall_contacts": 1.0, "recall_bookings": 0.0}}], 4)
        self.assertEqual(E.get_row(sw, "R1", wk(3))["recall_rate_state"], "suppressed")   # 4 bookings / 40 contacts
        self.assertTrue(pd.isna(E.get_row(sw, "R1", wk(3))["recall_rate_r4"]))
        self.assertEqual(E.get_row(sw, "R2", wk(3))["recall_rate_state"], "ok")
        self.assertEqual(E.get_row(sw, "R2", wk(3))["recall_rate_r4"], 0.0)
        self.assertEqual(E.get_row(sw, "R3", wk(3))["recall_rate_state"], "not_applicable")
        self.assertEqual(E.get_row(sw, "R4", wk(3))["recall_rate_state"], "low_volume")
        self.assertIn(row("SYN-030", "2026-06-15")["recall_rate_state"], {"insufficient_history", "low_volume", "suppressed"})


# ---------------------------------------------------------------------------------------------- exceptions
def conv_rows(buy):
    return lambda i, a: {"completed_exams": 100, "purchasing_customers": buy(i), "no_show_appointments": 0, "booked_appointments": 110,
                         "cancelled_appointments": 10, "available_appointment_slots": 120}


class Exceptions(unittest.TestCase):
    def peer_frame(self, focal_buy, peer_buys, n_weeks=5):
        specs = [{"id": f"P{j}", "opened": "2020-01-06", "rows": conv_rows(lambda i, b=b: b)} for j, b in enumerate(peer_buys)]
        specs.append({"id": "F", "opened": "2020-01-06", "rows": conv_rows(lambda i: focal_buy)})
        return build(specs, n_weeks)[0]

    def test_PY_EXC_01_rule_a_boundaries(self):
        r = E.get_row(self.peer_frame(45, [50] * 6), "F", wk(4))     # exactly 10% below median and below P25
        self.assertTrue(r["conversion_rule_a"])
        r = E.get_row(self.peer_frame(46, [50] * 6), "F", wk(4))     # 8% below median
        self.assertFalse(r["conversion_rule_a"])
        r = E.get_row(self.peer_frame(43, [40, 40, 50, 50, 50, 50]), "F", wk(4))  # >=10% below median but not below P25 (0.425)
        self.assertFalse(r["conversion_rule_a"])
        r = E.get_row(self.peer_frame(45, [50] * 4), "F", wk(4))     # only 4 peers and no 8-week baseline yet
        self.assertFalse(r["conversion_a_eval"])
        self.assertEqual(r["conversion_exc_state"], "unavailable")
        r = E.get_row(self.peer_frame(45, [50] * 4, n_weeks=16), "F", wk(15))  # baseline exists: own-baseline rule only
        self.assertFalse(r["conversion_a_eval"])
        self.assertTrue(r["conversion_b_eval"])
        self.assertEqual(r["conversion_exc_state"], "no_flag_own_baseline_only")

    def test_PY_EXC_02_rule_b_three_consecutive_weeks_and_interruption(self):
        drop = lambda i: 60 if i < 12 else 40  # noqa: E731
        sw, _ = build([{"id": "B", "opened": "2020-01-06", "rows": conv_rows(drop)}], 17)
        runs = [int(E.get_row(sw, "B", wk(i))["conversion_b_run"]) for i in range(11, 17)]
        self.assertEqual(runs, [0, 0, 1, 2, 3, 4])
        self.assertFalse(E.get_row(sw, "B", wk(14))["conversion_rule_b"])
        self.assertTrue(E.get_row(sw, "B", wk(15))["conversion_rule_b"])
        red = lambda i, a: dict(conv_rows(drop)(i, a), **({"data_completeness_pct": 80.0} if i == 14 else {}))  # noqa: E731
        sw2, _ = build([{"id": "B", "opened": "2020-01-06", "rows": red}], 17)
        self.assertFalse(sw2["conversion_rule_b"].any())
        self.assertEqual([int(E.get_row(sw2, "B", wk(i))["conversion_b_run"]) for i in (13, 14, 15, 16)], [1, 0, 1, 2])

    def test_PY_EXC_03_stage_grouping_keeps_every_kpi(self):
        latest = {(f["store_id"], f["stage"]): f for f in E.stage_flags(SW, "2026-08-17")}
        for sid in ["SYN-025", "SYN-026", "SYN-027", "SYN-028"]:
            self.assertEqual(latest[(sid, "Fulfilment")]["kpis"], ["on_time", "turnaround"])
        self.assertNotIn(("SYN-029", "Fulfilment"), latest)
        self.assertNotIn(("SYN-030", "Fulfilment"), latest)

    def test_PY_EXC_04_consecutive_runs_defined_every_week(self):
        for k in E.EXCEPTION_KPIS:
            for sid, s in SW.sort_values("week_start").groupby("store_id"):
                prev = 0
                for _, r in s.iterrows():
                    expect = prev + 1 if r[f"{k}_flag"] else 0
                    self.assertEqual(int(r[f"{k}_flag_run"]), expect)
                    prev = expect

    def test_PY_EXC_05_exception_states(self):
        self.assertEqual(row("SYN-022", "2026-05-25")["conversion_exc_state"], "unavailable")
        self.assertEqual(row("SYN-030", "2026-08-17")["conversion_exc_state"], "no_flag_own_baseline_only")
        self.assertEqual(row("SYN-030", "2026-08-17")["recall_rate_exc_state"], "not_eligible")
        self.assertEqual(row("SYN-005", "2026-05-25")["conversion_exc_state"], "flag")
        self.assertTrue(row("SYN-005", "2026-05-25")["conversion_rule_b"])
        self.assertEqual(row("SYN-014", "2026-08-17")["conversion_exc_state"], "no_flag")

    def test_PY_EXC_06_recall_eligibility(self):
        elig = SW[SW["recall_rate_flag"]]
        self.assertTrue((elig["maturity_cohort"] != "New").all())
        self.assertTrue((elig["recall_rate_d4"] >= 40).all())


# ---------------------------------------------------------------------------------------------- ramp
def ramp_specs(focal_exams, red_age=None):
    specs = [{"id": f"P{j}", "opened": "2026-01-05", "fmt": "Grocery-hosted", "rows": lambda i, a: {"completed_exams": 75}} for j in range(5)]
    specs.append({"id": "F", "opened": "2026-01-05", "fmt": "Grocery-hosted",
                  "rows": lambda i, a: dict({"completed_exams": focal_exams, "purchasing_customers": 30}, **({"data_refresh_status": "Stale"} if a == red_age else {}))})
    return specs


class Ramp(unittest.TestCase):
    def test_PY_RAMP_01_persistence_boundary_and_interruption(self):
        sw, _ = build(ramp_specs(52), 10)          # index 69.3 from age 3
        ages = {int(r["weeks_since_opening"]): r for _, r in sw[sw["store_id"] == "F"].iterrows()}
        self.assertEqual([int(ages[a]["ramp_below_run"]) for a in range(3, 8)], [1, 2, 3, 4, 5])
        self.assertFalse(ages[5]["ramp_flag"])
        self.assertTrue(ages[6]["ramp_flag"])
        sw, _ = build(ramp_specs(60), 10)          # index exactly 80: not below
        self.assertFalse(sw[sw["store_id"] == "F"]["ramp_flag"].any())
        self.assertAlmostEqual(E.get_row(sw, "F", wk(5))["ramp_index"], 80.0, places=9)
        sw, _ = build(ramp_specs(52, red_age=5), 10)  # Red week breaks the run
        ages = {int(r["weeks_since_opening"]): r for _, r in sw[sw["store_id"] == "F"].iterrows()}
        self.assertEqual([int(ages[a]["ramp_below_run"]) for a in range(3, 10)], [1, 2, 0, 1, 2, 3, 4])
        self.assertEqual(ages[5]["ramp_state"], "red")
        self.assertTrue(ages[9]["ramp_flag"])
        self.assertFalse(any(ages[a]["ramp_flag"] for a in range(3, 9)))

    def test_PY_RAMP_02_dataset_ramp_records(self):
        young = SW[(SW["weeks_since_opening"] >= 3) & (SW["weeks_since_opening"] <= 104)]
        self.assertTrue(young["ramp_state"].isin(["ok", "red", "insufficient_history", "peer_suppressed"]).all())
        self.assertTrue((SW.loc[SW["weeks_since_opening"] > 104, "ramp_state"] == "not_eligible").all())
        self.assertAlmostEqual(row("SYN-014", "2026-08-17")["ramp_index"], 102.19, places=1)
        stores_with_curves = set(young["store_id"])
        self.assertGreater(len(stores_with_curves), 2)


# ---------------------------------------------------------------------------------------------- definitions and safety
class DefinitionsAndSafety(unittest.TestCase):
    def test_PY_DEF_01_turnaround_simplification_documented_and_applied(self):
        cols = set(pd.read_csv(os.path.join(ROOT, "data", "synthetic_store_weekly.csv"), nrows=1).columns)
        self.assertNotIn("orders_ready", cols)  # no orders-ready count exists: all placed orders assumed ready
        self.assertTrue((DATA.loc[DATA["orders_placed"] > 0, "average_turnaround_days"] > 0).all())
        f = DATA[DATA["week_start"] == pd.Timestamp("2026-08-17")]
        self.assertAlmostEqual(E.pooled(f)["turnaround"], (f["average_turnaround_days"] * f["orders_placed"]).sum() / f["orders_placed"].sum(), places=12)
        self.assertIn("Synthetic simplification", E.KPI_HELP["turnaround"]["limitations"])

    def test_PY_DEF_02_negative_revenue_allowed_by_calculation(self):
        sw, _ = build([{"id": "V", "opened": "2020-01-06", "rows": lambda i, a: {"eyewear_revenue": -2000.0} if i == 3 else {}}], 4)
        r = E.get_row(sw, "V", wk(3))
        self.assertEqual(r["rev_per_exam_state"], "ok")
        self.assertAlmostEqual(r["rev_per_exam_r4"], (9000 * 3 - 2000) / 300, places=9)

    def test_PY_SAFE_01_empty_and_zero_denominators(self):
        p = E.pooled(DATA.iloc[0:0])
        self.assertEqual(p["stores"], 0)
        self.assertIsNone(p["utilization"])
        self.assertIsNone(p["exams_per_store_week"])
        z = DATA.head(1).copy()
        z[["available_appointment_slots", "booked_appointments", "cancelled_appointments", "held"]] = 0
        self.assertIsNone(E.pooled(z)["utilization"])

    def test_PY_JSON_01_summary_is_strict_json_and_red_rows_null(self):
        with open(os.path.join(ROOT, "data", "analysis_summary.json"), encoding="utf-8") as fh:
            text = fh.read()
        for bad in ("NaN", "Infinity"):
            self.assertNotIn(bad, text)
        d = json.loads(text)
        red = [r for r in d["store_weekly"]["SYN-022"] if r["dq"] == "Red"]
        self.assertEqual(len(red), 3)
        self.assertTrue(all(r["k"][k]["v"] is None for r in red for k in r["k"]))
        self.assertEqual(d["meta"]["versions"]["exception_rules"], "v0.2")
        self.assertTrue(all(c["passed"] for c in d["checks"]))
        self.assertEqual(len(d["checks"]), 32)


if __name__ == "__main__":
    unittest.main(verbosity=2)
