#!/usr/bin/env python3
"""Read-only checks of the exact publicly released Judson native authority.

Optional extraction is restricted to this candidate's authority-replay directory.
No owner file, publication, or repository state is modified.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

EXPECTED_BYTES = 69370499
EXPECTED_SHA = "0aa85116679703b632333f4003b3373f42bb7b282c3719bea3731257c0fe55e0"
MANIFEST_SHA = "4294d16f96ea7fa405d6841e308e7c90c08152a2c7eb6cefe45a44e5b705bcd1"
PUBLIC_URL = "https://zenodo.org/records/22062449/files/ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2_SOURCE_BACKEND.zip?download=1"

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def id_hash(values):
    return sha("".join(x + "\n" for x in sorted(set(values))).encode())

def inspect(path: Path, extract: bool = False):
    require(path.stat().st_size == EXPECTED_BYTES, "source archive size drift")
    with path.open("rb") as stream:
        require(hashlib.file_digest(stream, "sha256").hexdigest() == EXPECTED_SHA, "source archive hash drift")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        require(len(entries) == 416, "archive inventory count drift")
        names = [i.filename for i in entries]
        require(len(names) == len(set(names)), "duplicate archive paths")
        require(sum(i.file_size for i in entries) < 512 * 1024 * 1024, "unexpected archive expansion")
        facts = []
        for entry in entries:
            rel = PurePosixPath(entry.filename)
            require(not rel.is_absolute() and ".." not in rel.parts and "\\" not in entry.filename and ":" not in entry.filename, "unsafe ZIP path")
            require(not stat.S_ISLNK(entry.external_attr >> 16), "ZIP symlink forbidden")
            digest, count = hashlib.sha256(), 0
            with archive.open(entry) as stream:
                for data in iter(lambda: stream.read(512 * 1024), b""):
                    digest.update(data)
                    count += len(data)
            require(count == entry.file_size, "ZIP entry size mismatch")
            facts.append({"path": entry.filename, "bytes": count, "sha256": digest.hexdigest()})
        raw = archive.read("backend/v1/manifest.json")
        require(len(raw) == 5669 and sha(raw) == MANIFEST_SHA, "native manifest identity drift")
        manifest = json.loads(raw)
        tables, checked = {}, []
        for fact in manifest["files"]:
            name = "backend/v1/" + fact["path"]
            data = archive.read(name)
            require(len(data) == fact["bytes"] and sha(data) == fact["sha256"], "manifest binding mismatch: " + name)
            count = None
            if name.endswith(".jsonl"):
                rows = [json.loads(line) for line in data.decode("utf-8").splitlines()]
                require(all(isinstance(r, dict) for r in rows), "non-object native row")
                tables[fact["path"]] = rows
                count = len(rows)
            elif name.endswith(".csv"):
                count = len(list(csv.reader(io.StringIO(data.decode("utf-8"), newline=""))))
            if fact["rows"] is not None:
                require(count == fact["rows"], "native row-count mismatch: " + name)
            checked.append({**fact, "observed_rows": count})

        units = {r["id"]: r for r in tables["topology/units.jsonl"]}
        identity = tables["identity/id-map.jsonl"]
        segments = {r["id"]: r for r in tables["text/segments.en-US.jsonl"]}
        translations = tables["text/translations.id-ID.jsonl"]
        require(len(units) == 3323 and len(identity) == 3323, "unit or identity coverage drift")
        require({r["unit_id"] for r in identity} == set(units), "native identity coverage is not exact")
        require(len(segments) == 4466 and len(translations) == 4466, "segment count drift")
        require({r["segment_id"] for r in translations} == set(segments), "translation/source segment coverage mismatch")
        require(all(r["unit_id"] in units for r in segments.values()), "segment points outside unit graph")
        require(all(r["source_sha256"] == segments[r["segment_id"]]["source_sha256"] for r in translations), "translation source-hash mismatch")

        courses = {r["id"]: r for r in tables["courses/courses.jsonl"]}
        memberships = tables["courses/course-units.jsonl"]
        require({r["code"] for r in courses.values()} == {"C30", "C40"}, "unexpected native course roles")
        require(len(memberships) == 23 and len({r["unit_id"] for r in memberships}) == 23, "chapter selection duplicates or gaps")
        require(all(r["course_id"] in courses and units[r["unit_id"]]["kind"] == "chapter" for r in memberships), "course chapter membership invalid")
        by_chapter = {r["unit_id"]: courses[r["course_id"]]["code"] for r in memberships}
        derived = collections.Counter()
        for uid, unit in units.items():
            seen, current = set(), uid
            while current in units and current not in by_chapter:
                require(current not in seen, "native parent cycle")
                seen.add(current)
                current = units[current].get("parent_id")
            derived[by_chapter.get(current, "outside_two_chapter_selectors")] += 1

        native_ids = {r["id"] for rows in tables.values() for r in rows if isinstance(r.get("id"), str)}
        relations = tables["topology/relations.jsonl"]
        require(len(relations) == 6505, "relation count drift")
        unresolved = sorted({r[k] for r in relations for k in ("from_id", "to_id") if r[k] not in native_ids})
        states = collections.Counter(r["state"] for r in translations)
        frozen = [r for r in translations if r["state"] == "source_frozen"]
        result = {
            "schema_id": "interlanguage/judson-native-public-authority-check/v1",
            "status": "PASS_ARCHIVE_MANIFEST_AND_DECLARED_GRAPH_BINDINGS",
            "public_source_archive": {"url": PUBLIC_URL, "bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA},
            "network_requests": 0,
            "archive_entries": len(facts),
            "uncompressed_bytes": sum(r["bytes"] for r in facts),
            "zip_stream_crc_and_sha_checks": "pass_every_entry",
            "archive_member_facts": facts,
            "native_manifest": {"path": "backend/v1/manifest.json", "bytes": len(raw), "sha256": sha(raw)},
            "native_manifest_file_bindings": checked,
            "unit_count": len(units),
            "unit_identity_set_sha256": id_hash(units),
            "persistent_identity_rows": len(identity),
            "relation_count": len(relations),
            "relation_type_counts": dict(sorted(collections.Counter(r["type"] for r in relations).items())),
            "unresolved_relation_endpoint_ids": unresolved,
            "chapter_membership_counts": dict(sorted(collections.Counter(courses[r["course_id"]]["code"] for r in memberships).items())),
            "derived_ancestry_view_counts": dict(sorted(derived.items())),
            "translation_segment_pairs": len(translations),
            "translation_state_counts": dict(sorted(states.items())),
            "source_frozen_content_locales": dict(sorted(collections.Counter(r.get("content_locale", "missing") for r in frozen).items())),
            "source_frozen_reason_codes": dict(sorted(collections.Counter(str(r.get("state_reason")) for r in frozen).items())),
            "excluded_claims": ["native builder replay not performed by this script", "no semantic translation review", "no central adapter admission", "no learner HTML anchor verification", "no Sage execution"],
        }
        if extract:
            dest = Path(__file__).resolve().parent / "authority-replay"
            require(dest.resolve().is_relative_to(Path(__file__).resolve().parent), "extraction outside candidate root")
            for entry, fact in zip(entries, facts, strict=True):
                target = dest.joinpath(*PurePosixPath(entry.filename).parts)
                require(target.resolve().is_relative_to(dest.resolve()), "unsafe extraction target")
                if entry.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                data = archive.read(entry)
                if target.exists():
                    require(target.is_file() and sha(target.read_bytes()) == fact["sha256"], "existing replay input differs; refusing overwrite")
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as stream:
                        stream.write(data)
            result["extraction"] = {"path_relative_to_candidate": "authority-replay", "entries": len(entries), "overwrite_existing_bytes": False}
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--extract-replay", action="store_true")
    args = parser.parse_args()
    print(json.dumps(inspect(args.source_archive, args.extract_replay), sort_keys=True, ensure_ascii=False, indent=2))
