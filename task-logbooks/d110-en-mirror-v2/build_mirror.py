#!/usr/bin/env python3
"""Build the bounded D110 English mirror from one exact upstream Git tree."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import base64
import tarfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath


REPO = "leanprover-community/mathematics_in_lean"
COMMIT = "dd6d752fedb14082f557913c2dccb2d4851e5173"
TREE = "757ef238a7e2ded30db5b3d388ff299fc28f23d5"
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
TARGET = REPO_ROOT / "docs" / "en" / "courses" / "D110"
UA = {"User-Agent": "Codex-D110-mirror", "Accept": "application/vnd.github+json"}
MATHJAX_VERSION = "4.1.3"
MATHJAX_REGISTRY_URL = f"https://registry.npmjs.org/mathjax/{MATHJAX_VERSION}"
MATHJAX_EXTERNAL_SRC = b"https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js"
MATHJAX_LOCAL_SRC = b"_vendor/mathjax/tex-mml-chtml.js"

def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def transform_html(data: bytes) -> bytes:
    """Localize the inherited MathJax URL; navigation is coordinator-owned."""
    return data.replace(MATHJAX_EXTERNAL_SRC, MATHJAX_LOCAL_SRC)


def main() -> None:
    if TARGET.exists():
        raise SystemExit(f"refusing to overwrite existing target: {TARGET}")

    commit_url = f"https://api.github.com/repos/{REPO}/git/commits/{COMMIT}"
    commit_doc = json.loads(fetch(commit_url))
    if commit_doc.get("sha") != COMMIT or commit_doc.get("tree", {}).get("sha") != TREE:
        raise RuntimeError("requested commit/tree binding did not verify")

    tree_url = f"https://api.github.com/repos/{REPO}/git/trees/{TREE}?recursive=1"
    tree_doc = json.loads(fetch(tree_url))
    if tree_doc.get("truncated"):
        raise RuntimeError("Git tree API returned a truncated inventory")
    selected = sorted(
        (
            item
            for item in tree_doc["tree"]
            if item["type"] == "blob"
            and (item["path"] == "LICENSE" or item["path"].startswith("html/"))
        ),
        key=lambda item: item["path"],
    )
    if not selected or not any(item["path"] == "html/index.html" for item in selected):
        raise RuntimeError("selected upstream inventory is incomplete")

    archive_url = f"https://codeload.github.com/{REPO}/zip/{COMMIT}"
    archive = fetch(archive_url)
    archive_sha256 = hashlib.sha256(archive).hexdigest()

    inventory = []
    TARGET.mkdir(parents=True)
    try:
        with zipfile.ZipFile(io.BytesIO(archive), "r") as zf:
            roots = {name.split("/", 1)[0] for name in zf.namelist() if "/" in name}
            if len(roots) != 1:
                raise RuntimeError("unexpected upstream archive root")
            root = next(iter(roots))
            for item in selected:
                upstream_path = item["path"]
                member = f"{root}/{upstream_path}"
                source = zf.read(member)
                if len(source) != item["size"] or git_blob_sha(source) != item["sha"]:
                    raise RuntimeError(f"Git blob verification failed: {upstream_path}")
                target_rel = upstream_path[5:] if upstream_path.startswith("html/") else upstream_path
                destination = TARGET / Path(PurePosixPath(target_rel))
                destination.parent.mkdir(parents=True, exist_ok=True)
                output = transform_html(source) if target_rel.endswith(".html") else source
                destination.write_bytes(output)
                inventory.append(
                    {
                        "upstream_path": upstream_path,
                        "target_path": target_rel,
                        "git_blob_sha1": item["sha"],
                        "source_bytes": len(source),
                        "source_sha256": hashlib.sha256(source).hexdigest(),
                        "mirrored_bytes": len(output),
                        "mirrored_sha256": hashlib.sha256(output).hexdigest(),
                        "navigation_injected": False,
                        "mathjax_localized": target_rel.endswith(".html") and MATHJAX_EXTERNAL_SRC in source,
                    }
                )

        mathjax_doc = json.loads(fetch(MATHJAX_REGISTRY_URL))
        if mathjax_doc.get("version") != MATHJAX_VERSION:
            raise RuntimeError("MathJax registry version mismatch")
        mathjax_tarball_url = mathjax_doc["dist"]["tarball"]
        mathjax_integrity = mathjax_doc["dist"]["integrity"]
        mathjax_tarball = fetch(mathjax_tarball_url)
        algorithm, encoded_digest = mathjax_integrity.split("-", 1)
        if algorithm != "sha512" or hashlib.sha512(mathjax_tarball).digest() != base64.b64decode(encoded_digest):
            raise RuntimeError("MathJax npm integrity verification failed")
        mathjax_files = []
        with tarfile.open(fileobj=io.BytesIO(mathjax_tarball), mode="r:gz") as tf:
            members = sorted((member for member in tf.getmembers() if member.isfile()), key=lambda member: member.name)
            for member in members:
                if not member.name.startswith("package/"):
                    raise RuntimeError(f"unexpected MathJax tar member: {member.name}")
                rel = PurePosixPath(member.name).relative_to("package")
                if ".." in rel.parts:
                    raise RuntimeError(f"unsafe MathJax tar member: {member.name}")
                extracted = tf.extractfile(member)
                if extracted is None:
                    raise RuntimeError(f"could not read MathJax tar member: {member.name}")
                data = extracted.read()
                destination = TARGET / "_vendor" / "mathjax" / Path(rel)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                mathjax_files.append(
                    {
                        "target_path": (PurePosixPath("_vendor/mathjax") / rel).as_posix(),
                        "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                )
        if not (TARGET / "_vendor" / "mathjax" / "tex-mml-chtml.js").is_file():
            raise RuntimeError("MathJax combined component missing from pinned package")

        upstream_md = f"""# D110 · Mathematics in Lean — original English mirror

