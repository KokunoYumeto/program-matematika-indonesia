#!/usr/bin/env python3
"""Write and verify a canonical SHA-256 inventory for one release directory."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


CHECKSUM_NAME = "CHECKSUMS.sha256"
CHECKSUM_LINE = re.compile(r"^(?P<sha256>[0-9a-f]{64})  (?P<name>[^\\/\r\n]+)$")
LEARNER_PDF = re.compile(r"^00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v(?P<version>[^/]+)\.pdf$")
LEARNER_HTML = re.compile(r"^01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v(?P<version>[^/]+)\.html$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def release_files(release_dir: Path, output: Path) -> list[Path]:
    files = sorted(
        (
            path
            for path in release_dir.iterdir()
            if path.is_file() and path.resolve() != output.resolve()
        ),
        key=lambda path: path.name,
    )
    for path in files:
        if "\n" in path.name or "\r" in path.name:
            raise ValueError(f"release filename contains a line break: {path.name!r}")
    return files


def canonical_payload(files: list[Path]) -> bytes:
    lines = [f"{sha256_file(path)}  {path.name}" for path in files]
    return ("\n".join(lines) + "\n").encode("ascii")


def assert_learner_first(files: list[Path]) -> None:
    if len(files) < 2:
        raise ValueError("release inventory cannot establish learner-first ordering")
    pdf_match = LEARNER_PDF.fullmatch(files[0].name)
    html_match = LEARNER_HTML.fullmatch(files[1].name)
    if not pdf_match or not html_match or pdf_match.group("version") != html_match.group("version"):
        raise ValueError("release inventory must sort first as the 00 learner PDF and 01 learner HTML")


def verify(output: Path, files: list[Path], expected_count: int) -> None:
    if len(files) != expected_count:
        raise ValueError(
            f"release inventory contains {len(files)} files; expected {expected_count}"
        )
    assert_learner_first(files)
    payload = output.read_bytes()
    expected_payload = canonical_payload(files)
    if payload != expected_payload:
        raise ValueError("checksum inventory is not the canonical live-file inventory")
    lines = payload.decode("ascii").splitlines()
    if len(lines) != expected_count:
        raise ValueError("checksum inventory line count mismatch")
    parsed_names: list[str] = []
    for line in lines:
        match = CHECKSUM_LINE.fullmatch(line)
        if not match:
            raise ValueError(f"invalid checksum line: {line!r}")
        parsed_names.append(match.group("name"))
    expected_names = [path.name for path in files]
    if parsed_names != expected_names or len(parsed_names) != len(set(parsed_names)):
        raise ValueError("checksum filenames are not unique canonical release filenames")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-dir", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    release_dir = args.release_dir.resolve()
    if not release_dir.is_dir():
        raise ValueError(f"release directory does not exist: {release_dir}")
    output = release_dir / CHECKSUM_NAME
    files = release_files(release_dir, output)
    assert_learner_first(files)
    if not args.verify_only:
        if len(files) != args.expected_count:
            raise ValueError(
                f"release inventory contains {len(files)} files; expected {args.expected_count}"
            )
        output.write_bytes(canonical_payload(files))
    if not output.is_file():
        raise ValueError(f"checksum inventory does not exist: {output}")
    verify(output, files, args.expected_count)
    print(
        f"PASS: {output} binds {len(files)} release files; "
        f"sha256={sha256_file(output)}"
    )


if __name__ == "__main__":
    main()
