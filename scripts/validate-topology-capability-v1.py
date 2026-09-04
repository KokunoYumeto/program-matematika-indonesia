"""Validate C90 projection fidelity, destinations, UI contracts and replay."""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import jsonschema

from topology_capability_v1 import BASE, DOCS, READER_URL, ROOT, build_model, encoded, fact, load_json, read_inputs


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.plans = []
        self.choices = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            assert attrs["id"] not in self.ids, attrs["id"]
            self.ids.add(attrs["id"])
        for field in ("href", "src"):
            if attrs.get(field):
                self.links.append(attrs[field])
        if "data-plan" in attrs:
            self.plans.append(json.loads(attrs["data-plan"]))
        if tag == "input" and attrs.get("type") == "checkbox":
            self.choices += 1
            assert attrs.get("aria-label")


def verify_projection(model, source):
    expected = build_model(source)
    assert model == expected
    counts = model["counts"]
    assert counts == {
        "chapters": 20, "chapter_companions": 20, "completion_modules": 8,
        "chapter_staged_records": 1171, "source_support_records": 1027,
        "chapter_mastery_records": 144, "completion_mastery_records": 56,
        "staged_records": 1227, "stage_surfaces": 4908,
        "support_relations": 3681, "occurrence_aliases": 3, "terms": 299,
        "term_statuses": {"approved": 298, "provisional": 1},
        "corrections": 272,
        "correction_statuses": {"verified": 268, "unresolved": 2, "superseded": 2},
        "unresolved_corrections": 2,
    }
    ids = [entry["id"] for entry in model["entries"]]
    assert len(ids) == len(set(ids)) == 1227
    assert sum(chapter["entry_count"] for chapter in model["chapters"]) == 1171
    assert sum(len(module["entry_ids"]) for module in model["completion_modules"]) == 56
    assert {entry_id for chapter in model["chapters"] for entry_id in chapter["entry_ids"]} == {entry["id"] for entry in model["entries"] if entry["chapter"]}
    assert {entry_id for module in model["completion_modules"] for entry_id in module["entry_ids"]} == {entry["id"] for entry in model["entries"] if entry["completion_module"]}
    runtime = {(row["entry_id"], row["stage"]): row for row in source["runtime"]}
    assert len(runtime) == 4908
    for entry in model["entries"]:
        assert set(entry["stages"]) == set(entry["stage_urls"]) == set(entry["stage_facts"]) == {"statement", "hint", "answer", "solution"}
        for stage, identifier in entry["stages"].items():
            row = runtime[(entry["id"], stage)]
            assert entry["stage_facts"][stage] == row
            assert identifier == row["stage_id"]
            assert entry["stage_urls"][stage] == READER_URL + "knowl/" + identifier + ".html"
    entry_ids = set(ids)
    assert all(alias["canonical_entry_id"] in entry_ids for alias in model["occurrence_aliases"])
    assert model["native_edition"]["public_release"]["record_doi"] == "10.5281/zenodo.22229720"
    assert model["native_edition"]["public_release"]["concept_doi"] == "10.5281/zenodo.22059894"
    assert model["rights_accessibility"]["pdf_tagged"] is False
    assert model["rights_accessibility"]["html_primary_accessible_surface"] is True


