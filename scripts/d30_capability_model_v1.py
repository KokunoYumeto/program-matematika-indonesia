#!/usr/bin/env python3
"""Deterministic zero-copy model for the D30 learning-capability adapter."""

from __future__ import annotations

import copy
import csv
import hashlib
import html
import json
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote


CONTRACT = "course-learning-capability/1"
COURSE_ID = "D30"
NATIVE_COURSE_ID = "course.o009.d30"
REPOSITORY = "https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id"
PAGES = "https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/"
CONTENT_COMMIT = "d0111bc20dc813f5fde12eb715be4cf6dd5a94bd"
CONTENT_TREE = "4bc91cba4fad7cbfbd284267be3d07cafb36251e"
LOCAL_CHECKOUT_COMMIT = "4e2377bba35bfa3665151f5b987059580ff4a40c"
LOCAL_CHECKOUT_TREE = "9acffeb5caf8897e518457295bf6cb1aed246936"
RECORD_ID = 22182655
DOI = "10.5281/zenodo.22182655"
CONCEPT_DOI = "10.5281/zenodo.22059941"
ZENODO_RECORD = f"https://zenodo.org/records/{RECORD_ID}"
ZENODO_FILES = f"https://zenodo.org/api/records/{RECORD_ID}/files/"
AUTHORITATIVE_ORIGINALS = (
    {"label": "Random Services — Probability, Mathematical Statistics, and Stochastic Processes", "url": "https://www.randomservices.org/random/"},
    {"label": "QuantEcon — Continuous Time Markov Chains", "url": "https://continuous-time-mcs.quantecon.org/"},
    {"label": "Gordan Žitković — Introduction to Stochastic Processes", "url": "https://gordanz.github.io/stochastic-book/"},
)

EXPECTED_COUNTS = {
    "entities": 2538,
    "segments": 6333,
    "relations": 3256,
    "units": 2133,
    "high_level_units": 57,
    "rights": 42,
    "terms": 249,
    "corrections": 489,
    "translations": 9,
    "outcomes": 102,
    "labs": 5,
    "theory_units": 36,
    "overview_units": 3,
    "original_bridge_units": 4,
    "mastery_problems": 36,
    "assessment_forms": 2,
    "public_files": 6,
}

PUBLIC_FILES = {
    "00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38.pdf": (39843697, "dda34267df928672e03e04b4c8a36d768aab2d33bc1194b269074da0d2d24e40"),
    "PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_38.zip": (3029582, "e32dba5a896fb847192bbe944e7fd3db4d95f61ee57e33751bbff3108fca214a"),
    "PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_SOURCE_BACKEND_CHECKPOINT_38.zip": (5850300, "7586a6a55a57ebeb40dcfb3116eec740f8cdfeb728c70d9d1d20c2a11c6304f4"),
    "RELEASE_MANIFEST_CHECKPOINT_38.json": (4759, "b84a353b9c89e26b5851585e52f31e21a3201249b0a9e2d404501907fec91378"),
    "ZENODO_METADATA_CHECKPOINT_38.json": (4816, "5c75125a4e65668ab659dea82b3561be3ea47da91731054420af94aec00a12b7"),
    "SHA256SUMS_CHECKPOINT_38.txt": (625, "b529593280c3dad93a6b4617687353f561c0f5a0ab4ff0cf23a982aa345fa836"),
}

SOURCE_INPUTS = (
    "backend/BACKEND_MANIFEST.json",
    "backend/entities.jsonl",
    "backend/segments.jsonl",
    "backend/relations.csv",
    "backend/unit_map.csv",
    "backend/terms.csv",
    "backend/corrections.csv",
    "backend/translations.csv",
    "backend/outcomes.csv",
    "build/site/BUILD_RECEIPT.json",
    "build/site/PACKAGE_MANIFEST.csv",
    "release/RELEASE_MANIFEST_CHECKPOINT_38.json",
    "release/ZENODO_METADATA_CHECKPOINT_38.json",
    "00_control/ZENODO_PUBLICATION_RECEIPT_CHECKPOINT_38.json",
    "00_control/GITHUB_PUBLICATION_RECEIPT.json",
    "00_control/COMPLETION_AUDIT_CHECKPOINT_38.json",
)

FORBIDDEN_KEYS = frozenset({
    "body", "content", "formula", "html", "latex", "markdown", "payload",
    "prose", "solution_text", "source_text", "target_text", "tex",
})

