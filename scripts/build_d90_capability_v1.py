"""Build the D90 zero-copy learner/educator capability adapter."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

from d90_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    DEFAULT_ADAPTER,
    DEFAULT_NATIVE,
    LOCALE,
    NATIVE_COURSE_ID,
    RELEASE_COMMIT,
    RELEASE_TREE,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_bytes,
    write_json,
)


STYLE = """
:root{color-scheme:light;--ink:#162f38;--muted:#53686f;--paper:#f4f1e8;--card:#fff;--line:#c6d2d5;--accent:#066a78;--warn:#a9572a}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1120px;margin:auto;padding:28px 20px 64px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.5rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.05;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.12rem;max-width:78ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:1.5rem 0}.card,details,.notice{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{display:block;font-size:1.8rem;font-weight:760}.muted{color:var(--muted)}details{margin:.75rem 0}summary{cursor:pointer;font-weight:700}.chain{display:flex;gap:.45rem;flex-wrap:wrap;align-items:center}.chain a{border:1px solid var(--line);border-radius:999px;padding:.2rem .55rem;text-decoration:none}.notice{border-left:6px solid var(--warn)}code{overflow-wrap:anywhere}.index{columns:2;column-width:280px}.index li{break-inside:avoid;margin:.35rem 0}a:focus-visible,summary:focus-visible{outline:3px solid #d58a25;outline-offset:3px}
""".strip()


NEGATIVE_FIXTURES = (
    ("hash-drift", "source_lock.inputs[1].sha256", "replace", "00" * 32, "D90-SOURCE-LOCK"),
    ("altered-native-id", "native_record_index[0].id", "replace", "program.d90.changed", "D90-NATIVE-ID-SEQUENCE"),
    ("dropped-native-id", "native_record_index[-1]", "remove", None, "D90-NATIVE-ID-COUNT"),
    ("collapsed-absence-states", "native_record_index[*].presence", "remove", None, "D90-STATE-PROJECTION"),
    ("flattened-rights", "rights_index[*].component_id", "replace", "component.all", "D90-RIGHTS-FLATTENED"),
    ("bad-anchor", "shared_surfaces[0].public_anchor", "replace", "https://example.invalid/#lost", "D90-ORIGINAL03-ANCHOR"),
    ("copied-body", "learner_map.body", "add", "forbidden native body", "D90-COPIED-NATIVE-BODY"),
    ("false-lab-completion", "claim_boundary.lab_completion_claimed", "replace", True, "D90-FALSE-CLAIM:lab_completion_claimed"),
    ("false-accessibility", "public_evidence.accessibility.wcag_conformance_claimed", "replace", True, "D90-FALSE-ACCESSIBILITY-CLAIM"),
    ("false-reversibility", "claim_boundary.reversible_exchange_claimed", "replace", True, "D90-FALSE-CLAIM:reversible_exchange_claimed"),
    ("false-live-results", "claim_boundary.learner_result_instances", "replace", 1, "D90-LIVE-LEARNER-RESULT-CLAIM"),
    ("false-universal-solution-coverage", "claim_boundary.full_solution_coverage_beyond_observed_records_claimed", "replace", True, "D90-FALSE-CLAIM:full_solution_coverage_beyond_observed_records_claimed"),
    ("case-key-collapsed", "capabilities.case_sensitive_key_caveat.collisions", "replace", [], "D90-CASE-SENSITIVE-KEY-CAVEAT"),
)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="id"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        '<nav><a href="D90.html">Pelajar</a><a href="D90-pengajar.html">Pengajar</a>'
        '<a href="capabilities.json">Kapabilitas JSON</a></nav>'
        f"{body}</main></body></html>\n"
    )


def _chain_block(chain: dict[str, Any]) -> str:
    stages = '<span aria-hidden="true">→</span>'.join(
        f'<a href="{esc(stage["public_anchor"])}"><code>{esc(stage["id"])}</code></a>'
        for stage in chain["stages"]
    )
    return f'<details><summary><code>{esc(chain["chain_id"])}</code></summary><p class="chain">{stages}</p></details>'


def render_learner(bundle: dict[str, Any]) -> str:
    learning = bundle["learner_map"]
    counts = bundle["capabilities"]["counts"]
    prompts = "".join(_chain_block(row) for row in learning["prompt_chains"])
    practices = "".join(_chain_block(row) for row in learning["practice_chains"])
    assessments = "".join(
        f'<li><a href="{esc(row["public_anchor"])}"><code>{esc(row["id"])}</code></a> · {esc(row["surface_type"])}</li>'
        for row in learning["assessment_containers"]
    )
    milestones = "".join(
        f'<li><a href="{esc(row["public_anchor"])}"><code>{esc(row["id"])}</code></a></li>'
        for row in learning["capstone"]["milestones"]
    )
    labs = "".join(
        f'<li><a href="{esc(row["public_anchor"])}"><code>{esc(row["id"])}</code></a></li>'
        for row in learning["labs"]
    )
    return shell(
        "D90 · Peta kapabilitas pelajar",
        f"""
<p class="muted">D90 · <code>{esc(CONTRACT)}</code> · <code>{esc(NATIVE_COURSE_ID)}</code></p>
<h1>Peta identitas belajar D90</h1>
<p class="lede">Adapter tipis ini menautkan identitas permukaan Original-03 ke pembaca publik native. Konten kursus tetap berada di edisi native.</p>
<div class="grid"><div class="card"><span class="metric">{counts['original03_surfaces']}</span>identitas permukaan</div><div class="card"><span class="metric">{counts['prompt_chains']}</span>rantai prompt</div><div class="card"><span class="metric">{counts['practice_chains']}</span>rantai latihan</div><div class="card"><span class="metric">0</span>hasil pelajar diklaim</div></div>
<p><a href="{esc(learning['reader']['html'])}">Pembaca HTML native</a> · <a href="{esc(learning['reader']['pdf'])}">PDF native</a> · <a href="{esc(learning['reader']['epub'])}">EPUB native</a></p>
<div class="notice"><strong>Batas klaim:</strong> adapter tidak menyalin badan prompt, petunjuk, jawaban, solusi, TeX, HTML, PDF, EPUB, atau dataset; tidak mengklaim pengerjaan lab, kiriman, percobaan, atau hasil pelajar.</div>
<h2>Prompt → petunjuk 1 → petunjuk 2 → jawaban → solusi</h2>{prompts}
<h2>Latihan, lab, dan capstone bertahap</h2>{practices}
<h2>Wadah asesmen</h2><ol class="index">{assessments}</ol>
<h2>Lab komputasional</h2><ul>{labs}</ul>
<h2>Capstone dan milestone</h2><p><a href="{esc(learning['capstone']['public_anchor'])}"><code>{esc(learning['capstone']['id'])}</code></a> · <a href="{esc(learning['capstone']['project_unit']['public_anchor'])}"><code>{esc(learning['capstone']['project_unit']['id'])}</code></a></p><ol>{milestones}</ol>
""",
    )


def render_educator(bundle: dict[str, Any]) -> str:
    educator = bundle["educator_map"]
    counts = bundle["capabilities"]["counts"]
    rubrics = "".join(
        f'<li><a href="{esc(row["public_anchor"])}"><code>{esc(row["id"])}</code></a></li>'
        for row in educator["rubrics"]
    )
    assessments = "".join(
        f'<li><a href="{esc(row["public_anchor"])}"><code>{esc(row["id"])}</code></a> · {esc(row["surface_type"])}</li>'
        for row in educator["assessment_containers"]
    )
    return shell(
        "D90 · Peta kapabilitas pengajar",
        f"""
<p class="muted">D90 · tampilan pengajar · <code>{esc(CONTRACT)}</code></p>
<h1>Identitas asesmen dan tata kelola D90</h1>
<p class="lede">Permukaan yang sama dipakai oleh peta pelajar dan pengajar, dengan tautan stabil ke edisi publik native serta indeks hak, koreksi, dan istilah yang tetap terpisah.</p>
<div class="grid"><div class="card"><span class="metric">{counts['learner_assessment_containers']}</span>wadah asesmen</div><div class="card"><span class="metric">{counts['educator_rubrics']}</span>rubrik bukti</div><div class="card"><span class="metric">{counts['component_rights']}</span>rekaman hak</div><div class="card"><span class="metric">{counts['corrections']}</span>koreksi</div><div class="card"><span class="metric">{counts['terms']}</span>istilah</div></div>
<div class="notice"><strong>Batas klaim:</strong> cakupan solusi hanya mengikuti rekaman yang teramati; tidak ada hasil pelajar langsung, klaim kelulusan lab, klaim WCAG, atau pertukaran reversibel.</div>
<h2>Wadah asesmen</h2><ol class="index">{assessments}</ol>
<h2>Rubrik pembuktian</h2><ol>{rubrics}</ol>
<h2>Indeks tata kelola</h2><ul><li><a href="../data/rights-index.jsonl">Hak per komponen</a></li><li><a href="../data/corrections-index.jsonl">Koreksi</a></li><li><a href="../data/terms-index.jsonl">Terminologi</a></li><li><a href="../data/claim-boundary.json">Batas klaim mesin</a></li></ul>
""",
    )


def _fixture_bytes() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for fixture_id, path, operation, value, expected in NEGATIVE_FIXTURES:
        payload = {
            "schema": "d90-negative-fixture/1",
            "fixture_id": fixture_id,
            "mutation": {"operation": operation, "path": path},
            "expected_error": expected,
        }
        if operation != "remove":
            payload["mutation"]["value"] = value
        files[f"fixtures/negative/{fixture_id}.json"] = canonical_json_bytes(payload)
    return files


def build(native_root: Path, adapter: Path) -> dict[str, Any]:
    bundle = derive_projection(native_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"D90 native projection failed: {errors}")

    files = {
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/native-record-index.jsonl": canonical_jsonl_bytes(bundle["native_record_index"]),
        "data/rights-index.jsonl": canonical_jsonl_bytes(bundle["rights_index"]),
        "data/corrections-index.jsonl": canonical_jsonl_bytes(bundle["corrections_index"]),
        "data/terms-index.jsonl": canonical_jsonl_bytes(bundle["terms_index"]),
        "data/shared-learning-surfaces.jsonl": canonical_jsonl_bytes(bundle["shared_surfaces"]),
        "data/staged-relations.jsonl": canonical_jsonl_bytes(bundle["staged_relations"]),
        "data/learner-map.json": canonical_json_bytes(bundle["learner_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/D90.html": render_learner(bundle).encode("utf-8"),
        "views/D90-pengajar.html": render_educator(bundle).encode("utf-8"),
        # Keep the capability metadata beside the rendered pages as well as in
        # the canonical data directory.  The byte-identical companion makes
        # the relative link above work both when the adapter's ``views``
        # directory is opened directly and after the pages are staged into the
        # public ``docs/backend/d90`` directory.
        "views/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "README.md": (
            "# D90 zero-copy capability adapter\n\n"
            "This adapter projects the pinned D90 native backend into `course-learning-capability/1`. "
            "It preserves all 4,877 native identities and their status/presence markers, while exposing "
            "the 438-record Original-03 learner/educator slice through stable public HTML anchors.\n\n"
            "It contains metadata, identity, state, rights, correction, terminology, relationship, and "
            "public-evidence projections only. Native prose, solution bodies, TeX, HTML, PDF, EPUB, and "
            "datasets remain external at the pinned GitHub commit and Zenodo record. Component rights are "
            "not flattened. No live learner result, lab completion, universal solution coverage, WCAG "
            "conformance, or reversible exchange is claimed.\n"
        ).encode("utf-8"),
        **_fixture_bytes(),
    }
    for relative, data in files.items():
        write_bytes(adapter / relative, data)

    manifest = {
        "schema": "d90-capability-manifest/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "locale": LOCALE,
        "native_family": "advanced_optimization_convex_analysis",
        "content_policy": "identity_state_rights_evidence_only",
        "native_release": {"commit": RELEASE_COMMIT, "tree": RELEASE_TREE},
        "projection": {
            "central_course_truth_rewritten": False,
            "component_rights_preserved": True,
            "external_pinned_native_checkout_required_for_replay": True,
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "public_state_changed": False,
            "reversible_exchange_claimed": False,
        },
        "counts": bundle["capabilities"]["counts"],
        "inputs": bundle["source_lock"]["inputs"],
        "outputs": [identity(adapter / path, display_path=path) for path in sorted(files)],
        "validation_path": "validation.json",
        "package_receipt_path": "build/PACKET_BUILD_RECEIPT.json",
    }
    write_json(adapter / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
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
                "original03_surfaces": manifest["counts"]["original03_surfaces"],
                "staged_relations": manifest["counts"]["staged_relations"],
            }
        ).decode("utf-8"),
        end="",
    )


if __name__ == "__main__":
    main()
