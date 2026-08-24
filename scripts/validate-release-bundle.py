#!/usr/bin/env python3
"""Validate a central release bundle before Zenodo upload."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


EXPECTED_MIGRATIONS = {
    "dmoi4-id-0.1.0-to-interlanguage-v1.0.0": {
        "corpus": "Discrete Mathematics: An Open Introduction 4 — Bahasa Indonesia",
        "result": "lossless-zero-copy-pass",
    },
    "o002-b80-id-2026.08.22.1-to-interlanguage-v1.0.0": {
        "corpus": "Komputasi Matematis dan Eksperimen yang Dapat Direproduksi — Bahasa Indonesia",
        "result": "lossless-zero-copy-one-to-one-native-catalog-adapter-pass",
    },
    "openlogic-id-olp-0722-to-interlanguage-v1.0.0": {
        "corpus": "Open Logic Project — OLP-0722, Bahasa Indonesia",
        "result": "deterministic-zero-copy-pass",
    },
    "judson-id-v1-2026.08.21.1": {
        "corpus": "Judson — Abstract Algebra: Theory and Applications, Bahasa Indonesia",
        "result": "additive-zero-copy-pass",
    },
    "yaintt-r014-id-to-interlanguage-v1.0.0": {
        "corpus": "Yet Another Introductory Number Theory Textbook, Bahasa Indonesia",
        "result": "lossless-additive-adapter-pass",
    },
    "r012-applied-combinatorics-id-to-v1": {
        "corpus": "Keller–Trotter — Applied Combinatorics, Bahasa Indonesia",
        "result": "lossless-additive-one-common-record-per-native-record-pass",
    },
    "mathematics-in-lean-id-v4.30.0-id.3-to-interlanguage-v1.0.0": {
        "corpus": "Mathematics in Lean — Bahasa Indonesia v4.30.0-id.3",
        "result": "lossless-zero-copy-one-to-one-pass",
    },
    "prealgebra2e-r001-id-v0.2.7-to-interlanguage-v1.0.0": {
        "corpus": "OpenStax Prealgebra 2e — Bahasa Indonesia v0.2.7",
        "result": "lossless-streaming-zero-copy-adapter-pass",
    },
    "o005-c120-id-v1.01-complete-r5-to-interlanguage-v1.0.0": {
        "corpus": "Lega v1.01 — Pemodelan Matematis, Bahasa Indonesia",
        "result": "lossless-replayable-zero-copy-adapter-pass",
    },
    "o018-c130-r017-book1-id5-to-interlanguage-v1": {
        "corpus": "Open Optimization Book 1 + laboratorium Pyomo/HiGHS O018, Bahasa Indonesia",
        "result": "lossless-zero-copy-one-to-one-plus-segment-variant-projection-pass",
    },
}

MIGRATION_RECEIPT_FILENAMES = {
    "applied-combinatorics-id-v1": "applied-combinatorics-id-backend-v1-migration-receipt.json",
    "dmoi4-id-v1": "dmoi4-id-backend-v1-migration-receipt.json",
    "judson-id-v1": "judson-id-backend-v1-migration-receipt.json",
    "mathematics-in-lean-id-v1": "mathematics-in-lean-id-backend-v1-migration-receipt.json",
    "o002-b80-id-v1": "o002-b80-id-backend-v1-migration-receipt.json",
    "o005-c120-id-v1": "o005-c120-id-backend-v1-migration-receipt.json",
    "o018-c130-id-v1": "o018-c130-id-backend-v1-migration-receipt.json",
    "openlogic-id-v1": "openlogic-id-backend-v1-migration-receipt.json",
    "prealgebra2e-id-v1": "prealgebra2e-id-backend-v1-migration-receipt.json",
    "yaintt-id-v1": "yaintt-id-backend-v1-migration-receipt.json",
}

PRIVATE_BYTE_MARKERS = (
    bytes([70, 108, 111, 114, 105, 115]).lower(),
    bytes([99, 58, 92, 117, 115, 101, 114, 115, 92]),
    bytes([99, 58, 47, 117, 115, 101, 114, 115, 47]),
    bytes([47, 117, 115, 101, 114, 115, 47]),
    bytes([46, 99, 111, 100, 101, 120, 47, 97, 116, 116, 97, 99, 104, 109, 101, 110, 116, 115]),
    bytes([102, 105, 108, 101, 58, 47, 47]),
    b"new " + b"zenodo " + b"token.md",
    b"github " + b"tokens.md",
    b"zenodo " + b"token.md",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def assert_public_bytes(label: str, data: bytes) -> None:
    lowered = data.lower()
    if any(marker in lowered for marker in PRIVATE_BYTE_MARKERS):
        raise ValueError(f"private or credential-bearing marker in public artifact: {label}")


def verify_source_zip(
    path: Path,
    root: Path,
    source_commit: str,
    allowed_generated_source_paths: set[str],
) -> dict:
    tracked_paths = set(
        subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", source_commit],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    commit_bound_entries = 0
    generated_entries = 0
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"source ZIP CRC failure: {bad}")
        names = archive.namelist()
        manifest_bytes = archive.read("SOURCE_MANIFEST.json")
        assert_public_bytes("source ZIP:SOURCE_MANIFEST.json", manifest_bytes)
        manifest = json.loads(manifest_bytes)
        if manifest.get("schema_id") != "program-matematika-indonesia/source-manifest/v2":
            raise ValueError("source ZIP manifest schema is not v2")
        declared = {entry["path"]: entry for entry in manifest["files"]}
        actual = set(names) - {"SOURCE_MANIFEST.json"}
        if set(declared) != actual:
            raise ValueError("source ZIP manifest inventory mismatch")
        for name, entry in declared.items():
            data = archive.read(name)
            if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise ValueError(f"source ZIP entry mismatch: {name}")
            assert_public_bytes(f"source ZIP:{name}", data)
            source_path = entry.get("source_path")
            if not isinstance(source_path, str) or not source_path or source_path.startswith("/") or ".." in Path(source_path).parts:
                raise ValueError(f"source ZIP entry has no portable source_path: {name}")
            if source_path in tracked_paths:
                committed = subprocess.run(
                    ["git", "show", f"{source_commit}:{source_path}"],
                    cwd=root,
                    check=True,
                    capture_output=True,
                ).stdout
                if committed != data:
                    raise ValueError(f"source ZIP entry differs from source commit: {source_path}")
                commit_bound_entries += 1
            elif source_path in allowed_generated_source_paths:
                generated_entries += 1
            else:
                raise ValueError(f"source ZIP entry is neither commit-bound nor admitted generated output: {source_path}")
    return {
        "entries": len(names),
        "manifest_entries": len(declared),
        "source_commit": manifest.get("source_commit"),
        "commit_bound_entries": commit_bound_entries,
        "admitted_generated_entries": generated_entries,
        "privacy_scan": "pass",
        "result": "pass",
    }


def verify_backend_zip(path: Path, package: Path) -> dict:
    prefix = "program-matematika-indonesia-backend-v1/"
    expected = {
        prefix + source.relative_to(package).as_posix(): source
        for source in package.rglob("*")
        if source.is_file()
    }
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"backend ZIP CRC failure: {bad}")
        if set(archive.namelist()) != set(expected):
            raise ValueError("backend ZIP inventory mismatch")
        for name, source in expected.items():
            data = archive.read(name)
            if data != source.read_bytes():
                raise ValueError(f"backend ZIP entry mismatch: {name}")
            assert_public_bytes(f"backend ZIP:{name}", data)
    return {"entries": len(expected), "privacy_scan": "pass", "result": "pass"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--record-id", required=True, type=int)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--release-dir", required=True, type=Path)
    parser.add_argument("--backend-package", required=True, type=Path)
    parser.add_argument("--output-report", required=True, type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    release = args.release_dir.resolve()
    backend = args.backend_package.resolve()
    version = args.version

    if not release.is_relative_to(root) or not backend.is_relative_to(root):
        raise ValueError("release and backend package must remain inside the project root")
    output_report = args.output_report.resolve()
    if output_report.parent != release:
        raise ValueError("local validation report must be written directly inside the release directory")
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise ValueError("source commit must be a full lowercase Git SHA-1")
    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if current_head != args.source_commit:
        raise ValueError("source commit does not equal the currently validated repository HEAD")

    static = subprocess.run(
        ["node", str(root / "scripts" / "validate-static-site.mjs")],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    static_result = json.loads(static.stdout)

    migration_receipts = sorted((root / "backend" / "migrations").glob("*/MIGRATION_RECEIPT.json"))
    receipt_directories = {path.parent.name for path in migration_receipts}
    if receipt_directories != set(MIGRATION_RECEIPT_FILENAMES):
        raise ValueError("complete-corpus migration receipt directory identity set mismatch")
    migrations = subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "scripts" / "validate-migration-receipt-v1.py"),
            "--schema",
            str(root / "schemas" / "backend-migration-receipt-v1.schema.json"),
            *[str(path) for path in migration_receipts],
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    migration_result = json.loads(migrations.stdout)

    receipt_documents = {}
    for path in migration_receipts:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        migration_id = receipt["migration_id"]
        if migration_id in receipt_documents:
            raise ValueError(f"duplicate migration ID: {migration_id}")
        receipt_documents[migration_id] = receipt
        receipt_filename = MIGRATION_RECEIPT_FILENAMES[path.parent.name]
        copied_receipt = release / receipt_filename
        if not copied_receipt.is_file() or copied_receipt.read_bytes() != path.read_bytes():
            raise ValueError(f"release migration receipt is absent or changed: {receipt_filename}")
    if set(receipt_documents) != set(EXPECTED_MIGRATIONS):
        raise ValueError("complete-corpus migration receipt identity set mismatch")
    migration_target_records = sum(receipt["target"]["record_count"] for receipt in receipt_documents.values())
    if len(receipt_documents) != 10 or migration_target_records != 809296:
        raise ValueError("complete-corpus migration proof boundary must contain ten receipts and 809,296 target records")

    catalog_path = release / f"program-matematika-indonesia-catalog-v{version}.json"
    catalog_schema_path = release / "program-matematika-indonesia-catalog-v1.schema.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_schema = json.loads(catalog_schema_path.read_text(encoding="utf-8"))
    expected_schema_uri = f"https://zenodo.org/records/{args.record_id}/files/program-matematika-indonesia-catalog-v1.schema.json"
    if catalog.get("$schema") != expected_schema_uri or catalog_schema.get("$id") != expected_schema_uri:
        raise ValueError("catalog schema reference and schema identity are not bound to this release")
    if catalog_schema_path.read_bytes() != (root / "schemas" / "catalog-v1.schema.json").read_bytes():
        raise ValueError("release catalog schema is not byte-identical to the validated root schema")
    Draft202012Validator(catalog_schema, format_checker=FormatChecker()).validate(catalog)
    if catalog.get("sourceCommit") != args.source_commit:
        raise ValueError("catalog sourceCommit does not equal the validated repository commit")
    if catalog["program"]["zenodo"] != f"https://doi.org/10.5281/zenodo.{args.record_id}":
        raise ValueError("catalog Zenodo DOI does not match reserved record")
    if catalog["counts"]["courseRoles"] != 40 or catalog["counts"]["unresolvedRoles"] != 0:
        raise ValueError("catalog course/source closure mismatch")
    expected_completed_role_ids = [
        "A00", "B10", "B40", "B80", "B90", "C10", "C30", "C40", "C60", "C70", "C80", "C110", "C120", "C130", "D110"
    ]
    expected_completed_record_dois = [
        "10.5281/zenodo.22070683",
        "10.5281/zenodo.22060439",
        "10.5281/zenodo.22070458",
        "10.5281/zenodo.22053905",
        "10.5281/zenodo.22062144",
        "10.5281/zenodo.22073827",
        "10.5281/zenodo.22062449",
        "10.5281/zenodo.22052196",
        "10.5281/zenodo.22062005",
        "10.5281/zenodo.21932787",
        "10.5281/zenodo.22054086",
        "10.5281/zenodo.22070943",
        "10.5281/zenodo.22070653",
        "10.5281/zenodo.22062017",
    ]
    if catalog["counts"].get("completedPublicCourseRoles") != 15:
        raise ValueError("catalog completed-public course-role count is not 15")
    if catalog["counts"].get("completedPublicRecords") != 14:
        raise ValueError("catalog completed-public record count is not 14")
    if catalog["program"].get("completedPublicCourseRoleIds") != expected_completed_role_ids:
        raise ValueError("catalog completed-public course-role identities are not the v0.50 canonical set")
    if catalog["program"].get("completedPublicRecordDois") != expected_completed_record_dois:
        raise ValueError("catalog completed-public DOI identities are not the v0.50 canonical set")
    published_role_ids = [course["id"] for course in catalog["courses"] if course["state"] == "published"]
    if published_role_ids != expected_completed_role_ids:
        raise ValueError("catalog published course states do not match completed-public role identities")
    courses_by_id = {course["id"]: course for course in catalog["courses"]}
    expected_lebl_repository = "https://github.com/KokunoYumeto/lebl-mathematics-family-id"
    expected_b40_repository = "https://github.com/KokunoYumeto/hefferon-linear-algebra-id"
    expected_c10_edition = "https://zenodo.org/records/22073827/files/Analisis_Dasar_I_Bahasa_Indonesia_v6.3.pdf?download=1"
    expected_c20_edition = "https://zenodo.org/records/22073827/files/Analisis_Dasar_II_Bahasa_Indonesia_v6.3_WIP_sampai_11.2_Latihan.pdf?download=1"
    if (
        courses_by_id["C10"].get("zenodo") != "https://doi.org/10.5281/zenodo.22073827"
        or courses_by_id["C10"].get("edition") != expected_c10_edition
        or courses_by_id["C10"].get("repository") != expected_lebl_repository
    ):
        raise ValueError("C10 does not point to the exact verified Lebl U319 edition")
    if (
        courses_by_id["B40"].get("state") != "published"
        or courses_by_id["B40"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070458"
        or courses_by_id["B40"].get("repository") != expected_b40_repository
    ):
        raise ValueError("B40 does not point to the exact verified Hefferon edition")
    if (
        courses_by_id["A00"].get("state") != "published"
        or courses_by_id["A00"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070683"
        or courses_by_id["A00"].get("repository") != "https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID"
    ):
        raise ValueError("A00 does not point to the exact verified Prealgebra 2e v0.2.7 edition")
    if (
        courses_by_id["C120"].get("state") != "published"
        or courses_by_id["C120"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070943"
        or courses_by_id["C120"].get("repository") != "https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id"
    ):
        raise ValueError("C120 does not point to the exact verified modeling edition")
    if (
        courses_by_id["C130"].get("state") != "published"
        or courses_by_id["C130"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070653"
        or courses_by_id["C130"].get("repository") != "https://github.com/KokunoYumeto/open-optimization-or-book-id"
    ):
        raise ValueError("C130 does not point to the exact verified operations-research edition")
    if (
        courses_by_id["C20"].get("state") != "production"
        or courses_by_id["C20"].get("zenodo") != "https://doi.org/10.5281/zenodo.22073827"
        or courses_by_id["C20"].get("edition") != expected_c20_edition
        or courses_by_id["C20"].get("repository") != expected_lebl_repository
    ):
        raise ValueError("C20 is not preserved as the exact production-state U319 WIP")
    for role_id, expected_units in (("B70", "15 unit"), ("C50", "50 unit")):
        course = courses_by_id[role_id]
        if (
            course.get("state") != "production"
            or course.get("edition")
            or course.get("zenodo") != "https://doi.org/10.5281/zenodo.22073827"
            or course.get("repository") != expected_lebl_repository
            or expected_units not in course.get("note", "")
            or "belum lengkap" not in course.get("note", "")
        ):
            raise ValueError(f"{role_id} does not preserve its exact partial U319 evidence")
    if (
        courses_by_id["C140"].get("state") != "production"
        or courses_by_id["C140"].get("zenodo") != "https://doi.org/10.5281/zenodo.22071140"
        or courses_by_id["C140"].get("repository") != "https://github.com/KokunoYumeto/mathematical-statistics-id"
        or courses_by_id["C140"].get("edition") != "https://zenodo.org/records/22071140/files/00_statistika-matematis-id-reader-2026.08.23.16.pdf?download=1"
    ):
        raise ValueError("C140 does not preserve the verified incomplete Random checkpoint 16")
    if (
        courses_by_id["D20"].get("state") != "production"
        or courses_by_id["D20"].get("zenodo") != "https://doi.org/10.5281/zenodo.22072541"
        or courses_by_id["D20"].get("repository") != "https://github.com/KokunoYumeto/functional-analysis-erdman-id"
        or courses_by_id["D20"].get("edition") != "https://zenodo.org/records/22072541/files/analisis-fungsional-dan-aljabar-operator-id-bab-1-12.pdf?download=1"
    ):
        raise ValueError("D20 does not preserve the verified incomplete Erdman Chapter 12 checkpoint")
    if (
        courses_by_id["D30"].get("state") != "production"
        or courses_by_id["D30"].get("zenodo") != "https://doi.org/10.5281/zenodo.22074332"
        or courses_by_id["D30"].get("edition") != "https://zenodo.org/api/records/22074332/files/00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_20.pdf/content"
        or courses_by_id["D30"].get("repository") != "https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id"
        or "223 halaman" not in courses_by_id["D30"].get("note", "")
    ):
        raise ValueError("D30 does not preserve the verified incomplete checkpoint-20 boundary")
    if (
        courses_by_id["D40"].get("state") != "production"
        or courses_by_id["D40"].get("zenodo") != "https://doi.org/10.5281/zenodo.22074306"
        or courses_by_id["D40"].get("edition") != "https://zenodo.org/api/records/22074306/files/PERSAMAAN_DIFERENSIAL_PARSIAL_DIONNE_ID_UNIT_07.pdf/content"
        or "8 simpul FEniCSx (7 wajib + 1 pengayaan)" not in courses_by_id["D40"].get("corpus", "")
        or "46 halaman" not in courses_by_id["D40"].get("note", "")
    ):
        raise ValueError("D40 does not preserve the verified Unit-07 boundary and eight-node FEniCSx architecture")
    if (
        courses_by_id["D50"].get("state") != "production"
        or courses_by_id["D50"].get("zenodo") != "https://doi.org/10.5281/zenodo.22073928"
        or courses_by_id["D50"].get("edition") != "https://zenodo.org/api/records/22073928/files/geometri-diferensial-manifold-mulus-hingga-unit-10-id.pdf/content"
        or "165 halaman" not in courses_by_id["D50"].get("note", "")
    ):
        raise ValueError("D50 does not preserve the verified incomplete Unit-10 boundary")
    if (
        courses_by_id["D60"].get("state") != "production"
        or courses_by_id["D60"].get("zenodo") != "https://doi.org/10.5281/zenodo.22074233"
        or courses_by_id["D60"].get("edition") != "https://kokunoyumeto.github.io/algebraic-topology-id/units-001-025/"
        or courses_by_id["D60"].get("repository") != "https://github.com/KokunoYumeto/algebraic-topology-id"
        or "Unit 25 (298 halaman)" not in courses_by_id["D60"].get("note", "")
        or "Unit 24 (286 halaman)" not in courses_by_id["D60"].get("note", "")
    ):
        raise ValueError("D60 does not distinguish the verified Pages Unit-25 and Zenodo Unit-24 boundaries")
    if (
        courses_by_id["D100"].get("state") != "production"
        or courses_by_id["D100"].get("zenodo") != "https://doi.org/10.5281/zenodo.22070936"
        or courses_by_id["D100"].get("edition") != "https://zenodo.org/api/records/22070936/files/kurva-aljabar-id-unit-08.pdf/content"
        or "161 halaman" not in courses_by_id["D100"].get("note", "")
        or "bukan rilis publik" not in courses_by_id["D100"].get("note", "")
    ):
        raise ValueError("D100 does not preserve the public Unit-08 and internal Unit-09 distinction")

    expected_catalog_migrations = []
    for migration_id, metadata in EXPECTED_MIGRATIONS.items():
        expected_catalog_migrations.append(
            {
                "corpus": metadata["corpus"],
                "recordCount": receipt_documents[migration_id]["target"]["record_count"],
                "result": metadata["result"],
            }
        )
    actual_catalog_migrations = catalog["program"]["backend"]["completeCorpusMigrations"]
    if sorted(actual_catalog_migrations, key=lambda row: row["corpus"]) != sorted(expected_catalog_migrations, key=lambda row: row["corpus"]):
        raise ValueError("catalog migration claims do not match the validated receipt identities and counts")

    backend_report_path = backend / "validation_report.json"
    backend_report = json.loads(backend_report_path.read_text(encoding="utf-8"))
    if backend_report["result"] != "pass" or backend_report["checks"]["deterministic_replay"]["result"] != "byte-identical":
        raise ValueError("backend validation report is not admitted")
    if backend_report["checks"]["record_count"] != catalog["program"]["backend"]["centralRecordCount"]:
        raise ValueError("catalog/backend record count mismatch")
    if backend_report["checks"]["record_count"] != 2122:
        raise ValueError("central backend record count must remain exactly 2,122")

    html_path = release / f"program-matematika-indonesia-v{version}.html"
    html = html_path.read_text(encoding="utf-8")
    for required in (
        f"10.5281/zenodo.{args.record_id}",
        f"v{version}",
        "40 korpus terpilih",
        "Produksi yang belum selesai tetap dilabeli dengan jelas",
    ):
        if required not in html:
            raise ValueError(f"standalone HTML missing {required!r}")

    og_path = release / f"program-matematika-indonesia-og-v{version}.png"
    if not og_path.is_file() or og_path.read_bytes() != (root / "docs" / "og.png").read_bytes():
        raise ValueError("release social-preview image is absent or differs from the validated site image")

    source_zip = release / f"program-matematika-indonesia-source-v{version}.zip"
    backend_zip = release / f"program-matematika-indonesia-backend-v1-v{version}.zip"
    generated_catalog_source_path = (
        f"releases/v{version}/program-matematika-indonesia-catalog-v{version}.json"
    )
    zip_results = {
        "source": verify_source_zip(
            source_zip,
            root,
            args.source_commit,
            {generated_catalog_source_path},
        ),
        "backend": verify_backend_zip(backend_zip, backend),
    }
    if zip_results["source"]["source_commit"] != args.source_commit:
        raise ValueError("source ZIP manifest is not bound to the validated repository commit")

    receipt_release_names = set(MIGRATION_RECEIPT_FILENAMES.values())
    expected_release_names = {
        "BACKEND_CONVERGENCE_V1.md",
        "MIGRATION_HANDOFF_V1.md",
        f"RELEASE_NOTES_v{version}.md",
        "interlanguage-backend-migration-receipt-v1.schema.json",
        "interlanguage-math-backend-v1.schema.json",
        "interlanguage-source-format-profile-v1.schema.json",
        "program-matematika-indonesia-catalog-v1.schema.json",
        f"program-matematika-indonesia-catalog-v{version}.json",
        f"program-matematika-indonesia-og-v{version}.png",
        f"program-matematika-indonesia-v{version}.html",
        f"program-matematika-indonesia-backend-v1-validation-v{version}.json",
        f"program-matematika-indonesia-backend-v1-v{version}.zip",
        f"program-matematika-indonesia-source-v{version}.zip",
        *receipt_release_names,
    }
    actual_release_names = {
        path.name
        for path in release.iterdir()
        if path.is_file() and path.name not in {"CHECKSUMS.sha256", output_report.name}
    }
    if actual_release_names != expected_release_names:
        missing = sorted(expected_release_names - actual_release_names)
        extra = sorted(actual_release_names - expected_release_names)
        raise ValueError(f"release inventory mismatch; missing={missing}; extra={extra}")

    files = []
    for path in sorted(candidate for candidate in release.iterdir() if candidate.is_file() and candidate.name in expected_release_names):
        assert_public_bytes(f"release:{path.name}", path.read_bytes())
        files.append({"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)})

    report = {
        "schema_id": "program-matematika-indonesia/local-release-validation/v2",
        "version": version,
        "reserved_zenodo_record_id": args.record_id,
        "result": "pass",
        "checks": {
            "static_site": static_result,
            "catalog_draft_2020_12": "pass",
            "catalog_course_roles": catalog["counts"]["courseRoles"],
            "catalog_unresolved_roles": catalog["counts"]["unresolvedRoles"],
            "catalog_completed_public_course_roles": catalog["counts"]["completedPublicCourseRoles"],
            "catalog_completed_public_records": catalog["counts"]["completedPublicRecords"],
            "catalog_schema_identity_and_bytes": "pass",
            "source_commit_binding": args.source_commit,
            "backend": backend_report["checks"],
            "complete_corpus_migrations": migration_result,
            "complete_corpus_migration_target_records": migration_target_records,
            "migration_claim_cross_check": "pass",
            "release_inventory": {"files_before_report": len(files), "result": "exact"},
            "privacy_scan": "pass",
            "zip_verification": zip_results,
            "standalone_html": "pass",
            "github_transport": "available_for_bounded_push_after_release_validation",
        },
        "files_before_checksum": files,
    }
    report_bytes = (json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    assert_public_bytes("local release validation report", report_bytes)
    output_report.write_bytes(report_bytes)
    print(json.dumps({"result": "pass", "report": str(output_report), "sha256": sha256_file(output_report)}, sort_keys=True))


if __name__ == "__main__":
    main()
