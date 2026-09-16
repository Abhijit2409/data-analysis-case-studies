"""Build the LinkedIn image on where 'Unknown' closures come from (plus the admin-type sensitivity check) and render it with Edge."""
import pathlib
import subprocess
from openpyxl import load_workbook

ROOT = pathlib.Path(__file__).resolve().parents[2]
WB = ROOT / "outputs" / "Vancouver311_Closure_Outcomes_Workbook.xlsx"
OUT_DIR = ROOT / "outputs" / "v2_redesign"
HTML = OUT_DIR / "LinkedIn_Unknown_Closures_source.html"
PNG = OUT_DIR / "LinkedIn_Unknown_Closures.png"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
NAVY, TEAL, LIGHT = "#1D3557", "#2A9D8F", "#D5DAE0"

wb = load_workbook(WB, data_only=True, read_only=True)
A, DQ = wb["Analysis"], wb["Data_Quality_Log"]
a = lambda ref: A[ref].value

assert a("A107") == "H. Where 'Unknown' closures come from"
assert [a(f"{c}108") for c in "ABCDEF"] == ["Request type", "Closed as 'Unknown'", "Closed cases of this type", "Unknown rate within type",
                                            "Share of all 'Unknown'", "Admin/internal-sounding?"]
def unk(r, label):
    assert a(f"A{r}") == label
    return {"n": a(f"B{r}"), "closed": a(f"C{r}"), "rate": a(f"D{r}"), "share": a(f"E{r}"), "admin": a(f"F{r}")}
bins = unk(109, "Garbage Bin Request Case")
park = unk(110, "Parking Enforcement Transfer Case")
assert a("A113") == "Top two request types' share of all 'Unknown' closures"
top2 = a("B113")

assert a("A20") == "5. Unknown or N/A" and a("A16") == "1. Service recorded as provided" and a("A22") == "Total closed"
UNK_ALL, UNK_S, UNK_SX = a("B20"), a("C20"), a("E20")
SP_S, SP_SX = a("C16"), a("E16")
CLOSED_X = a("D22")
assert DQ["B18"].value == "Administrative/internal-sounding types"
ADMIN_N = DQ["D18"].value

others_n = UNK_ALL - bins["n"] - park["n"]
assert abs(others_n / UNK_ALL - (1 - top2)) < 1e-9
assert (UNK_ALL, f"{top2:.1%}", f"{UNK_S:.1%}", f"{UNK_SX:.1%}", f"{SP_S:.1%}", f"{SP_SX:.1%}", ADMIN_N, CLOSED_X) == \
       (15971, "99.4%", "5.9%", "3.6%", "57.5%", "60.2%", 12033, 257765)
assert bins["admin"] == "No" and park["admin"] == "Yes"

BAR_W = 928
def detail(name, d, tag, colour):
    return f"""<div class="type">
 <div class="top"><span class="name"><i style="background:{colour}"></i>{name}</span><span class="share">{d['share']:.1%} of all &ldquo;Unknown&rdquo;</span></div>
 <div class="line">{d['n']:,} of its {d['closed']:,} closed cases recorded &ldquo;Unknown&rdquo;</div>
 <div class="track"><div class="fill" style="width:{d['rate'] * 100:.2f}%;background:{colour}"></div><span class="rate">{d['rate']:.1%}</span></div>
 {f'<div class="tag">{tag}</div>' if tag else ''}
</div>"""

