import re, glob, collections, os
files = sorted(glob.glob("phase-*.md"))
fam = ["BO","BR","FR","NFR","DR","PR","SR","KPI","US","UAT","SH","A","U","DQ","EV","TQ","CP","MDM"]
pat = re.compile(r'(?<![A-Za-z0-9-])(' + "|".join(sorted(fam, key=len, reverse=True)) + r')-(\d{1,2})(?![0-9])')
where = collections.defaultdict(set)
for f in files:
    txt = open(f, encoding="utf-8").read()
    for m in pat.finditer(txt):
        where[(m.group(1), int(m.group(2)))].add(os.path.basename(f)[6:8])
for fm in fam:
    ids = sorted(n for (f_, n) in where if f_ == fm)
    if not ids: continue
    gaps = [i for i in range(1, max(ids)+1) if i not in ids]
    print(f"{fm}: 1..{max(ids)} count={len(ids)} gaps={gaps}")
print()
# For key families show which phases mention each
for fm in ["BO","BR","FR","NFR","DR","PR","SR","KPI","US","UAT"]:
    for n in sorted(n for (f_, n) in where if f_ == fm):
        print(f"{fm}-{n:02d}: phases {sorted(where[(fm,n)])}")