This directory is an additive, program-hosted mirror of the checked-in HTML edition of **Mathematics in Lean**, by Jeremy Avigad, Patrick Massot, and the Lean community.

- Authoritative original: https://leanprover-community.github.io/mathematics_in_lean/
- Upstream source: https://github.com/{REPO}
- Bound commit: `{COMMIT}`
- Bound root tree: `{TREE}`
- Mirrored upstream scope: `html/` plus `LICENSE`
- Book text: CC BY 4.0, as stated in the rendered copyright notice retained on every HTML page.
- Repository code and build assets: Apache License 2.0 under the retained root [LICENSE](LICENSE).
- Retained components keep their embedded copyright and license notices.

Program navigation is intentionally absent from these admitted pages. The root coordinator owns injection of the standard `data-central-surface-navigation=v1` overlay. The build inventory in `task-logbooks/d110-en-mirror-v2/upstream-inventory.json` records the Git blob identity and SHA-256 of every source file; the validator reverses only the local MathJax URL rewrite and proves that every recovered HTML file matches its bound upstream Git blob.

For offline formula rendering, the inherited unpinned MathJax 4 CDN request is redirected to a complete local copy of npm package `mathjax@{MATHJAX_VERSION}`, verified against npm integrity `{mathjax_integrity}`. MathJax is Apache-2.0 licensed; its package metadata and license are retained in `_vendor/mathjax/`.
"""
        (TARGET / "UPSTREAM.md").write_text(upstream_md, encoding="utf-8", newline="\n")

        manifest = {
            "schema": "d110-upstream-inventory-v1",
            "repository": REPO,
            "commit": COMMIT,
            "tree": TREE,
            "rights": {
                "book_text": "CC BY 4.0 per rendered copyright notice",
                "repository_code_and_build_assets": "Apache-2.0 under retained root LICENSE",
                "vendored_mathjax": "Apache-2.0 under _vendor/mathjax/LICENSE",
                "embedded_notices": "retained components keep their embedded notices",
            },
            "archive_url": archive_url,
            "downloaded_archive_bytes": len(archive),
            "downloaded_archive_sha256": archive_sha256,
            "source_blob_count": len(inventory),
            "source_html_count": sum(row["target_path"].endswith(".html") for row in inventory),
            "source_bytes": sum(row["source_bytes"] for row in inventory),
            "files": inventory,
            "vendored_dependencies": {
                "mathjax": {
                    "name": "mathjax",
                    "version": MATHJAX_VERSION,
                    "registry_url": MATHJAX_REGISTRY_URL,
                    "tarball_url": mathjax_tarball_url,
                    "integrity": mathjax_integrity,
                    "tarball_bytes": len(mathjax_tarball),
                    "tarball_sha256": hashlib.sha256(mathjax_tarball).hexdigest(),
                    "file_count": len(mathjax_files),
                    "files": mathjax_files,
                }
            },
        }
        (HERE / "upstream-inventory.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
        )

    except Exception:
        if TARGET.exists():
            shutil.rmtree(TARGET)
        raise


if __name__ == "__main__":
    main()