BUNDLE_FILES = {
    "record_index": ("data/native-record-index.jsonl", "jsonl"),
    "segment_index": ("data/native-segment-index.jsonl", "jsonl"),
    "relations": ("data/relations-index.jsonl", "jsonl"),
    "rights": ("data/rights-index.jsonl", "jsonl"),
    "terms": ("data/terms-index.jsonl", "jsonl"),
    "corrections": ("data/corrections-index.jsonl", "jsonl"),
    "capabilities": ("data/capabilities.json", "json"),
    "claim_boundary": ("data/claim-boundary.json", "json"),
    "public_evidence": ("data/public-evidence.json", "json"),
    "learner_map": ("data/learner-map.json", "json"),
    "educator_map": ("data/educator-map.json", "json"),
    "learning_map": ("data/learning-map.json", "json"),
}


class D30Error(ValueError):
    """A D30 adapter failure with a stable diagnostic code."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def canonical_json_line(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256_bytes(data)}


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    write_bytes(path, b"".join(canonical_json_line(row) for row in rows))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def source_url(row: dict[str, Any]) -> str:
    locator = str(row.get("source_locator") or "")
    if locator.startswith(("https://", "http://")):
        return locator
    # ``path`` names the rendered/native course surface, while
    # ``source_locator`` names the exact original evidence.  Prefer the latter
    # for the original link whenever the owner backend supplies it.
    path = locator.split("#", 1)[0].split(":L", 1)[0] or str(row.get("path") or "")
    if not path:
        return f"{REPOSITORY}/tree/{CONTENT_COMMIT}"
    return f"{REPOSITORY}/blob/{CONTENT_COMMIT}/{quote(path, safe='/')}"


def reader_path(path: str) -> str:
    value = path.replace("\\", "/")
    if value.startswith("source/"):
        value = value[7:]
    if value.endswith(".Rmd"):
        value = value[:-4] + ".html"
    elif value.endswith(".md"):
        value = value[:-3] + ".html"
    return value


def reader_url(row: dict[str, Any]) -> str:
    path = reader_path(str(row.get("path") or ""))
    base = PAGES + quote(path, safe="/") if path else PAGES
    return base + "#" + quote(str(row.get("id") or ""), safe="._:-")


def label_for(row: dict[str, Any]) -> str:
    payload = row.get("payload") or {}
    title = payload.get("title") or payload.get("label")
    if title:
        return str(title)
    path = Path(str(row.get("path") or ""))
    if path.name:
        return path.stem.replace("-", " ").replace("_", " ").strip().title()
    return str(row.get("id") or "D30")


class _LocalizedTitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depths = {"title": 0, "h1": 0}
        self.parts: dict[str, list[str]] = {"title": [], "h1": []}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.depths:
            self.depths[tag] += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self.depths and self.depths[tag]:
            self.depths[tag] -= 1

    def handle_data(self, data: str) -> None:
        for tag, depth in self.depths.items():
            if depth:
                self.parts[tag].append(data)

    def value(self) -> tuple[str, str]:
        for tag in ("h1", "title"):
            value = " ".join("".join(self.parts[tag]).split())
            if value:
                return value, tag
        raise D30Error("D30-LOCALIZED-TITLE-MISSING")


def manifested_localized_title(native: Path, row: dict[str, Any], manifest_rows: dict[str, dict[str, str]]) -> tuple[str, dict[str, Any]]:
    relative = reader_path(str(row.get("path") or ""))
    evidence = manifest_rows.get(relative)
    if evidence is None or not relative.casefold().endswith(".html"):
        raise D30Error("D30-LOCALIZED-PAGE-UNMANIFESTED:" + relative)
    page = native / "build/site" / relative
    observed = file_identity(page)
    expected = {"bytes": int(evidence["bytes"]), "sha256": evidence["sha256"]}
    if observed != expected:
        raise D30Error("D30-LOCALIZED-PAGE-HASH:" + relative)
    parser = _LocalizedTitleParser()
    parser.feed(page.read_text(encoding="utf-8"))
    title, element = parser.value()
    return title, {"path": relative, **observed, "element": element}


def unit_kind(row: dict[str, Any]) -> str:
    return str((row.get("payload") or {}).get("unit_kind") or row.get("record_type") or "unit")


def is_high_level(row: dict[str, Any]) -> bool:
    return (
        row.get("record_type") == "unit"
        and row.get("parent_id") == NATIVE_COURSE_ID
        and unit_kind(row) not in {"prerequisites", "program"}
    )


def thin_record(row: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema": "d30-native-record-reference/1",
        "native_id": row["id"],
        "record_type": row["record_type"],
        "parent_id": row.get("parent_id"),
        "order": row.get("order"),
        "path": row.get("path"),
        "resource_id": row.get("resource_id"),
        "edition_id": row.get("edition_id"),
        "source_local_id": row.get("source_local_id"),
        "source_locator": row.get("source_locator"),
        "source_sha256": row.get("source_sha256"),
        "target_sha256": row.get("target_sha256"),
        "locale": row.get("locale"),
        "translation_state": row.get("translation_state"),
        "source_target_relationship": row.get("source_target_relationship"),
        "concept_ids": row.get("concept_ids", []),
        "rights_id": row.get("rights_id"),
        "status": row.get("status"),
        "supersedes": row.get("supersedes"),
        "body_embedded": False,
    }
    payload = row.get("payload") or {}
    if row.get("record_type") == "unit":
        value.update({"unit_kind": unit_kind(row), "title": label_for(row), "reader_url": reader_url(row), "original_url": source_url(row)})
    elif row.get("record_type") == "rights":
        value.update({"license": payload.get("license", "see native rights record"), "license_url": payload.get("license_url")})
    elif row.get("record_type") == "outcome":
        value["cognitive_level"] = payload.get("cognitive_level")
    return value


def thin_segment(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "d30-native-segment-reference/1",
        "native_id": row["id"],
        "parent_id": row.get("parent_id"),
        "order": row.get("order"),
        "path": row.get("path"),
        "source_locator": row.get("source_locator"),
        "source_sha256": row.get("source_sha256"),
        "target_sha256": row.get("target_sha256"),
        "locale": row.get("locale"),
        "translation_state": row.get("translation_state"),
        "source_target_relationship": row.get("source_target_relationship"),
        "concept_ids": row.get("concept_ids", []),
        "rights_id": row.get("rights_id"),
        "status": row.get("status"),
        "segment_kind": str((row.get("payload") or {}).get("segment_kind") or "native-segment"),
        "body_embedded": False,
    }


def forbidden_key_paths(value: Any, prefix: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            here = f"{prefix}.{key}"
            if key.lower() in FORBIDDEN_KEYS:
                found.append(here)
            found.extend(forbidden_key_paths(child, here))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(forbidden_key_paths(child, f"{prefix}[{index}]"))
    return found


def load_bundle(root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, (relative, kind) in BUNDLE_FILES.items():
        result[key] = read_jsonl(root / relative) if kind == "jsonl" else read_json(root / relative)
    return result


def mutate_bundle(bundle: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(bundle)
    operation = mutation["operation"]
    if operation == "drop-native-id":
        changed["record_index"].pop()
    elif operation == "copy-body":
        changed["record_index"][0]["body"] = "forbidden copied native prose"
    elif operation == "alter-hash":
        changed["public_evidence"]["files"][0]["sha256"] = "0" * 64
    elif operation == "flatten-rights":
        for row in changed["record_index"]:
            row["rights_id"] = "rights.d30.blanket"
    elif operation == "bad-reader-link":
        changed["learner_map"]["units"][0]["reader_url"] = "https://example.invalid/copied"
    elif operation == "collapse-state":
        for row in changed["record_index"]:
            row["translation_state"] = "available"
    else:
        raise D30Error("D30-UNKNOWN-MUTATION")
    return changed


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    records = bundle["record_index"]
    segments = bundle["segment_index"]
    relations = bundle["relations"]
    caps = bundle["capabilities"]
    public = bundle["public_evidence"]
    learner = bundle["learner_map"]
    learning = bundle["learning_map"]
    if len(records) != EXPECTED_COUNTS["entities"] or len({x.get("native_id") for x in records}) != len(records):
        errors.append("D30-NATIVE-ID-SET")
    if len(segments) != EXPECTED_COUNTS["segments"] or len({x.get("native_id") for x in segments}) != len(segments):
        errors.append("D30-SEGMENT-ID-SET")
    if len(relations) != EXPECTED_COUNTS["relations"] or len({x.get("relation_id") for x in relations}) != len(relations):
        errors.append("D30-RELATION-ID-SET")
    if forbidden_key_paths(bundle):
        errors.append("D30-ZERO-COPY")
    states = {x.get("translation_state") for x in records}
    if not {"authored", "built", "draft", "external_dependency", "source_frozen", "structurally_verified", "translated"}.issubset(states):
        errors.append("D30-STATE-FIDELITY")
    rights = {x.get("native_id") for x in bundle["rights"]}
    native_rights = {x.get("native_id") for x in records if x.get("record_type") == "rights"}
    referenced_rights = {x.get("rights_id") for x in records if x.get("rights_id")}
    if len(rights) != EXPECTED_COUNTS["rights"] or rights != native_rights or not referenced_rights.issubset(native_rights) or any(x.get("record_type") == "rights" and x.get("rights_id") is not None for x in records):
        errors.append("D30-RIGHTS-BOUNDARY")
    if len(bundle["terms"]) != EXPECTED_COUNTS["terms"] or len(bundle["corrections"]) != EXPECTED_COUNTS["corrections"]:
        errors.append("D30-LEDGER-COUNTS")
    file_map = {x.get("filename"): (x.get("bytes"), x.get("sha256")) for x in public.get("files", [])}
    if file_map != PUBLIC_FILES or public.get("record_id") != RECORD_ID or public.get("all_public_sha256_exact") is not True:
        errors.append("D30-PUBLIC-IDENTITY")
    if len(learner.get("units", [])) != EXPECTED_COUNTS["high_level_units"] or not all(str(x.get("reader_url", "")).startswith(PAGES) and str(x.get("original_url", "")).startswith((REPOSITORY, "https://", "http://")) for x in learner.get("units", [])):
        errors.append("D30-PUBLIC-ROUTES")
    if learning.get("contract") != CONTRACT or learning.get("course_id") != COURSE_ID or len(learning.get("units", [])) != EXPECTED_COUNTS["high_level_units"]:
        errors.append("D30-SHARED-CONTRACT")
    if caps.get("zero_copy", {}).get("native_bodies_embedded") is not False or caps.get("scope", {}).get("mastery_problems") != 36 or caps.get("scope", {}).get("assessment_forms") != 2:
        errors.append("D30-CAPABILITY-TRUTH")
    return sorted(set(errors))


def render_html(title: str, intro: str, units: list[dict[str, Any]], educator: bool = False) -> bytes:
    rows = []
    for unit in units:
        links = (
            f'<a href="{html.escape(unit["reader_url"], quote=True)}">Pembaca publik</a> · '
            f'<a href="{html.escape(unit["original_url"], quote=True)}">Sumber asli terkunci</a>'
        )
        rows.append(
            f'<li id="{html.escape(unit["native_id"], quote=True)}"><code>{html.escape(unit["native_id"])}</code>'
            f'<strong>{html.escape(unit["title"])}</strong><span>{html.escape(unit["unit_kind"])}</span>{links}</li>'
        )
    role_note = "Peta pengajar: hak, relasi, asesmen, dan provenance tetap terpisah." if educator else "Peta pembelajar: buka isi pada pembaca publik native."
    originals = "".join(
        f'<li><a href="{html.escape(row["url"], quote=True)}">{html.escape(row["label"])}</a></li>'
        for row in AUTHORITATIVE_ORIGINALS
    )
    page = f'''<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>body{{font:16px/1.5 system-ui;max-width:1100px;margin:auto;padding:2rem;color:#172033}}nav a{{margin-right:1rem}}li{{display:grid;gap:.25rem;padding:1rem 0;border-bottom:1px solid #ccd5e0}}code,span{{color:#526174}}strong{{font-size:1.08rem}}a{{color:#075ea8}}</style></head>
<body><nav aria-label="Program"><a href="/en/">English program /en/</a><a href="/id/">Program Indonesia /id/</a></nav>
<header><p>D30 · course-learning-capability/1 · zero-copy</p><h1>{html.escape(title)}</h1><p>{html.escape(intro)}</p><p>{html.escape(role_note)}</p><p><a href="{PAGES}">Pembaca native lengkap</a> · <a href="{ZENODO_RECORD}">Rekaman asli Zenodo</a> · <a href="{REPOSITORY}/tree/{CONTENT_COMMIT}">Sumber asli pada commit terkunci</a></p></header>
<section aria-labelledby="authoritative-originals"><h2 id="authoritative-originals">Sumber asli otoritatif</h2><ul>{originals}</ul></section>
<main><ol>{''.join(rows)}</ol></main></body></html>
'''
    return page.encode("utf-8")
