"""Build the thin D120 learner/educator capability adapter."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from d120_capability_model_v1 import (
    CONTRACT,
    COURSE_ID,
    LOCALE,
    NATIVE_COURSE_ID,
    PAGES_ROOT,
    RELEASE_VERSION,
    canonical_json_bytes,
    derive_projection,
    identity,
    projection_errors,
    write_json,
)


PROJECT = Path(__file__).resolve().parents[1]
WORKSPACE = PROJECT.parents[2]
DEFAULT_NATIVE = WORKSPACE / "outputs/01a0216a-4b9f-7d30-a376-60e4e3859979"
DEFAULT_ADAPTER = PROJECT / "backend/course-capsule-v1/adapters/d120-capability-v1"


STYLE = """
:root{color-scheme:light;--ink:#173832;--muted:#506963;--paper:#f4f3ea;--card:#fff;--line:#c9d7d1;--accent:#086c63;--warm:#b96328}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1120px;margin:auto;padding:28px 20px 60px}nav{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--accent);text-underline-offset:3px}
h1{font-size:clamp(2rem,5vw,3.4rem);line-height:1.05;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.15rem;max-width:76ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:1.5rem 0}.card,details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{font-size:1.8rem;font-weight:750;display:block}.muted{color:var(--muted)}details{margin:.8rem 0}summary{cursor:pointer;font-weight:700}.unit-head{display:flex;justify-content:space-between;gap:1rem;align-items:baseline;flex-wrap:wrap}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.85rem}.practice{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:8px;padding:0;list-style:none}.practice li{border-left:4px solid var(--accent);padding:.45rem .7rem;background:#f7faf8}.notice{border-left:6px solid var(--warm);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}.assessment{border-left:5px solid var(--accent)}code{overflow-wrap:anywhere}table{width:100%;border-collapse:collapse;background:white}th,td{border-bottom:1px solid var(--line);padding:.7rem;text-align:left;vertical-align:top}.table-wrap{overflow:auto}a:focus-visible,summary:focus-visible{outline:3px solid #d48624;outline-offset:3px}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def shell(title: str, body: str) -> str:
    return (
        "<!doctype html><html lang=\"id\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{esc(title)}</title><style>{STYLE}</style></head><body><main>"
        "<nav><a href=\"../../id/#course-D120\">Program matematika</a>"
        "<a href=\"../index.html\">Pusat backend</a>"
        "<a href=\"D120.html\">Pelajar</a>"
        "<a href=\"D120-pengajar.html\">Pengajar</a></nav>"
        f"{body}</main></body></html>\n"
    )


def local_text(row: dict, field: str, fallback: str = "") -> str:
    return row.get("localization", {}).get(field, fallback)


def render_learner(bundle: dict) -> str:
    learning = bundle["learning_map"]
    counts = bundle["capabilities"]["counts"]
    units = []
    for unit in learning["units"]:
        outcomes = "".join(
            f"<li><code>{esc(outcome['id'])}</code> — {esc(local_text(outcome, 'description', 'Deskripsi ada pada sumber native.'))}</li>"
            for outcome in unit["outcomes"]
        )
        practice = "".join(
            "<li>"
            f"<a href=\"{esc(item['exercise_url'])}\">{esc(item['exercise_id'])}</a> · "
            f"<a href=\"{esc(item['guidance_url'])}\">panduan {esc(item['guidance_id'])}</a>"
            "</li>"
            for item in unit["practice"]
        )
        units.append(
            "<details>"
            f"<summary><span class=\"unit-head\"><span>Unit {unit['ordinal']} · {esc(unit['title'])}</span>"
            f"<span class=\"pill\">{len(unit['outcomes'])} hasil · {len(unit['practice'])} latihan</span></span></summary>"
            f"<p><a href=\"{esc(unit['public_reader']['url'])}\">Buka unit native</a> · "
            f"kompetensi <code>{esc(unit['competency']['id'])}</code> · penilaian <code>{esc(unit['assessment_id'])}</code></p>"
            f"<h3>Hasil belajar</h3><ol>{outcomes}</ol><h3>Latihan dan panduan sumber</h3><ul class=\"practice\">{practice}</ul>"
            "</details>"
        )
    body = f"""
<p class="muted">D120 · <code>{NATIVE_COURSE_ID}</code> · edisi {RELEASE_VERSION}</p>
<h1>Kerja Matematika yang Dapat Ditelusuri</h1>
<p class="lede">Jalur sembilan unit untuk membaca riset, merekonstruksi argumen, menulis eksposisi, mengelola provenance, menjalankan komputasi yang dapat direproduksi, menangani errata, dan menyusun kontribusi yang dapat diaudit.</p>
<div class="grid" aria-label="Ringkasan kursus">
<div class="card"><span class="metric">{counts['units']}</span>unit berurutan</div>
<div class="card"><span class="metric">{counts['learning_outcomes']}</span>hasil belajar</div>
<div class="card"><span class="metric">{counts['exercises']}</span>latihan + 54 panduan</div>
<div class="card"><span class="metric">{counts['assessments']}</span>rancangan penilaian</div>
</div>
<p><a href="{PAGES_ROOT}">Buka pembaca lengkap</a> · <a href="{esc(learning['portable_reader'])}">Unduh pembaca HTML luring</a> · <a href="learning-map.json">Data jalur terbuka</a></p>
<div class="notice"><strong>Batas kebenaran:</strong> backend ini menyediakan definisi dan templat. Ia tidak menyatakan bahwa siapa pun telah mengirim tugas, mengikuti acara, lulus, atau memperoleh kredensial. Setiap “solusi” native di pasangan latihan adalah panduan, bukan solusi lengkap.</div>
<h2>Urutan belajar</h2>
{''.join(units)}
<h2>Prasyarat program</h2><p>{' · '.join(f'<code>{esc(item)}</code>' for item in learning['prerequisites'])}</p>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in learning['limitations'])}</ul>
"""
    return shell("D120 · Kerja Matematika yang Dapat Ditelusuri", body)


def render_educator(bundle: dict) -> str:
    educator = bundle["educator_map"]
    counts = bundle["capabilities"]["counts"]
    assessment_blocks = []
    for assessment in educator["assessments"]:
        criteria = "".join(
            f"<li><code>{esc(item['criterion_id'])}</code> — {esc(local_text(item, 'criterion_text', local_text(item, 'label', 'Kriteria native')))}</li>"
            for item in assessment["rubric"]["criteria"]
        )
        assessment_blocks.append(
            "<details class=\"assessment\">"
            f"<summary>{esc(local_text(assessment, 'label', assessment['assessment_id']))} "
            f"<span class=\"pill\">{esc(assessment['kind'])}</span></summary>"
            f"<p>{esc(local_text(assessment, 'description'))}</p>"
            f"<p><strong>Instruksi:</strong> {esc(local_text(assessment, 'instructions'))}</p>"
            f"<p><code>{esc(assessment['assessment_id'])}</code> · autentisitas: <code>{esc(assessment['authenticity'])}</code> · "
            f"{len(assessment['outcome_ids'])} hasil · {len(assessment['evidence_spec_ids'])} spesifikasi bukti</p>"
            f"<p>Penilai: {', '.join(f'<code>{esc(item)}</code>' for item in assessment['evaluator_role_ids'])}</p>"
            f"<h3>Rubrik <code>{esc(assessment['rubric']['rubric_id'])}</code></h3><ol>{criteria}</ol>"
            "</details>"
        )
    credential_rows = "".join(
        f"<tr><th scope=\"row\"><code>{esc(row['credential_state_id'])}</code></th>"
        f"<td>{esc(local_text(row, 'state_label', row['state_code']))}</td><td>{'Ya' if row['terminal'] else 'Tidak'}</td>"
        f"<td>{'Ya' if row['claims_external_participation'] else 'Tidak'}</td></tr>"
        for row in educator["credential_state_definitions"]
    )
    body = f"""
<p class="muted">D120 · tampilan pengajar · <code>{CONTRACT}</code></p>
<h1>Rute, penilaian, dan bukti untuk pengajar</h1>
<p class="lede">Tampilan ini menghubungkan identitas unit yang dilihat pelajar dengan 71 hasil belajar, 14 penilaian, 14 rubrik, 79 kriteria, 79 spesifikasi bukti, dan lima peran evaluator—tanpa menciptakan rekaman pelajar fiktif.</p>
<div class="grid" aria-label="Ringkasan penilaian">
<div class="card"><span class="metric">9</span>penilaian unit/capstone</div>
<div class="card"><span class="metric">5</span>penilaian autentik</div>
<div class="card"><span class="metric">{counts['criteria']}</span>kriteria rubrik</div>
<div class="card"><span class="metric">0</span>hasil pelajar yang diklaim</div>
</div>
<p><a href="educator-map.json">Unduh peta pengajar</a> · <a href="{PAGES_ROOT}wrapper/">Buka perangkat penyampaian native</a> · <a href="D120.html">Lihat jalur pelajar yang sama</a></p>
<div class="notice"><strong>Interpretasi wajib:</strong> semua objek submission, attempt, result, dan credential di sumber adalah templat atau definisi keadaan. Lima contoh kalibrasi bersifat sintetis dan tidak memberi kredit. Jalur tindakan komunitas mempertahankan alternatif lokal yang lebih lemah; adapter tidak mengklaim pengiriman atau penerimaan eksternal.</div>
<h2>Rancangan penilaian</h2>{''.join(assessment_blocks)}
<h2>Definisi keadaan kredensial</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Label</th><th>Terminal</th><th>Mengklaim partisipasi eksternal</th></tr></thead><tbody>{credential_rows}</tbody></table></div>
<h2>Batas adapter</h2><ul>{''.join(f'<li>{esc(item)}</li>' for item in educator['limitations'])}</ul>
"""
    return shell("D120 · Tampilan pengajar", body)


def build(native_root: Path, adapter: Path) -> dict:
    bundle = derive_projection(native_root)
    errors = projection_errors(bundle)
    if errors:
        raise ValueError(f"Native projection failed: {errors}")

    files = {
        "input/source-lock.json": canonical_json_bytes(bundle["source_lock"]),
        "data/learning-map.json": canonical_json_bytes(bundle["learning_map"]),
        "data/educator-map.json": canonical_json_bytes(bundle["educator_map"]),
        "data/capabilities.json": canonical_json_bytes(bundle["capabilities"]),
        "data/ledger-references.json": canonical_json_bytes(bundle["ledger_references"]),
        "data/public-evidence.json": canonical_json_bytes(bundle["public_evidence"]),
        "data/rights-and-terms.json": canonical_json_bytes(bundle["rights_and_terms"]),
        "data/claim-boundary.json": canonical_json_bytes(bundle["claim_boundary"]),
        "views/D120.html": render_learner(bundle).encode("utf-8"),
        "views/D120-pengajar.html": render_educator(bundle).encode("utf-8"),
        "fixtures/negative-fixtures.json": canonical_json_bytes({
            "schema": "d120-negative-fixture-index/1",
            "course_id": COURSE_ID,
            "fixtures": [
                "duplicate_unit", "missing_unit", "orphan_exercise", "wrong_guidance_kind",
                "missing_outcome", "wrong_locale", "fragment_promoted_to_semantic_id",
                "learner_attempt_claim", "learner_submission_claim", "learner_result_claim",
                "credential_assertion_claim", "community_participation_claim",
                "missing_assessment", "rubric_criterion_loss", "base_ledger_count_change",
                "wrapper_ledger_count_change", "ledger_collapse", "nonanonymous_github",
                "nonanonymous_zenodo", "blanket_license_claim", "native_body_copy",
                "central_truth_rewrite", "public_state_change", "input_hash_change",
            ],
        }),
        "README.md": (
            "# D120 common capability adapter\n\n"
            "This is a zero-copy projection of the native O017/D120 backend into "
            "`course-learning-capability/1`. It preserves native IDs, separates the "
            "1,107-row base relation ledger from the 1,704-row semantic-wrapper ledger, "
            "and gives learners and educators shared unit, outcome, exercise, guidance, "
            "assessment, rubric and evidence identities. Course prose, source files, "
            "PDFs and archives remain in the native public edition.\n\n"
            "No learner attempt, submission, result, external participation or credential "
            "is claimed. HTML fragments are locators only. Rights remain component-specific.\n"
        ).encode("utf-8"),
    }
    for relative, data in files.items():
        target = adapter / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    outputs = [identity(adapter / path, display_path=path) for path in sorted(files)]
    counts = bundle["capabilities"]["counts"]
    manifest = {
        "schema": "d120-capability-manifest/1",
        "course_id": COURSE_ID,
        "native_course_id": NATIVE_COURSE_ID,
        "contract": CONTRACT,
        "contract_2_3_1_conformance": "not_claimed",
        "locale": LOCALE,
        "native_family": "research_practice",
        "native_release": RELEASE_VERSION,
        "content_policy": "selected_localized_metadata_and_evidence_only",
        "projection": {
            "zero_copy_native_bodies": True,
            "native_ids_preserved": True,
            "base_and_wrapper_ledgers_distinct": True,
            "renderer_fragments_are_locators_only": True,
            "central_course_truth_rewritten": False,
            "public_state_changed": False,
            "strict_native_roundtrip_claimed": False,
        },
        "counts": counts,
        "inputs": bundle["source_lock"]["inputs"],
        "outputs": outputs,
        "validation_path": "validation.json",
    }
    write_json(adapter / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-root", type=Path, default=DEFAULT_NATIVE)
    parser.add_argument("--adapter", type=Path, default=DEFAULT_ADAPTER)
    args = parser.parse_args()
    manifest = build(args.native_root.resolve(), args.adapter.resolve())
    print(canonical_json_bytes({
        "state": "pass",
        "course_id": COURSE_ID,
        "outputs": len(manifest["outputs"]),
        "units": manifest["counts"]["units"],
        "exercises": manifest["counts"]["exercises"],
        "assessments": manifest["counts"]["assessments"],
    }).decode("utf-8"), end="")


if __name__ == "__main__":
    main()
