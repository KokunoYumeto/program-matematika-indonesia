#!/usr/bin/env python3
"""Prove a deterministic zero-copy Open Logic OLP-0722 backend-v1 migration.

The public release already contains a frozen 722-row source/target closure and
all Indonesian TeX payloads.  The frozen upstream commit supplies the matching
English payloads.  This program validates every byte against the release
inventory, constructs and strictly validates the common-backend records twice,
and writes only a compact migration receipt.  It does not duplicate the full
derived backend package on disk.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import uuid
import zipfile
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
WORKFLOW = "program-matematika-indonesia/openlogic-v1-migrator-1.0.0"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
RECORDED_AT = "2026-08-14T00:00:00Z"
SOURCE_COMMIT = "9620cc73f9c8e0ad003c514a5d3748f29611c4c0"
SOURCE_TREE = "f67757bb9305b173634082ab4cefd5601a707a34"
RELEASE_COMMIT = "34af65419e4c5c5580dae60a48454c485ddf504c"
RELEASE_TREE = "a7fcb6b970d9bafc82c36f51447931cf05a146cb"
RELEASE_VERSION = "OLP-0722-20260814"

EXPECTED_INPUTS = {
    "upstream": {
        "bytes": 1_899_150,
        "sha256": "ced94fb4617614404e828da9ca1d2c992be2fc1e1bc9204901d7a56fdb6eb930",
        "url": f"https://codeload.github.com/OpenLogicProject/OpenLogic/zip/{SOURCE_COMMIT}",
    },
    "localized_source": {
        "bytes": 1_580_716,
        "sha256": "492fd7369de367e2e748b0cbac8ba9a4c8c624f2a756a8943de445b9650283ed",
        "url": "https://zenodo.org/records/21932787/files/01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip?download=1",
    },
    "evidence": {
        "bytes": 2_000_807,
        "sha256": "273f790b9ddfaade9a6388c0d8cbd8b89006fca8f8c0da89cb2b5afcf1ae9441",
        "url": "https://zenodo.org/records/21932787/files/02_OPENLOGIC_id_EVIDENCE_AND_PROVENANCE_OLP-0722.zip?download=1",
    },
}

PUBLIC_ARTIFACTS = [
    {
        "name": "00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf",
        "bytes": 5_593_664,
        "sha256": "bf538d5e1994a7a7600703c9d24616696f77e43e9312fb51078095ff0c963c0a",
        "kind": "complete_linked_pdf_reader",
    },
    {
        "name": "01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip",
        "bytes": 1_580_716,
        "sha256": "492fd7369de367e2e748b0cbac8ba9a4c8c624f2a756a8943de445b9650283ed",
        "kind": "editable_source_archive",
    },
    {
        "name": "02_OPENLOGIC_id_EVIDENCE_AND_PROVENANCE_OLP-0722.zip",
        "bytes": 2_000_807,
        "sha256": "273f790b9ddfaade9a6388c0d8cbd8b89006fca8f8c0da89cb2b5afcf1ae9441",
        "kind": "evidence_and_provenance_archive",
    },
    {
        "name": "03_OPENLOGIC_id_SHA256_MANIFEST_OLP-0722.txt",
        "bytes": 401,
        "sha256": "d5b2f18fb24fd5469dafcb9ab91717b04a62d0fb437a68984b2c94ac254e9c60",
        "kind": "release_checksum_manifest",
    },
]


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def rid(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, f'{record_type}|{stable_key}')}"


def base(record_type: str, stable_key: str, status: str = "active", **fields: object) -> dict:
    return {
        "id": rid(record_type, stable_key),
        "record_type": record_type,
        "recorded_at": RECORDED_AT,
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "stable_key": stable_key,
        "status": status,
        "supersedes_id": None,
        "workflow_id": WORKFLOW,
        **fields,
    }


def read_zip_text(archive: zipfile.ZipFile, name: str) -> tuple[str, bytes]:
    data = archive.read(name)
    return data.decode("utf-8"), data


def csv_rows(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def verify_input(path: Path, label: str) -> dict:
    expected = EXPECTED_INPUTS[label]
    actual = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    if actual["bytes"] != expected["bytes"] or actual["sha256"] != expected["sha256"]:
        raise ValueError(f"{label} archive identity mismatch: {actual}")
    return {**actual, "public_url": expected["url"]}


def referenced_urns(value: object, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "extensions":
                continue
            yield from referenced_urns(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from referenced_urns(child, (*path, str(index)))
    elif isinstance(value, str) and value.startswith("urn:uuid:"):
        yield path, value


def build_backend(upstream_path: Path, localized_path: Path, evidence_path: Path, schema: dict, profile_schema: dict) -> tuple[dict, dict]:
    table_names = sorted(schema["properties"]["tables"]["properties"])
    tables: dict[str, list[dict]] = {name: [] for name in table_names}

    def add(table: str, record: dict) -> str:
        tables[table].append(record)
        return record["id"]

    with zipfile.ZipFile(upstream_path) as upstream, zipfile.ZipFile(localized_path) as localized, zipfile.ZipFile(evidence_path) as evidence:
        upstream_files = [name for name in upstream.namelist() if not name.endswith("/")]
        if not upstream_files:
            raise ValueError("empty upstream archive")
        upstream_root = upstream_files[0].split("/", 1)[0]

        closure_bytes = localized.read("SOURCE_CLOSURE_0722.csv")
        closure = csv_rows(closure_bytes)
        evidence_bytes = evidence.read("control/OPENLOGIC_CLOSURE_MANIFEST_20260812.csv")
        evidence_rows = csv_rows(evidence_bytes)
        evidence_by_id = {row["closure_id"]: row for row in evidence_rows}
        final_replay_bytes = evidence.read("release_evidence/COMPLETE_0722_CLOSURE_REPLAY.json")
        final_replay = json.loads(final_replay_bytes)
        qa_state_bytes = evidence.read("release_evidence/QA_STATE.json")
        qa_state = json.loads(qa_state_bytes)
        if len(closure) != 722 or len(evidence_by_id) != 722:
            raise ValueError(f"closure cardinality mismatch: {len(closure)} / {len(evidence_by_id)}")
        if [int(row["stable_order"]) for row in closure] != list(range(1, 723)):
            raise ValueError("closure stable_order is not exactly 1..722")
        if [row["closure_id"] for row in closure] != [f"OLP-{index:04d}" for index in range(1, 723)]:
            raise ValueError("closure IDs are not exactly OLP-0001..OLP-0722")

        license_bytes = localized.read("LICENSE")
        rights_id = add(
            "rights",
            base(
                "rights",
                "openlogic-project:cc-by-4.0",
                assertion_status="verified_from_frozen_release",
                attribution="Open Logic Project contributors; Indonesian translation and changes identified in the frozen release",
                authority="Frozen upstream and Indonesian release both state CC BY 4.0",
                change_notice="Retain attribution and identify translated/modified material.",
                license_expression="CC-BY-4.0",
                nonendorsement="No Open Logic Project endorsement is implied.",
                notice_locator="01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip!/LICENSE",
                notice_sha256=sha256_bytes(license_bytes),
                source_component_id="Open Logic Project OLP-0722 source and Indonesian translation",
                third_party_status="Component-level exceptions, if any, remain governed by the frozen source notices.",
            ),
        )
        resource_id = add(
            "resources",
            base(
                "resource",
                "openlogic-project",
                authority_policy=f"Frozen official upstream commit {SOURCE_COMMIT}; frozen Indonesian OLP-0722 release inventory.",
                creator_name="Open Logic Project contributors",
                official_reader="https://doi.org/10.5281/zenodo.21932787",
                official_repository="https://github.com/KokunoYumeto/OpenLogic-id",
                original_title="Open Logic Project / Open Logic Text",
                resource_key="openlogic-project",
                work_type="modular_logic_textbook_corpus",
                extensions={
                    "interlanguage.openlogic": {
                        "closure_ids": ["OLP-0001", "OLP-0722"],
                        "closure_rows": 722,
                        "canonical_reader_reachable": 642,
                        "retained_non_reader": 80,
                    }
                },
            ),
        )
        source_edition_id = add(
            "editions",
            base(
                "edition",
                f"openlogic-project:{SOURCE_COMMIT}:en",
                archive_sha256=EXPECTED_INPUTS["upstream"]["sha256"],
                commit_sha=SOURCE_COMMIT,
                edition_kind="frozen_upstream_source",
                locale="en",
                release_date=None,
                resource_id=resource_id,
                rights_id=rights_id,
                source_edition_id=None,
                tree_sha=SOURCE_TREE,
                vcs_ref=SOURCE_COMMIT,
                vcs_type="git",
                version_label=SOURCE_COMMIT,
            ),
        )
        target_edition_id = add(
            "editions",
            base(
                "edition",
                f"openlogic-id:{RELEASE_VERSION}",
                archive_sha256=EXPECTED_INPUTS["localized_source"]["sha256"],
                commit_sha=RELEASE_COMMIT,
                edition_kind="complete_indonesian_translation",
                locale="id-ID",
                release_date="2026-08-14",
                resource_id=resource_id,
                rights_id=rights_id,
                source_edition_id=source_edition_id,
                tree_sha=RELEASE_TREE,
                vcs_ref="id-olp-0722-20260814",
                vcs_type="git",
                version_label=RELEASE_VERSION,
            ),
        )

        unit_ids: dict[str, str] = {}
        source_path_unit: dict[str, str] = {}
        source_revision_ids: dict[str, str] = {}
        reader_reachable = 0
        target_total_bytes = 0
        source_total_bytes = 0
        source_crlf_materializations = 0
        historical_target_hash_mismatches = 0

        for row in closure:
            closure_id = row["closure_id"]
            detail = evidence_by_id.get(closure_id)
            if detail is None:
                raise ValueError(f"missing evidence row {closure_id}")
            for field in ("stable_order", "source_commit", "source_path", "source_sha256", "source_bytes", "target_path"):
                if row[field].lower() != detail[field].lower():
                    raise ValueError(f"closure/evidence mismatch {closure_id}:{field}")
            if row["target_sha256"].lower() != detail["target_sha256"].lower() or row["target_bytes"] != detail["target_bytes"]:
                historical_target_hash_mismatches += 1

            source_name = f"{upstream_root}/{row['source_path']}"
            target_name = f"source/{row['target_path']}"
            source_blob = upstream.read(source_name)
            source_data = source_blob
            target_data = localized.read(target_name)
            if len(source_data) != int(row["source_bytes"]) or sha256_bytes(source_data) != row["source_sha256"].lower():
                # The frozen production witness was checked out on Windows and
                # records CRLF worktree bytes.  GitHub codeload correctly
                # exposes the LF Git blobs.  Reproduce only that declared EOL
                # materialization and require the frozen hash to match exactly.
                lf_blob = source_blob.replace(b"\r\n", b"\n")
                materialized = lf_blob.replace(b"\n", b"\r\n")
                if len(materialized) != int(row["source_bytes"]) or sha256_bytes(materialized) != row["source_sha256"].lower():
                    raise ValueError(f"source byte identity mismatch {closure_id}")
                source_data = materialized
                source_crlf_materializations += 1
            source_text = source_data.decode("utf-8")
            target_text = target_data.decode("utf-8")
            if len(target_data) != int(row["target_bytes"]) or sha256_bytes(target_data) != row["target_sha256"].lower():
                raise ValueError(f"target byte identity mismatch {closure_id}")
            if len(source_text.splitlines()) != int(row["source_lines"]) or len(target_text.splitlines()) != int(row["target_lines"]):
                raise ValueError(f"line count mismatch {closure_id}")
            source_total_bytes += len(source_data)
            target_total_bytes += len(target_data)

            file_id = add(
                "files",
                base(
                    "file",
                    f"openlogic:{closure_id}:file",
                    canonical_path=row["source_path"],
                    media_type="application/x-tex",
                    parse_mode="openlogic-latex-module",
                    resource_id=resource_id,
                    role=detail.get("source_role") or "latex_module",
                    extensions={"interlanguage.openlogic": {"closure_id": closure_id, "target_path": row["target_path"]}},
                ),
            )
            source_revision_id = add(
                "file_revisions",
                base(
                    "file_revision",
                    f"openlogic:{closure_id}:source:{row['source_sha256'].lower()}",
                    actual_path=row["source_path"],
                    bytes=len(source_data),
                    edition_id=source_edition_id,
                    file_id=file_id,
                    generated=False,
                    git_blob_sha1=git_blob_sha1(source_blob),
                    sha256=row["source_sha256"].lower(),
                    source_revision_id=None,
                    extensions={
                        "interlanguage.openlogic": {
                            "git_blob_bytes": len(source_blob),
                            "git_blob_sha256": sha256_bytes(source_blob),
                            "checkout_materialization": "CRLF" if source_data != source_blob else "identity",
                        }
                    },
                ),
            )
            target_revision_id = add(
                "file_revisions",
                base(
                    "file_revision",
                    f"openlogic:{closure_id}:target:{row['target_sha256'].lower()}",
                    actual_path=row["target_path"],
                    bytes=len(target_data),
                    edition_id=target_edition_id,
                    file_id=file_id,
                    generated=False,
                    git_blob_sha1=git_blob_sha1(target_data),
                    sha256=row["target_sha256"].lower(),
                    source_revision_id=source_revision_id,
                ),
            )
            source_revision_ids[closure_id] = source_revision_id
            unit_id = add(
                "units",
                base(
                    "unit",
                    f"openlogic:{closure_id}",
                    first_edition_id=source_edition_id,
                    identity_anchor=closure_id,
                    identity_basis="frozen OLP closure ID and source path",
                    resource_id=resource_id,
                    rights_default_id=rights_id,
                    source_label=detail.get("source_title_locator") or closure_id,
                    source_local_id=closure_id,
                    source_path=row["source_path"],
                    source_xml_path=None,
                    unit_kind=detail.get("source_role") or "latex_module",
                    extensions={
                        "interlanguage.openlogic": {
                            "stable_order": int(row["stable_order"]),
                            "canonical_reader_reachable": detail.get("canonical_reader_reachable", "").lower() == "true",
                            "inclusion_class": detail.get("inclusion_class"),
                            "source_olfileid": detail.get("source_olfileid") or None,
                            "environment_total": int(detail.get("environment_total") or 0),
                            "math_segment_count": int(detail.get("math_segment_count") or 0),
                        }
                    },
                ),
            )
            unit_ids[closure_id] = unit_id
            source_path_unit[row["source_path"]] = unit_id
            if detail.get("canonical_reader_reachable", "").lower() == "true":
                reader_reachable += 1

            segment_id = add(
                "segments",
                base(
                    "segment",
                    f"openlogic:{closure_id}:whole-file",
                    identity_anchor=closure_id,
                    ordinal=1,
                    segment_kind="latex_module_file",
                    segmentation_profile="openlogic-olp-closure-file-v1",
                    unit_id=unit_id,
                    extensions={
                        "interlanguage.source-profile": {
                            "format_profile": "latex",
                            "profile_version": "1.0.0",
                            "authority_file_revision_id": source_revision_id,
                            "authority_path": row["source_path"],
                            "identity_strategy": "source_order",
                            "active_source_path": row["source_path"],
                            "include_stack": [value for value in detail.get("incoming_importers", "").split("|") if value],
                            "macro_context_sha256": None,
                            "conditional_state": "active",
                            "environment": detail.get("source_role") or None,
                            "label": detail.get("source_olfileid") or None,
                            "references": [],
                            "external_documents": [],
                            "aux_dependencies": [value for value in detail.get("imports_resolved_ordered", "").split("|") if value],
                            "includegraphics_resolution": None,
                            "toolchain_dependencies": ["LuaLaTeX", "Open Logic TeX macros"],
                            "raw_start_byte": 0,
                            "raw_end_byte": len(source_data),
                            "raw_slice_sha256": row["source_sha256"].lower(),
                        }
                    },
                ),
            )
            source_variant_id = add(
                "segment_variants",
                base(
                    "segment_variant",
                    f"openlogic:{closure_id}:source-en",
                    edition_id=source_edition_id,
                    format="text/x-tex",
                    locale="en",
                    payload=source_text,
                    payload_sha256=row["source_sha256"].lower(),
                    rights_id=rights_id,
                    role="source",
                    segment_id=segment_id,
                    source_variant_id=None,
                    translation_state="source_authority",
                ),
            )
            add(
                "segment_variants",
                base(
                    "segment_variant",
                    f"openlogic:{closure_id}:target-id-ID",
                    edition_id=target_edition_id,
                    format="text/x-tex",
                    locale="id-ID",
                    payload=target_text,
                    payload_sha256=row["target_sha256"].lower(),
                    rights_id=rights_id,
                    role="translation",
                    segment_id=segment_id,
                    source_variant_id=source_variant_id,
                    translation_state="translated_frozen",
                    extensions={"interlanguage.openlogic": {"target_file_revision_id": target_revision_id}},
                ),
            )

        if source_total_bytes != 3_051_826 or target_total_bytes != 3_222_301 or reader_reachable != 642:
            raise ValueError(
                f"aggregate closure mismatch source={source_total_bytes} target={target_total_bytes} reader={reader_reachable}"
            )

        module_id = add(
            "modules",
            base(
                "module",
                f"openlogic:{RELEASE_VERSION}:complete-closure",
                closure_profile="all 722 frozen OLP modules; reader reachability is a separate attribute",
                description="Complete modular Indonesian Open Logic corpus, including 642 reader-reachable and 80 retained non-reader modules.",
                edition_id=target_edition_id,
                locale="id-ID",
                manifest_sha256=sha256_bytes(closure_bytes),
                module_kind="complete_configured_corpus",
                module_version=RELEASE_VERSION,
                root_unit_id=unit_ids["OLP-0001"],
                title="Open Logic Project — Edisi Lengkap Bahasa Indonesia",
            ),
        )
        for row in closure:
            closure_id = row["closure_id"]
            detail = evidence_by_id[closure_id]
            add(
                "module_members",
                base(
                    "module_member",
                    f"openlogic:{RELEASE_VERSION}:member:{closure_id}",
                    entity_id=unit_ids[closure_id],
                    inclusion_reason=detail.get("inclusion_reason") or "Frozen complete-corpus closure",
                    module_id=module_id,
                    order_path=f"{int(row['stable_order']):04d}",
                    required=True,
                    role="reader_module" if detail.get("canonical_reader_reachable", "").lower() == "true" else "retained_non_reader_module",
                ),
            )

        replay_counts = final_replay.get("counts", {})
        replay_results = final_replay.get("results", {})
        for field in (
            "missing_targets",
            "source_hash_mismatches",
            "target_inventory_hash_mismatches",
            "control_character_files",
            "brace_delta_mismatches",
            "localized_olfileid_policy_failures",
        ):
            if replay_counts.get(field) != 0 or replay_results.get(field) != []:
                raise ValueError(f"final closure replay does not pass {field}")
        if qa_state.get("version") != RELEASE_VERSION or qa_state.get("source_replay", {}).get("rows") != 722:
            raise ValueError("final QA state identity mismatch")
        add(
            "qa_events",
            base(
                "qa_event",
                f"openlogic:{RELEASE_VERSION}:complete-release-qa",
                input_hash=sha256_bytes(closure_bytes),
                method="Final 722-row source/target hash replay plus complete reader build, text-layer checks, and 1,116-page render inspection",
                qa_type="complete_release_closure",
                result="pass_with_explicit_nonblocking_disclosures",
                reviewer_kind="mixed_deterministic_and_documented_ai_review",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name="OpenLogic OLP-0722 closure workflow",
                tool_version=RELEASE_VERSION,
                witness_locator="02_OPENLOGIC_id_EVIDENCE_AND_PROVENANCE_OLP-0722.zip!/release_evidence/QA_STATE.json",
                extensions={
                    "interlanguage.openlogic": {
                        "module_id": module_id,
                        "closure_replay_sha256": sha256_bytes(final_replay_bytes),
                        "qa_state_sha256": sha256_bytes(qa_state_bytes),
                        "translation_writer_batch_checks": "722/722",
                        "retained_independent_batch_receipts_through": "OLP-0321",
                        "later_units_without_equivalent_retained_independent_receipts": 401,
                        "reviewed_active_environment_difference_files": replay_counts.get("active_environment_sequence_differences"),
                        "reviewed_reference_label_import_difference_files": replay_counts.get("reference_label_citation_import_asset_sequence_differences"),
                        "reviewed_semantic_token_difference_files": replay_counts.get("semantic_token_base_sequence_differences"),
                        "reader_pages": qa_state.get("reader_pages"),
                        "rendered_pages_inspected": qa_state.get("rendered_inspection", {}).get("pages_inspected"),
                        "accessibility_claim": qa_state.get("accessibility", {}).get("claim"),
                    }
                },
            ),
        )

        relation_count = 0
        for row in closure:
            detail = evidence_by_id[row["closure_id"]]
            imports = [value for value in detail.get("imports_resolved_ordered", "").split("|") if value]
            if len(imports) != int(detail.get("import_count") or 0):
                raise ValueError(f"import count mismatch {row['closure_id']}")
            for ordinal, target_path in enumerate(imports, start=1):
                if target_path not in source_path_unit:
                    raise ValueError(f"resolved import outside closure {row['closure_id']} -> {target_path}")
                add(
                    "relations",
                    base(
                        "relation",
                        f"openlogic:{row['closure_id']}:imports:{ordinal}:{target_path}",
                        assertion_method="frozen_import_graph",
                        confidence="high",
                        edition_id=target_edition_id,
                        from_id=unit_ids[row["closure_id"]],
                        ordinal=ordinal,
                        relation_type="imports",
                        source_locator=f"{row['source_path']}:olimport",
                        strength="hard",
                        to_id=source_path_unit[target_path],
                    ),
                )
                relation_count += 1

        artifact_ids = []
        checksum_sha = PUBLIC_ARTIFACTS[-1]["sha256"]
        for artifact in PUBLIC_ARTIFACTS:
            artifact_ids.append(
                add(
                    "artifacts",
                    base(
                        "artifact",
                        f"openlogic:{RELEASE_VERSION}:{artifact['name']}",
                        artifact_kind=artifact["kind"],
                        build_receipt="02_OPENLOGIC_id_EVIDENCE_AND_PROVENANCE_OLP-0722.zip!/release_evidence",
                        bytes=artifact["bytes"],
                        edition_id=target_edition_id,
                        locale="id-ID",
                        manifest_sha256=checksum_sha,
                        public_uri=f"https://zenodo.org/records/21932787/files/{artifact['name']}?download=1",
                        sha256=artifact["sha256"],
                        toolchain_id="OpenLogic OLP-0722 release workflow",
                        tree_sha256=None,
                    ),
                )
            )
        for platform, uri in (
            ("zenodo", "https://doi.org/10.5281/zenodo.21932787"),
            ("github", "https://github.com/KokunoYumeto/OpenLogic-id/releases/tag/id-olp-0722-20260814"),
        ):
            add(
                "release_snapshots",
                base(
                    "release_snapshot",
                    f"openlogic:{RELEASE_VERSION}:{platform}",
                    archive_sha256=None,
                    artifact_ids=artifact_ids,
                    commit_sha=RELEASE_COMMIT,
                    edition_id=target_edition_id,
                    immutable=True,
                    publication_uri=uri,
                    release_date="2026-08-14",
                    release_version=RELEASE_VERSION,
                    snapshot_kind=f"public_{platform}_release",
                    tree_sha=RELEASE_TREE,
                    status="published",
                ),
            )
        add(
            "build_recipes",
            base(
                "build_recipe",
                f"openlogic:{RELEASE_VERSION}:reader-build",
                command=["pwsh", "-File", "build/BUILD.ps1"],
                edition_id=target_edition_id,
                environment={"engine": "LuaLaTeX", "source_archive": "01_OPENLOGIC_id_EDITABLE_SOURCES_OLP-0722.zip"},
                input_ids=[module_id],
                name="Build the complete linked Indonesian reader",
                output_ids=[artifact_ids[0]],
                resource_id=resource_id,
                verification={"pages": 1116, "pdf_sha256": PUBLIC_ARTIFACTS[0]["sha256"], "all_page_render_review": "pass"},
                working_directory="source",
            ),
        )

        assignment_targets = [resource_id, source_edition_id, target_edition_id, module_id, *artifact_ids]
        for target_id in assignment_targets:
            add(
                "rights_assignments",
                base(
                    "rights_assignment",
                    f"openlogic:cc-by-4.0:{target_id}",
                    assignment_status="compiled_from_frozen_release",
                    inheritance="direct_or_default_component_assignment",
                    precedence=100,
                    rights_id=rights_id,
                    scope_role="source_translation_and_release_metadata",
                    target_id=target_id,
                ),
            )

        for records in tables.values():
            records.sort(key=lambda record: record["id"])
        backend = {
            "$schema": "schema/backend-v1.schema.json",
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "dataset_id": rid("dataset", f"openlogic-id:{RELEASE_VERSION}"),
            "dataset_version": f"openlogic-id-{RELEASE_VERSION}-backend-v1",
            "tables": dict(sorted(tables.items())),
        }
        profile_validator = Draft202012Validator(profile_schema, format_checker=FormatChecker())
        profile_count = 0
        for records in tables.values():
            for record in records:
                profile = record.get("extensions", {}).get("interlanguage.source-profile")
                if profile is not None:
                    profile_validator.validate(profile)
                    profile_count += 1
        diagnostics = {
            "closure_manifest_bytes": len(closure_bytes),
            "closure_manifest_sha256": sha256_bytes(closure_bytes),
            "evidence_manifest_bytes": len(evidence_bytes),
            "evidence_manifest_sha256": sha256_bytes(evidence_bytes),
            "source_content_bytes": source_total_bytes,
            "target_content_bytes": target_total_bytes,
            "source_crlf_materializations": source_crlf_materializations,
            "historical_manifest_target_hash_mismatches": historical_target_hash_mismatches,
            "reader_reachable": reader_reachable,
            "retained_non_reader": len(closure) - reader_reachable,
            "import_relations": relation_count,
            "validated_source_profiles": profile_count,
            "final_closure_replay_bytes": len(final_replay_bytes),
            "final_closure_replay_sha256": sha256_bytes(final_replay_bytes),
            "final_qa_state_bytes": len(qa_state_bytes),
            "final_qa_state_sha256": sha256_bytes(qa_state_bytes),
        }
        return backend, diagnostics


def validate_backend(backend: dict, schema: dict) -> dict:
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(backend)
    records = sorted(
        [record for rows in backend["tables"].values() for record in rows],
        key=lambda record: (record["record_type"], record["id"]),
    )
    ids = [record["id"] for record in records]
    duplicates = [value for value, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"duplicate IDs: {duplicates[:10]}")
    known = set(ids)
    allowed_external = {"supersedes_id", "source_edition_id", "source_revision_id", "source_variant_id", "source_occurrence_id"}
    dangling = []
    for record in records:
        for field_path, value in referenced_urns(record):
            if field_path == ("id",):
                continue
            leaf = field_path[-1] if field_path else ""
            if leaf in allowed_external and value not in known:
                continue
            if value not in known:
                dangling.append({"record": record["id"], "field": "/".join(field_path), "value": value})
    if dangling:
        raise ValueError(f"dangling references: {dangling[:10]}")
    payload = b"".join((canonical(record) + "\n").encode("utf-8") for record in records)
    return {
        "record_count": len(records),
        "table_count": len(backend["tables"]),
        "nonempty_table_count": sum(bool(rows) for rows in backend["tables"].values()),
        "table_counts": {name: len(rows) for name, rows in backend["tables"].items()},
        "global_unique_ids": len(known),
        "foreign_key_closure": "pass",
        "strict_schema": "pass",
        "virtual_records_jsonl_bytes": len(payload),
        "virtual_records_jsonl_sha256": sha256_bytes(payload),
        "table_sha256": {
            name: sha256_bytes(b"".join((canonical(row) + "\n").encode("utf-8") for row in rows))
            for name, rows in backend["tables"].items()
        },
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-zip", required=True, type=Path)
    parser.add_argument("--localized-source-zip", required=True, type=Path)
    parser.add_argument("--evidence-zip", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--source-profile-schema", required=True, type=Path)
    parser.add_argument("--output-receipt", required=True, type=Path)
    args = parser.parse_args()

    inputs = {
        "upstream": verify_input(args.upstream_zip, "upstream"),
        "localized_source": verify_input(args.localized_source_zip, "localized_source"),
        "evidence": verify_input(args.evidence_zip, "evidence"),
    }
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    profile_schema = json.loads(args.source_profile_schema.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(profile_schema)

    first, diagnostics = build_backend(
        args.upstream_zip, args.localized_source_zip, args.evidence_zip, schema, profile_schema
    )
    first_validation = validate_backend(first, schema)
    second, second_diagnostics = build_backend(
        args.upstream_zip, args.localized_source_zip, args.evidence_zip, schema, profile_schema
    )
    second_validation = validate_backend(second, schema)
    first_hash = sha256_bytes(canonical(first).encode("utf-8"))
    second_hash = sha256_bytes(canonical(second).encode("utf-8"))
    if first_hash != second_hash or diagnostics != second_diagnostics or first_validation != second_validation:
        raise ValueError("two independent in-memory assemblies are not byte-identical")

    receipt = {
        "schema_name": "interlanguage-math-modular-backend-migration-receipt",
        "schema_version": SCHEMA_VERSION,
        "migration_id": "openlogic-id-olp-0722-to-interlanguage-v1.0.0",
        "migration_mode": "deterministic-zero-copy-source-target-reconstruction",
        "source": {
            "work": "Open Logic Project / Open Logic Text",
            "source_commit": SOURCE_COMMIT,
            "source_tree": SOURCE_TREE,
            "target_release_commit": RELEASE_COMMIT,
            "target_release_tree": RELEASE_TREE,
            "target_release_version": RELEASE_VERSION,
            "target_version_doi": "10.5281/zenodo.21932787",
            "target_concept_doi": "10.5281/zenodo.21932786",
            "inputs": inputs,
        },
        "target": {
            "dataset_id": first["dataset_id"],
            "dataset_version": first["dataset_version"],
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "schema_path": args.schema.as_posix(),
            "schema_bytes": args.schema.stat().st_size,
            "schema_sha256": sha256_file(args.schema),
            "source_profile_schema_path": args.source_profile_schema.as_posix(),
            "source_profile_schema_bytes": args.source_profile_schema.stat().st_size,
            "source_profile_schema_sha256": sha256_file(args.source_profile_schema),
            **first_validation,
        },
        "coverage": diagnostics,
        "transformation": {
            "source_files_verified": 722,
            "target_files_verified": 722,
            "source_payload_bytes_changed": 0,
            "target_payload_bytes_changed": 0,
            "source_or_target_paths_changed": 0,
            "closure_ids_changed": 0,
            "derived_identity_algorithm": "UUIDv5(namespace, record_type|stable_key)",
            "derived_records_materialized": False,
            "reason_not_materialized": "The three small frozen public inputs plus this deterministic script reconstruct the validated package exactly without redundant multi-projection storage.",
        },
        "validation": {
            "result": "pass",
            "input_filename_size_sha256": "pass",
            "722_source_hashes_and_lengths": "pass",
            "722_target_hashes_and_lengths": "pass",
            "aggregate_source_and_target_bytes": "pass",
            "strict_backend_schema": "pass",
            "strict_source_profile_schema": "pass",
            "global_id_uniqueness": "pass",
            "foreign_key_closure": "pass",
            "two_independent_assemblies": "byte-identical",
            "canonical_backend_sha256": first_hash,
        },
        "public_artifacts": PUBLIC_ARTIFACTS,
        "credentials_recorded": False,
    }
    write_json(args.output_receipt, receipt)
    print(
        canonical(
            {
                "result": "pass",
                "records": first_validation["record_count"],
                "tables": first_validation["table_count"],
                "receipt": str(args.output_receipt),
                "receipt_sha256": sha256_file(args.output_receipt),
            }
        )
    )


if __name__ == "__main__":
    main()