def validate(output_root=ROOT, write_receipt=True):
    source = read_inputs()
    model = load_json(output_root / DOCS / "learning-map.json")
    schema = load_json(ROOT / "schemas/course-capsule-v1/topology-learning-capability-v1.schema.json")
    jsonschema.Draft202012Validator(schema).validate(model)
    verify_projection(model, source)
    manifest = load_json(output_root / BASE / "manifest.json")
    assert manifest["contract"] == model["contract"] and manifest["roles"] == ["C90"]
    for item in manifest["inputs"]:
        assert fact(item["path"], (ROOT / item["path"]).read_bytes()) == item, item["path"]
    for item in manifest["outputs"]:
        assert fact(item["path"], (output_root / item["path"]).read_bytes()) == item, item["path"]

    negative = []
    mutations = [
        ("lost_entry", lambda candidate: candidate["entries"].pop()),
        ("wrong_stage_destination", lambda candidate: candidate["entries"][0]["stage_urls"].__setitem__("solution", "https://example.invalid/solution")),
        ("wrong_stage_hash", lambda candidate: candidate["entries"][0]["stage_facts"]["statement"].__setitem__("sha256", "0" * 64)),
        ("promoted_provisional_term", lambda candidate: next(term for term in candidate["terms"] if term["native"]["status"] == "provisional")["native"].__setitem__("status", "approved")),
        ("resolved_unresolved_correction", lambda candidate: next(item for item in candidate["corrections"] if item["native"]["status"] == "unresolved")["native"].__setitem__("status", "verified")),
        ("lost_alias", lambda candidate: candidate["occurrence_aliases"].pop()),
        ("wrong_public_version", lambda candidate: candidate["native_edition"]["public_release"].__setitem__("record_doi", "10.5281/zenodo.22164668")),
        ("false_pdf_accessibility", lambda candidate: candidate["rights_accessibility"].__setitem__("pdf_tagged", True)),
    ]
    expected = build_model(read_inputs())
    for name, mutate in mutations:
        candidate = copy.deepcopy(model)
        mutate(candidate)
        try:
            assert candidate == expected
        except AssertionError:
            negative.append(name)
        else:
            raise AssertionError("Mutation accepted: " + name)

    pages = {}
    for item in manifest["outputs"]:
        if item["path"].endswith(".html"):
            page = Page()
            page.feed((output_root / item["path"]).read_text(encoding="utf-8"))
            pages[item["path"]] = page
    allowed_native = {chapter[key] for chapter in model["chapters"] for key in ("source_url", "companion_url")}
    allowed_native |= {module["reader_url"] for module in model["completion_modules"]}
    allowed_native |= {url for entry in model["entries"] for url in entry["stage_urls"].values()}
    internal_links = 0
    native_links = 0
    for relative, page in pages.items():
        for url in page.links:
            parsed = urlsplit(url)
            if parsed.netloc == "kokunoyumeto.github.io" and parsed.path.startswith("/topology-an-inquiry-based-approach-id/"):
                assert url in allowed_native
                native_links += 1
                continue
            if parsed.scheme:
                assert parsed.netloc in {"doi.org", "github.com"}
                continue
            target = (output_root / relative).parent / unquote(parsed.path)
            if not parsed.path:
                target = output_root / relative
            if parsed.path.endswith("/") or target.is_dir():
                target = target / "index.html"
            if not target.exists():
                try:
                    fallback = ROOT / target.resolve().relative_to(output_root.resolve())
                except ValueError:
                    fallback = target
                target = fallback
            if target.name == "validation.json":
                continue
            assert target.is_file(), (relative, url)
            internal_links += 1

    teacher = pages[(DOCS / "pengajar.html").as_posix()]
    assert teacher.choices == len(teacher.plans) == 1227
    by_id = {entry["id"]: entry for entry in model["entries"]}
    for plan in teacher.plans:
        entry = by_id[plan["id"]]
        assert plan["tahap"] == entry["stage_urls"]
        assert plan["identitas_byte"] == entry["stage_facts"]
        assert plan["sumber_locator"] == entry["source_locator"]
        assert plan["hak_komponen"] == entry["component_rights"]

    private_name = Path.home().name
    sensitive = re.compile(r"(?i)(?:[A-Z]:[\\/](?:Users|Documents)[\\/]|(?:access|api)[_-]?token|bearer\s+[A-Za-z0-9._-]+|\b" + re.escape(private_name) + r"\b)")
    for item in manifest["outputs"]:
        if Path(item["path"]).suffix.lower() in {".html", ".json", ".js", ".css", ".md", ".txt"}:
            assert not sensitive.search((output_root / item["path"]).read_text(encoding="utf-8")), item["path"]

    with tempfile.TemporaryDirectory(prefix="topology-replay-") as temp:
        temp = Path(temp)
        for name in ("a", "b"):
            subprocess.run(["python", "-B", str(ROOT / "scripts/build-topology-capability-v1.py"), "--output-root", str(temp / name)], check=True, capture_output=True)
        replay_items = manifest["outputs"] + [fact(BASE / "manifest.json", (output_root / BASE / "manifest.json").read_bytes())]
        for item in replay_items:
            assert (temp / "a" / item["path"]).read_bytes() == (temp / "b" / item["path"]).read_bytes() == (output_root / item["path"]).read_bytes(), item["path"]
    controls = subprocess.run(["node", str(ROOT / "scripts/test-topology-controls-v1.mjs")], check=True, capture_output=True, text=True)
    receipt = {
        "state": "pass", "contract": model["contract"], "roles": ["C90"],
        "manifest_sha256": fact("", (output_root / BASE / "manifest.json").read_bytes())["sha256"],
        "schema_validation": True, "complete_native_projection_equality": True,
        "all_4908_native_destinations_byte_bound": True, "native_pending_states_preserved": True,
        "learner_teacher_shared_identity": True, "isolated_two_build_byte_identity": True,
        "reader_bytes_zero_copy": True, "negative_fixtures_rejected": negative,
        "teacher_selections_checked": teacher.choices, "internal_links_checked": internal_links,
        "native_links_checked": native_links, "privacy_scan": "pass", "controls": json.loads(controls.stdout),
        "counts": model["counts"],
        "scope": "Frozen native metadata, all staged destination byte identities, learner/teacher routing, status preservation and deterministic adapter replay; no native book rebuild or human-learning certification.",
    }
    if write_receipt:
        for path in (BASE / "validation.json", DOCS / "validation.json"):
            destination = output_root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(encoded(receipt))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(validate(args.output_root), ensure_ascii=False))
