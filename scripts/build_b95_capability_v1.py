"""Build the B95/R011-B039 zero-copy capability adapter.

The producer checkout is an input only.  This builder emits a metadata and
locator projection under ``backend/course-capsule-v1/adapters/b95-capability-v1``;
it never copies native segment, exercise, answer, solution, PDF, or TeX bodies.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

from b95_capability_model_v1 import (
    BOUNDARY_ID,
    CONTRACT,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    GITHUB_DOWNLOAD_BASE,
    LOCALE,
    NATIVE_COURSE_ID,
    NATIVE_EDITION_ID,
    NATIVE_ROLE_ID,
    RELEASE_ID,
    RELEASE_TAG,
    REPOSITORY,
    READER_FILENAME,
    READER_GITHUB_URL,
    READER_ZENODO_URL,
    UPSTREAM_COMMIT,
    UPSTREAM_REPOSITORY,
    UPSTREAM_TREE,
    ZENODO_CONCEPT_ID,
    ZENODO_RECORD,
    ZENODO_RECORD_ID,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_bytes,
    write_json,
)


STYLE = """
:root{color-scheme:light;--ink:#172d36;--muted:#53666d;--paper:#f3f0e7;--card:#fff;--line:#cad3d5;--accent:#086d78;--warn:#9d542c}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1160px;margin:auto;padding:28px 20px 64px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.4rem);line-height:1.06;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.12rem;max-width:78ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.5rem 0}.card,details,.notice{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:760}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:700}.notice{border-left:6px solid var(--warn)}code{overflow-wrap:anywhere}.index{columns:2;column-width:330px}.index li{break-inside:avoid;margin:.35rem 0}.compact{font-size:.92rem}a:focus-visible,summary:focus-visible{outline:3px solid #d58a25;outline-offset:3px}
""".strip()


# These declarations are deliberately identity-only.  They are fixtures for
# the validator, not copies of native payloads.
NEGATIVE_FIXTURES: tuple[tuple[str, str, str, Any, str], ...] = (
    ("hash-drift", "source_lock.inputs[0].sha256", "replace", "00" * 32, "B95-SOURCE-LOCK"),
    ("altered-native-id", "native_record_index[0].id", "replace", "urn:b95:changed", "B95-NATIVE-ID-SEQUENCE"),
    ("dropped-native-id", "native_record_index[-1]", "remove", None, "B95-NATIVE-ID-COUNT"),
    ("copied-body", "learner_map.body", "add", "forbidden native body", "B95-COPIED-NATIVE-BODY"),
    ("copied-segment-text", "claim_boundary.target_segment_text_copied", "replace", 1, "B95-BOUNDARY:target_segment_text_copied"),
    ("false-solutions", "claim_boundary.answer_or_solution_bodies_copied", "replace", 1, "B95-BOUNDARY:answer_or_solution_bodies_copied"),
    ("false-semantic-html", "public_evidence.reader.semantic_html_established", "replace", True, "B95-READER-CLAIMS"),
    ("false-wcag", "claim_boundary.wcag_conformance_claimed", "replace", True, "B95-CLAIM:wcag_conformance_claimed"),
    ("false-reversibility", "claim_boundary.reversible_exchange_claimed", "replace", True, "B95-CLAIM:reversible_exchange_claimed"),
    ("flattened-rights", "rights_index", "replace", [{"id": "all"}], "B95-RIGHTS-COUNT"),
    ("public-access-drift", "public_evidence.zenodo.access_right", "replace", "restricted", "B95-PUBLIC-ACCESS"),
    ("bad-chapter-route", "learner_map.chapters[0].public_route", "replace", "https://example.invalid/", "B95-CHAPTER-ROUTES"),
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        '<nav><a href="B95.html">Pelajar</a><a href="B95-pengajar.html">Pengajar</a>'
        '<a href="capabilities.json">Kapabilitas JSON</a></nav>'
        f"{body}</main></body></html>\n"
    )


def render_learner(bundle: dict[str, Any]) -> str:
    learning = bundle["learner_map"]
    counts = bundle["capabilities"]["counts"]
    chapters = "".join(
        f'<details><summary>Bab {row["chapter"]} · {esc(row["title_id"])} · {row["exercise_count"]} identitas latihan</summary>'
        f'<p><a href="{esc(row["public_route"])}">Buka pembaca pada halaman {row["start_page"]}</a> · '
        '<span class="muted">tautan menuju awal bab; identitas latihan tidak berisi isi soal.</span></p>'
        f'<p>{len(row["section_unit_ids"])} unit bagian · {row["public_answer_count"]} identitas jawaban publik · '
        f'{row["o001_gap_count"]} celah O001</p>'
        '<ul class="index compact">'
        + "".join(f'<li><code>{esc(unit_id)}</code></li>' for unit_id in row["exercise_ids"])
        + "</ul></details>"
        for row in learning["chapters"]
    )
    return shell(
        "B95 · Peta belajar statistika",
        f"""
<p class="muted">B95 · <code>{esc(CONTRACT)}</code> · <code>{esc(NATIVE_COURSE_ID)}</code> · {esc(LOCALE)}</p>
<h1>Peta belajar statistika berbasis data</h1>
<p class="lede">Adapter tipis ini menghubungkan struktur bab dan identitas latihan ke pembaca native Bahasa Indonesia. Isi buku, teks segmen, dan isi jawaban tetap berada di backend native yang dirilis.</p>
<div class="grid"><div class="card"><span class="metric">{counts['reader_pages']}</span>halaman pembaca</div><div class="card"><span class="metric">{counts['chapters']}</span>bab</div><div class="card"><span class="metric">{counts['sections']}</span>bagian</div><div class="card"><span class="metric">{counts['exercises']}</span>identitas latihan</div><div class="card"><span class="metric">{counts['concepts']}</span>konsep</div></div>
<p><a href="{esc(learning['reader']['home'])}">Buka rilis native</a> · <a href="{esc(learning['reader']['pdf'])}">Unduh {esc(READER_FILENAME)}</a> · <a href="../data/exercise-index.jsonl">Indeks latihan mesin</a></p>
<div class="notice"><strong>Batas klaim:</strong> proyeksi ini zero-copy dan metadata-only. Ia tidak mengklaim HTML semantik, MathML, EPUB, kepatuhan WCAG, paket luring, kunci jawaban, atau solusi. Rute selain awal bab hanya memberi konteks pembaca.</div>
<h2>Bab dan navigasi</h2>{chapters}
""",
    )


def render_educator(bundle: dict[str, Any]) -> str:
    educator = bundle["educator_map"]
    counts = bundle["capabilities"]["counts"]
    status_rows = "".join(
        f"<li><code>{esc(status)}</code>: {count}</li>"
        for status, count in educator["correction_status_counts"].items()
    )
    # Keep this view useful without embedding any native prose.  IDs and unit
    # kinds are enough for deterministic selection; full metadata is in JSONL.
    units = "".join(
        f'<li><a href="{esc(row["public_route"])}"><code>{esc(row["id"])}</code></a> · '
        f'{esc(row.get("unit_type"))} · bab {esc(row.get("chapter"))} · {esc(row.get("route_precision"))}</li>'
        for row in educator["selectable_units"]
    )
    return shell(
        "B95 · Peta pengajar statistika",
        f"""
<p class="muted">B95 · tampilan pengajar · <code>{esc(CONTRACT)}</code></p>
<h1>Perencanaan dan tata kelola B95</h1>
<p class="lede">Gunakan identitas unit yang sama dengan peta pelajar, lalu buka konteks bab pada pembaca native. Konsep, istilah, koreksi, relasi, hak komponen, segmen, dan lokalisasi tersedia sebagai indeks metadata terpisah.</p>
<div class="grid"><div class="card"><span class="metric">{counts['units']}</span>unit</div><div class="card"><span class="metric">{counts['concepts']}</span>konsep</div><div class="card"><span class="metric">{counts['terms']}</span>istilah</div><div class="card"><span class="metric">{counts['corrections']}</span>koreksi</div><div class="card"><span class="metric">{counts['component_rights']}</span>rekaman hak</div></div>
<div class="notice"><strong>Batas klaim:</strong> tampilan ini bukan panduan guru atau kunci jawaban. Isi teks dan solusi tidak disalin; hak komponen dan status koreksi dipertahankan per rekaman.</div>
<h2>Indeks tata kelola</h2><ul><li><a href="../data/concept-index.jsonl">Konsep</a></li><li><a href="../data/terms-index.jsonl">Terminologi</a></li><li><a href="../data/corrections-index.jsonl">Koreksi</a></li><li><a href="../data/rights-index.jsonl">Hak per komponen</a></li><li><a href="../data/relation-index.jsonl">Relasi</a></li><li><a href="../data/segment-index.jsonl">Identitas segmen</a></li><li><a href="../data/localization-index.jsonl">Identitas lokalisasi</a></li><li><a href="../data/claim-boundary.json">Batas klaim mesin</a></li></ul>
<h2>Status koreksi native</h2><ul>{status_rows}</ul>
<h2>Semua identitas unit</h2><ol class="index compact">{units}</ol>
""",
    )


def _fixture_bytes() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for fixture_id, path, operation, value, expected in NEGATIVE_FIXTURES:
        mutation: dict[str, Any] = {"operation": operation, "path": path}
        if operation != "remove":
            mutation["value"] = value
        payload = {
            "schema": "b95-negative-fixture/1",
            "fixture_id": fixture_id,
            "mutation": mutation,
            "expected_error": expected,
        }
        files[f"fixtures/negative/{fixture_id}.json"] = canonical_json_bytes(payload)
    return files


def build(native_root: Path, adapter: Path) -> dict[str, Any]:
    bundle = derive_projection(native_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"B95 native projection failed: {errors}")

    # The exact final completion receipt is copied byte-for-byte as evidence;
    # it is not normalized or interpreted as adapter content.
    completion_receipt = native_root / "qa/b039-publication/R011-B039_FINAL_COMPLETION_RECEIPT.json"
    files: dict[str, bytes] = {
        "input/public-native-readback.json": completion_receipt.read_bytes(),
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/native-record-index.jsonl": canonical_jsonl_bytes(bundle["native_record_index"]),
        "data/unit-index.jsonl": canonical_jsonl_bytes(bundle["unit_index"]),
        "data/exercise-index.jsonl": canonical_jsonl_bytes(bundle["exercise_index"]),
        "data/concept-index.jsonl": canonical_jsonl_bytes(bundle["concept_index"]),
        "data/relation-index.jsonl": canonical_jsonl_bytes(bundle["relation_index"]),
        "data/terms-index.jsonl": canonical_jsonl_bytes(bundle["terms_index"]),
        "data/corrections-index.jsonl": canonical_jsonl_bytes(bundle["corrections_index"]),
        "data/rights-index.jsonl": canonical_jsonl_bytes(bundle["rights_index"]),
        "data/segment-index.jsonl": canonical_jsonl_bytes(bundle["segment_index"]),
        "data/localization-index.jsonl": canonical_jsonl_bytes(bundle["localization_index"]),
        "data/evidence-index.jsonl": canonical_jsonl_bytes(bundle["evidence_index"]),
        "data/learner-map.json": canonical_json_bytes(bundle["learner_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "data/release-inventory.json": canonical_json_bytes(bundle["evidence"]["inventory_bindings"]),
        "views/B95.html": render_learner(bundle).encode("utf-8"),
        "views/B95-pengajar.html": render_educator(bundle).encode("utf-8"),
        "views/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        **_fixture_bytes(),
        "README.md": (
            "# B95 zero-copy capability adapter\n\n"
            "This adapter projects the pinned R011-B039 (`R011-B039`) Indonesian OpenIntro "
            "Statistics backend into `course-learning-capability/1`. It preserves stable "
            "native identifiers, the nine-chapter hierarchy, exercise identities, terminology, "
            "correction states, component rights, and public release evidence.\n\n"
            "No native segment/localization body, exercise prose, answer, solution, PDF, TeX, "
            "or source archive is copied here. The producer checkout remains an external input "
            "and is never modified by these scripts. The public reader is a 462-page PDF; "
            "semantic HTML, MathML, EPUB, WCAG conformance, offline portability, teacher manual, "
            "and answer-key claims are intentionally false.\n\n"
            "The current B039 export bytes are bound by the release inventory and completion/"
            "publication receipts. The public release tag target is recorded separately because "
            "the tag's tracked tree is not asserted to contain the dirty working-tree export.\n"
        ).encode("utf-8"),
    }
    for relative, data in files.items():
        write_bytes(adapter / relative, data)

    manifest = {
        "schema": "b95-capability-manifest/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "boundary_id": BOUNDARY_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "native_edition_id": NATIVE_EDITION_ID,
        "locale": LOCALE,
        "native_family": "openintro_statistics_fourth_edition",
        "content_policy": "identity_structure_terminology_rights_evidence_only",
        "authority": {
            "upstream_repository": UPSTREAM_REPOSITORY,
            "upstream_commit": UPSTREAM_COMMIT,
            "upstream_tree": UPSTREAM_TREE,
            "public_repository": REPOSITORY,
            "public_release_tag": RELEASE_TAG,
            "public_release_id": RELEASE_ID,
            "public_release_tag_target_sha": bundle["public_evidence"]["repository"].get("tag_target_sha"),
            "tag_contains_current_working_tree_exports": False,
            "current_export_binding": "B039 release backend inventory plus expanded local manifest and publication receipts",
        },
        "projection": {
            "central_course_truth_rewritten": False,
            "component_rights_preserved": True,
            "excluded_boundary_preserved": True,
            "external_native_backend_required_for_replay": True,
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "public_access_state_changed": False,
            "reversible_exchange_claimed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["inputs"],
        "output_paths": sorted(files),
        "outputs": [identity(adapter / path, display_path=path) for path in sorted(files)],
        "validation_path": "validation.json",
        "package_receipt_path": "build/PACKET_BUILD_RECEIPT.json",
        "negative_fixture_count": len(NEGATIVE_FIXTURES),
        "public_evidence": {
            "github_release_url": bundle["public_evidence"]["repository"]["release_url"],
            "zenodo_record": ZENODO_RECORD,
            "zenodo_record_id": ZENODO_RECORD_ID,
            "zenodo_concept_id": ZENODO_CONCEPT_ID,
            "reader_github_url": READER_GITHUB_URL,
            "reader_zenodo_url": READER_ZENODO_URL,
            "anonymous_readback": True,
        },
    }
    write_json(adapter / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    manifest = build(args.native_root.resolve(), args.adapter.resolve())
    print(
        canonical_json_bytes(
            {
                "state": "pass",
                "course_id": COURSE_ID,
                "outputs": len(manifest["outputs"]),
                "native_records": manifest["counts"]["native_records"],
                "units": manifest["counts"]["units"],
                "exercises": manifest["counts"]["exercises"],
            }
        ).decode("utf-8"),
        end="",
    )


if __name__ == "__main__":
    main()
