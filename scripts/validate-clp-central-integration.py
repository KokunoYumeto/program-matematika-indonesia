#!/usr/bin/env python3
"""Read-only preflight for the central CLP v2.3.1 integration.

This check deliberately sits beside (rather than changing) the existing
course-capsule and CLP package validators.  It answers the narrower question
that is easy to get wrong during a successor release: do the four CLP rows in
the central integration authority, the seven learner routes, the package
manifest/validation evidence, and the generated course projections all refer
to the same bytes?

The program is read-only.  It never extracts a ZIP, writes a receipt, edits a
JSON file, or changes publication state.  A report is printed to stdout and a
non-zero exit status means at least one check failed.

The sealed CLP adapter manifest is the one deliberate exception to the
repository-publication locator rule: its frozen provenance inventory contains
relative ``outputs/`` paths from the candidate handoff.  Those paths are
accepted only under the exact, immutable candidate prefix declared below.
This exception applies only while inspecting the embedded ZIP manifest;
sidecars, authority rows, validation receipts, and generated capsules remain
strictly free of ``tmp/``/``outputs/`` locators.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse


VALIDATOR_VERSION = "1.0.2"
TARGET_ROLES = ("B20", "B30", "B50", "B60")
EXPECTED_ROUTE_COUNTS = {"B20": 2, "B30": 1, "B50": 2, "B60": 2}
EXPECTED_ACTION_SEQUENCE = (
    ("B20", "textbook"),
    ("B20", "problembook"),
    ("B30", "combined_textbook_problembook"),
    ("B50", "textbook"),
    ("B50", "problembook"),
    ("B60", "textbook"),
    ("B60", "problembook"),
)
EXPECTED_EVIDENCE_KINDS = (
    "central_adapter_manifest",
    "learner_route_validation",
    "deterministic_validation_receipt",
)
CLP_PACKAGE_ID = "urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26"
CLP_FAMILY_ID = "family-06-clp"
EXPECTED_ROLE_BINDINGS = 13
# v0.62.17 is an additive successor over the nine already verified adapter
# roles.  Keep the exact set here so a count-only pass cannot hide a dropped
# legacy binding or an accidental replacement by an unrelated role.
EXPECTED_ADAPTER_ROLE_IDS = frozenset(
    {
        "A00",
        "B10",
        "B20",
        "B30",
        "B50",
        "B60",
        "C30",
        "C40",
        "C80",
        "C130",
        "D20",
        "D60",
        "D110",
    }
)
EXPECTED_COURSE_CAPSULES = 40
EXPECTED_VERIFIED_ADAPTERS = 13
EXPECTED_SIDECAR_ACTIONS = 7
EXPECTED_SIDECAR_PAGES = 4077
EXPECTED_SIDECAR_BYTES = 35639691

# The ZIP is sealed and its manifest identity is recorded in the central
# package index.  Do not normalize, rewrite, or broaden this prefix: the
# seven ``outputs/`` provenance paths in that sealed manifest must begin with
# this exact relative candidate path.  A different UUID, casing, separator,
# or leading component is rejected by the embedded-manifest policy check.
SEALED_CANDIDATE_OUTPUTS_PREFIX = (
    "outputs/01a01ec1-e685-70d0-b022-211396334723/"
    "curriculum_logbook/backend_adapters/clp_family_v231_candidate/"
)

_ABSOLUTE_PATH_RE = re.compile(r"^(?:[A-Za-z]:|[\\/]{1,2})")
_URI_CREDENTIAL_RE = re.compile(
    r"(?i)^[A-Za-z][A-Za-z0-9+.-]*://[^/\s:@]+(?::[^/\s@]*)?@"
)
_URI_CREDENTIAL_ANYWHERE_RE = re.compile(
    r"(?i)(?:^|[\s(<'\"])[A-Za-z][A-Za-z0-9+.-]*://[^/\s:@]+(?::[^/\s@]*)?@"
)
_NONPUBLIC_URI_RE = re.compile(r"(?i)^(?:file|data|ftp):")
_INLINE_CREDENTIAL_RE = re.compile(
    r"(?i)(?:^|[?&#\s])"
    r"(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd|"
    r"secret|token)=[^&#\s]+"
)
_CREDENTIAL_KEY_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|"
    r"passwd|secret|token|credential|authorization|cookie|bearer)"
)
_AUTH_HEADER_RE = re.compile(
    r"(?i)\b(?:authorization|proxy-authorization|cookie|set-cookie)\s*:\s*\S+"
)
_PRIVATE_KEY_RE = re.compile(
    r"(?i)-----begin [^-]*private key-----"
)

DEFAULTS = {
    "index": Path(
        "backend/course-capsule-v1/authority/clp-family-v231/"
        "v23-adapter-index-v2.json"
    ),
    "overrides": Path(
        "backend/course-capsule-v1/authority/integration-overrides-v1.json"
    ),
    "sidecar": Path(
        "backend/course-capsule-v1/authority/clp-family-v231/"
        "learner-reader-actions-v1.json"
    ),
    "route_input": Path(
        "backend/course-capsule-v1/authority/clp-family-v231/"
        "clp-learner-route-input-v1.json"
    ),
    "capsules": Path(
        "backend/course-capsule-v1/generated/course-capsules.json"
    ),
    "capsule_manifest": Path(
        "backend/course-capsule-v1/generated/manifest.json"
    ),
}


class DuplicateKeyError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=_unique_object)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return {"bytes": size, "sha256": digest.hexdigest()}


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return f"external/{path.name}"


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def safe_locator(locator: Any) -> tuple[bool, str]:
    """Return (safe, reason) for a locator stored in a public authority row."""
    if not isinstance(locator, str) or not locator.strip():
        return False, "locator is not a non-empty string"
    if "\x00" in locator or "\\" in locator:
        return False, "NUL or backslash is forbidden"
    if re.search(r"(^|/)(?:tmp|outputs)(?:/|$)", locator, re.IGNORECASE):
        return False, "private tmp/outputs segment"
    if re.search(r"(^|/)\.\.(?:/|$)", locator):
        return False, "parent traversal segment"
    if re.match(r"^[A-Za-z]:", locator) or locator.startswith("/"):
        return False, "absolute or drive-qualified path"
    if locator.startswith(("file:", "data:", "ftp:")):
        return False, "non-public locator scheme"
    if locator.startswith("release-asset:"):
        payload = locator[len("release-asset:") :]
        path_part, sep, fragment = payload.partition("#")
        if not path_part or not sep or not fragment:
            return False, "release-asset locator needs path#member"
        if fragment.startswith("/") or ".." in PurePosixPath(fragment).parts:
            return False, "unsafe release-asset member"
        return safe_locator(path_part)
    if locator.startswith(("http://", "https://")):
        parsed = urlparse(locator)
        if parsed.username or parsed.password:
            return False, "URL credentials are forbidden"
        if not parsed.netloc:
            return False, "URL host is missing"
        return True, "public URL"
    return True, "repository-relative locator"


def repo_locator(root: Path, locator: str) -> Path | None:
    """Resolve a safe repository-relative locator, or None for URL/asset refs."""
    if locator.startswith("release-asset:") or locator.startswith(("http://", "https://")):
        return None
    candidate = (root / PurePosixPath(locator)).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def identity_matches(actual: dict[str, Any], expected: dict[str, Any]) -> bool:
    return (
        actual.get("bytes") == expected.get("bytes")
        and actual.get("sha256") == expected.get("sha256")
    )


def identity_fields(value: Any) -> tuple[int | None, str | None]:
    if not isinstance(value, dict):
        return None, None
    size = value.get("bytes")
    digest = value.get("sha256")
    return size if isinstance(size, int) else None, digest if isinstance(digest, str) else None


def add_check(report: dict[str, Any], label: str, passed: bool, detail: Any = None) -> None:
    row = {"label": label, "status": "pass" if passed else "fail"}
    if detail is not None:
        row["detail"] = detail
    report["checks"].append(row)
    if not passed:
        report["failures"].append(row)


def read_json_checked(
    report: dict[str, Any], path: Path, label: str
) -> Any | None:
    report["files_read"].append(display_path(path, report["repo"]))
    try:
        value = load_json(path)
    except Exception as exc:  # noqa: BLE001 - report all independent failures
        add_check(report, f"read {label}", False, {"path": display_path(path, report["repo"]), "error": str(exc)})
        return None
    try:
        identity = file_identity(path)
    except Exception as exc:  # noqa: BLE001 - keep independent checks running
        add_check(report, f"identity {label}", False, {"path": display_path(path, report["repo"]), "error": str(exc)})
        return value
    add_check(report, f"read {label}", True, {"path": display_path(path, report["repo"]), **identity})
    return value


def compare_identity_check(
    report: dict[str, Any], label: str, actual: dict[str, Any] | None, expected: dict[str, Any]
) -> None:
    passed = actual is not None and identity_matches(actual, expected)
    add_check(report, label, passed, {"expected": expected, "actual": actual})


def route_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("course_id")), str(row.get("role"))


def validate_sidecar(
    report: dict[str, Any], sidecar: Any, route_input: Any, sidecar_path: Path, route_input_path: Path
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    actions = sidecar.get("actions") if isinstance(sidecar, dict) else None
    routes = route_input.get("routes") if isinstance(route_input, dict) else None
    if not isinstance(actions, list):
        add_check(report, "sidecar actions array", False, "missing actions array")
        actions = []
    if not isinstance(routes, list):
        add_check(report, "route input routes array", False, "missing routes array")
        routes = []
    summary = sidecar.get("summary", {}) if isinstance(sidecar, dict) else {}
    add_check(report, "sidecar schema", isinstance(sidecar, dict) and sidecar.get("schema_id") == "interlanguage/learner-reader-actions/v1")
    add_check(report, "sidecar status", isinstance(sidecar, dict) and sidecar.get("status") == "verified_route_evidence_projection")
    add_check(report, "sidecar action count", len(actions) == EXPECTED_SIDECAR_ACTIONS, {"actual": len(actions), "expected": EXPECTED_SIDECAR_ACTIONS})
    add_check(report, "sidecar summary action count", summary.get("action_count") == EXPECTED_SIDECAR_ACTIONS)
    add_check(report, "sidecar summary verified count", summary.get("verified_action_count") == EXPECTED_SIDECAR_ACTIONS)
    add_check(report, "sidecar summary course count", summary.get("course_count") == len(TARGET_ROLES))
    add_check(report, "sidecar summary pages", summary.get("pages") == EXPECTED_SIDECAR_PAGES)
    add_check(report, "sidecar summary bytes", summary.get("bytes") == EXPECTED_SIDECAR_BYTES)
    add_check(
        report,
        "sidecar has no tmp/outputs locator",
        not (sidecar_forbidden := list(scan_forbidden(sidecar))),
        sidecar_forbidden,
    )
    add_check(
        report,
        "route input has no tmp/outputs locator",
        not (route_input_forbidden := list(scan_forbidden(route_input))),
        route_input_forbidden,
    )
    expected_keys = list(EXPECTED_ACTION_SEQUENCE)
    actual_keys = [route_key(row) for row in actions if isinstance(row, dict)]
    add_check(report, "sidecar route sequence", actual_keys == expected_keys, {"actual": actual_keys, "expected": expected_keys})
    action_map = {route_key(row): row for row in actions if isinstance(row, dict)}
    route_map = {route_key(row): row for row in routes if isinstance(row, dict)}
    add_check(report, "route input count", len(routes) == EXPECTED_SIDECAR_ACTIONS)
    add_check(report, "sidecar unique action identities", len(action_map) == len(actions))
    parity_fields = ("course_id", "volume", "role", "kind", "format", "scope", "pages", "bytes", "sha256", "filename", "url", "license", "route_granularity")
    for key in expected_keys:
        action = action_map.get(key)
        route = route_map.get(key)
        add_check(report, f"route present {key[0]}/{key[1]}", action is not None and route is not None)
        if action is None or route is None:
            continue
        for field in parity_fields:
            add_check(report, f"sidecar parity {key[0]}/{key[1]}/{field}", action.get(field) == route.get(field), {"sidecar": action.get(field), "route_input": route.get(field)})
        add_check(report, f"sidecar verified state {key[0]}/{key[1]}", action.get("state") == "verified")
        digest = action.get("sha256")
        add_check(report, f"sidecar digest shape {key[0]}/{key[1]}", isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None)
        safe, reason = safe_locator(action.get("url"))
        add_check(report, f"sidecar URL safety {key[0]}/{key[1]}", safe and str(action.get("url")).startswith("https://"), reason)
    # The source identity in the sidecar binds it to the compact route input.
    source = sidecar.get("source", {}) if isinstance(sidecar, dict) else {}
    expected_source = file_identity(route_input_path) if route_input_path.exists() else None
    if expected_source:
        add_check(report, "sidecar source byte/hash parity", source.get("bytes") == expected_source["bytes"] and source.get("sha256") == expected_source["sha256"], {"sidecar": {"bytes": source.get("bytes"), "sha256": source.get("sha256")}, "route_input": expected_source})
    return action_map, route_map


def resolve_archive(root: Path, package: dict[str, Any], explicit: str | None) -> Path | None:
    raw = explicit or ((package.get("archive") or {}).get("path") if isinstance(package, dict) else None)
    if not raw:
        return None
    path = Path(raw)
    return path if path.is_absolute() else root / path


def read_zip_manifest(
    report: dict[str, Any],
    archive: Path,
    package: dict[str, Any],
    actual_archive: dict[str, Any] | None = None,
) -> tuple[bytes | None, dict[str, Any] | None]:
    if not archive.exists():
        add_check(report, "CLP archive exists", False, display_path(archive, report["repo"]))
        return None, None
    if actual_archive is None:
        try:
            actual_archive = file_identity(archive)
        except Exception as exc:  # noqa: BLE001
            add_check(report, "CLP archive identity", False, str(exc))
            return None, None
    report["files_read"].append(display_path(archive, report["repo"]))
    expected_archive = package.get("archive", {}) if isinstance(package, dict) else {}
    compare_identity_check(report, "CLP archive identity", actual_archive, expected_archive)
    try:
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
            add_check(report, "CLP archive has unique member names", len(names) == len(set(names)))
            add_check(report, "CLP archive contains manifest.json", "manifest.json" in names)
            if "manifest.json" not in names:
                return None, None
            with zf.open("manifest.json", "r") as stream:
                manifest_bytes = stream.read()
            actual_manifest = {"bytes": len(manifest_bytes), "sha256": sha256_bytes(manifest_bytes)}
            expected_manifest = package.get("manifest", {})
            compare_identity_check(report, "embedded manifest identity", actual_manifest, expected_manifest)
            try:
                manifest = json.loads(manifest_bytes.decode("utf-8"), object_pairs_hook=_unique_object)
            except Exception as exc:  # noqa: BLE001
                add_check(report, "embedded manifest JSON", False, str(exc))
                return manifest_bytes, None
            add_check(report, "embedded manifest JSON", True)
            add_check(report, "embedded manifest package id", manifest.get("package_id") == CLP_PACKAGE_ID, manifest.get("package_id"))
            embedded_version = manifest.get("adapter_version", manifest.get("extension_version"))
            add_check(report, "embedded manifest adapter version", embedded_version == package.get("adapter_version"), {"embedded": embedded_version, "index": package.get("adapter_version")})
            allowlisted_outputs: list[tuple[str, str]] = []
            manifest_forbidden = list(
                scan_embedded_manifest_policy(
                    manifest, allowed_outputs=allowlisted_outputs
                )
            )
            add_check(
                report,
                "embedded manifest sealed provenance path policy",
                not manifest_forbidden,
                {
                    "allowlisted_prefix": SEALED_CANDIDATE_OUTPUTS_PREFIX,
                    "allowlisted_output_path_count": len(allowlisted_outputs),
                    "violations": manifest_forbidden,
                },
            )
            # The sealed manifest's ``files`` list intentionally excludes ZIP
            # control members (manifest/seal/checksum).  Only require the
            # structural list here; the full member accounting remains the
            # responsibility of validate-clp-successor-v231.py.
            add_check(report, "embedded manifest files list", isinstance(manifest.get("files"), list) and bool(manifest.get("files")))
            return manifest_bytes, manifest
    except Exception as exc:  # noqa: BLE001
        add_check(report, "read CLP archive", False, str(exc))
        return None, None


def evidence_local_identity(
    report: dict[str, Any], root: Path, evidence: dict[str, Any], kind: str, archive_manifest_identity: dict[str, Any] | None, archive_identity: dict[str, Any] | None, explicit_manifest: Path | None, explicit_validation: Path | None, sidecar_path: Path
) -> dict[str, Any] | None:
    locator = evidence.get("locator")
    safe, reason = safe_locator(locator)
    add_check(report, f"safe locator {kind}", safe, {"locator": locator, "reason": reason})
    if not safe:
        return None
    expected = {"bytes": evidence.get("bytes"), "sha256": evidence.get("sha256")}
    if not isinstance(expected["bytes"], int) or not isinstance(expected["sha256"], str):
        add_check(report, f"identity fields {kind}", False, expected)
        return None
    add_check(
        report,
        f"identity digest shape {kind}",
        bool(re.fullmatch(r"[0-9a-f]{64}", expected["sha256"])),
        expected["sha256"],
    )
    actual: dict[str, Any] | None = None
    if kind == "central_adapter_manifest" and archive_manifest_identity is not None:
        if isinstance(locator, str) and locator.startswith("release-asset:"):
            member = locator.split("#", 1)[1] if "#" in locator else ""
            add_check(report, "manifest release-asset member", member == "manifest.json", member)
            actual = archive_manifest_identity
        elif explicit_manifest is not None and explicit_manifest.exists():
            try:
                actual = file_identity(explicit_manifest)
            except Exception as exc:  # noqa: BLE001
                add_check(report, "read explicit manifest", False, str(exc))
    elif kind == "learner_route_validation":
        path = repo_locator(root, locator) if isinstance(locator, str) else None
        if path is not None and path.exists():
            try:
                actual = file_identity(path)
            except Exception as exc:  # noqa: BLE001
                add_check(report, "read route evidence", False, str(exc))
        elif Path(sidecar_path).exists():
            # A route evidence row normally names the canonical sidecar.  If a
            # caller supplied an equivalent public URL, still compare against
            # the sidecar bytes rather than performing network I/O.
            if isinstance(locator, str) and locator.replace("\\", "/") == display_path(sidecar_path, root):
                try:
                    actual = file_identity(sidecar_path)
                except Exception as exc:  # noqa: BLE001
                    add_check(report, "read sidecar evidence", False, str(exc))
    elif kind == "deterministic_validation_receipt":
        path = explicit_validation if explicit_validation is not None else (repo_locator(root, locator) if isinstance(locator, str) else None)
        if path is not None and path.exists():
            try:
                actual = file_identity(path)
            except Exception as exc:  # noqa: BLE001
                add_check(report, "read validation evidence", False, str(exc))
            try:
                validation = load_json(path)
                add_check(
                    report,
                    "validation receipt status is pass",
                    isinstance(validation, dict)
                    and str(validation.get("status", "")).lower() == "pass",
                    validation.get("status") if isinstance(validation, dict) else None,
                )
                add_check(
                    report,
                    "validation receipt has no tmp/outputs locator",
                    not (validation_forbidden := list(scan_forbidden(validation))),
                    validation_forbidden,
                )
                if isinstance(validation, dict):
                    # Some CLP receipts carry the manifest identity under
                    # ``package.manifest`` (older receipt) while the generic
                    # replay receipt carries the archive identity under
                    # ``derived.archive``.  When either is present, bind it to
                    # the exact ZIP/member already checked above; do not let a
                    # stale pass receipt silently certify a different build.
                    package = validation.get("package", {})
                    generic = validation.get("generic", {})
                    manifest_claims: list[dict[str, Any]] = []
                    if isinstance(package, dict):
                        if isinstance(package.get("manifest"), dict):
                            manifest_claims.append(package["manifest"])
                        if "manifest_bytes" in package or "manifest_sha256" in package:
                            manifest_claims.append({"bytes": package.get("manifest_bytes"), "sha256": package.get("manifest_sha256")})
                    if isinstance(generic, dict) and isinstance(generic.get("manifest"), dict):
                        manifest_claims.append(generic["manifest"])
                    for claim in manifest_claims:
                        if archive_manifest_identity is not None:
                            compare_identity_check(report, "validation manifest identity", archive_manifest_identity, claim)
                    derived_archive = validation.get("derived", {}).get("archive")
                    if isinstance(derived_archive, dict) and archive_identity is not None:
                        compare_identity_check(report, "validation archive identity", archive_identity, derived_archive)
            except Exception as exc:  # noqa: BLE001
                add_check(report, "validation receipt JSON", False, str(exc))
    compare_identity_check(report, f"evidence identity {kind}", actual, expected)
    return actual


def scan_forbidden(value: Any, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from scan_forbidden(child, f"{path}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from scan_forbidden(child, f"{path}/{index}")
    elif isinstance(value, str) and re.search(r"(^|[/\\])(?:tmp|outputs)(?:[/\\]|$)", value, re.IGNORECASE):
        yield path, value


def scan_embedded_manifest_policy(
    value: Any,
    path: str = "",
    parent_key: str = "",
    *,
    allowed_outputs: list[tuple[str, str]] | None = None,
) -> Iterable[tuple[str, Any]]:
    """Audit strings in the sealed manifest without weakening public rows.

    The sealed candidate's manifest predates the central repository and
    intentionally records seven relative outputs/ provenance paths.  The
    only accepted outputs/ values are those beginning with
    SEALED_CANDIDATE_OUTPUTS_PREFIX byte-for-byte.  This function does not
    resolve or read those paths; it only checks their lexical form.

    Every other private-locator rule remains strict here: tmp/ paths,
    absolute/drive-qualified paths, traversal, URI credentials, inline
    credential assignments, authentication headers, and private-key markers
    are rejected.  Credential-bearing values are redacted in the diagnostic
    tuple so a malformed manifest cannot leak a secret through the report.
    Callers auditing sidecars, authority rows, receipts, or generated
    capsules must continue to use scan_forbidden (or their existing strict
    checks), not this allowlist.
    """
    if isinstance(value, dict):
        for key, child in value.items():
            yield from scan_embedded_manifest_policy(
                child,
                f"{path}/{key}",
                str(key),
                allowed_outputs=allowed_outputs,
            )
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            yield from scan_embedded_manifest_policy(
                child,
                f"{path}/{index}",
                parent_key,
                allowed_outputs=allowed_outputs,
            )
        return
    if not isinstance(value, str):
        return

    text = value
    credential_match = (
        bool(_URI_CREDENTIAL_RE.search(text))
        or bool(_URI_CREDENTIAL_ANYWHERE_RE.search(text))
        or bool(_INLINE_CREDENTIAL_RE.search(text))
        or bool(_AUTH_HEADER_RE.search(text))
        or bool(_PRIVATE_KEY_RE.search(text))
        or (
            bool(parent_key)
            and bool(_CREDENTIAL_KEY_RE.search(parent_key))
            and bool(text.strip())
        )
    )
    if credential_match:
        # Never echo a credential-bearing value into the machine-readable
        # report.  The path and reason remain sufficient for remediation.
        yield path, {"reason": "credential-like value", "value": "<redacted>"}
        return

    if "\x00" in text:
        yield path, {"reason": "NUL byte in embedded manifest string", "value": text}
        return
    if _NONPUBLIC_URI_RE.match(text):
        yield path, {"reason": "non-public URI scheme", "value": text}
        return
    if _ABSOLUTE_PATH_RE.match(text):
        yield path, {"reason": "absolute or drive-qualified path", "value": text}
        return

    has_outputs_segment = bool(
        re.search(r"(^|[/\\])outputs([/\\]|$)", text, re.IGNORECASE)
    )
    if has_outputs_segment:
        # Exact prefix comparison is deliberately case- and separator-
        # sensitive.  A path that merely contains the prefix, changes its
        # casing, or uses a backslash is not the sealed candidate path.
        if not text.startswith(SEALED_CANDIDATE_OUTPUTS_PREFIX):
            yield path, {
                "reason": "outputs path is outside sealed candidate prefix",
                "value": text,
                "allowlisted_prefix": SEALED_CANDIDATE_OUTPUTS_PREFIX,
            }
            return
        suffix = text[len(SEALED_CANDIDATE_OUTPUTS_PREFIX) :]
        parts = PurePosixPath(text).parts
        prefix_parts = PurePosixPath(
            SEALED_CANDIDATE_OUTPUTS_PREFIX.rstrip("/")
        ).parts
        malformed = (
            not suffix
            or "\\" in text
            or suffix.startswith("/")
            or ":" in suffix
            or bool(
                re.search(
                    r"(^|/)(?:[A-Za-z]:|[\\/]{1,2})", suffix
                )
            )
            or any(part in ("", ".", "..") for part in parts)
            or tuple(parts[: len(prefix_parts)]) != prefix_parts
        )
        if malformed:
            yield path, {
                "reason": "malformed sealed candidate outputs path",
                "value": text,
                "allowlisted_prefix": SEALED_CANDIDATE_OUTPUTS_PREFIX,
            }
            return
        if allowed_outputs is not None:
            allowed_outputs.append((path, text))
        return

    # tmp/ remains forbidden even though outputs/ is allowlisted for this one
    # sealed manifest.  Keep this segment test lexical and narrow so ordinary
    # prose containing the word "tmp" is unaffected.
    if re.search(r"(^|[/\\])tmp([/\\]|$)", text, re.IGNORECASE):
        yield path, {"reason": "private tmp path", "value": text}
        return

    # Reject traversal in path-like strings.  This supplements the absolute
    # path check while avoiding a blanket ban on punctuation in prose fields.
    if (
        ("/" in text or "\\" in text)
        and any(
            part == ".."
            for part in PurePosixPath(text.replace("\\", "/")).parts
        )
    ):
        yield path, {"reason": "parent traversal segment", "value": text}


def validate_generated_manifest_outputs(
    report: dict[str, Any], capsule_manifest: dict[str, Any], capsule_manifest_path: Path
) -> None:
    """Bind manifest output identities to the files actually being checked."""
    add_check(
        report,
        "generated manifest has no tmp/outputs locator",
        not (manifest_forbidden := list(scan_forbidden(capsule_manifest))),
        manifest_forbidden,
    )
    # The manifest paths are relative to the course-capsule output root (the
    # parent of the generated directory), not to the manifest file itself.
    output_root = capsule_manifest_path.parent.parent
    output = capsule_manifest.get("output")
    if isinstance(output, dict) and isinstance(output.get("path"), str):
        output_path = output_root / PurePosixPath(output["path"])
        try:
            output_path.resolve().relative_to(report["repo"].resolve())
            output_inside_repo = True
        except ValueError:
            output_inside_repo = False
        if not output_inside_repo:
            add_check(report, "generated JSONL manifest path safety", False, str(output.get("path")))
        elif output_path.exists():
            compare_identity_check(report, "generated JSONL manifest identity", file_identity(output_path), output)
        else:
            add_check(report, "generated JSONL output exists", False, display_path(output_path, report["repo"]))
    projections = capsule_manifest.get("projections", {})
    projection = projections.get("course_capsules_json") if isinstance(projections, dict) else None
    if isinstance(projection, dict) and isinstance(projection.get("path"), str):
        projection_path = output_root / PurePosixPath(projection["path"])
        try:
            projection_path.resolve().relative_to(report["repo"].resolve())
            projection_inside_repo = True
        except ValueError:
            projection_inside_repo = False
        if not projection_inside_repo:
            add_check(report, "generated JSON manifest path safety", False, str(projection.get("path")))
        elif projection_path.exists():
            compare_identity_check(report, "generated JSON manifest identity", file_identity(projection_path), projection)
        else:
            add_check(report, "generated JSON output exists", False, display_path(projection_path, report["repo"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root (default: current directory)")
    for key, default in DEFAULTS.items():
        parser.add_argument(f"--{key.replace('_', '-')}", default=str(default))
    parser.add_argument("--archive", help="CLP ZIP path; otherwise use index package.archive.path")
    parser.add_argument("--manifest", help="raw CLP manifest path (optional override for evidence identity)")
    parser.add_argument("--validation", help="deterministic validation receipt path")
    args = parser.parse_args(argv)
    root = Path(args.repo).resolve()
    report: dict[str, Any] = {
        "schema_id": "interlanguage/clp-central-integration-validation/v1",
        "validator_version": VALIDATOR_VERSION,
        "read_only": True,
        "repo": root,
        "files_read": [],
        "files_written": [],
        "checks": [],
        "failures": [],
    }

    index = read_json_checked(report, root / args.index, "adapter index")
    overrides = read_json_checked(report, root / args.overrides, "integration overrides")
    sidecar_path = root / args.sidecar
    route_input_path = root / args.route_input
    sidecar = read_json_checked(report, sidecar_path, "learner route sidecar")
    route_input = read_json_checked(report, route_input_path, "compact route input")
    capsules = read_json_checked(report, root / args.capsules, "generated capsules")
    capsule_manifest = read_json_checked(report, root / args.capsule_manifest, "generated capsule manifest")

    if not isinstance(index, dict):
        index = {}
    adapters = index.get("adapters", []) if isinstance(index.get("adapters"), list) else []
    packages = index.get("packages", []) if isinstance(index.get("packages"), list) else []
    add_check(report, "index adapter row count 13", len(adapters) == EXPECTED_ROLE_BINDINGS, len(adapters))
    adapter_role_ids = [row.get("role_id") for row in adapters if isinstance(row, dict)]
    add_check(report, "index adapter role identities unique", len(adapter_role_ids) == len(set(adapter_role_ids)))
    add_check(
        report,
        "index adapter role-ID set exact",
        set(adapter_role_ids) == set(EXPECTED_ADAPTER_ROLE_IDS),
        {
            "actual": sorted(adapter_role_ids, key=str),
            "expected": sorted(EXPECTED_ADAPTER_ROLE_IDS),
        },
    )
    for role in TARGET_ROLES:
        rows = [row for row in adapters if isinstance(row, dict) and row.get("role_id") == role]
        add_check(report, f"index binding {role} unique", len(rows) == 1, len(rows))
        if rows:
            add_check(report, f"index binding {role} CLP family", rows[0].get("native_family_id") == CLP_FAMILY_ID, rows[0].get("native_family_id"))
            add_check(report, f"index binding {role} route count", rows[0].get("course_specific_route_count") == EXPECTED_ROUTE_COUNTS[role], rows[0].get("course_specific_route_count"))
            add_check(report, f"index binding {role} package id", rows[0].get("adapter_package_id") == CLP_PACKAGE_ID, rows[0].get("adapter_package_id"))
    summary = index.get("summary", {}) if isinstance(index, dict) else {}
    add_check(report, "index role binding count 13", summary.get("role_bindings") == EXPECTED_ROLE_BINDINGS, summary.get("role_bindings"))
    clp_packages = [pkg for pkg in packages if isinstance(pkg, dict) and pkg.get("package_id") == CLP_PACKAGE_ID]
    add_check(report, "index CLP package unique", len(clp_packages) == 1, len(clp_packages))
    package = clp_packages[0] if clp_packages else {}
    add_check(report, "index CLP package family", package.get("native_family_id") == CLP_FAMILY_ID, package.get("native_family_id"))

    action_map: dict[tuple[str, str], dict[str, Any]] = {}
    if sidecar is not None and route_input is not None:
        action_map, _ = validate_sidecar(report, sidecar, route_input, sidecar_path, route_input_path)

    archive = resolve_archive(root, package, args.archive)
    archive_manifest_bytes = None
    archive_manifest = None
    archive_identity: dict[str, Any] | None = None
    if archive is None:
        add_check(report, "CLP archive path available", False)
    else:
        if archive.exists():
            try:
                archive_identity = file_identity(archive)
            except Exception:
                archive_identity = None
        archive_manifest_bytes, archive_manifest = read_zip_manifest(report, archive, package, archive_identity)
    archive_manifest_identity = (
        {"bytes": len(archive_manifest_bytes), "sha256": sha256_bytes(archive_manifest_bytes)}
        if archive_manifest_bytes is not None
        else None
    )

    semantic_rows: dict[str, Any] = {}
    semantic = overrides.get("semantic_adapters", {}) if isinstance(overrides, dict) else {}
    for role in TARGET_ROLES:
        row = semantic.get(role) if isinstance(semantic, dict) else None
        semantic_rows[role] = row
        add_check(report, f"semantic adapter row {role} exists", isinstance(row, dict))
        if not isinstance(row, dict):
            continue
        add_check(report, f"semantic adapter {role} verified", row.get("status") == "verified", row.get("status"))
        add_check(report, f"semantic adapter {role} contract", row.get("contract_version") == "2.3.1", row.get("contract_version"))
        add_check(report, f"semantic adapter {role} mapping scope", row.get("mapping_scope") == "reversible_native_course_route_adapter", row.get("mapping_scope"))
        evidence = row.get("evidence")
        add_check(report, f"semantic adapter {role} evidence array", isinstance(evidence, list) and [item.get("kind") for item in evidence if isinstance(item, dict)] == list(EXPECTED_EVIDENCE_KINDS))
        if not isinstance(evidence, list):
            continue
        for item in evidence:
            if not isinstance(item, dict):
                continue
            kind = item.get("kind")
            explicit_manifest = Path(args.manifest) if args.manifest else None
            if explicit_manifest is not None and not explicit_manifest.is_absolute():
                explicit_manifest = root / explicit_manifest
            explicit_validation = Path(args.validation) if args.validation else None
            if explicit_validation is not None and not explicit_validation.is_absolute():
                explicit_validation = root / explicit_validation
            evidence_local_identity(report, root, item, str(kind), archive_manifest_identity, archive_identity, explicit_manifest, explicit_validation, sidecar_path)
        forbidden = list(scan_forbidden(row))
        add_check(report, f"semantic adapter {role} has no tmp/outputs locator", not forbidden, forbidden)
    row_evidence = [semantic_rows[role].get("evidence") for role in TARGET_ROLES if isinstance(semantic_rows[role], dict)]
    if row_evidence:
        baseline = canonical(row_evidence[0])
        add_check(report, "four semantic rows share identical evidence identities", all(canonical(value) == baseline for value in row_evidence), {"row_count": len(row_evidence)})

    if isinstance(capsules, list):
        capsule_ids = [row.get("course_id") for row in capsules if isinstance(row, dict)]
        add_check(
            report,
            "generated course capsule IDs unique",
            len(capsule_ids) == len(set(capsule_ids)),
            {"actual_count": len(capsule_ids), "unique_count": len(set(capsule_ids))},
        )
        capsule_by_id = {row.get("course_id"): row for row in capsules if isinstance(row, dict)}
        add_check(report, "generated course capsule count", len(capsules) == EXPECTED_COURSE_CAPSULES, {"actual": len(capsules), "expected": EXPECTED_COURSE_CAPSULES})
        verified_capsule_count = sum(
            1
            for row in capsules
            if isinstance(row, dict)
            and (((row.get("layers") or {}).get("interoperability") or {}).get("semantic_adapter") or {}).get("status") == "verified"
        )
        add_check(
            report,
            "generated verified semantic capsule count 13",
            verified_capsule_count == EXPECTED_VERIFIED_ADAPTERS,
            {"actual": verified_capsule_count, "expected": EXPECTED_VERIFIED_ADAPTERS},
        )
        for role in TARGET_ROLES:
            capsule = capsule_by_id.get(role)
            add_check(report, f"generated capsule {role} exists", isinstance(capsule, dict))
            if not isinstance(capsule, dict):
                continue
            adapter = ((capsule.get("layers") or {}).get("interoperability") or {}).get("semantic_adapter")
            expected = semantic_rows.get(role)
            add_check(report, f"generated capsule {role} adapter verified", isinstance(adapter, dict) and adapter.get("status") == "verified")
            add_check(report, f"generated capsule {role} adapter parity", isinstance(expected, dict) and canonical(adapter) == canonical(expected))
            add_check(report, f"generated capsule {role} no tmp/outputs locator", not list(scan_forbidden(adapter or {})))
            add_check(report, f"generated capsule {role} has no private locator", not list(scan_forbidden(capsule)))
    if isinstance(capsule_manifest, dict):
        validate_generated_manifest_outputs(
            report, capsule_manifest, root / args.capsule_manifest
        )
        manifest_summary = capsule_manifest.get("summary", {})
        add_check(report, "generated manifest course count", manifest_summary.get("course_count") == EXPECTED_COURSE_CAPSULES, manifest_summary.get("course_count"))
        # The number 13 is the count of verified semantic adapter projections,
        # not the total number of course capsules (which remains 40).
        add_check(report, "generated manifest verified adapter count 13", manifest_summary.get("verified_semantic_adapter_count") == EXPECTED_VERIFIED_ADAPTERS, manifest_summary.get("verified_semantic_adapter_count"))

    report["metrics"] = {
        "clp_roles": list(TARGET_ROLES),
        "clp_route_actions": len(action_map),
        "expected_clp_route_actions": EXPECTED_SIDECAR_ACTIONS,
        "index_role_bindings": summary.get("role_bindings"),
        "expected_index_role_bindings": EXPECTED_ROLE_BINDINGS,
        "generated_course_capsules": len(capsules) if isinstance(capsules, list) else None,
        "expected_generated_course_capsules": EXPECTED_COURSE_CAPSULES,
        "generated_verified_semantic_capsules": (
            sum(
                1
                for row in capsules
                if isinstance(row, dict)
                and (((row.get("layers") or {}).get("interoperability") or {}).get("semantic_adapter") or {}).get("status") == "verified"
            )
            if isinstance(capsules, list)
            else None
        ),
        "generated_verified_semantic_adapters": (capsule_manifest or {}).get("summary", {}).get("verified_semantic_adapter_count") if isinstance(capsule_manifest, dict) else None,
        "expected_generated_verified_semantic_adapters": EXPECTED_VERIFIED_ADAPTERS,
    }
    report["repo"] = str(root)
    report["status"] = "pass" if not report["failures"] else "fail"
    # Avoid leaking an absolute workspace path in the JSON report while still
    # retaining deterministic file identities above.
    report["repo"] = "."
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
