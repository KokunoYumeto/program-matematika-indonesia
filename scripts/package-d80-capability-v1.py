"""Build and independently replay the deterministic D80 capability packet."""
from __future__ import annotations

import hashlib
import io
import csv
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT.parent / "methods-of-algebra-volume-2-id"
BASE = Path("backend/course-capsule-v1/adapters/d80-capability-v1")
TARGET = Path("releases/d80-learning-capability-v1")
ARCHIVE_NAME = "D80_NATIVE_LEARNING_CAPABILITY_V1.zip"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: str, data: bytes) -> dict[str, object]:
    return {"path": path, "bytes": len(data), "sha256": sha(data)}


manifest_bytes = (ROOT / BASE / "manifest.json").read_bytes()
manifest = json.loads(manifest_bytes)
validation_bytes = (ROOT / BASE / "validation.json").read_bytes()
validation = json.loads(validation_bytes)
assert manifest["contract"] == validation["contract"] == "course-learning-capability/1"
assert validation["state"] == "pass"
assert validation["manifest_sha256"] == sha(manifest_bytes)

files: dict[str, bytes] = {}
for path in sorted((ROOT / BASE).rglob("*")):
    if path.is_file():
        files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
for path in (
    "scripts/build_d80_capability_v1.py",
    "scripts/d80_capability_model_v1.py",
    "scripts/package-d80-capability-v1.py",
    "scripts/validate_d80_capability_v1.py",
    "docs/backend/d80/D80.html",
    "docs/backend/d80/D80-pengajar.html",
    "docs/backend/d80/learning-map.json",
    "docs/backend/d80/validation.json",
):
    files[path] = (ROOT / path).read_bytes()

for row in manifest["inputs"]:
    source = NATIVE / row["path"]
    data = source.read_bytes()
    assert {"bytes": len(data), "sha256": sha(data)} == {
        "bytes": row["bytes"],
        "sha256": row["sha256"],
    }, row["path"]
    files[(Path("native") / row["path"]).as_posix()] = data

# The native unit index points to 146 exact translation targets. They are not
# duplicated in the source lock because the locked target manifest is their
# identity authority, but a self-replaying packet must carry the bytes.
target_manifest_path = next(
    row["path"] for row in manifest["inputs"]
    if row["role"] == "translation_target_manifest"
)
with (NATIVE / target_manifest_path).open("r", encoding="utf-8-sig", newline="") as handle:
    target_rows = list(csv.DictReader(handle))
assert len(target_rows) == 146
for row in target_rows:
    data = (NATIVE / row["path"]).read_bytes()
    assert {"bytes": len(data), "sha256": sha(data)} == {
        "bytes": int(row["bytes"]),
        "sha256": row["sha256"],
    }, row["path"]
    files[(Path("native") / row["path"]).as_posix()] = data
for row in manifest["outputs"]:
    path = (BASE / row["path"]).as_posix()
    assert identity(row["path"], files[path]) == row

files["START_HERE.md"] = b"""# D80 category and homological methods capability packet

Open docs/backend/d80/D80.html for the learner route and
docs/backend/d80/D80-pengajar.html for the aligned educator view.

Rebuild and validate with Python 3 from this archive root:

    python -B scripts/build_d80_capability_v1.py --native-root native
    python -B scripts/validate_d80_capability_v1.py --native-root native

The packet contains the 20 exact frozen native inputs needed for replay, the
146 translated-source unit identities, two separately attributed independent
mastery bridges, all eleven negative fixtures, and the generated thin adapter.
It preserves the 50 superseded checkpoint hashes and the malformed 67-character
historical value rather than treating them as current target identities.

This packet does not claim native static MathML, WCAG conformance, source-book
solutions, a deterministic replay of the native TeX build, or completion of the
40-role program backend. The original producer repository and public editions
remain authoritative for the book itself.
"""
files["PACKET_INVENTORY.json"] = (
    json.dumps(
        {
            "schema": "d80-capability-packet/1",
            "native_input_count": len(manifest["inputs"]),
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
with tempfile.TemporaryDirectory(prefix="d80-capability-packet-replay-") as temporary:
    replay = Path(temporary)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        assert archive.testzip() is None
        for path, data in files.items():
            assert archive.read(path) == data
        archive.extractall(replay)
    for command in (
        ["python", "-B", "scripts/build_d80_capability_v1.py", "--native-root", "native"],
        ["python", "-B", "scripts/validate_d80_capability_v1.py", "--native-root", "native"],
    ):
        run = subprocess.run(command, cwd=replay, capture_output=True, text=True)
        assert run.returncode == 0, run.stdout + run.stderr
    replay_paths = [
        (BASE / row["path"]).as_posix() for row in manifest["outputs"]
    ] + [
        (BASE / "manifest.json").as_posix(),
        (BASE / "validation.json").as_posix(),
    ]
    for path in replay_paths:
        assert (replay / path).read_bytes() == files[path], path

target = ROOT / TARGET
target.mkdir(parents=True, exist_ok=True)
(target / ARCHIVE_NAME).write_bytes(payload)
receipt = {
    "schema": "d80-capability-packet-build/1",
    "state": "pass",
    "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip(),
    "archive": identity(ARCHIVE_NAME, payload),
    "entries": len(files),
    "native_inputs": len(manifest["inputs"]),
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
