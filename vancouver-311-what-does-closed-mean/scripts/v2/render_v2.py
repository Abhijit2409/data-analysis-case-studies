"""Render every page of the v2 PDF to PNG for visual inspection."""
import pathlib
import sys
import pypdfium2 as pdfium

ROOT = pathlib.Path(__file__).resolve().parents[2]
PDF = ROOT / "outputs" / "v2_redesign" / "Vancouver311_What_Does_Closed_Mean_v2.pdf"
OUT = ROOT / "build" / "v2_pages"
OUT.mkdir(parents=True, exist_ok=True)
scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.6
doc = pdfium.PdfDocument(str(PDF))
for i in range(len(doc)):
    doc[i].render(scale=scale).to_pil().save(OUT / f"page{i + 1}.png")
print("rendered", len(doc), "pages at scale", scale, "->", OUT)