page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Unknown closures card</title>
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: #FFFFFF; }}
body {{ width: 1080px; height: 1350px; overflow: hidden; font-family: "Segoe UI", Arial, sans-serif; color: #1F2933; }}
.card {{ position: relative; height: 1350px; padding: 58px 76px 0; }}
.kicker {{ font-size: 20px; letter-spacing: 2.4px; text-transform: uppercase; color: #1F7A70; font-weight: 600; margin: 0 0 12px; }}
h1 {{ font-size: 50px; line-height: 1.12; color: {NAVY}; margin: 0 0 16px; font-weight: 700; letter-spacing: -0.5px; }}
.dek {{ font-size: 24px; line-height: 1.4; color: #3E4C59; margin: 0 0 16px; }}
.split {{ display: flex; height: 58px; border-radius: 4px; overflow: hidden; margin: 0 0 8px; }}
.split div {{ height: 58px; color: #FFFFFF; font-size: 24px; font-weight: 700; line-height: 58px; padding-left: 14px; white-space: nowrap; overflow: hidden; }}
.split-labels {{ display: flex; justify-content: space-between; font-size: 19px; color: #616E7C; margin: 0 0 26px; }}
.type {{ border-top: 1.5px solid #E4E7EB; padding: 16px 0 14px; }}
.top {{ display: flex; justify-content: space-between; align-items: baseline; }}
.name {{ font-size: 27px; font-weight: 700; color: {NAVY}; }}
.name i {{ display: inline-block; width: 20px; height: 20px; border-radius: 3px; margin-right: 10px; vertical-align: -1px; }}
.share {{ font-size: 23px; font-weight: 700; color: {NAVY}; }}
.line {{ font-size: 22px; color: #3E4C59; margin: 4px 0 8px; }}
.track {{ position: relative; height: 34px; background: #F0F2F5; border-radius: 3px; }}
.fill {{ height: 34px; border-radius: 3px; }}
.rate {{ position: absolute; left: 12px; top: 0; line-height: 34px; font-size: 20px; font-weight: 700; color: #FFFFFF; }}
.tag {{ font-size: 18px; color: #616E7C; margin-top: 6px; }}
h2 {{ font-size: 27px; color: {NAVY}; margin: 22px 0 12px; font-weight: 700; }}
.stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
.stat {{ background: #F5F7FA; border-top: 5px solid #8D99AE; padding: 12px 20px; }}
.stat .l {{ font-size: 21px; color: #3E4C59; }}
.stat .v {{ font-size: 40px; font-weight: 700; color: {NAVY}; line-height: 1.2; }}
.stat .v span {{ color: #8D99AE; font-weight: 600; margin: 0 8px; }}
.note {{ font-size: 18px; color: #616E7C; line-height: 1.4; margin: 10px 0 0; }}
.callout {{ margin-top: 20px; background: #EEF6F5; border-left: 8px solid {TEAL}; padding: 14px 22px; font-size: 22px; line-height: 1.4; }}
.callout b {{ color: {NAVY}; }}
footer {{ position: absolute; left: 76px; right: 76px; bottom: 30px; display: flex; justify-content: space-between; gap: 30px;
  font-size: 17px; color: #7B8794; border-top: 1.5px solid #E4E7EB; padding-top: 12px; }}
</style></head>
<body><div class="card">
<div class="kicker">Vancouver 3-1-1 &middot; &ldquo;Unknown&rdquo; closures &middot; 2025</div>
<h1>{UNK_ALL:,} closures say &ldquo;Unknown.&rdquo; {top2:.1%} come from two request types.</h1>
<p class="dek">Where the {UNK_ALL:,} closed cases recorded as &ldquo;Unknown&rdquo; come from:</p>
<div class="split">
 <div style="width:{bins['share'] * BAR_W:.1f}px;background:{NAVY}">{bins['share']:.1%}</div>
 <div style="width:{park['share'] * BAR_W:.1f}px;background:{TEAL}">{park['share']:.1%}</div>
 <div style="width:{(1 - top2) * BAR_W:.1f}px;background:{LIGHT}"></div>
</div>
<div class="split-labels"><span>Garbage bin requests &middot; Parking enforcement transfers</span><span>All other types: {others_n:,} ({1 - top2:.1%})</span></div>

{detail("Garbage Bin Request", bins, "", NAVY)}
{detail("Parking Enforcement Transfer", park, "One of four request types the study flags as administrative-sounding (a name-based rule)", TEAL)}

<h2>Set the four flagged types aside, and the split shifts</h2>
<div class="stats">
 <div class="stat"><div class="l">&ldquo;Unknown&rdquo; share of closed cases</div><div class="v">{UNK_S:.1%}<span>&rarr;</span>{UNK_SX:.1%}</div></div>
 <div class="stat"><div class="l">&ldquo;Service provided&rdquo; share</div><div class="v">{SP_S:.1%}<span>&rarr;</span>{SP_SX:.1%}</div></div>
</div>
<p class="note">Sensitivity check: excludes {ADMIN_N:,} records in the four flagged types; {CLOSED_X:,} closed cases remain. The flag is the analyst&rsquo;s rule, not a City classification.</p>

<div class="callout"><b>Needs confirmation with City staff:</b> whether &ldquo;Unknown&rdquo; is a default for some intake paths. The public data doesn&rsquo;t say why.</div>

<footer><span>Independent analysis of City of Vancouver open data. Not affiliated with or endorsed by the City.</span><span>Abhijit Mishra</span></footer>
</div></body></html>
"""
HTML.write_text(page, encoding="utf-8")
subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                "--window-size=1080,1350", f"--screenshot={PNG}", HTML.resolve().as_uri()], check=True, timeout=120)
print("bins:", bins, "| park:", park, "| others:", others_n, f"({1 - top2:.2%})")
print("sensitivity:", f"Unknown {UNK_S:.1%} -> {UNK_SX:.1%}; SP {SP_S:.1%} -> {SP_SX:.1%}; admin records {ADMIN_N:,}; closed remaining {CLOSED_X:,}")
print("wrote", PNG, PNG.stat().st_size)
