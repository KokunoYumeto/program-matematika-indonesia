from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "backend/course-capsule-v1/authority"
SCHEMA_ROOT = ROOT / "schemas/course-capsule-v1/v2"
PUBLIC_DATA = ROOT / "docs/data"
PUBLIC_SCHEMA = ROOT / "docs/schema/v2"
VALIDATION = ROOT / "backend/course-capsule-v1/validation"
SNAPSHOT_ID = "urn:interlanguage:program-matematika-indonesia:v23-adapters:v0.62.14-prepublication:2026-08-31"

DATA_FILES = {
    "adapter": "v23-adapter-index-v2.json",
    "pattern": "modular-backend-pattern-index-v2.json",
    "feature": "feature-adoption-provenance-v1.json",
    "comparison": "comparison-evidence-manifest-v1.json",
}
SCHEMA_FILES = {
    "adapter": "v23-adapter-index-v2.schema.json",
    "pattern": "modular-backend-pattern-index-v2.schema.json",
    "feature": "feature-adoption-provenance-v1.schema.json",
    "comparison": "comparison-evidence-manifest-v1.schema.json",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identify(path: Path, relative_to: Path = ROOT) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(relative_to).as_posix(),
        "bytes": len(data),
        "sha256": sha256(data),
    }


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


schemas = {name: load_json(SCHEMA_ROOT / filename) for name, filename in SCHEMA_FILES.items()}
instances = {name: load_json(AUTHORITY / filename) for name, filename in DATA_FILES.items()}

for schema in schemas.values():
    Draft202012Validator.check_schema(schema)
