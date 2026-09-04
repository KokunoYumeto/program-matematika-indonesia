"""Build and independently replay the deterministic C90 topology packet."""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = Path("backend/course-capsule-v1/adapters/topology-capability-v1")
TARGET = Path("releases/topology-learning-capability-v1")
ARCHIVE_NAME = "TOPOLOGY_NATIVE_LEARNING_CAPABILITY_V1.zip"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: str, data: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(data), "sha256": sha(data)}


manifest_bytes = (ROOT / BASE / "manifest.json").read_bytes()
manifest = json.loads(manifest_bytes)
validation_bytes = (ROOT / BASE / "validation.json").read_bytes()
validation = json.loads(validation_bytes)
assert manifest["contract"] == validation["contract"] == "topology-learning-capability/1"
assert validation["state"] == "pass"
assert validation["manifest_sha256"] == sha(manifest_bytes)

paths = {row["path"] for row in manifest["inputs"] + manifest["outputs"]}
paths.update(
    (BASE / name).as_posix()
    for name in ("manifest.json", "validation.json", "README.md")
)
paths.update(
    {
        "scripts/package-topology-capability-v1.py",
        "docs/backend/topology/validation.json",
        "docs/backend/index.html",
        "docs/id/index.html",
    }
)
files = {path: (ROOT / path).read_bytes() for path in sorted(paths)}

for row in manifest["inputs"] + manifest["outputs"]:
    assert identity(row["path"], files[row["path"]]) == row

files["START_HERE.md"] = b"""# C90 Topology learner and educator capability packet

Open docs/backend/topology/C90.html for the course route. Use latihan.html for
the 1,227 staged support and mastery records, pengajar.html to assemble an
educator activity packet, istilah.html for terminology, and catatan.html for
corrections, rights, accessibility, and release boundaries.

Rebuild with Node 22 and Python plus jsonschema from this archive root:

    python -B scripts/build-topology-capability-v1.py
    python -B scripts/validate-topology-capability-v1.py

The frozen native metadata, all 4,908 staged destination byte identities,
schema, controls, and negative fixtures are included. The original reader
remains externally linked and is not duplicated here. See the adapter README
for scope and preserved limitations. This packet does not claim completion of
the 40-role backend or a new human, linguistic, mathematical, or accessibility
certification of the underlying book.
"""
files["PACKET_INVENTORY.json"] = (
    json.dumps(
        {
            "schema": "topology-capability-packet/1",
            "files": [identity(path, data) for path, data in sorted(files.items())],
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n"
).encode("utf-8")


def build_zip() -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(
        stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path, data in sorted(files.items()):
            relative = Path(path)
            assert not relative.is_absolute() and ".." not in relative.parts
            info = zipfile.ZipInfo(path, (2026, 9, 4, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compresslevel=9)
    return stream.getvalue()


payload = build_zip()
assert payload == build_zip()
with tempfile.TemporaryDirectory(prefix="topology-packet-replay-") as temporary:
    replay = Path(temporary)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert archive.testzip() is None
        for path, data in files.items():
            assert archive.read(path) == data
        archive.extractall(replay)  # All members were checked as relative above.
    for command in (
        ["python", "-B", "scripts/build-topology-capability-v1.py"],
        ["python", "-B", "scripts/validate-topology-capability-v1.py"],
    ):
        run = subprocess.run(command, cwd=replay, capture_output=True, text=True)
        assert run.returncode == 0, run.stdout + run.stderr
    replay_paths = [row["path"] for row in manifest["outputs"]] + [
        (BASE / "manifest.json").as_posix(),
        (BASE / "validation.json").as_posix(),
        "docs/backend/topology/validation.json",
    ]
    for path in replay_paths:
        assert (replay / path).read_bytes() == files[path], path

target = ROOT / TARGET
target.mkdir(parents=True, exist_ok=True)
(target / ARCHIVE_NAME).write_bytes(payload)
receipt = {
    "schema": "topology-capability-packet-build/1",
    "state": "pass",
    "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip(),
    "archive": identity(ARCHIVE_NAME, payload),
    "entries": len(files),
    "deterministic_zip_replay": True,
    "crc_and_full_entry_readback": True,
    "extracted_packet_build_and_validation": True,
    "adapter_manifest_sha256": validation["manifest_sha256"],
    "public_release_verified": False,
}
(target / "PACKET_BUILD_RECEIPT.json").write_text(
    json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(receipt))
