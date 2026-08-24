#!/usr/bin/env python3
"""Export the living curriculum catalog as a strict common-backend v1 package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import uuid
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_NAME = "interlanguage-math-modular-backend"
SCHEMA_VERSION = "1.0.0"
WORKFLOW = "program-matematika-indonesia/backend-v1-exporter-1.0.0"


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


class Builder:
    def __init__(self, catalog: dict, namespace: uuid.UUID, table_names: list[str], catalog_path: Path, license_path: Path, metadata_notice_path: Path):
        self.catalog = catalog
        self.namespace = namespace
        self.tables: dict[str, list[dict]] = {name: [] for name in table_names}
        self.catalog_path = catalog_path
        self.catalog_sha = sha256_file(catalog_path)
        self.catalog_bytes = catalog_path.stat().st_size
        self.license_path = license_path
        self.license_sha = sha256_file(license_path)
        self.metadata_notice_path = metadata_notice_path
        self.metadata_notice_sha = sha256_file(metadata_notice_path)
        self.recorded_at = f"{catalog['snapshotDate']}T00:00:00Z"
        self.program_version = catalog["program"]["version"]
        self.source_commit = catalog["sourceCommit"]

    def rid(self, record_type: str, stable_key: str) -> str:
        return f"urn:uuid:{uuid.uuid5(self.namespace, f'{record_type}|{stable_key}')}"

    def base(self, record_type: str, stable_key: str, status: str = "active", **fields: object) -> dict:
        return {
            "id": self.rid(record_type, stable_key),
            "record_type": record_type,
            "recorded_at": self.recorded_at,
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "stable_key": stable_key,
            "status": status,
            "supersedes_id": None,
            "workflow_id": WORKFLOW,
            **fields,
        }

    def add(self, table: str, record: dict) -> str:
        self.tables[table].append(record)
        return record["id"]

    def relation(self, stable_key: str, from_id: str, to_id: str, relation_type: str, ordinal: int, locator: str, strength: str = "hard") -> str:
        return self.add(
            "relations",
            self.base(
                "relation",
                stable_key,
                assertion_method="direct_catalog_assertion",
                confidence="high",
                edition_id=self.hub_edition_id,
                from_id=from_id,
                ordinal=ordinal,
                relation_type=relation_type,
                source_locator=locator,
                strength=strength,
                to_id=to_id,
            ),
        )

    def build(self) -> dict:
        program = self.catalog["program"]
        github = program["repositories"]["github"]
        zenodo_record_id = program["zenodo"].rsplit(".", 1)[-1]

        self.rights_id = self.add(
            "rights",
            self.base(
                "rights",
                "program-matematika-indonesia:CC-BY-4.0-metadata",
                assertion_status="verified_from_local_notice",
                attribution="Program Matematika Indonesia",
                authority="Release notes state the curriculum descriptions and original metadata are CC BY 4.0.",
                change_notice="Identify modifications and preserve attribution.",
                license_expression="CC-BY-4.0",
                nonendorsement="No endorsement is implied for selected external resources.",
                notice_locator="README.md",
                notice_sha256=self.metadata_notice_sha,
                source_component_id="program-matematika-indonesia curriculum descriptions and original metadata",
                third_party_status="Selected corpora retain their own component rights; this grant covers hub metadata and software only.",
            ),
        )
        self.code_rights_id = self.add(
            "rights",
            self.base(
                "rights",
                "program-matematika-indonesia:MIT-code",
                assertion_status="verified_from_local_notice",
                attribution="Copyright holders of Program Matematika Indonesia",
                authority="LICENSE in the hub source tree",
                change_notice="Preserve the MIT notice.",
                license_expression="MIT",
                nonendorsement="No endorsement is implied.",
                notice_locator="LICENSE",
                notice_sha256=self.license_sha,
                source_component_id="program-matematika-indonesia software and schema tooling",
                third_party_status="External dependencies retain their own licenses.",
            ),
        )

        self.hub_resource_id = self.add(
            "resources",
            self.base(
                "resource",
                "program-matematika-indonesia",
                authority_policy="Hub metadata authority; corpus authority remains with each owning lane.",
                creator_name="Program Matematika Indonesia and the local Codex production workflows",
                # The learner-facing site is the reader. Zenodo is the durable
                # archive and must not be promoted ahead of the learning UI.
                official_reader=program["website"],
                official_repository=github["url"],
                original_title=program["title"],
                resource_key="program-matematika-indonesia",
                work_type="living_curriculum_hub",
                extensions={
                    "interlanguage.publication": {
                        "learner_start_url": program["website"],
                        "archive_url": program["zenodo"],
                        "github_status": github["status"],
                        "github_last_confirmed_at": github["lastConfirmedAt"],
                        "zenodo_concept": program["zenodoConcept"],
                    }
                },
            ),
        )

        self.hub_edition_id = self.add(
            "editions",
            self.base(
                "edition",
                f"program-matematika-indonesia:{self.program_version}",
                archive_sha256=None,
                commit_sha=self.source_commit,
                edition_kind="living_curriculum_snapshot",
                locale=program["language"],
                release_date=self.catalog["snapshotDate"],
                resource_id=self.hub_resource_id,
                rights_id=self.rights_id,
                source_edition_id=None,
                tree_sha=None,
                vcs_ref=self.source_commit,
                vcs_type="git",
                version_label=self.program_version,
            ),
        )

        program_id = self.add(
            "programs",
            self.base(
                "program",
                program["id"],
                curriculum_version=self.program_version,
                locale=program["language"],
                program_key=program["id"],
                rights_id=self.rights_id,
                title=program["title"],
                status=program["status"],
                extensions={
                    "interlanguage.curriculum": {
                        "completed_public_course_role_ids": program["completedPublicCourseRoleIds"],
                        "completed_public_record_dois": program["completedPublicRecordDois"],
                        "course_role_owner_lanes": {
                            course["id"]: course["ownerLane"] for course in self.catalog["courses"]
                        },
                        "selected_corpus_roles": program["selectedCorpusRoles"],
                        "total_course_roles": program["totalCourseRoles"],
                        "unresolved_role_ids": program["unresolvedRoleIds"],
                    }
                },
            ),
        )

        topic_ids: dict[str, str] = {}
        for topic in self.catalog["topics"]:
            topic_ids[topic] = self.add(
                "concepts",
                self.base(
                    "concept",
                    f"curriculum-topic:{topic}",
                    concept_key=topic,
                    concept_scheme="program-matematika-indonesia/topic-v1",
                    definition_segment_id=None,
                    parent_concept_id=None,
                ),
            )

        route_id = self.add(
            "routes",
            self.base(
                "route",
                f"{program['id']}:full-learning-direction:{self.program_version}",
                program_id=program_id,
                course_id=None,
                route_key="full-learning-direction",
                route_kind="complete_program_scaffold",
                locale=program["language"],
                title="Arah Pembelajaran Matematika Lengkap",
                description="Urutan lengkap empat puluh peran mata kuliah; prasyarat eksplisit tetap merupakan graf, bukan satu urutan linear paksa.",
                version_label=self.program_version,
            ),
        )

        course_ids: dict[str, str] = {}
        selected_resource_ids: dict[str, str] = {}
        unit_ids: dict[str, str] = {}
        segment_ids: dict[tuple[str, str], str] = {}
        variant_ids: dict[tuple[str, str], str] = {}

        for index, course in enumerate(self.catalog["courses"], start=1):
            course_key = course["id"]
            resource_key = f"selected-corpus:{course_key}"
            # Prefer the actual readable edition (HTML/PDF) over its archival
            # record. A DOI is preservation metadata, not a student start URL.
            reader = course.get("reader") or course.get("edition") or course.get("zenodo")
            repository = course.get("repository", "")
            selected_resource_ids[course_key] = self.add(
                "resources",
                self.base(
                    "resource",
                    resource_key,
                    authority_policy="Curriculum selection statement only; exact pinned source authority, rights, and build closure remain in the owning corpus lane.",
                    creator_name="See the selected corpus authority record",
                    official_reader=reader,
                    official_repository=repository,
                    original_title=course["corpus"],
                    resource_key=resource_key,
                    work_type="selected_curriculum_corpus",
                    status=course["state"],
                    extensions={
                        "interlanguage.curriculum-selection": {
                            "course_role_id": course_key,
                            "display_note": course["note"],
                            "learner_start_url": reader,
                            "owner_lane": course["ownerLane"],
                            "archive_url": course.get("zenodo"),
                            "zenodo": course.get("zenodo"),
                        }
                    },
                ),
            )
            course_ids[course_key] = self.add(
                "courses",
                self.base(
                    "course",
                    f"course:{course_key}",
                    course_key=course_key,
                    curriculum_source_locator=f"/courses/{index - 1}",
                    curriculum_source_sha256=self.catalog_sha,
                    order_key=f"{index:03d}",
                    outcome=course["outcome"],
                    prerequisite_course_keys=course["prerequisites"],
                    program_id=program_id,
                    resource_keys=[resource_key],
                    role=course_key,
                    scope=course["purpose"],
                    stage=course["level"],
                    title=course["title"],
                    status=course["state"],
                    extensions={
                        "interlanguage.curriculum-owner": {
                            "owner_lane": course["ownerLane"],
                        }
                    },
                ),
            )
            unit_ids[course_key] = self.add(
                "units",
                self.base(
                    "unit",
                    f"curriculum-course-role:{course_key}",
                    first_edition_id=self.hub_edition_id,
                    identity_anchor=course_key,
                    identity_basis="stable_curriculum_role_id",
                    resource_id=self.hub_resource_id,
                    rights_default_id=self.rights_id,
                    source_label=course["title"],
                    source_local_id=course_key,
                    source_path=f"releases/v{self.program_version}/program-matematika-indonesia-catalog-v{self.program_version}.json",
                    source_xml_path=None,
                    unit_kind="curriculum_course_role",
                    status=course["state"],
                ),
            )

            for ordinal, field in enumerate(("title", "purpose", "outcome", "corpus", "note"), start=1):
                stable = f"curriculum-course-role:{course_key}:{field}"
                segment_id = self.add(
                    "segments",
                    self.base(
                        "segment",
                        stable,
                        identity_anchor=f"{course_key}:{field}",
                        ordinal=ordinal,
                        segment_kind=f"curriculum_{field}",
                        segmentation_profile="program-catalog-v1",
                        unit_id=unit_ids[course_key],
                        status=course["state"],
                    ),
                )
                text = course[field]
                variant_id = self.add(
                    "segment_variants",
                    self.base(
                        "segment_variant",
                        f"{stable}:id-ID",
                        edition_id=self.hub_edition_id,
                        format="text/plain; charset=utf-8",
                        locale="id-ID",
                        payload=text,
                        payload_sha256=sha256_bytes(text.encode("utf-8")),
                        rights_id=self.rights_id,
                        role="original_id-ID_hub_expression",
                        segment_id=segment_id,
                        source_variant_id=None,
                        translation_state="original_authored_id-ID",
                        status=course["state"],
                    ),
                )
                segment_ids[(course_key, field)] = segment_id
                variant_ids[(course_key, field)] = variant_id

            self.add(
                "aliases",
                self.base(
                    "alias",
                    f"course:{course_key}:catalog-role-id",
                    edition_id=self.hub_edition_id,
                    entity_id=course_ids[course_key],
                    scheme="program-catalog-course-role-id",
                    scope=program["id"],
                    unique_in_scope=True,
                    value=course_key,
                ),
            )
            self.add(
                "route_members",
                self.base(
                    "route_member",
                    f"route:full-learning-direction:{course_key}",
                    route_id=route_id,
                    entity_id=course_ids[course_key],
                    ordinal=index,
                    order_path=f"{index:03d}",
                    role="course",
                    required=True,
                    inclusion_reason="Declared course role in the complete curriculum scaffold.",
                ),
            )

        relation_ordinal = 0
        for index, course in enumerate(self.catalog["courses"]):
            key = course["id"]
            relation_ordinal += 1
            self.relation(f"program-contains-course:{key}", program_id, course_ids[key], "contains", relation_ordinal, f"/courses/{index}")
            relation_ordinal += 1
            self.relation(f"course-has-topic:{key}", course_ids[key], topic_ids[course["topic"]], "classified_as", relation_ordinal, f"/courses/{index}/topic")
            relation_ordinal += 1
            self.relation(f"course-selects-resource:{key}", course_ids[key], selected_resource_ids[key], "selects_resource", relation_ordinal, f"/courses/{index}/corpus")
            relation_ordinal += 1
            self.relation(f"course-described-by-unit:{key}", course_ids[key], unit_ids[key], "described_by", relation_ordinal, f"/courses/{index}")
            for field_index, field in enumerate(("title", "purpose", "outcome", "corpus", "note"), start=1):
                relation_ordinal += 1
                self.relation(
                    f"unit-contains-segment:{key}:{field}",
                    unit_ids[key],
                    segment_ids[(key, field)],
                    "contains",
                    field_index,
                    f"/courses/{index}/{field}",
                )
            for prereq in course["prerequisites"]:
                relation_ordinal += 1
                self.relation(
                    f"course-prerequisite:{prereq}:{key}",
                    course_ids[prereq],
                    course_ids[key],
                    "prerequisite_for",
                    relation_ordinal,
                    f"/courses/{index}/prerequisites",
                )

        catalog_relative = f"releases/v{self.program_version}/program-matematika-indonesia-catalog-v{self.program_version}.json"
        file_id = self.add(
            "files",
            self.base(
                "file",
                "curriculum-catalog-json",
                canonical_path=catalog_relative,
                media_type="application/json",
                parse_mode="program-catalog-v1",
                resource_id=self.hub_resource_id,
                role="curriculum_authority_snapshot",
            ),
        )
        file_revision_id = self.add(
            "file_revisions",
            self.base(
                "file_revision",
                f"curriculum-catalog-json:{self.catalog_sha}",
                actual_path=catalog_relative,
                bytes=self.catalog_bytes,
                edition_id=self.hub_edition_id,
                file_id=file_id,
                generated=True,
                git_blob_sha1=None,
                sha256=self.catalog_sha,
                source_revision_id=None,
            ),
        )
        artifact_id = self.add(
            "artifacts",
            self.base(
                "artifact",
                f"curriculum-catalog-json:{self.program_version}",
                artifact_kind="curriculum_catalog_json",
                build_receipt=f"releases/v{self.program_version}/ZENODO_PUBLICATION_RECEIPT_v{self.program_version}.json",
                bytes=self.catalog_bytes,
                edition_id=self.hub_edition_id,
                locale="id-ID",
                manifest_sha256=None,
                public_uri=f"https://zenodo.org/records/{zenodo_record_id}/files/program-matematika-indonesia-catalog-v{self.program_version}.json?download=1",
                sha256=self.catalog_sha,
                toolchain_id="scripts/export-release-catalog.mjs",
                tree_sha256=None,
            ),
        )
        self.add(
            "release_snapshots",
            self.base(
                "release_snapshot",
                f"program-matematika-indonesia:{self.program_version}:zenodo-{zenodo_record_id}",
                edition_id=self.hub_edition_id,
                snapshot_kind="public_zenodo_version",
                release_version=self.program_version,
                release_date=self.catalog["snapshotDate"],
                commit_sha=self.source_commit,
                tree_sha=None,
                archive_sha256=None,
                artifact_ids=[artifact_id],
                publication_uri=program["zenodo"],
                immutable=True,
                status="published",
            ),
        )
        self.add(
            "build_recipes",
            self.base(
                "build_recipe",
                "curriculum-catalog-export-v1",
                resource_id=self.hub_resource_id,
                edition_id=self.hub_edition_id,
                name="Export the deterministic curriculum catalog",
                command=["node", "scripts/export-release-catalog.mjs", "<output.json>", self.source_commit],
                working_directory=".",
                input_ids=[file_revision_id],
                output_ids=[artifact_id],
                environment={"node": ">=22.13.0"},
                verification={"catalog_sha256": self.catalog_sha, "public_readback": "pass"},
            ),
        )
        self.add(
            "qa_events",
            self.base(
                "qa_event",
                f"curriculum-backend-v1-builder:{self.catalog_sha}",
                input_hash=self.catalog_sha,
                method="strict Draft 2020-12 validation, global ID closure, and byte-identical deterministic assembly replay",
                qa_type="backend_package_generation",
                result="builder_pass",
                reviewer_kind="deterministic_tool",
                severity_p1=0,
                severity_p2=0,
                severity_p3=0,
                tool_name="export-curriculum-backend-v1.py",
                tool_version="1.0.0",
                witness_locator="validation_report.json",
            ),
        )

        # The hub's MIT grant covers hub-authored metadata and software only.
        # External corpus rights remain separate in each owning corpus package.
        assignable = [
            record
            for table, records in self.tables.items()
            if table not in {"rights", "rights_assignments"}
            for record in records
            if record["record_type"] not in {"rights", "rights_assignment"}
        ]
        for record in assignable:
            assigned_rights_id = self.code_rights_id if record["record_type"] in {"build_recipe", "qa_event"} else self.rights_id
            self.add(
                "rights_assignments",
                self.base(
                    "rights_assignment",
                    f"hub-metadata-rights:{record['id']}",
                    assignment_status="compiled",
                    inheritance="direct_hub_metadata_assignment",
                    precedence=100,
                    rights_id=assigned_rights_id,
                    scope_role="software_record" if assigned_rights_id == self.code_rights_id else "record_metadata",
                    target_id=record["id"],
                ),
            )

        for records in self.tables.values():
            records.sort(key=lambda record: record["id"])
        return {
            "$schema": "schema/backend-v1.schema.json",
            "schema_name": SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "dataset_id": self.rid("dataset", f"{program['id']}:{self.program_version}"),
            "dataset_version": f"{program['id']}-v{self.program_version}-backend-v1",
            "tables": dict(sorted(self.tables.items())),
        }


def all_records(backend: dict) -> list[dict]:
    records = [record for rows in backend["tables"].values() for record in rows]
    return sorted(records, key=lambda record: (record["record_type"], record["id"]))


def check_closure(backend: dict) -> None:
    records = all_records(backend)
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        duplicates = [key for key, count in Counter(ids).items() if count > 1]
        raise ValueError(f"duplicate record IDs: {duplicates[:10]}")
    known = set(ids)
    for relation in backend["tables"]["relations"]:
        for field in ("from_id", "to_id"):
            if relation[field] not in known:
                raise ValueError(f"dangling relation endpoint {field}={relation[field]}")
    for member in backend["tables"]["route_members"]:
        if member["route_id"] not in known or member["entity_id"] not in known:
            raise ValueError(f"dangling route member {member['id']}")
    for assignment in backend["tables"]["rights_assignments"]:
        if assignment["rights_id"] not in known or assignment["target_id"] not in known:
            raise ValueError(f"dangling rights assignment {assignment['id']}")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(canonical(record) + "\n")


def write_lossless_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["id", "record_type", "record_json"])
        for record in records:
            writer.writerow([record["id"], record["record_type"], canonical(record)])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--namespace", required=True, type=Path)
    parser.add_argument("--source-profile-schema", required=True, type=Path)
    parser.add_argument("--license", required=True, type=Path)
    parser.add_argument("--metadata-notice", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    namespace_doc = json.loads(args.namespace.read_text(encoding="utf-8"))
    table_names = sorted(schema["properties"]["tables"]["properties"])
    namespace = uuid.UUID(namespace_doc["namespace"])

    builder_one = Builder(catalog, namespace, table_names, args.catalog, args.license, args.metadata_notice)
    backend = builder_one.build()
    builder_two = Builder(catalog, namespace, table_names, args.catalog, args.license, args.metadata_notice)
    replay = builder_two.build()
    if canonical(backend) != canonical(replay):
        raise ValueError("deterministic in-memory replay mismatch")
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(backend)
    check_closure(backend)

    if args.output.exists():
        shutil.rmtree(args.output)
    (args.output / "data").mkdir(parents=True)
    (args.output / "csv").mkdir(parents=True)
    (args.output / "schema").mkdir(parents=True)
    shutil.copyfile(args.schema, args.output / "schema" / "backend-v1.schema.json")
    shutil.copyfile(args.namespace, args.output / "schema" / "namespace.json")
    shutil.copyfile(args.source_profile_schema, args.output / "schema" / "source-format-profile-v1.schema.json")

    write_json(args.output / "backend.json", backend)
    records = all_records(backend)
    write_jsonl(args.output / "records.jsonl", records)
    write_lossless_csv(args.output / "records.csv", records)
    for table_name, rows in backend["tables"].items():
        write_jsonl(args.output / "data" / f"{table_name}.jsonl", rows)
        write_lossless_csv(args.output / "csv" / f"{table_name}.csv", rows)

    files = []
    for path in sorted(p for p in args.output.rglob("*") if p.is_file() and p.name != "manifest.json"):
        files.append(
            {
                "path": path.relative_to(args.output).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "schema_name": "interlanguage-math-modular-backend-package",
        "schema_version": SCHEMA_VERSION,
        "dataset_id": backend["dataset_id"],
        "dataset_version": backend["dataset_version"],
        "source": {
            "catalog_path": args.catalog.name,
            "catalog_bytes": args.catalog.stat().st_size,
            "catalog_sha256": sha256_file(args.catalog),
            "source_commit": catalog["sourceCommit"],
        },
        "identity_namespace": str(namespace),
        "record_count": len(records),
        "table_counts": {name: len(rows) for name, rows in backend["tables"].items()},
        "deterministic_replay": "byte-identical canonical assembly",
        "schema_validation": "pass",
        "closure_validation": "pass",
        "files": files,
    }
    write_json(args.output / "manifest.json", manifest)
    print(canonical({"output": str(args.output), "records": len(records), "tables": len(table_names), "manifest_sha256": sha256_file(args.output / "manifest.json")}))


if __name__ == "__main__":
    main()
