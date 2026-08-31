"""Admit the exact manager Judson candidate without modifying its native data."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "backend/course-capsule-v1/adapters/judson-v231"
ARCHIVE = ROOT / "backend/course-capsule-v1/builds/program-matematika-indonesia-judson-c30-c40-v2.3.1.zip"
HANDOFF_SHA = "03fad8f0fba97de85e133908ae5129f2cfc18ffb5ae39145a8c16e191da2721e"
TREE_SHA = "4a9deaab4d97455917453ea1af2a357763d9222ba25b4571e2a9444e5bd226d0"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fact(data):
    return {"bytes": len(data), "sha256": digest(data)}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def safe_relative(name):
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in name,
            "unsafe package member")
    return path


def tree(root):
    entries = {}
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "symlink in sealed candidate")
        if path.is_file():
            entries[path.relative_to(root).as_posix()] = path.read_bytes()
    return entries


def tree_hash(entries):
    rows = "".join(f"{name}\0{len(data)}\0{digest(data)}\n"
                   for name, data in sorted(entries.items()))
    return digest(rows.encode("utf-8"))


def zip_bytes(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            safe_relative(name)
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    result = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(result)) as archive:
        require(archive.testzip() is None, "adapter archive CRC failed")
        require(archive.namelist() == sorted(entries), "adapter archive inventory drift")
        for name, data in entries.items():
            require(archive.read(name) == data, f"adapter archive bytes differ: {name}")
    return result


def preserve(path, data, *, allow_update=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() == data:
            return
        require(allow_update, f"existing admission differs: {path.name}")
        path.write_bytes(data)
    else:
        path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manager-root", type=Path, required=True)
    args = parser.parse_args()
    source = args.manager_root.resolve(strict=True)
    handoff_bytes = (source / "MANAGER_INTEGRATION_HANDOFF_20260831.json").read_bytes()
    require(fact(handoff_bytes) == {"bytes": 9077, "sha256": HANDOFF_SHA}, "manager handoff identity drift")
    handoff = json.loads(handoff_bytes)
    require(len(handoff["files"]) == 21, "handoff inventory drift")
    verified_handoff_files = {}
    for entry in handoff["files"]:
        data = (source / safe_relative(entry["path"])).read_bytes()
        require(fact(data) == {key: entry[key] for key in ("bytes", "sha256")},
                f"manager evidence drift: {entry['path']}")
        verified_handoff_files[entry["path"]] = data
    first = tree(source / "build-a-routes2")
    second = tree(source / "build-b-routes2")
    require(first == second, "independent candidate trees differ")
    require(len(first) == 65 and sum(map(len, first.values())) == 111681966, "candidate boundary drift")
    require(tree_hash(first) == TREE_SHA, "candidate tree identity drift")
    manifest = json.loads(first["manifest.json"])
    require(len(manifest["files"]) == 62, "candidate manifest inventory drift")
    for entry in manifest["files"]:
        name = safe_relative(entry["path"]).as_posix()
        require(name in first, f"manifest-bound file is absent: {name}")
        require(fact(first[name]) == {key: entry[key] for key in ("bytes", "sha256")},
                f"manifest-bound identity differs: {name}")
    # The publishable archive is the valid manifest-rooted 65-file adapter only.
    # Internal coordination evidence is retained locally but never embedded in
    # the public archive or declared as a package input.
    entries = dict(first)
    # Original candidate status remains historical. Admission is a separate overlay.
    archive_data = zip_bytes(entries)
    require(archive_data == zip_bytes(entries), "adapter ZIP replay differs")
    # Materialize the complete 65-file replay tree. A loose manifest that names
    # files present only inside the preservation ZIP is not a valid admitted
    # adapter checkout and must never pass the central build.
    copied = dict(first)
    copied["MANAGER_INTEGRATION_HANDOFF_20260831.json"] = handoff_bytes
    for entry in handoff["files"]:
        if not entry["path"].startswith("build-a-routes2/"):
            copied[f"evidence/{entry['path']}"] = verified_handoff_files[entry["path"]]
    for name, data in copied.items():
        preserve(DEST / name, data)
    preserve(ARCHIVE, archive_data, allow_update=True)
    receipt = {
        "schema_id": "interlanguage/judson-course-capsule-admission/v1",
        "recorded_at": "2026-08-31",
        "state": "locally_admitted_public_release_pending",
        "courses": ["C30", "C40"],
        "manager_handoff": fact(handoff_bytes),
        "package_tree_sha256": TREE_SHA,
        "package_files": 65,
        "package_bytes": 111681966,
        "independent_trees_identical": True,
        "manifest_bound_files_verified": len(manifest["files"]),
        "archive": {"path": ARCHIVE.relative_to(ROOT).as_posix(), **fact(archive_data)},
        "archive_members": {name: fact(data) for name, data in sorted(entries.items())},
        "inputs": {name: fact(data) for name, data in sorted(first.items())},
        "public_package_excludes_internal_coordination_evidence": True,
        "preservation": "Unmodified candidate plus separate admission; native source and WEB archives remain externally referenced.",
        "limits": ["Live chapter bytes differ from the frozen WEB edition at the recorded observation.",
                   "No descendant anchors, assessment engine or full offline dependency independence are claimed.",
                   "One graph serves two course selectors; no unit or prose duplication for the two views."],
    }
    receipt_data = (json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    preserve(DEST / "ADMISSION.json", receipt_data, allow_update=True)
    expected_destination = set(copied) | {"ADMISSION.json"}
    require(set(tree(DEST)) == expected_destination,
            "admitted destination contains missing or unbound files")
    print(json.dumps({"state": receipt["state"], "archive": receipt["archive"],
                      "admission": fact(receipt_data), "materialized_files": len(copied),
                      "manifest_bound_files_verified": len(manifest["files"]),
                      "two_build_byte_identity": True}, indent=2))


if __name__ == "__main__":
    main()
