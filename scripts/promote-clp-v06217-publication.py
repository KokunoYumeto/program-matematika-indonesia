"""Promote only the live CLP overlay after exact public readback; never edit releases."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "backend/course-capsule-v1/authority/clp-family-v231"
DURABLE = ROOT.parent / "program-matematika-indonesia/backend/course-capsule-v1/validation"
PACKAGE = "urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26"
ROLES = {"B20", "B30", "B50", "B60"}
SNAPSHOT = "urn:interlanguage:program-matematika-indonesia:v23-adapters:v0.62.17-postpublication:2026-09-04"
GH_URL = "https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.17"
ZIP_NAME = "CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip"
ZIP_SHA = "f2e2714c5f1349092e8cb574d6495e604086c9df3bc4bdf5bbe5974b5f61360d"
RECEIPTS = {
    "GITHUB_PUBLICATION_RECEIPT_v0.62.17.json": (23105, "1a8d3733c1bda0094c9f30ab94cacf2bd67de213038c4a46f2c2f933b74e1f41"),
    "ZENODO_PUBLICATION_RECEIPT_v0.62.17.json": (35615, "b439eef9dcd23b6c39dcf902f04de7e22f30ad1de3189c6c8c50fefe3ec52738"),
}


def identity(data: bytes) -> dict:
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--receipt", default="backend/course-capsule-v1/validation/CLP_POSTPUBLICATION_PROMOTION_20260904.json")
    args = parser.parse_args()
    receipt_bytes = {}
    receipts = {}
    for name, expected in RECEIPTS.items():
        raw = (DURABLE / name).read_bytes()
        fact = identity(raw)
        assert (fact["bytes"], fact["sha256"]) == expected, f"receipt identity differs: {name}"
        value = json.loads(raw)
        assert value["status"] == "pass" and value["version"] == "0.62.17"
        assert value["credentials_recorded"] is False
        receipt_bytes[name] = raw
        receipts[name.split("_")[0]] = value
    gh, zen = receipts["GITHUB"], receipts["ZENODO"]
    assert gh["public"] and gh["asset_count"] == 121 and gh["release_url"] == GH_URL
    assert zen["access"] == "open" and zen["file_count"] == 100
    assert zen["record_id"] == 22303203 and zen["concept_id"] == 22059707
    assert zen["predecessor"]["inventory_unchanged"] and zen["predecessor"]["record_id"] == 22231858
    public_zip = [r for r in gh["anonymous_readback"] if r["name"] == ZIP_NAME]
    assert len(public_zip) == 1 and public_zip[0]["bytes"] == 545418367 and public_zip[0]["sha256"] == ZIP_SHA
    assert zen["clp_reader_route_readback"]["files"] == 7 and zen["clp_reader_route_readback"]["pages"] == 4077

    index_path = AUTH / "v23-adapter-index-v2.json"
    index = json.loads(index_path.read_bytes())
    before = copy.deepcopy(index)
    packages = [p for p in index["packages"] if p["package_id"] == PACKAGE]
    assert len(packages) == 1
    clp = packages[0]
    assert clp["admission_state"] in {"admitted_pending_release", "published"}
    assert clp["archive"]["bytes"] == 545418367 and clp["archive"]["sha256"] == ZIP_SHA
    assert {r["role_id"] for r in index["adapters"] if r["adapter_package_id"] == PACKAGE} == ROLES
    clp.update(admission_state="published", release_url=GH_URL,
               public_asset_url=GH_URL.replace("/tag/", "/download/") + "/" + ZIP_NAME,
               public_replay_status="published_public_asset_readback_verified")
    clp.pop("planned_release", None)
    clp["known_limitations"] = [
        "Paket adapter pusat sudah dibaca balik publik pada v0.62.17; PDF tidak diklaim mengonsumsi adapter."
        if text.startswith("Paket adapter pusat menunggu") else text
        for text in clp["known_limitations"]
    ]
    index["snapshot"].update(snapshot_id=SNAPSHOT, as_of="2026-09-04T00:00:00Z",
                             central_release_record_doi=zen["doi"],
                             public_replay_state="postpublication_release_assets_readback_complete")
    published = {p["package_id"] for p in index["packages"] if p["admission_state"] == "published"}
    index["summary"].update(
        published_role_bindings=sum(r["adapter_package_id"] in published for r in index["adapters"]),
        pending_role_bindings=sum(r["adapter_package_id"] not in published for r in index["adapters"]),
        published_adapter_packages=len(published), pending_adapter_packages=len(index["packages"])-len(published),
        families_without_public_replay_complete_adapter=33-len({p["native_family_id"] for p in index["packages"] if p["package_id"] in published}),
    )
    assert index["summary"]["published_role_bindings"] == 13 and index["summary"]["pending_role_bindings"] == 0
    assert [p for p in index["packages"] if p["package_id"] != PACKAGE] == [p for p in before["packages"] if p["package_id"] != PACKAGE]
    assert index["adapters"] == before["adapters"], "native bindings changed"
    schema = json.loads((ROOT / "schemas/course-capsule-v1/v2/v23-adapter-index-v2.schema.json").read_bytes())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(index)
    outputs = {index_path: canonical(index)}

    sidecar_path = AUTH / "learner-reader-actions-v1.json"
    sidecar = json.loads(sidecar_path.read_bytes())
    original_actions = copy.deepcopy(sidecar["actions"])
    assert len(original_actions) == 7
    assert sum(row["pages"] for row in original_actions) == 4077
    sidecar["snapshot_id"] = SNAPSHOT
    assert sidecar["actions"] == original_actions, "native reader actions changed"
    sidecar_schema = json.loads((ROOT / "schemas/v1/learner-reader-actions-v1.schema.json").read_bytes())
    Draft202012Validator(sidecar_schema, format_checker=FormatChecker()).validate(sidecar)
    outputs[sidecar_path] = canonical(sidecar)

    pattern_path = AUTH / "modular-backend-pattern-index-v2.1.json"
    pattern = json.loads(pattern_path.read_bytes())
    pattern["snapshot"] = copy.deepcopy(index["snapshot"])
    for key in tuple(pattern["adapter_snapshot"]):
        if key in index["summary"]:
            pattern["adapter_snapshot"][key] = index["summary"][key]
    pattern["adapter_snapshot"]["adapter_index"].update(identity(outputs[index_path]))
    family = next(f for f in pattern["families"] if f["native_family_id"] == "family-06-clp")
    for binding in family["adapter_bindings"]:
        binding.update(admission_state="published", public_replay_status="published_public_asset_readback_verified")
    family["reversible_exchange_status"] = "Paket common-v2.3.1 publik pada v0.62.17; seluruh aset dibaca balik anonim dengan byte dan SHA-256 identik."
    family["limitations"] = [s for s in family["limitations"] if not s.startswith("Baca-balik publik paket adapter successor belum")]
    pattern_schema = json.loads((ROOT / "schemas/course-capsule-v1/v2.1/modular-backend-pattern-index-v2.1.schema.json").read_bytes())
    Draft202012Validator(pattern_schema, format_checker=FormatChecker()).validate(pattern)
    outputs[pattern_path] = canonical(pattern)
    for name in ("feature-adoption-provenance-v1.json", "comparison-evidence-manifest-v1.json"):
        path = AUTH / name
        value = json.loads(path.read_bytes())
        value["snapshot_id"] = SNAPSHOT
        for row in value.get("evidence", []):
            target = ROOT / row.get("path", "")
            if target in outputs:
                row.update(identity(outputs[target]))
        outputs[path] = canonical(value)
    for name, raw in receipt_bytes.items():
        outputs[ROOT / name] = raw
    rows = []
    for path, data in outputs.items():
        assert path.resolve().is_relative_to(ROOT) and not path.is_symlink()
        assert "releases" not in path.relative_to(ROOT).parts
        rows.append({"path": path.relative_to(ROOT).as_posix(), "before": identity(path.read_bytes()) if path.exists() else None, "after": identity(data)})
    if args.write:
        for path, data in outputs.items():
            path.write_bytes(data)
            assert path.read_bytes() == data
    report = {"schema": "clp-postpublication-promotion/v1", "status": "pass", "mode": "write" if args.write else "dry_run", "snapshot_id": SNAPSHOT,
              "github_release": GH_URL, "zenodo_doi": zen["doi"], "published_bindings": 13, "published_packages": 9, "pending_bindings": 0,
              "native_bindings_unchanged": True, "immutable_release_assets_unchanged": True, "files": rows}
    if args.write:
        receipt_path = (ROOT / args.receipt).resolve()
        assert receipt_path.is_relative_to(ROOT / "backend/course-capsule-v1/validation")
        receipt_path.write_bytes(canonical(report))
    print(json.dumps({k:v for k,v in report.items() if k != "files"}, separators=(",", ":")))


if __name__ == "__main__":
    main()
