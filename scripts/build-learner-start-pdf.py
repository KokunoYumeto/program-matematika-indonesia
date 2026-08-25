#!/usr/bin/env python3
"""Build the one-page learner entry sheet used as Zenodo's default preview."""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


SITE_URL = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
CONCEPT_URL = "https://doi.org/10.5281/zenodo.22059707"


def centered(canvas: Canvas, text: str, y: float, font: str, size: float, color) -> None:
    canvas.setFont(font, size)
    canvas.setFillColor(color)
    canvas.drawString((A4[0] - stringWidth(text, font, size)) / 2, y, text)


def build(output: Path, version: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(output), pagesize=A4, pageCompression=1)
    canvas.setTitle("Mulai belajar - Program Matematika Indonesia")
    canvas.setAuthor("Program Matematika Indonesia; OpenAI Codex gpt-5.6-sol, Ultra")
    canvas.setSubject("Pintu masuk untuk pelajar ke kurikulum matematika terbuka Bahasa Indonesia")

    width, height = A4
    navy = HexColor("#17243A")
    blue = HexColor("#245DA8")
    green = HexColor("#2E7D5A")
    pale = HexColor("#EEF4FA")
    ink = HexColor("#182234")
    muted = HexColor("#526176")

    canvas.setFillColor(navy)
    canvas.rect(0, height - 126, width, 126, stroke=0, fill=1)
    centered(canvas, "PROGRAM MATEMATIKA INDONESIA", height - 49, "Helvetica-Bold", 13, HexColor("#A9C7EE"))
    centered(canvas, "Mulai belajar matematika", height - 88, "Helvetica-Bold", 27, white)
    centered(canvas, "Dari fondasi sampai kesiapan riset", height - 111, "Helvetica", 13, HexColor("#D8E5F5"))

    canvas.setFillColor(pale)
    canvas.roundRect(44, height - 276, width - 88, 116, 12, stroke=0, fill=1)
    canvas.setFillColor(blue)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(64, height - 192, "Buka situs pembelajaran")
    canvas.setFont("Helvetica-Bold", 10.4)
    canvas.drawString(64, height - 220, SITE_URL)
    canvas.setFont("Helvetica", 10.5)
    canvas.setFillColor(ink)
    canvas.drawString(64, height - 247, "Pilih titik mulai, ikuti prasyarat, lalu buka pembaca HTML atau PDF.")
    canvas.linkURL(SITE_URL, (44, height - 276, width - 44, height - 160), relative=0, thickness=0)

    qr_widget = qr.QrCodeWidget(SITE_URL)
    bounds = qr_widget.getBounds()
    qr_size = 82
    scale = qr_size / max(bounds[2] - bounds[0], bounds[3] - bounds[1])
    drawing = Drawing(qr_size, qr_size, transform=[scale, 0, 0, scale, 0, 0])
    drawing.add(qr_widget)
    drawing.drawOn(canvas, width - 142, height - 259)

    stats_y = height - 326
    stats = [("40", "mata kuliah"), ("4", "tingkat belajar"), ("13", "pembaca HTML"), ("16", "peran selesai")]
    cell_w = (width - 88) / len(stats)
    for index, (number, label) in enumerate(stats):
        x = 44 + index * cell_w
        canvas.setFillColor(green if index % 2 == 0 else blue)
        canvas.setFont("Helvetica-Bold", 22)
        canvas.drawCentredString(x + cell_w / 2, stats_y, number)
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica", 9.5)
        canvas.drawCentredString(x + cell_w / 2, stats_y - 19, label)

    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(44, height - 397, "Tiga pintu masuk")
    entries = [
        ("A00", "Perbaiki fondasi", "Bilangan, pecahan, rasio, pengukuran, dan aljabar awal."),
        ("A30", "Mulai tingkat universitas", "Prakalkulus, lalu kalkulus dan pembuktian sebagai dua jalur dasar."),
        ("C/D", "Sudah fasih dengan bukti", "Pilih inti sarjana atau fondasi pascasarjana dari graf prasyarat."),
    ]
    y = height - 435
    for code, heading, body in entries:
        canvas.setFillColor(blue)
        canvas.roundRect(44, y - 12, 52, 30, 7, stroke=0, fill=1)
        canvas.setFillColor(white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawCentredString(70, y - 1, code)
        canvas.setFillColor(ink)
        canvas.setFont("Helvetica-Bold", 11.5)
        canvas.drawString(111, y + 6, heading)
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica", 9.5)
        canvas.drawString(111, y - 10, body)
        y -= 58

    canvas.setFillColor(HexColor("#FFF4D8"))
    canvas.roundRect(44, 112, width - 88, 82, 10, stroke=0, fill=1)
    canvas.setFillColor(ink)
    canvas.setFont("Helvetica-Bold", 11.5)
    canvas.drawString(62, 169, "Untuk pelajar: gunakan situs di atas.")
    canvas.setFont("Helvetica", 9.5)
    canvas.setFillColor(muted)
    canvas.drawString(62, 149, "JSON, schema, CSV, checksums, dan ZIP backend adalah antarmuka mesin.")
    canvas.drawString(62, 132, "PDF dan EPUB tetap tersedia sebagai format baca atau unduh sekunder.")

    canvas.setStrokeColor(HexColor("#CDD7E5"))
    canvas.line(44, 86, width - 44, 86)
    canvas.setFillColor(muted)
    canvas.setFont("Helvetica", 8.5)
    canvas.drawString(44, 68, f"Snapshot {version} - arsip konsep: {CONCEPT_URL}")
    canvas.drawRightString(width - 44, 68, "Bahasa Indonesia - akses terbuka")
    canvas.linkURL(CONCEPT_URL, (44, 56, 340, 82), relative=0, thickness=0)

    canvas.showPage()
    canvas.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    build(args.output, args.version)


if __name__ == "__main__":
    main()
