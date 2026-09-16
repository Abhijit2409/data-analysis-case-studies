"""Step 4 - Report charts (SVG, text kept as text) built only from build/results.json."""
import json
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import GROUPS, SHORT, G1, G2, G3

ROOT = pathlib.Path(__file__).resolve().parents[1]
R = json.loads((ROOT / "build" / "results.json").read_text())
OUT = ROOT / "build" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# Validated categorical palette (fixed order; colour follows the outcome group everywhere).
COL = dict(zip(GROUPS, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]))
LIGHT_FILLS = {"#1baf7a", "#eda100", "#e87ba4"}          # below 3:1 -> dark ink labels
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({
    "font.family": ["Segoe UI", "Arial", "sans-serif"], "font.size": 7.5, "svg.fonttype": "none",
    "axes.edgecolor": BASE, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0, "figure.facecolor": "white", "axes.facecolor": "white",
})

def save(fig, name):
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)

def seg_label_color(c):
    return INK if c in LIGHT_FILLS else "white"

# ---- 1. Citywide closed-case outcome groups
g = R["outcomes_all"]["groups"]
fig, ax = plt.subplots(figsize=(3.55, 1.85))
ys = list(range(len(g)))[::-1]
for y, x in zip(ys, g):
    ax.barh(y, x["share"], color=COL[x["group"]], height=0.62)
    ax.text(x["share"] + 0.01, y, f'{x["share"]:.1%}  ({x["count"]:,})', va="center", color=INK, fontsize=7.2)
ax.set_yticks(ys, [x["short"] for x in g])
ax.set_xlim(0, 0.8)
ax.xaxis.set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_color(BASE)
save(fig, "ch1_outcome_groups")

# ---- 2. Department outcome mix (12 largest departments by closed cases)
rows = sorted(R["dept_variation"]["rows"], key=lambda r: -r["closed"])[:12]
rows = sorted(rows, key=lambda r: r["Service provided"])
fig, ax = plt.subplots(figsize=(7.4, 2.9))
for i, r in enumerate(rows):
    left = 0.0
    for gname in GROUPS:
        w = r[SHORT[gname]]
        if w <= 0:
            continue
        ax.barh(i, w, left=left, color=COL[gname], height=0.66, edgecolor="white", linewidth=1.0)
        if w >= 0.08:
            ax.text(left + w / 2, i, f"{w:.0%}", ha="center", va="center", fontsize=6.8, color=seg_label_color(COL[gname]))
        left += w
labels = [f'{r["department"]}  ({r["closed"]:,})' for r in rows]
ax.set_yticks(range(len(rows)), labels, fontsize=7)
ax.set_xlim(0, 1)
ax.set_xticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"])
ax.xaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
handles = [plt.Rectangle((0, 0), 1, 1, color=COL[x]) for x in GROUPS]
ax.legend(handles, [SHORT[x] for x in GROUPS], ncol=6, loc="lower left", bbox_to_anchor=(-0.02, 1.0),
          frameon=False, fontsize=6.8, handlelength=1.0, columnspacing=1.1, handletextpad=0.4)
ax.set_xlabel("Share of the department's closed 2025 cases (number of closed cases in brackets)", fontsize=6.8)
save(fig, "ch2_department_mix")

# ---- 3. Monthly recorded demand
m = R["demand"]["by_month"]
fig, ax = plt.subplots(figsize=(3.55, 1.45))
names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
vals = [x["count"] for x in m]
ax.bar(range(12), vals, color=COL[G1], width=0.66)
for i in (vals.index(max(vals)), vals.index(min(vals))):
    ax.text(i, vals[i] + 400, f"{vals[i]:,}", ha="center", va="bottom", fontsize=6.6, color=INK)
ax.set_xticks(range(12), names, fontsize=6.6)
ax.set_ylim(0, max(vals) * 1.18)
ax.yaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
ax.set_yticks([0, 10000, 20000, 30000], ["0", "10k", "20k", "30k"])
ax.spines["left"].set_visible(False)
ax.tick_params(axis="y", labelsize=6.4, colors=MUTED)
save(fig, "ch3_monthly_demand")

# ---- 4. Focus family outcome mix by request type
F = R["focus"]
bt = F["by_type"] + [{"type": "All three types", **{SHORT[x["group"]]: x["share"] for x in F["groups"]}, "closed": F["closed"]}]
fig, ax = plt.subplots(figsize=(3.6, 1.5))
for i, r in enumerate(bt[::-1]):
    left = 0.0
    for gname in GROUPS:
        w = r[SHORT[gname]]
        if not w:
            continue
        ax.barh(i, w, left=left, color=COL[gname], height=0.62, edgecolor="white", linewidth=1.0)
        if w >= 0.08:
            ax.text(left + w / 2, i, f"{w:.0%}", ha="center", va="center", fontsize=6.6, color=seg_label_color(COL[gname]))
        left += w
ax.set_yticks(range(len(bt)), [f'{r["type"].replace(" Case", "")} ({r["closed"]:,})' for r in bt[::-1]], fontsize=6.8)
ax.set_xlim(0, 1)
ax.set_xticks([0, .5, 1], ["0%", "50%", "100%"])
ax.xaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
used = [x for x in GROUPS if any(r[SHORT[x]] for r in bt)]
ax.legend([plt.Rectangle((0, 0), 1, 1, color=COL[x]) for x in used], [SHORT[x] for x in used], ncol=3,
          loc="lower left", bbox_to_anchor=(-0.02, 1.0), frameon=False, fontsize=6.3, handlelength=1.0,
          columnspacing=0.8, handletextpad=0.35)
save(fig, "ch4_family_mix")

# ---- 5. Focus family recorded days to closure: p50-p90 by type and outcome
want = [("Service provided", COL[G1], "Service provided"),
        ("  of which: Further action has been planned", COL[G2], "Further action planned"),
        ("  of which: Referred to another service group", COL[G2], "Referred to another group")]
types = F["types"]
rows = []
for t in types:
    for key, c, lab in want:
        d = next(x for x in F["durations"] if x["type"] == t and x["group"] == key)
        rows.append((t.replace(" Case", ""), lab, c, d))
fig, ax = plt.subplots(figsize=(3.6, 2.1))
ypos, ylab, y = [], [], 0
for k, (t, lab, c, d) in enumerate(rows):
    if k and k % 3 == 0:
        y += 0.6
    yy = -y
    ax.plot([d["p50"], d["p90"]], [yy, yy], color=c, linewidth=2, solid_capstyle="round")
    ax.plot(d["p50"], yy, "o", color=c, markersize=5, markeredgecolor="white", markeredgewidth=1)
    ax.plot(d["p75"], yy, "|", color=c, markersize=6, markeredgewidth=1.4)
    ax.plot(d["p90"], yy, "o", color="white", markersize=4.6, markeredgecolor=c, markeredgewidth=1.4)
    ax.text(d["p90"] + 0.8, yy, f'{d["p50"]} / {d["p75"]} / {d["p90"]}   n={d["n"]:,}', va="center", fontsize=6.2, color=INK2)
    ypos.append(yy)
    ylab.append(f"{t}: {lab}")
    y += 1
ax.set_yticks(ypos, ylab, fontsize=6.5)
ax.set_xlim(0, 40)
ax.set_xlabel("Recorded calendar days to closure", fontsize=6.4)
ax.xaxis.grid(True, color=GRID, linewidth=0.5)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
save(fig, "ch5_family_durations")
print("charts written:", sorted(p.name for p in OUT.glob("*.svg")))
