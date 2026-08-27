#!/usr/bin/env python3
"""Build the one-page learner entry sheet used as Zenodo's default preview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas


DEFAULT_AUTHORITY = (
    Path(__file__).resolve().parent.parent
    / "backend"
    / "authority"
    / "curriculum-authority-v1.json"
)


def centered(canvas: Canvas, text: str, y: float, font: str, size: float, color) -> None:
    canvas.setFont(font, size)
    canvas.setFillColor(color)
    canvas.drawString((A4[0] - stringWidth(text, font, size)) / 2, y, text)


def load_catalog(authority_path: Path | None, catalog_path: Path | None) -> dict[str, Any]:
    if authority_path is not None and catalog_path is not None:
        raise ValueError("use either --authority or --catalog, not both")
    source = (catalog_path or authority_path or DEFAULT_AUTHORITY).resolve()
    document = json.loads(source.read_text(encoding="utf-8"))
    catalog = document.get("catalog", document)
    if not isinstance(catalog, dict) or not isinstance(catalog.get("program"), dict):
        raise ValueError(f"catalog metadata is absent from {source}")
    if not isinstance(catalog.get("courses"), list) or not catalog["courses"]:
        raise ValueError(f"course catalog is absent or empty in {source}")
    return catalog


def catalog_stats(catalog: dict[str, Any]) -> dict[str, Any]:
    courses = catalog["courses"]
    program = catalog["program"]
    ids = [course.get("id") for course in courses]
    if any(not isinstance(course_id, str) or not course_id for course_id in ids):
        raise ValueError("every course must have a non-empty ID")
    if len(ids) != len(set(ids)):
        raise ValueError("course IDs must be unique")
    completed = [course for course in courses if course.get("state") == "published"]
    readers = [course for course in courses if course.get("reader")]
    levels = sorted({course.get("level") for course in courses})
    if any(not isinstance(level, str) or not level for level in levels):
        raise ValueError("every course must have a non-empty level")
    declared_counts = catalog.get("counts", {})
    checks = {
        "courseRoles": len(courses),
        "completedPublicCourseRoles": len(completed),
    }
    for key, actual in checks.items():
        declared = declared_counts.get(key)
        if declared is not None and declared != actual:
            raise ValueError(f"catalog count {key}={declared!r} does not match {actual}")
    completed_ids = program.get("completedPublicCourseRoleIds")
    if completed_ids is not None and completed_ids != [course["id"] for course in completed]:
        raise ValueError("completed course IDs do not match published course states")
    site_url = program.get("website")
    concept_url = program.get("zenodoConcept")
    if not isinstance(site_url, str) or not site_url.startswith("https://"):
        raise ValueError("program.website must be an HTTPS learner route")
    if not isinstance(concept_url, str) or not concept_url.startswith("https://doi.org/"):
        raise ValueError("program.zenodoConcept must be a DOI URL")
    return {
        "courses": len(courses),
        "levels": len(levels),
        "html_readers": len(readers),
        "completed": len(completed),
        "site_url": site_url,
        "concept_url": concept_url,
    }


def build(output: Path, version: str, catalog: dict[str, Any]) -> None:
    stats = catalog_stats(catalog)
    site_url = stats["site_url"]
    concept_url = stats["concept_url"]
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
    canvas.drawString(64, height - 220, site_url)
    canvas.setFont("Helvetica", 10.5)
    canvas.setFillColor(ink)
    canvas.drawString(64, height - 247, "Pilih titik mulai, ikuti prasyarat, lalu buka pembaca HTML atau PDF.")
    canvas.linkURL(site_url, (44, height - 276, width - 44, height - 160), relative=0, thickness=0)

    qr_widget = qr.QrCodeWidget(site_url)
    bounds = qr_widget.getBounds()
    qr_size = 82
    scale = qr_size / max(bounds[2] - bounds[0], bounds[3] - bounds[1])
    drawing = Drawing(qr_size, qr_size, transform=[scale, 0, 0, scale, 0, 0])
    drawing.add(qr_widget)
    drawing.drawOn(canvas, width - 142, height - 259)

    stats_y = height - 326
    stat_cells = [
        (str(stats["courses"]), "mata kuliah"),
        (str(stats["levels"]), "tingkat belajar"),
        (str(stats["html_readers"]), "pembaca HTML"),
        (str(stats["completed"]), "peran selesai"),
    ]
    cell_w = (width - 88) / len(stat_cells)
    for index, (number, label) in enumerate(stat_cells):
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
    canvas.drawString(44, 68, f"Snapshot {version} - arsip konsep: {concept_url}")
    canvas.drawRightString(width - 44, 68, "Bahasa Indonesia - akses terbuka")
    canvas.linkURL(concept_url, (44, 56, 340, 82), relative=0, thickness=0)

    canvas.showPage()
    canvas.save()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--authority",
        type=Path,
        help=f"curriculum authority JSON (default: {DEFAULT_AUTHORITY})",
    )
    parser.add_argument("--catalog", type=Path, help="standalone catalog JSON")
    args = parser.parse_args()
    catalog = load_catalog(args.authority, args.catalog)
    catalog_version = catalog["program"].get("version")
    if catalog_version != args.version:
        raise ValueError(
            f"requested PDF version {args.version!r} does not match catalog version {catalog_version!r}"
        )
    build(args.output, args.version, catalog)


if __name__ == "__main__":
    main()
