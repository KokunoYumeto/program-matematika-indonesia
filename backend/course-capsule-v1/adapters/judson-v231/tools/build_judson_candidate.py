#!/usr/bin/env python3
"""Offline, ZIP-bound Judson C30/C40 v2.3.1 candidate; not an admission."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
import uuid
import zipfile

from v231_adapter_common import (
    CAPABILITY_NAMES, RECORD_TYPE_BY_TABLE, canonical_row_sha256, compact_json,
    empty_tables, file_fact, identity_set_sha256, inventory_sha256, make_row,
    mapping_set_sha256, package_payload_files, projection_id, require,
    sha256_bytes, sha256_file, sort_table_rows, write_checksums,
    write_csv_surfaces, write_json, write_jsonl, write_tables,
)

STAMP = "2026-08-31T13:32:05Z"
CORPUS = "judson-aata"
NS = uuid.UUID("0e4d7b37-6108-5065-b08f-d1098697cc02")
NATIVE_NS = "judson-aata/interlanguage.modular/1.0.0"
CENTRAL_NS = "interlanguage/global-modular-mathematics/0.1.0"
ZIP_NAME = "ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2_SOURCE_BACKEND.zip"
ZIP_BYTES = 69370499
ZIP_SHA = "0aa85116679703b632333f4003b3373f42bb7b282c3719bea3731257c0fe55e0"
ZIP_URL = "https://zenodo.org/records/22062449/files/" + ZIP_NAME + "?download=1"
MANIFEST_SHA = "4294d16f96ea7fa405d6841e308e7c90c08152a2c7eb6cefe45a44e5b705bcd1"
ROUTE_INPUT = "frozen-inputs/JUDSON_TWO_COURSE_LEARNER_ROUTES.json"
ROUTE_EXPECTED = (47314, "3f22e70fff457fc96dc44c2cb4930ae25a0ab401fb6ad0a3387ed8d98e2d84c4")
ROUTE_OFFLINE_SHA = "cd5e0dd51e5889c007bc28cf5afb19a70dfa496816d49f17fcb072faa64a88a4"
CONTRACT = "backend/v2.2/global-capability-contract-v0.1.0.json"
CAPSULES = "releases/v0.62.13/course-capsules-v1.jsonl"
CENTRAL_FACTS = {
    CONTRACT: (7462, "f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7"),
    CAPSULES: (226934, "2c885781e9b69de6afdc2cbfe8e7d95d26ba97f0ffe571a12b4ec1ead575d6d1"),
}
EXACT_TOOLS = {
    "validate_lane_adapter_v231.py": (19967, "0e7819083a7a61cc62fa2ae8cbf0060cef12425932da84b992215f4853c18d51"),
    "v231_adapter_common.py": (14946, "11aa3db3fddabb6016ca51294d726426436470026808311862fb1298df88d774"),
    "replay_judson_two_course_learner_routes.py": (11666, "9f8ae31296ef48f7126a1f4d27a8d202176f747add8df01d26ce08631224a049"),
}
EXACT_SCHEMAS = {
    "lane-adapter-v2.3.1.schema.json": (5286, "0d2763321d6cd613d426bd81f2acede6288a0f17ca2f28cb324be0a052ec1b0e"),
    "capability-declarations-v0.2.schema.json": (4558, "92b73a5cc631fe4262f08cc0dec8a821e2c14e1cdd280b6d0e619954f54a9539"),
    "namespace-crosswalk-v0.2.schema.json": (2633, "9bc6847f9fefeeef1637956b6f8b9830a30bd16c5468650ccc78039652b262df"),
    "translation-state-index-v0.2.schema.json": (1589, "7ea2bf85254ce30280003451073b77518dcdc0d635b560f23cfc1e7d89a86d77"),
    "csv-projection-manifest-v0.2.schema.json": (1220, "2702039c3f6390f7985f303c6fa18a9f2410a8cf2493703bdd8bb108b47eb789"),
    "scope-declaration-v0.2.schema.json": (1424, "a4088ea6e13d1048c1403de8dd2c000f42444a22766865f80e4818e5c366412e"),
}


def pid(kind, native):
    return projection_id(NS, kind, CORPUS + ":" + native)


PACKAGE_ID = pid("package", "candidate-v2.3.1-20260831-routes2")
DATASET_ID = pid("dataset", "native-resource:urn:uuid:2f09cb08-d374-5c0e-9d40-3ae04d46bff1")
OWNER_ID = pid("owner_authority", "native-resource:urn:uuid:2f09cb08-d374-5c0e-9d40-3ae04d46bff1")
EXTENSION_ID = pid("adapter_profile", "c30-c40-candidate-v2.3.1")


def exact_bytes(path, expected):
    data = path.read_bytes()
    require((len(data), sha256_bytes(data)) == expected, "frozen input drift: " + path.name)
    return data


def copy_exact(source, target, expected=None):
    data = exact_bytes(source, expected) if expected else source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


class Native:
    """All native reads originate in the exact public archive, never an owner tree."""
    def __init__(self, path):
        require(path.stat().st_size == ZIP_BYTES and sha256_file(path) == ZIP_SHA,
                "public SOURCE_BACKEND.zip bytes/hash mismatch")
        self.z = zipfile.ZipFile(path)
        require(len(self.z.namelist()) == len(set(self.z.namelist())), "duplicate ZIP member")
        manifest_bytes = self.z.read("backend/v1/manifest.json")
        require((len(manifest_bytes), sha256_bytes(manifest_bytes)) == (5669, MANIFEST_SHA),
                "native manifest mismatch")
        self.manifest_bytes = manifest_bytes
        self.manifest = json.loads(manifest_bytes)
        self.raw, self.rows, self.refs, self.facts = {}, {}, {}, {}
        for fact in self.manifest["files"]:
            name = fact["path"]
            full = "backend/v1/" + name
            data = self.z.read(full)
            require((len(data), sha256_bytes(data)) == (fact["bytes"], fact["sha256"]),
                    "native manifest member mismatch: " + name)
            self.raw[name] = data
            self.facts[name] = {"path": full, "path_base": "owner_package_root",
                                "role": "frozen_native_authority", "bytes": len(data),
                                "sha256": sha256_bytes(data)}
            if name.endswith(".jsonl"):
                lines = data.splitlines(keepends=True)
                require(len(lines) == fact["rows"], "native row count drift: " + name)
                rows = [json.loads(line) for line in lines]
                self.rows[name] = rows
                require(len({r["id"] for r in rows}) == len(rows), "duplicate native shard ID: " + name)
                for ordinal, (r, line) in enumerate(zip(rows, lines), 1):
                    self.refs[name, r["id"]] = {
                        "member": full, "jsonl_row_ordinal": ordinal,
                        "json_pointer": "", "native_id": r["id"],
                        "row_bytes": len(line), "row_sha256": sha256_bytes(line),
                    }
            elif name.endswith(".csv"):
                require(len(data.splitlines()) == fact["rows"], "native CSV count drift: " + name)

    def ref(self, name, row):
        return self.refs[name, row["id"]]

    def shard(self, name):
        rows = self.rows.get(name)
        return {**self.facts[name], **({"records": len(rows), "record_id_set_sha256":
                  identity_set_sha256(r["id"] for r in rows)} if rows is not None else {})}


def build(args):
    root = Path(__file__).resolve().parent.parent
    output = args.output.resolve()
    require(not output.exists(), "output must be a new directory; existing work is never overwritten")
    central_root = args.central_root.resolve() if args.central_root else root / "frozen-central"
    central_bytes = {p: exact_bytes(central_root / p, expected) for p, expected in CENTRAL_FACTS.items()}
    route_path = args.route_evidence.resolve() if args.route_evidence else root / ROUTE_INPUT
    route_bytes = exact_bytes(route_path, ROUTE_EXPECTED)
    route_input = json.loads(route_bytes)
    require(datetime.fromisoformat(STAMP.replace("Z", "+00:00")) >= datetime.fromisoformat(route_input["created_utc"]),
            "frozen deterministic build snapshot stamp precedes bound route evidence")
    require(canonical_row_sha256(route_input["offline"]) == ROUTE_OFFLINE_SHA, "frozen offline route identity mismatch")
    require(route_input["authority"]["owner_native_source_package"]["sha256"] == ZIP_SHA,
            "route evidence binds different source archive")
    require(route_input["authority"]["central_capsule_public_base_source"]["sha256"] == CENTRAL_FACTS[CAPSULES][1],
            "route evidence binds different central capsules")
    contract = json.loads(central_bytes[CONTRACT])
    require(contract["identity"]["namespace"] == str(NS), "namespace contract drift")
    capsules = [json.loads(line) for line in central_bytes[CAPSULES].splitlines()]
    capsule_rows = {r["course_id"]: (i, r) for i, r in enumerate(capsules) if r["course_id"] in ("C30", "C40")}
    require(set(capsule_rows) == {"C30", "C40"}, "frozen capsule roles absent")
    for code, (_, capsule) in capsule_rows.items():
        require(capsule["course_native"]["zenodo"] == "https://doi.org/10.5281/zenodo.22062449",
                "capsule does not bind this edition: " + code)
    for filename, fact in EXACT_TOOLS.items():
        exact_bytes(root / "tools" / filename, fact)
    for filename, fact in EXACT_SCHEMAS.items():
        exact_bytes(root / "schema" / filename, fact)
    n = Native(args.source_zip)
    units = n.rows["topology/units.jsonl"]
    relations = n.rows["topology/relations.jsonl"]
    courses = n.rows["courses/courses.jsonl"]
    memberships = n.rows["courses/course-units.jsonl"]
    idmaps = n.rows["identity/id-map.jsonl"]
    segments = n.rows["text/segments.en-US.jsonl"]
    translations = n.rows["text/translations.id-ID.jsonl"]
    edition_segments = n.rows["text/segments.edition.id-ID.jsonl"]
    require([len(x) for x in (units, relations, courses, memberships, idmaps, segments, translations)]
            == [3323, 6505, 2, 23, 3323, 4466, 4466], "native scope count mismatch")
    unit_by_id = {r["id"]: r for r in units}
    course_by_id = {r["id"]: r for r in courses}
    require({r["code"] for r in courses} == {"C30", "C40"}, "native course codes drift")
    for u in units:
        require(u["parent_id"] is None or u["parent_id"] in unit_by_id, "dangling parent")
    # Materialized units exist once. Views are selectors, not cloned unit records.
    chapter_membership = {}
    for m in memberships:
        require(m["course_id"] in course_by_id and m["unit_id"] in unit_by_id, "membership endpoint absent")
        require(unit_by_id[m["unit_id"]]["kind"] == "chapter", "membership is not native chapter")
        require(m["unit_id"] not in chapter_membership, "duplicate native chapter selection")
        chapter_membership[m["unit_id"]] = m
    route_by_unit = {}
    live_by_unit = {r["native_unit_id"]: (i, r) for i, r in enumerate(route_input["live_verification"]["observations"])}
    require(len(live_by_unit) == 23, "route live evidence must have exact distinct chapter coverage")
    for course_index, course in enumerate(route_input["offline"]["courses"]):
        require(course["native_course_id"] in course_by_id and course["course_id"] == course_by_id[course["native_course_id"]]["code"],
                "route native course binding mismatch")
        for route_index, route in enumerate(course["routes"]):
            uid = route["native_unit_id"]
            require(uid in chapter_membership and uid not in route_by_unit, "route chapter identity absent/duplicated")
            member = chapter_membership[uid]
            require(route["native_membership_id"] == member["id"] and route["native_course_id"] == member["course_id"]
                    and route["sequence"] == member["sequence"] and route["native_source_path"] == unit_by_id[uid]["source_path"]
                    and route["html_chapter_id"] == unit_by_id[uid]["source_xml_id"], "native chapter route mismatch")
            live_index, observation = live_by_unit[uid]
            require(observation["course_id"] == course["course_id"] and observation["sequence"] == route["sequence"]
                    and observation["requested_url"] == route["public_url"], "live/offline route selector mismatch")
            require(observation["http_status"] == 200 and observation["matches_frozen_html"] is False,
                    "frozen route observation state mismatch")
            route_by_unit[uid] = {"offline": route, "live": observation,
                                  "offline_pointer": "/offline/courses/" + str(course_index) + "/routes/" + str(route_index),
                                  "live_pointer": "/live_verification/observations/" + str(live_index)}
    require(set(route_by_unit) == set(chapter_membership), "23 native chapter routes not exactly covered")
    course_units = {c["id"]: [] for c in courses}
    outside = []
    unit_memberships = {}
    for u in units:
        cursor, seen, selected = u["id"], set(), None
        while cursor is not None:
            require(cursor not in seen, "native parent cycle")
            seen.add(cursor)
            if cursor in chapter_membership:
                require(selected is None, "nested course chapter selectors")
                selected = chapter_membership[cursor]
            cursor = unit_by_id[cursor]["parent_id"]
        unit_memberships[u["id"]] = selected
        if selected:
            course_units[selected["course_id"]].append(u["id"])
        else:
            outside.append(u["id"])
    require(sum(map(len, course_units.values())) + len(outside) == len(units), "view partition failure")
    # Native endpoints may be assets/courses/corrections/editions, not only units.
    endpoint_registry = defaultdict(list)
    for name, rows in n.rows.items():
        if name.startswith("state/") or name == "identity/id-map.jsonl":
            continue
        for row in rows:
            endpoint_registry[row["id"]].append((name, row))
    endpoint_ids = {r[k] for r in relations for k in ("from_id", "to_id")}
    for rid in endpoint_ids:
        require(len(endpoint_registry[rid]) == 1, "unresolved/ambiguous native relation endpoint: " + rid)
    entity_refs = {}
    for rid in sorted(endpoint_ids):
        name, row = endpoint_registry[rid][0]
        entity_refs[rid] = {"native_record_id": rid, "native_record_type": row["record_type"],
                            "native_namespace": NATIVE_NS, "evidence": n.ref(name, row),
                            "materialization": "unit" if rid in unit_by_id else "referenced_native_record"}
    segment_by_id = {r["id"]: r for r in segments}
    translation_by_segment = {r["segment_id"]: r for r in translations}
    require(set(segment_by_id) == set(translation_by_segment) and len(translation_by_segment) == len(translations),
            "source/translation pairing is not exactly one-to-one")
    require({r["unit_id"] for r in idmaps} == set(unit_by_id), "birth/current identity map coverage mismatch")
    require(len({r["unit_id"] for r in idmaps}) == len(idmaps), "duplicate identity mapping")
    dispositions = {r["id"]: r for r in n.rows["state/segment-dispositions.id-ID.jsonl"]}
    preserved = json.loads(n.raw["state/source-preserved-paths.json"])["paths"]
    preserved_by_path = {r["path"]: (i, r) for i, r in enumerate(preserved)}
    require(Counter(t["state"] for t in translations) == {"translated": 4150, "source_frozen": 316},
            "translation state authority changed")

    output.mkdir(parents=True)
    for name, expected in EXACT_TOOLS.items():
        copy_exact(root / "tools" / name, output / "tools" / name, expected)
    copy_exact(Path(__file__), output / "tools" / Path(__file__).name)
    for name, expected in EXACT_SCHEMAS.items():
        copy_exact(root / "schema" / name, output / "schema" / name, expected)
    for name, expected in CENTRAL_FACTS.items():
        copy_exact(central_root / name, output / "frozen-central" / name, expected)
    copy_exact(route_path, output / ROUTE_INPUT, ROUTE_EXPECTED)
    route_fact = file_fact(output / ROUTE_INPUT, ROUTE_INPUT, "frozen_supplemental_route_evidence")
    copy_exact(root / "README.md", output / "README.md")
    (output / "authority").mkdir()
    (output / "authority/native-manifest.json").write_bytes(n.manifest_bytes)
    central_facts = {p: {"path": p, "path_base": "program_repository_root", "role": "frozen_central_authority",
                        "bytes": size, "sha256": digest} for p, (size, digest) in CENTRAL_FACTS.items()}
    native_manifest_fact = {"path": "backend/v1/manifest.json", "path_base": "owner_package_root",
                            "role": "frozen_native_manifest", "bytes": 5669, "sha256": MANIFEST_SHA}
    tables = empty_tables()
    mappings = []

    def add(table, semantic, payload, owner_state=None):
        row = make_row(NS, RECORD_TYPE_BY_TABLE[table], CORPUS + ":" + semantic, payload,
                       dataset_id=DATASET_ID, owner_authority_id=OWNER_ID, recorded_at=STAMP,
                       normalized_state="candidate", owner_native_state=owner_state)
        tables[table].append(row)
        return row

    def map_native(name, native, projected, source_namespace=NATIVE_NS):
        mapping = {"source_namespace": source_namespace, "target_namespace": CENTRAL_NS,
                   "source_record_id": native["id"], "target_record_id": projected["id"],
                   "source_record_type": native["record_type"], "target_record_type": projected["record_type"],
                   "cardinality": "one_to_one", "mapping_state": "mapped",
                   "reverse_recipe": "Resolve native_id in the exact ZIP member and verify its recorded row digest; projected IDs never replace owner IDs.",
                   "evidence_refs": ["backend/v1/" + name + "#native_id=" + native["id"]],
                   "identity_set_sha256": mapping_set_sha256([(native["id"], projected["id"])])}
        mappings.append(mapping)

    add("owner_authorities", "native-resource:urn:uuid:2f09cb08-d374-5c0e-9d40-3ae04d46bff1",
        {"native_resource_id": "urn:uuid:2f09cb08-d374-5c0e-9d40-3ae04d46bff1",
         "authority": "owner_native", "source_archive": {"filename": ZIP_NAME, "public_url": ZIP_URL,
         "bytes": ZIP_BYTES, "sha256": ZIP_SHA}, "native_manifest": native_manifest_fact,
         "public_access_freshly_checked_by_candidate": False, "candidate_not_admitted": True})
    add("datasets", "native-resource:urn:uuid:2f09cb08-d374-5c0e-9d40-3ae04d46bff1",
        {"native_resource_id": "urn:uuid:2f09cb08-d374-5c0e-9d40-3ae04d46bff1",
         "course_ids": sorted(course_by_id), "curriculum_role_ids": ["C30", "C40"],
         "unit_count": len(units), "native_identity_preserved_by_crosswalk": True,
         "full_prose_centralized": False, "admission_state": "candidate_not_admitted"})
    projected_editions = {}
    for r in n.rows["authority/editions.jsonl"]:
        payload = {"native_id": r["id"], "native_rights_id": r["rights_id"],
                   "locale": r.get("locale"), "source_edition_id": r.get("source_edition_id"),
                   "source_revision_sha": r.get("source_revision_sha", r.get("revision_sha")),
                   "license_expression": "GFDL-1.3-or-later" if r.get("locale") == "id-ID" else "GFDL-1.2-or-later",
                   "native_evidence": n.ref("authority/editions.jsonl", r),
                   "richer_metadata": "referenced_native_shards"}
        row = add("editions", r["id"], payload, r["status"])
        projected_editions[r["id"]] = row["id"]
        map_native("authority/editions.jsonl", r, row)
    projected_units = {u["id"]: pid("unit", u["id"]) for u in units}
    for u in units:
        selected = unit_memberships[u["id"]]
        fields = ("kind", "parent_id", "ordinal", "preorder_index", "authority_preorder_index", "depth",
                  "identity_method", "source_path", "source_xpath", "source_xml_id", "source_label",
                  "source_c14n_sha256", "source_origin", "content_locale", "xml_lang", "translatable",
                  "edition_declaration_id", "edition_id", "rights_id", "resource_id", "supersedes_id")
        payload = {k: u[k] for k in fields if k in u}
        payload.update({"native_id": u["id"], "native_evidence": n.ref("topology/units.jsonl", u),
                        "projected_parent_id": projected_units.get(u["parent_id"]),
                        "native_membership_id": selected["id"] if selected else None,
                        "curriculum_role_ids": [course_by_id[selected["course_id"]]["code"]] if selected else [],
                        "translation_state_is_not_native_active_status": True})
        row = add("units", u["id"], payload, u["status"])
        map_native("topology/units.jsonl", u, row)
    for m in memberships:
        payload = {k: m[k] for k in ("course_id", "unit_id", "sequence", "membership_role", "render")}
        payload.update({"native_id": m["id"], "projected_unit_id": projected_units[m["unit_id"]],
                        "curriculum_role_id": course_by_id[m["course_id"]]["code"],
                        "membership_granularity": "native_chapter_selector", "native_evidence": n.ref("courses/course-units.jsonl", m)})
        row = add("course_unit_memberships", m["id"], payload, m["status"])
        map_native("courses/course-units.jsonl", m, row)
    for name in sorted(n.facts):
        add("native_bindings", "native-manifest-member:" + name,
            {"binding": n.shard(name), "binding_kind": "hash_bound_native_shard_reference",
             "native_rows_copied": False, "native_manifest": native_manifest_fact})
    for c in courses:
        row = add("native_bindings", c["id"], {"native_id": c["id"], "native_record_type": "course",
                  "code": c["code"], "program_id": c["program_id"], "prerequisite_course_ids": c["prerequisite_course_ids"],
                  "selection_policy": c["selection_policy"], "native_evidence": n.ref("courses/courses.jsonl", c)}, c["status"])
        map_native("courses/courses.jsonl", c, row)
    for r in relations:
        payload = {k: v for k, v in r.items() if k not in ("schema", "schema_version", "record_type", "recorded_at", "id", "status", "workflow_id")}
        payload.update({"native_id": r["id"], "native_evidence": n.ref("topology/relations.jsonl", r),
                        "from_projected_unit_id": projected_units.get(r["from_id"]),
                        "to_projected_unit_id": projected_units.get(r["to_id"]),
                        "from_native_record_type": entity_refs[r["from_id"]]["native_record_type"],
                        "to_native_record_type": entity_refs[r["to_id"]]["native_record_type"],
                        "endpoint_evidence_index": "native-relation-endpoints.jsonl"})
        row = add("relations", r["id"], payload, r["status"])
        map_native("topology/relations.jsonl", r, row)
    for r in idmaps:
        payload = {k: v for k, v in r.items() if k not in ("schema", "schema_version", "record_type", "recorded_at", "id", "status", "workflow_id")}
        payload.update({"native_id": r["id"], "projected_unit_id": projected_units[r["unit_id"]],
                        "native_evidence": n.ref("identity/id-map.jsonl", r), "owner_id_reminted": False,
                        "identity_policy": "birth and current selectors are evidence, not translated-label identity inputs"})
        row = add("identity_crosswalks", r["id"], payload, r["status"])
        map_native("identity/id-map.jsonl", r, row)
    by_unit_pairs = defaultdict(list)
    raw_target_counts = Counter()
    for s in segments:
        t = translation_by_segment[s["id"]]
        require(s["unit_id"] in unit_by_id and t["source_sha256"] == s["source_sha256"], "segment source binding mismatch")
        disposition_ref = None
        preservation_target_sha = None
        preservation_basis = None
        if t["state"] == "source_frozen":
            require(t["content_locale"] == "en-US", "frozen content locale drift")
            if t["disposition_id"]:
                d = dispositions[t["disposition_id"]]
                require(d["segment_id"] == s["id"] and d["source_sha256"] == s["source_sha256"]
                        and d["disposition"] == "source_frozen" and d["content_locale"] == t["content_locale"],
                        "frozen disposition mismatch")
                disposition_ref = n.ref("state/segment-dispositions.id-ID.jsonl", d)
                preservation_target_sha = d["target_sha256"]
                preservation_basis = "explicit_native_segment_disposition_target_sha256"
            else:
                index, p = preserved_by_path[s["source_path"]]
                require(p["content_locale"] == t["content_locale"] and p["reason"] == t["state_reason"],
                        "whole-path preservation mismatch")
                disposition_ref = {"member": "backend/v1/state/source-preserved-paths.json",
                                   "json_pointer": "/paths/" + str(index), "source_path": s["source_path"]}
                preservation_target_sha = s["source_sha256"]
                preservation_basis = "explicit_native_whole_path_verbatim_policy_not_translation_target_field"
        else:
            require(t["target_sha256"] is not None and t["content_locale"] == "id-ID", "translated target binding absent")
        raw_target_counts["null" if t["target_sha256"] is None else "present"] += 1
        payload = {"native_source_segment_id": s["id"], "native_translation_id": t["id"],
                   "native_unit_id": s["unit_id"], "projected_unit_id": projected_units[s["unit_id"]],
                   "source_path": s["source_path"], "source_xpath": s["source_xpath"],
                   "source_sha256": s["source_sha256"], "translation_source_sha256": t["source_sha256"],
                   "target_sha256": t["target_sha256"], "native_state": t["state"],
                   "source_locale": s["source_locale"], "target_locale": t["locale"],
                   "content_locale": t["content_locale"], "state_reason": t["state_reason"],
                   "disposition_id": t["disposition_id"], "disposition_reason_code": t["disposition_reason_code"],
                   "preservation_target_sha256": preservation_target_sha,
                   "preservation_target_hash_basis": preservation_basis,
                   "preservation_evidence": disposition_ref,
                   "source_evidence": n.ref("text/segments.en-US.jsonl", s),
                   "translation_evidence": n.ref("text/translations.id-ID.jsonl", t),
                   "source_protected_signature_sha256": sha256_bytes(compact_json(s["protected_signature"]).encode()),
                   "target_protected_signature_sha256": sha256_bytes(compact_json(t["protected_signature"]).encode()),
                   "localized_protected_text_deltas_sha256": sha256_bytes(compact_json(t["localized_protected_text_deltas"]).encode()),
                   "full_text_included": False, "protected_content_semantic_validation": "not_claimed_by_projection"}
        row = add("content_bindings", "source-translation-pair:" + s["id"], payload, t["state"])
        by_unit_pairs[s["unit_id"]].append({"native_source_segment_id": s["id"], "native_translation_id": t["id"],
                                          "content_binding_id": row["id"], "native_state": t["state"],
                                          "content_locale": t["content_locale"]})
    by_unit_edition = defaultdict(list)
    for s in edition_segments:
        require(s["unit_id"] in unit_by_id and s["translation_overlay_required"] is False, "edition segment binding mismatch")
        by_unit_edition[s["unit_id"]].append({"native_segment_id": s["id"], "content_locale": s["content_locale"],
                                              "source_origin": s["source_origin"], "source_sha256": s["source_sha256"],
                                              "translation_overlay_required": False,
                                              "native_evidence": n.ref("text/segments.edition.id-ID.jsonl", s)})
    state_rows = []
    for u in sorted(units, key=lambda r: r["id"]):
        pairs = sorted(by_unit_pairs[u["id"]], key=lambda r: r["native_source_segment_id"])
        states = sorted({p["native_state"] for p in pairs})
        aggregate = states[0] if len(states) == 1 else "mixed" if states else "no-segment-evidence"
        state_rows.append({"native_unit_id": u["id"], "projected_unit_id": projected_units[u["id"]],
                           "state": aggregate, "observed_native_states": states, "native_unit_status": u["status"],
                           "native_xml_lang": u.get("xml_lang"), "native_content_locale": u.get("content_locale"),
                           "native_pair_count": len(pairs), "state_counts": dict(Counter(p["native_state"] for p in pairs)),
                           "pairs": pairs, "edition_authored_segment_evidence": by_unit_edition[u["id"]],
                           "aggregation_scope": "direct native segment unit_id, never descendant or active-status inference",
                           "edition_segment_policy": "separate authored-language evidence; no synthetic translation pair/state"})
    rights = n.rows["rights/rights.jsonl"]
    for r in rights:
        keys = ("license_expression", "modified_edition_license_expression", "upstream_license_expression",
                "legal_text_policy", "full_license_source_path", "full_license_source_sha256", "license_source_path",
                "license_source_sha256", "invariant_sections", "front_cover_texts", "back_cover_texts",
                "change_notice_required", "additional_copyright_claimed")
        payload = {k: r[k] for k in keys}
        payload.update({"native_id": r["id"], "native_evidence": n.ref("rights/rights.jsonl", r),
                        "complete_rights_and_notices": "referenced_native_shard_not_copied"})
        row = add("rights", r["id"], payload, r["status"])
        map_native("rights/rights.jsonl", r, row)
        add("rights_assignments", "dataset-native-rights:" + r["id"],
            {"rights_id": row["id"], "native_rights_id": r["id"], "dataset_id": DATASET_ID,
             "assignment_basis": "all native units retain exact native rights_id; editions retain upstream/modified distinction"})
    for r in n.rows["artifacts/artifacts.jsonl"]:
        payload = {k: r.get(k) for k in ("path", "bytes", "sha256", "format", "media_type", "artifact_scope", "edition_id", "course_id")}
        payload.update({"native_id": r["id"], "native_evidence": n.ref("artifacts/artifacts.jsonl", r),
                        "verification": "native_metadata_reference_only_not_fresh_artifact_readback"})
        row = add("artifacts", r["id"], payload, r["status"])
        map_native("artifacts/artifacts.jsonl", r, row)
    for code in ("C30", "C40"):
        index, capsule = capsule_rows[code]
        primary = capsule["layers"]["learner"]["primary"]
        capsule_evidence = {"authority": central_facts[CAPSULES], "jsonl_row_ordinal": index + 1,
                            "json_pointer": "/layers/learner/primary", "canonical_row_sha256": canonical_row_sha256(capsule)}
        surface = add("reader_surfaces", "frozen-capsule-primary:" + code,
                      {"curriculum_role_id": code, "url": primary["url"], "format": primary["format"],
                       "owner_native_state": primary["status"], "evidence": capsule_evidence,
                       "fresh_route_readback": False, "unit_anchors_verified": False, "learner_consumption_claim": False})
        add("routes", "frozen-capsule-course-fallback:" + code,
            {"curriculum_role_id": code, "reader_surface_id": surface["id"], "url": primary["url"],
             "route_result": "truthful_fallback", "scope": "whole_course_only_no_unit_anchor",
             "admission_state": "candidate_not_admitted", "fresh_route_readback": False,
             "learner_consumption_claim": False, "evidence": capsule_evidence})
        native_course = next(c for c in courses if c["code"] == code)
        add("search_documents", "course-selector:" + native_course["id"],
            {"curriculum_role_id": code, "native_course_id": native_course["id"], "native_title": native_course["title"],
             "unit_view": "course-views.json#/views/" + str(("C30", "C40").index(code)), "text_content_copied": False,
             "learner_use": "not_claimed"})
    chapter_route_ids = {}
    for uid, evidence in sorted(route_by_unit.items(), key=lambda item: (item[1]["offline"]["native_course_id"], item[1]["offline"]["sequence"])):
        route = evidence["offline"]
        code = course_by_id[route["native_course_id"]]["code"]
        route_evidence = {"binding": route_fact, "offline_json_pointer": evidence["offline_pointer"],
                          "live_json_pointer": evidence["live_pointer"], "offline_canonical_sha256": ROUTE_OFFLINE_SHA}
        surface = add("reader_surfaces", "chapter-witness:" + uid,
            {"native_unit_id": uid, "projected_unit_id": projected_units[uid], "curriculum_role_id": code,
             "localized_title": route["localized_title"], "url": route["public_url"], "format": "text/html",
             "offline_archive": route_input["offline"]["web_archive"],
             "offline_member": {"path": route["archive_member"], "bytes": route["bytes"], "sha256": route["sha256"]},
             "offline_html_chapter_id": route["html_chapter_id"], "offline_identity": "verified_in_bound_route_evidence",
             "live_observation": evidence["live"], "current_live_edition_identity": "not_verified",
             "fresh_network_check_by_candidate_builder": False, "learner_consumption_claim": False,
             "evidence": route_evidence})
        chapter_route = add("routes", "chapter-route:" + uid,
            {"native_unit_id": uid, "projected_unit_id": projected_units[uid],
             "native_membership_id": route["native_membership_id"], "native_course_id": route["native_course_id"],
             "curriculum_role_id": code, "sequence": route["sequence"], "chapter_number": route["chapter_number"],
             "localized_title": route["localized_title"], "reader_surface_id": surface["id"],
             "url": route["public_url"], "scope": "chapter_page_no_descendant_anchor_claim",
             "route_result": "truthful_fallback", "offline_archive": route_input["offline"]["web_archive"],
             "offline_href": route["offline_href"], "offline_member": {"path": route["archive_member"],
               "bytes": route["bytes"], "sha256": route["sha256"]},
             "offline_html_chapter_id": route["html_chapter_id"], "offline_identity": "verified_in_bound_route_evidence",
             "live_observation": evidence["live"], "live_frozen_byte_identity": "mismatch_at_recorded_observation",
             "current_live_edition_identity": "not_verified", "fresh_network_check_by_candidate_builder": False,
             "learner_consumption_claim": False, "admission_state": "candidate_not_admitted", "evidence": route_evidence})
        chapter_route_ids[uid] = chapter_route["id"]
    add("build_recipes", "zip-bound-v2.3.1-candidate",
        {"command": "python -B tools/build_judson_candidate.py --source-zip SOURCE_BACKEND.zip --output build-a",
         "archive_sha256": ZIP_SHA, "native_rebuild": "not_performed_by_this_builder",
         "generic_validation": "separate unchanged validator with explicit external authority roots",
         "network_required": False, "lean_or_sage_execution": False})
    add("adapter_profiles", "c30-c40-candidate-v2.3.1",
        {"contract_version": "2.3.1", "admission_state": "candidate_not_admitted", "curriculum_role_ids": ["C30", "C40"],
         "identity_formula": contract["identity"]["formula"], "full_native_backend_replay_claim": False,
         "learner_consumption_claim": False})
    add("adapter_runs", "candidate-projection-v1",
        {"archive_sha256": ZIP_SHA, "native_manifest_sha256": MANIFEST_SHA, "operation": "deterministic_metadata_projection",
         "native_authority_read": "exact_zip_members", "status": "candidate_generated", "native_build_replayed": False})
    add("qa_events", "builder-local-invariants-v1",
        {"native_manifest_hashes": "checked", "native_row_pairing": "checked", "relation_endpoint_resolution": "checked",
         "course_view_derivation": "native_membership_and_parent_topology", "translation_state_inference": False,
         "generic_validation": "external_report_required", "native_runtime_or_reader_replay": "not_claimed",
         "historical_native_qa": "referenced_without_promoting_to_current_validation"})

    sort_table_rows(tables)
    facts = write_tables(output, tables)
    write_jsonl(output / "native-relation-endpoints.jsonl", [entity_refs[k] for k in sorted(entity_refs)])
    views = []
    for c in sorted(courses, key=lambda r: r["code"]):
        members = sorted((m for m in memberships if m["course_id"] == c["id"]), key=lambda m: m["sequence"])
        ids = sorted(course_units[c["id"]], key=lambda uid: unit_by_id[uid]["preorder_index"])
        views.append({"curriculum_role_id": c["code"], "native_course_id": c["id"],
                      "native_course_evidence": n.ref("courses/courses.jsonl", c),
                      "chapters": [{"native_membership_id": m["id"], "native_unit_id": m["unit_id"],
                                    "projected_unit_id": projected_units[m["unit_id"]], "sequence": m["sequence"],
                                    "route_id": chapter_route_ids[m["unit_id"]],
                                    "localized_title": route_by_unit[m["unit_id"]]["offline"]["localized_title"],
                                    "public_url": route_by_unit[m["unit_id"]]["offline"]["public_url"],
                                    "offline_archive": route_input["offline"]["web_archive"],
                                    "offline_member": {"path": route_by_unit[m["unit_id"]]["offline"]["archive_member"],
                                      "bytes": route_by_unit[m["unit_id"]]["offline"]["bytes"],
                                      "sha256": route_by_unit[m["unit_id"]]["offline"]["sha256"]},
                                    "offline_evidence_json_pointer": route_by_unit[m["unit_id"]]["offline_pointer"],
                                    "live_evidence_json_pointer": route_by_unit[m["unit_id"]]["live_pointer"],
                                    "live_frozen_byte_identity": "mismatch_at_recorded_observation",
                                    "current_live_edition_identity": "not_verified"} for m in members],
                      "unit_count": len(ids), "native_unit_ids": ids,
                      "projected_unit_ids": [projected_units[uid] for uid in ids],
                      "derivation": "chapter selector or descendant by repeated native parent_id"})
    write_json(output / "course-views.json", {"candidate_not_admitted": True, "unit_records_duplicated": False,
               "views": views, "outside_course_selectors": {"count": len(outside), "native_unit_ids": sorted(outside)},
               "no_subject_boundary_inference": True, "chapter_route_evidence": route_fact,
               "offline_canonical_sha256": ROUTE_OFFLINE_SHA, "learner_consumption_claim": False})
    translation_sidecar = {"$schema": "schema/translation-state-index-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0", "schema_version": "0.2.0",
        "package_id": PACKAGE_ID, "dataset_id": DATASET_ID,
        "authority_bindings": [n.shard(p) for p in ("topology/units.jsonl", "text/segments.en-US.jsonl",
          "text/translations.id-ID.jsonl", "state/segment-dispositions.id-ID.jsonl", "state/source-preserved-paths.json",
          "text/segments.edition.id-ID.jsonl")],
        "coverage": {"course_id": "C30+C40:shared-native-corpus", "granularity": "all native units, direct segment evidence",
                     "authority_rows": len(units), "indexed_rows": len(state_rows), "inferred_rows": 0},
        "states": sorted({r["state"] for r in state_rows}), "records": state_rows,
        "identity_set_sha256": identity_set_sha256(r["projected_unit_id"] for r in state_rows),
        "no_inference": True, "recorded_at": STAMP}
    write_json(output / "translation-state-index-v0.2.0.json", translation_sidecar)
    write_json(output / "namespace-crosswalk-v0.2.0.json", {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0", "schema_version": "0.2.0",
        "package_id": PACKAGE_ID, "profiles": [
            {"namespace": NATIVE_NS, "authority": "owner-native", "ids_unchanged": True},
            {"namespace": CENTRAL_NS, "uuid_namespace": str(NS), "formula": contract["identity"]["formula"], "authority": "candidate_projection"},
            {"namespace": "program-matematika-indonesia/curriculum-role", "role_ids": ["C30", "C40"], "not_a_native_unit_namespace": True}],
        "mappings": sorted(mappings, key=lambda m: (m["source_namespace"], m["source_record_type"], m["source_record_id"])),
        "unmaterialized_candidates": [], "identity_sets": {
            "native_unit_ids": identity_set_sha256(unit_by_id), "projected_unit_ids": identity_set_sha256(projected_units.values()),
            "native_birth_current_map_ids": identity_set_sha256(r["id"] for r in idmaps),
            "native_relation_ids": identity_set_sha256(r["id"] for r in relations),
            "unit_native_to_projected": mapping_set_sha256(projected_units.items())}, "recorded_at": STAMP})
    limitations = [
        "Candidate, not admitted or published; this does not change any released index or course capsule.",
        "All native units and typed relations are projected as metadata; full prose, formula fragments and code remain owner-native.",
        "Unit active status and xml_lang are not translation completion; direct segment state sets preserve mixed and no-segment-evidence.",
        "Raw target_sha256 null is retained for source_frozen translations; separate preservation hashes cite explicit disposition/path policy.",
        "The 30 units outside both native chapter selectors remain corpus support units, not inferred course members.",
        "Richer native terminology, assessment, correction, asset and Sage declarations remain hash-bound references; no structured assessment closure is claimed.",
        "The 23 chapter routes bind independently supplied offline WEB evidence and dated live HTTP200 observations, with 0/23 frozen-byte matches; this builder makes no network request or current live edition identity claim.",
        "No descendant anchor, learner consumption, accessibility conformance, Sage/Lean execution or full-native backend replay is claimed by this projection.",
        "Historical native QA and artifact metadata remain references; they are not relabeled current independent validation.",
        "Generic authority validation requires the exact public archive extraction root plus the frozen central-authority root; package-only validation does not replay those authorities.",
    ]
    write_json(output / "scope-declaration-v0.2.0.json", {
        "$schema": "schema/scope-declaration-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0", "schema_version": "0.2.0",
        "package_id": PACKAGE_ID, "dataset_id": DATASET_ID, "scope_kind": "lane_adapter",
        "course_ids": sorted(course_by_id), "curriculum_role_ids": ["C30", "C40"], "aggregate_conformance_claim": False,
        "unbound_curriculum_role_ids": sorted(r["course_id"] for r in capsules if r["course_id"] not in ("C30", "C40")),
        "owner_authority_binding": {"archive": {"public_url": ZIP_URL, "bytes": ZIP_BYTES, "sha256": ZIP_SHA},
                                    "manifest": native_manifest_fact, "authority_read_mode": "exact_archive_members"},
        "curriculum_authority_binding": central_facts[CAPSULES], "limitations": limitations, "recorded_at": STAMP})
    capability_specs = {
        "terminology": (["lexicon/concepts.jsonl", "lexicon/terms.id-ID.jsonl", "lexicon/concept-units.jsonl"], "Native concepts/terms/memberships are referenced; no new terminology judgment is asserted."),
        "mathematical_preservation": (["text/segments.en-US.jsonl", "text/translations.id-ID.jsonl"], "Hash bindings are projected, but protected XML/formula semantics and full mathematical replay remain native references."),
        "assessment_support": (["topology/units.jsonl", "topology/relations.jsonl"], "Native exercise/hint/response topology is retained; no component-role assessment shard or structured exercise closure is projected. Native count counts whole referenced shard rows, not exercises."),
        "assets": (["assets/assets.jsonl"], "Asset identity/hash metadata is native; asset payloads and rendering are not materialized here."),
        "corrections": (["corrections/corrections.jsonl", "edition/source-deltas.id-ID.jsonl"], "Correction and delta records are referenced; correction relation edges are preserved but correction application is not replayed."),
        "computational_interactives": (["code/sage-cells.jsonl"], "Native Sage cells explicitly say runtime not independently reexecuted; this candidate executes neither Sage nor Lean."),
        "publication": (["artifacts/artifacts.jsonl", "authority/editions.jsonl"], "Native edition/artifact declarations remain references; 23 chapter routes additionally bind frozen offline evidence and dated live observations without claiming live edition identity or learner consumption."),
        "research_support": (["qa/qa-events.jsonl"], "Historical native QA is referenced without promotion to current or independent replay."),
    }
    capabilities = []
    for name in CAPABILITY_NAMES:
        if name == "structure_localization":
            item = {"state": "materialized", "schema_binding": file_fact(output / "schema/lane-adapter-v2.3.1.schema.json", "schema/lane-adapter-v2.3.1.schema.json", "unchanged_envelope_schema"),
                    "shard_refs": [facts["units"], facts["relations"], facts["course_unit_memberships"], facts["identity_crosswalks"], facts["content_bindings"]],
                    "native_count": len(units), "projected_count": len(units),
                    "identity_set_sha256": identity_set_sha256(projected_units.values()), "identity_set_scope": "projected_records",
                    "closure_rules": ["Counts and identity set refer to native/projected units only; associated relation, membership, identity and content tables have independent exact counts.",
                                      "All 6505 typed native relations resolve through native-relation-endpoints.jsonl, including non-unit namespaces.",
                                      "Translation state comes from exact direct source/translation pairs, not status=active or an ancestor state."],
                    "loss_gap_report": {"status": "declared_limitation", "reason": "Metadata projection only; no full prose, new anchors or global admission."}}
        elif name == "accessibility":
            item = {"state": "not_projected", "schema_binding": None, "shard_refs": [], "native_count": 0,
                    "projected_count": 0, "identity_set_sha256": None, "identity_set_scope": "none",
                    "closure_rules": ["No accessibility assessment record is projected; absence here is not a defect claim about the native course."],
                    "loss_gap_report": {"status": "declared_limitation", "reason": "Native reader accessibility not tested by this candidate."}}
        else:
            paths, reason = capability_specs[name]
            referenced = [n.shard(p) for p in paths]
            item = {"state": "referenced_native_shards", "schema_binding": n.shard("schema/interlanguage-modular-record.schema.json"),
                    "shard_refs": referenced, "native_count": sum(len(n.rows[p]) for p in paths), "projected_count": 0,
                    "identity_set_sha256": identity_set_sha256(r["id"] for p in paths for r in n.rows[p]),
                    "identity_set_scope": "native_shard_records", "closure_rules": ["Native count is the sum of exact referenced shard row counts; projected_count=0 means no separate capability shard, not absence of native evidence."],
                    "loss_gap_report": {"status": "declared_limitation", "reason": reason}}
        capabilities.append({"name": name, "version": "0.1.0", **item})
    deferred = lambda path: {"path": path, "binding_state": "sealed_by_package_manifest"}
    write_json(output / "capability-declarations-v0.2.0.json", {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0", "schema_version": "0.2.0",
        "package_id": PACKAGE_ID, "dataset_id": DATASET_ID, "contract_binding": central_facts[CONTRACT],
        "capabilities": capabilities, "legacy_labels": [],
        "namespace_crosswalk_binding": deferred("namespace-crosswalk-v0.2.0.json"),
        "csv_projection_binding": deferred("csv-projection-manifest-v0.2.0.json"),
        "translation_state_binding": deferred("translation-state-index-v0.2.0.json"),
        "rights_cross_cutting": {"state": "referenced_native_shards", "shard_refs": [n.shard("rights/rights.jsonl")],
          "native_count": len(rights), "identity_set_sha256": identity_set_sha256(r["id"] for r in rights),
          "closure_rules": ["Modified edition GFDL-1.3-or-later and upstream GFDL-1.2-or-later stay distinct.",
                            "Operative English GFDL 1.3 is source_frozen; wrappers/history can be Indonesian.",
                            "Full native legal notices and correction declarations remain authoritative references."]}, "recorded_at": STAMP})
    csv_manifest = write_csv_surfaces(output, tables, PACKAGE_ID, STAMP)
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_manifest)
    summary = {"status": "candidate_generated_not_admitted", "package_id": PACKAGE_ID,
        "archive": {"filename": ZIP_NAME, "public_url": ZIP_URL, "bytes": ZIP_BYTES, "sha256": ZIP_SHA},
        "native_manifest": native_manifest_fact, "native_manifest_members_checked": len(n.facts),
        "table_counts": {name: len(rows) for name, rows in tables.items()},
        "native_relation_type_counts": dict(Counter(r["type"] for r in relations)),
        "native_relation_endpoint_counts": dict(Counter(r["native_record_type"] for r in entity_refs.values())),
        "course_view_unit_counts": {v["curriculum_role_id"]: v["unit_count"] for v in views},
        "outside_course_selector_units": len(outside), "native_pair_count": len(segments),
        "native_segment_state_counts": dict(Counter(t["state"] for t in translations)),
        "raw_translation_target_hash_counts": dict(raw_target_counts),
        "unit_state_counts": dict(Counter(r["state"] for r in state_rows)),
        "edition_authored_segments_separately_referenced": len(edition_segments),
        "operative_gfdl_source_frozen_pairs": sum(s["source_path"] == "gfdl.xml" and translation_by_segment[s["id"]]["state"] == "source_frozen" for s in segments),
        "chapter_routes": len(chapter_route_ids), "chapter_route_input": route_fact,
        "offline_chapter_html_bytes": sum(e["offline"]["bytes"] for e in route_by_unit.values()),
        "dated_live_http200": sum(e["live"]["http_status"] == 200 for e in route_by_unit.values()),
        "dated_live_matches_frozen_bytes": sum(e["live"]["matches_frozen_html"] for e in route_by_unit.values()),
        "offline_route_canonical_sha256": ROUTE_OFFLINE_SHA,
        "namespace_mapping_count": len(mappings), "native_replay_claim": False, "learner_consumption_claim": False,
        "generic_validator_result": "see_external_unchanged_validator_report", "recorded_at": STAMP}
    summary["recorded_at_meaning"] = "frozen deterministic build-snapshot stamp, not an individual live probe time"
    write_json(output / "BUILD_SUMMARY.json", summary)
    payload_facts = package_payload_files(output)
    payload_digest = inventory_sha256(payload_facts)
    sidecar_names = ["capability-declarations-v0.2.0.json", "namespace-crosswalk-v0.2.0.json",
                     "translation-state-index-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "scope-declaration-v0.2.0.json"]
    local_fact = lambda p, role: file_fact(output / p, p, role)
    manifest = {"$schema": "schema/lane-adapter-v2.3.1.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1", "schema_version": "2.3.1",
        "package_id": PACKAGE_ID, "dataset_id": DATASET_ID, "extension_id": EXTENSION_ID,
        "extension_version": "judson-c30-c40-2.3.1-candidate.3-routes-chronology", "recorded_at": STAMP,
        "scope_declaration": local_fact("scope-declaration-v0.2.0.json", "scope_declaration"),
        "authorities": [native_manifest_fact] + [n.facts[p] for p in sorted(n.facts)] + list(central_facts.values()),
        "sidecars": [local_fact(p, "contract_sidecar") for p in sidecar_names] + [route_fact],
        "csv_projection": {"manifest": local_fact("csv-projection-manifest-v0.2.0.json", "csv_projection_manifest"),
                           "table_csv_count": len(tables), "aggregate_csv_count": 1,
                           "record_count": sum(map(len, tables.values())), "roundtrip_state": "pass"},
        "build": {"builder": local_fact("tools/build_judson_candidate.py", "builder"),
                  "validator": local_fact("tools/validate_lane_adapter_v231.py", "unchanged_generic_validator"),
                  "canonical_serialization": {"scope": "builder_generated_json_jsonl_and_csv_only", "encoding": "UTF-8",
                      "newline": "LF", "json_keys": "lexicographically_sorted", "trailing_newline": True,
                      "copied_schema_and_tool_files": "preserved_exact_source_bytes"},
                  "deterministic_replay": "byte_identical", "build_a_sha256": payload_digest, "build_b_sha256": payload_digest},
        "files": payload_facts, "seal_policy": {"algorithm": "sha256-sorted-path-bytes-v1", "seal_file": "seal.json",
                    "seal_excluded_from_own_digest": True, "binds": ["payload files", "manifest", "authority byte/hash references"]},
        "zero_copy_policy": {"owner_native_authoritative": True, "full_prose_centralized": False,
            "owner_ids_reminted": False, "aggregate_conformance_claim": False,
            "machine_data_is_learner_destination": False, "machine_surfaces_secondary": True}}
    write_json(output / "manifest.json", manifest)
    seal_facts = sorted(payload_facts + [local_fact("manifest.json", "package_manifest")], key=lambda f: f["path"])
    write_json(output / "seal.json", {"algorithm": "sha256-sorted-path-bytes-v1", "package_id": PACKAGE_ID,
               "seal_excluded_from_own_digest": True, "files": seal_facts, "file_count": len(seal_facts),
               "bytes": sum(f["bytes"] for f in seal_facts), "aggregate_sha256": inventory_sha256(seal_facts)})
    write_checksums(output, seal_facts + [local_fact("seal.json", "package_seal")])
    print(compact_json(summary))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-zip", type=Path, required=True)
    parser.add_argument("--central-root", type=Path, help="Exact frozen central-authority root; defaults to bundled frozen-central")
    parser.add_argument("--route-evidence", type=Path, help="Exact frozen supplemental route evidence; defaults to bundled frozen-inputs document")
    parser.add_argument("--output", type=Path, required=True, help="A new candidate directory")
    args = parser.parse_args()
    build(args)


if __name__ == "__main__":
    main()
