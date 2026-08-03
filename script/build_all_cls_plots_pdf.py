#!/usr/bin/env python3
"""Bundle all completed core-level-shift spectra into one bookmarked PDF."""

from datetime import date
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


ROOT = Path("/Users/behnamazizi/Downloads/core level shifts")
OUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
OUT = OUT_DIR / "all_core_level_shift_plots_comparison.pdf"
COVER = TMP_DIR / "all_cls_cover.pdf"

SOURCES = [
    ("Planar - selected C 1s envelopes",
     ROOT / "planar/figures/planar_selected_C_envelopes.pdf"),
    ("Planar vs planar-COOH - all C 1s envelopes",
     ROOT / "planarCOOH/figures/planar_vs_PLDC_COOH_all_carbon_envelopes_zoomed.pdf"),
    ("Planar vs planar-COOH - N 1s envelopes",
     ROOT / "planarCOOH/figures/planar_vs_PLDC_COOH_N1s_envelopes.pdf"),
    ("Cross - C 1s envelopes", ROOT / "cross/figures/cross_C1s_envelopes.pdf"),
    ("Cross - N 1s envelopes", ROOT / "cross/figures/cross_N1s_envelopes.pdf"),
    ("TwistedH2 - C 1s envelopes", ROOT / "twistedH2/figures/twistedH2_C1s_envelopes.pdf"),
    ("TwistedH2 - N 1s envelopes", ROOT / "twistedH2/figures/twistedH2_N1s_envelopes.pdf"),
    ("TwistedO2 - C 1s envelopes", ROOT / "twistedO2/figures/twistedO2_C1s_envelopes.pdf"),
    ("TwistedO2 - N 1s envelopes", ROOT / "twistedO2/figures/twistedO2_N1s_envelopes.pdf"),
    ("TWco - C 1s envelopes", ROOT / "TWco/figures/TWco_C1s_envelopes.pdf"),
    ("TWco - N 1s envelopes", ROOT / "TWco/figures/TWco_N1s_envelopes.pdf"),
    ("TWDCOH - C 1s envelopes", ROOT / "TWDCOH/figures/TWDCOH_C1s_envelopes.pdf"),
    ("TWDCOH - N 1s envelopes", ROOT / "TWDCOH/figures/TWDCOH_N1s_envelopes.pdf"),
    ("Five-structure C 1s comparison",
     ROOT / "comparison_remaining/remaining_structures_C1s_comparison.pdf"),
    ("Five-structure N 1s comparison",
     ROOT / "comparison_remaining/remaining_structures_N1s_comparison.pdf"),
    ("Twisted structures - C 1s comparison",
     ROOT / "comparison_remaining/twisted_C1s_comparison.pdf"),
    ("Twisted structures - N 1s comparison",
     ROOT / "comparison_remaining/twisted_N1s_comparison.pdf"),
]


def make_cover() -> None:
    width, height = landscape(letter)
    c = canvas.Canvas(str(COVER), pagesize=(width, height))
    navy = HexColor("#173F5F")
    blue = HexColor("#4E79A7")
    orange = HexColor("#F28E2B")
    gray = HexColor("#4B5563")

    c.setFillColor(navy)
    c.rect(0, height - 22, width, 22, stroke=0, fill=1)
    c.setFillColor(blue)
    c.rect(0, 0, width * 0.58, 10, stroke=0, fill=1)
    c.setFillColor(orange)
    c.rect(width * 0.58, 0, width * 0.42, 10, stroke=0, fill=1)

    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 29)
    c.drawString(56, height - 102, "Core-Level-Shift Plot Comparison")
    c.setFillColor(gray)
    c.setFont("Helvetica", 15)
    c.drawString(58, height - 133, "Initial-state C 1s and N 1s spectra")

    c.setFillColor(HexColor("#F3F6F9"))
    c.roundRect(56, 178, width - 112, 225, 12, stroke=0, fill=1)
    c.setFillColor(navy)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(78, 374, "Included systems")
    c.setFillColor(gray)
    c.setFont("Helvetica", 12)
    systems = [
        "Planar and planar-COOH comparison",
        "Cross",
        "TwistedH2 and TwistedO2",
        "TWco and TWDCOH",
        "Five-structure and focused twisted comparisons",
    ]
    y = 346
    for item in systems:
        c.setFillColor(orange)
        c.circle(83, y + 3, 3.5, stroke=0, fill=1)
        c.setFillColor(gray)
        c.drawString(96, y, item)
        y -= 30

    c.setFillColor(gray)
    c.setFont("Helvetica", 10.5)
    c.drawString(58, 125, "The individual spectra are retained at their original vector quality.")
    c.drawString(58, 108, "PDF bookmarks provide direct navigation to every plot.")
    c.setFont("Helvetica-Oblique", 9.5)
    c.drawRightString(width - 58, 55, f"Compiled {date.today().isoformat()}")
    c.showPage()
    c.save()


def build() -> None:
    missing = [str(path) for _, path in SOURCES if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing source PDFs:\n" + "\n".join(missing))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    make_cover()

    writer = PdfWriter()
    cover_reader = PdfReader(str(COVER))
    writer.add_page(cover_reader.pages[0])
    writer.add_outline_item("Cover", 0)

    for title, path in SOURCES:
        reader = PdfReader(str(path))
        start_page = len(writer.pages)
        for page in reader.pages:
            writer.add_page(page)
        writer.add_outline_item(title, start_page)

    writer.add_metadata({
        "/Title": "Core-Level-Shift Plot Comparison",
        "/Subject": "Initial-state C 1s and N 1s core-level-shift spectra",
        "/Author": "Quantum ESPRESSO core-level-shift project",
        "/Creator": "build_all_cls_plots_pdf.py",
    })
    with OUT.open("wb") as stream:
        writer.write(stream)

    # Reopen as a structural integrity check before reporting success.
    check = PdfReader(str(OUT))
    expected_pages = 1 + sum(len(PdfReader(str(path)).pages) for _, path in SOURCES)
    if len(check.pages) != expected_pages:
        raise RuntimeError(f"Expected {expected_pages} pages, found {len(check.pages)}")
    print(f"Created {OUT}")
    print(f"Pages: {len(check.pages)}")


if __name__ == "__main__":
    build()