registry = Registry().with_resources(
    (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values()
)
for name, instance in instances.items():
    errors = sorted(
        Draft202012Validator(
            schemas[name], registry=registry, format_checker=FormatChecker()
        ).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    assert not errors, "\n".join(
        f"{name} /{'/'.join(map(str, error.absolute_path))}: {error.message}"
        for error in errors
    )

for name, filename in DATA_FILES.items():
    canonical = AUTHORITY / filename
    projection = PUBLIC_DATA / filename
    assert canonical.read_bytes() == projection.read_bytes(), f"{filename}: public projection drift"
    assert canonical.read_bytes() == canonical_bytes(instances[name]), f"{filename}: noncanonical JSON"
for name, filename in SCHEMA_FILES.items():
    canonical = SCHEMA_ROOT / filename
    projection = PUBLIC_SCHEMA / filename
    assert canonical.read_bytes() == projection.read_bytes(), f"{filename}: public schema drift"

release = ROOT / "releases/v0.62.13"
v1_pairs = [
    (release / "v23-adapter-index-v1.json", ROOT / "backend/authority/v23-adapter-index-v1.json"),
    (release / "v23-adapter-index-v1.json", PUBLIC_DATA / "v23-adapter-index-v1.json"),
    (release / "v23-adapter-index-v1.schema.json", ROOT / "schemas/v1/v23-adapter-index-v1.schema.json"),
    (release / "v23-adapter-index-v1.schema.json", ROOT / "docs/schema/v1/v23-adapter-index-v1.schema.json"),
    (release / "modular-backend-pattern-index-v1.json", ROOT / "backend/authority/modular-backend-pattern-index-v1.json"),
    (release / "modular-backend-pattern-index-v1.json", PUBLIC_DATA / "modular-backend-pattern-index-v1.json"),
]
for predecessor, projection in v1_pairs:
    assert predecessor.read_bytes() == projection.read_bytes(), f"immutable v1 drift: {projection}"

adapter = instances["adapter"]
assert adapter["snapshot"]["snapshot_id"] == SNAPSHOT_ID
assert adapter["snapshot"]["snapshot_kind"] == "live_successor_overlay"
assert adapter["snapshot"]["mutable_overlay"] is True
assert adapter["snapshot"]["central_release_record_doi"] is None
packages = adapter["packages"]
bindings = adapter["adapters"]
assert len(packages) == 8
assert len(bindings) == 9
assert len({row["package_id"] for row in packages}) == 8
assert len({row["role_id"] for row in bindings}) == 9
assert [row["role_id"] for row in bindings] == ["A00", "B10", "C30", "C40", "C80", "C130", "D20", "D60", "D110"]
package_by_id = {row["package_id"]: row for row in packages}
for binding in bindings:
    package = package_by_id[binding["adapter_package_id"]]
    assert binding["native_family_id"] == package["native_family_id"]
for package in packages:
    assert any(row["adapter_package_id"] == package["package_id"] for row in bindings)
    if package["admission_state"] == "published":
        assert package["public_replay_status"] == "published_public_asset_readback_verified"
        assert package["release_url"] and package["public_asset_url"]
        assert "planned_release" not in package
    else:
        assert package["public_replay_status"] == "pending_release_local_seal_verified"
        assert package["release_url"] is None and package["public_asset_url"] is None
        assert package["planned_release"]["state"] == "planned_not_public"

published_packages = {row["package_id"] for row in packages if row["admission_state"] == "published"}
family_ids = {row["native_family_id"] for row in packages}
published_family_ids = {row["native_family_id"] for row in packages if row["admission_state"] == "published"}
recomputed_summary = {
    "curriculum_roles": 40,
    "role_bindings": len(bindings),
    "published_role_bindings": sum(row["adapter_package_id"] in published_packages for row in bindings),
    "pending_role_bindings": sum(row["adapter_package_id"] not in published_packages for row in bindings),
    "distinct_adapter_packages": len(packages),
    "published_adapter_packages": len(published_packages),
    "pending_adapter_packages": len(packages) - len(published_packages),
    "represented_native_families": len(family_ids),
    "unbound_roles": 40 - len(bindings),
    "families_without_local_adapter": 33 - len(family_ids),
    "families_without_public_replay_complete_adapter": 33 - len(published_family_ids),
    "package_deduplicated_canonical_records": sum(row["canonical_records"] for row in packages),
}
assert adapter["summary"] == recomputed_summary
assert recomputed_summary == {
    "curriculum_roles": 40,
    "role_bindings": 9,
    "published_role_bindings": 5,
    "pending_role_bindings": 4,
    "distinct_adapter_packages": 8,
    "published_adapter_packages": 5,
    "pending_adapter_packages": 3,
    "represented_native_families": 8,
    "unbound_roles": 31,
    "families_without_local_adapter": 25,
    "families_without_public_replay_complete_adapter": 28,
    "package_deduplicated_canonical_records": 285829,
}

judson_package_ids = {row["adapter_package_id"] for row in bindings if row["role_id"] in {"C30", "C40"}}
assert judson_package_ids == {"urn:uuid:f2d0324c-322c-5f7b-a9e6-8beccf50656c"}
judson = package_by_id[next(iter(judson_package_ids))]
assert judson["canonical_records"] == 17745
assert judson["unit_records"] == 3323
assert judson["relation_records"] == 6505
assert judson["source_translation_pairs"] == 4466
assert {row["role_id"]: row["course_specific_route_count"] for row in bindings if row["role_id"] in {"C30", "C40"}} == {"C30": 15, "C40": 8}

openlogic = package_by_id["urn:uuid:601e07e9-660e-5f8e-97bb-228be6c69566"]
assert openlogic["canonical_records"] == 5807
assert openlogic["unit_records"] == 722
assert openlogic["ordered_import_relations"] == 725
assert openlogic["namespace_mappings"] == 1445
assert openlogic["rights_assignments"] == 728
assert openlogic["reader_reachable_units"] == 642
assert openlogic["retained_non_reader_units"] == 80
assert openlogic["reader_pages"] == 1116
assert openlogic["native_html_claimed"] is False
assert openlogic["unit_or_page_anchors_claimed"] is False

c130 = package_by_id["urn:uuid:a84539b5-455b-5baf-89a4-f4c0336e33ab"]
assert c130["native_family_id"] == "family-20-operations-research"
assert c130["dataset_id"] == "urn:uuid:2e16c60d-7ee3-52f4-9c05-2c4dea0b07ca"
assert c130["extension_id"] == "urn:uuid:d46eb7f0-cab9-5646-89cb-e4e82394c344"
assert c130["adapter_version"] == "0.1.0"
assert c130["contract_version"] == "2.3.1"
assert c130["admission_state"] == "admitted_pending_release"
assert c130["public_replay_status"] == "pending_release_local_seal_verified"
assert c130["canonical_records"] == 51704
assert c130["unit_records"] == 1993
assert c130["relation_records"] == 9545
assert c130["rights_assignments"] == 7634
assert c130["namespace_mappings"] == 17273
assert c130["public_artifacts"] == 83
assert c130["reader_pages"] == 666
assert c130["native_html_claimed"] is False
assert c130["unit_or_page_anchors_claimed"] is False
assert c130["jsonl_csv_table_pairs"] == 19
assert c130["manifest"]["path"] == "backend/course-capsule-v1/adapters/c130-v231/manifest.json"
assert c130["manifest"]["bytes"] == 22488
assert c130["manifest"]["sha256"] == "cad2922d9bd1facb33cc9d54a9836bb168fe0b8d996d9d4ef2e5d8c26053f239"
assert c130["archive"]["bytes"] == 21213937
assert c130["archive"]["sha256"] == "eb195d1aa555e9d5e639c1e35a08b6f4425be24cc93b7f1f633161e9cacee865"
c130_binding = next(row for row in bindings if row["role_id"] == "C130")
assert c130_binding["adapter_package_id"] == c130["package_id"]
assert c130_binding["native_family_id"] == "family-20-operations-research"
assert c130_binding["learner_runtime_relationship"] == "course_link_only_no_adapter_consumption_claim"

pattern = instances["pattern"]
assert pattern["snapshot"] == adapter["snapshot"]
assert len(pattern["families"]) == 33
assert [row["ordinal"] for row in pattern["families"]] == list(range(1, 34))
pattern_roles = [role for family in pattern["families"] for role in family["roles"]]
assert len(pattern_roles) == 40 and len(set(pattern_roles)) == 40
assert pattern["adapter_snapshot"]["adapter_index"] == identify(AUTHORITY / DATA_FILES["adapter"])
for family in pattern["families"]:
    expected_bindings = [row for row in bindings if row["role_id"] in family["roles"]]
    actual = family["adapter_bindings"]
    assert [row["role_id"] for row in actual] == [row["role_id"] for row in expected_bindings]
    for row in actual:
        package = package_by_id[row["adapter_package_id"]]
        assert row["admission_state"] == package["admission_state"]
        assert row["public_replay_status"] == package["public_replay_status"]

feature = instances["feature"]
assert feature["snapshot_id"] == SNAPSHOT_ID
assert [row["layer_id"] for row in feature["layers"]] == [
    "curriculum", "translation", "production", "learner", "educator", "federation", "interoperability"
]
evidence_by_id = {row["evidence_id"]: row for row in feature["evidence"]}
assert len(evidence_by_id) == len(feature["evidence"])
assert evidence_by_id["terminology_policy"]["kind"] == "design_policy"
assert evidence_by_id["terminology_policy"]["path"] == (
    "backend/course-capsule-v1/authority/terminology-policy-v1/"
    "canonical-register-policy.json"
)
for layer in feature["layers"]:
    for feature_row in layer["features"]:
        assert set(feature_row["evidence_ids"]) <= set(evidence_by_id)
for row in feature["evidence"]:
    evidence_path = ROOT / row["path"]
    assert evidence_path.is_file(), f"missing feature evidence: {row['path']}"
    assert identify(evidence_path) == {"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]}

comparison = instances["comparison"]
assert comparison["snapshot_id"] == SNAPSHOT_ID
assert [row["sequence"] for row in comparison["methodology"]["stages"]] == [1, 2, 3, 4]
assert {row["evidence_id"] for row in comparison["evidence"]} >= {"terminology_policy"}
assert comparison["sanitization"] == {
    "credentials_excluded": True,
    "absolute_local_paths_excluded": True,
    "coordination_transcripts_excluded": True,
    "public_safe_repository_relative_paths_only": True,
}
for row in comparison["evidence"]:
    assert not re.match(r"^(?:[A-Za-z]:|/)", row["path"])
    evidence_path = ROOT / row["path"]
    assert evidence_path.is_file(), f"missing comparison evidence: {row['path']}"
    actual = identify(evidence_path)
    assert actual["bytes"] == row["bytes"] and actual["sha256"] == row["sha256"]

public_outputs = [PUBLIC_DATA / filename for filename in DATA_FILES.values()] + [PUBLIC_SCHEMA / filename for filename in SCHEMA_FILES.values()]
for path in public_outputs:
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"[A-Za-z]:\\", text)
    assert not re.search(r"ghp_[A-Za-z0-9]+|access_token|api[_-]?key", text, flags=re.IGNORECASE)

VALIDATION.mkdir(parents=True, exist_ok=True)
receipt = {
    "schema_id": "interlanguage/program-matematika-indonesia-modular-backend-snapshot-validation/v1",
    "recorded_at": "2026-08-31",
    "snapshot_id": SNAPSHOT_ID,
    "status": "pass",
    "summary": recomputed_summary,
    "checks": [
        "four Draft 2020-12 schemas are structurally valid",
        "four authority instances validate without errors",
        "authority and public data/schema bytes are identical",
        "immutable v1 authority/public bytes equal v0.62.13",
        "nine unique role bindings resolve to eight unique packages",
        "Judson is one shared package for C30/C40 and is counted once",
        "published and pending package states obey URL/readback coupling",
        "33 families cover 40 roles exactly once",
        "seven feature-adoption layers resolve all evidence references",
        "comparison evidence paths and hashes replay",
        "public artifacts contain no absolute local paths or credential-like strings",
    ],
    "validator": identify(Path(__file__)),
    "validated_files": [
        *(identify(AUTHORITY / filename) for filename in DATA_FILES.values()),
        *(identify(SCHEMA_ROOT / filename) for filename in SCHEMA_FILES.values()),
    ],
}
receipt_bytes = canonical_bytes(receipt)
receipt_path = VALIDATION / "MODULAR_BACKEND_SNAPSHOT_V2_RECEIPT.json"
public_receipt_path = PUBLIC_DATA / "modular-backend-snapshot-v2-validation-receipt.json"
receipt_path.write_bytes(receipt_bytes)
public_receipt_path.write_bytes(receipt_bytes)
assert receipt_path.read_bytes() == public_receipt_path.read_bytes()

print(json.dumps({
    "status": "pass",
    "snapshot_id": SNAPSHOT_ID,
    "summary": recomputed_summary,
    "receipt": identify(receipt_path),
}, ensure_ascii=False, indent=2))
