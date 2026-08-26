#!/usr/bin/env python3
"""Build the read-only C100 geometry v2.1 pilot.

The pilot preserves the owner-native hierarchy, exercises, and hints as stable
addressable units.  It materializes only compact metadata and relations; the
validated textbook prose stays in the owner tree and is served separately as
an exact two-file semantic-HTML reader.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import unicodedata
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


SCHEMA_ID = "interlanguage/global-backend-v2.1-unit-search-pilot/0.1.0"
RECORDED_AT = "2026-08-26T00:00:00Z"
PROGRAM_ROOT = Path(__file__).resolve().parents[3]
PILOTS_ROOT = Path(__file__).resolve().parent
OWNER_ROOT = PROGRAM_ROOT.parent
C100_ROOT = OWNER_ROOT / "foundations-of-geometry-id"
C100_BACKEND = C100_ROOT / "backend"
ACCESSIBLE = C100_ROOT / "accessible" / "id-ID"
UPSTREAM = C100_ROOT / "source" / "upstream" / "birkhoff-0b0858e1e985f4c8dadbb6075ae9e095cd4a8981"
TARGET = C100_ROOT / "source" / "id-ID"
SOLUTIONS = C100_ROOT / "solutions" / "id-ID"
SOLUTION_RECEIPT = SOLUTIONS / "QA_RECEIPT_CUMULATIVE_CH01_20.json"
SOLUTION_PDF = SOLUTIONS / "output" / "pdf" / "SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf"
PUBLICATION_RECEIPT = C100_ROOT / "00_control" / "ZENODO_PUBLICATION_COMPLETE_COURSE_OPEN_20260825.json"
OUT = PILOTS_ROOT / "c100-geometry"

EXPECTED = {
    "catalog": (740567, "0c06319b7fa5a9dc28fae94be628ad44fa23f8c160be8e93d0e902c1325e02c2"),
    "schema": (1873, "7b7dc93183d776c154ab71b94161a27433f255572d470c4fa2e5399fdf88a8c2"),
    "unit_order": (9824, "6bdb6327096dbd1cfc7a7533bf3e3811d415660f2fcb857721910319560a749e"),
    "exercise_hints": (33676, "109ee0cd64f3cdb07d83a1f047e86df8068cb3389729b7dd614602f08962f43c"),
    "manifest": (227419, "9abcf47b5f452985fad2e7014c4b81ceca0adbf9ac47da05f1acb8d062af5452"),
    "receipt": (15411, "bed9576202445d50ee269b1319902f53c0dab945f91d60a0651ae2c2b252bc2d"),
    "validator": (171015, "d46ad89f0ac00cfb0e9e10d5a6bbf518968e5903dc3c661d7277ac7084f40451"),
    "html": (3994608, "1d3b49bc17a5956164d25b53ef6a2e79939a44f066fa87d84d00a66cca6da7ca"),
    "style": (5098, "553a606757f117c9edefb0c5c339d490fd55cefd9c10b40e4d60774c30e32887"),
    "publication_receipt": (6883, "7217c1ca89d398447adc23e108fa40aa5ceef1622d605bdd48f2bf9518dc6a14"),
    "solution_receipt": (35401, "aa56b2f12dbc3250b94691c6eb2344d35096f47f40da1c59ae326caa912d5212"),
    "solution_pdf": (2698925, "01b618884353905e5be06ac7c85249f2aa0b127687a7e93038f5b65d5fddcdc7"),
}

SOLUTION_MANIFEST_EXPECTED = {
    1: (21591, "351406d66b912946548bd2b1b570310767dca9234606a17f731d4002ed796967"),
    2: (13216, "a3fa66020c154e96f99a92708556c0e94cf223f69366016c55feeb0369c4f2c1"),
    3: (13152, "a92c375a4b367a743ba9e931983b3032b61869c0f0894247a048d0bdd2a6c193"),
    4: (9879, "2703fade169e200bdd9e7b26b3609c11389ee81d4ff1eaa0fc9f60cda8cc3d4f"),
    5: (28022, "93eea0d421155351ccd8ec387634b11ee28666eb2ce94912e848a81e9f129f83"),
    6: (15917, "cc7a69007f806112c70dc898d28b3a8ded567707718ce6d4d6ce832980698d11"),
    7: (36450, "41a8c3c7f9f44774b8e0a38668036a291d8577671a4aebf8b2948d5e99bde444"),
    8: (26251, "983bc6edf452db0610b254be37a5fd6ed3bb5864c24049ab6a09551d029e72bb"),
    9: (40079, "27da1174fa180aa2edad93684c00082a6af5e6d708cf1f4bcff3b58482805a6a"),
    10: (28860, "190097f39be6cd67fa61d0e503c43479253bdabed8744a4005876793845b1c40"),
    11: (24156, "cf43f4aee0bd0246ca70f5e7eda1652b08282cce7befc77ce843dcb159f89830"),
    12: (23057, "085632b26876e7eaada3444686bfcce52d230ed1f32c70e47ad3d3bd35cefdc0"),
    13: (20923, "e20dba6bbc9f6fbface6cfa6a80d5afff05d6cffdc3c87fc51f3d264294b9b07"),
    14: (26054, "ff7c3f6d2d2f2f1385ad38d03dd41fbba9e9e6429addc07ae12bcd76ef3ad843"),
    15: (26474, "1808e48910a328d10adaece4513a38aaef0ad872f951e1d954d9681040c99c18"),
    16: (19150, "cf46203b1368aef1d8f10b1f15f743007ff875c803505fa2f30d6c3755f53243"),
    17: (20364, "a89df10babfeae7fb3323f9bfb2a932355968b3c67142e880cf3d9f374c43c26"),
    18: (29205, "b4b114b4480626b75c18c22483648df6f757f178997d5987d41d50426d6c372a"),
    19: (23646, "3a8956cc7f6eb3b5d4e46e579908262901c1fd38f6156ab92f3fc1173f8b76bb"),
    20: (19959, "2769bc250d3727fb67a45007a649bd88faf647a5fafde0307fa940ae1a14f646"),
}

SOLUTION_TEX_EXPECTED = {
    1: (40030, "ffa1cf3170800ebd61f4a4f180724c4aaf90fe87c44ba863c3178f12a3ecb09c"),
    2: (23587, "fb8a5abc742e7c3f87bb8172434342033d3aea13baf4bf519b5b7d3cd0faf8e7"),
    3: (32146, "5557fbf2e7a148860b70816efa745a39ea670b494d7327d5db2872e051d25be8"),
    4: (21756, "5e4f444e8b1242f75fde98e7b8c0b1e6e499940fee196223dcd9c86262176502"),
    5: (42816, "6fdb190a592d6f7fa9b0c170dcbc7d5b20ec3fa36e1abea14f4f96838e7f46b0"),
    6: (20846, "517c732cc86df0c9d02f0f23a7a7af3c003f1fed63b2163878adbaeac36e638b"),
    7: (51769, "3702222f7b30a0b9eebb115b70b85d0d8fdf639bbe0c01b791df9541fe4324ab"),
    8: (37197, "bc4659a219640aff869d3762a85500c3c36cc9acf70866c9bfe431832720d392"),
    9: (62378, "176c390432a79e7d1d904cebdc853abccb63fb20eb561bc2fcd4dacf4bbc5a52"),
    10: (49845, "497a42b5c0247e58168444ecf1ba3e552f76e13bc294a1f118b6113801846ae2"),
    11: (43515, "12c07b6095ddd3173e613c00604b48398647c1f256d7ee066e58452700a8a138"),
    12: (40680, "ee1bb5bd441cbcc249dc4ec0d4f6cd4459f70618e796f5fcf601aba020796041"),
    13: (40814, "11e629cfc9c79bff519a80a15a4741c95933144fb2a8ad3e4bf142ce18b98226"),
    14: (54388, "40e2c4f22a5281a5269509598f56982c25d14683990d6b3c9c38dadabb5e8804"),
    15: (56260, "9c4e30cf1a1d62b536442ec3a34a3b5a872dfae9874d7f611fa8ec1c1d6d0122"),
    16: (37376, "24fc4d334a25456f1e82945a8b0413057af17647815f8ce2959fe36308153d39"),
    17: (40576, "5745ab46d387f970094b2481c623a88db2d9a8b8f829c8be6528623dbeb11692"),
    18: (49848, "59c80f2b5c2bfdc90c5669b0afff66a16f19ab2383ecb7b741f15d061693b17c"),
    19: (40590, "bcf65867f8b95ef08c179c8e426bf5f86f293fd984772497646f1f47d9accd05"),
    20: (55623, "9da4f1621f7cb730b3d9c9ebab031c85411e3f1c846d270505da2ac56abfcc36"),
}

AUTHORITIES = {
    "catalog": C100_BACKEND / "catalog-v0.json",
    "schema": C100_BACKEND / "schema-v0.json",
    "unit_order": C100_BACKEND / "unit-order-v0.csv",
    "exercise_hints": C100_BACKEND / "exercise-hints-v0.csv",
    "manifest": ACCESSIBLE / "manifest.json",
    "receipt": ACCESSIBLE / "receipt.json",
    "validator": ACCESSIBLE / "validator-report.json",
    "html": ACCESSIBLE / "index.html",
    "style": ACCESSIBLE / "style.css",
    "publication_receipt": PUBLICATION_RECEIPT,
    "solution_receipt": SOLUTION_RECEIPT,
    "solution_pdf": SOLUTION_PDF,
}

CHAPTER_DEPENDENCIES = (
    (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8),
    (7, 9), (9, 10), (7, 19), (7, 20), (5, 11), (11, 12),
    (12, 13), (13, 17), (10, 12), (10, 14), (10, 16), (10, 18),
    (14, 15), (15, 17), (16, 17),
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_identity(path: Path, expected: tuple[int, str]) -> None:
    if not path.is_file():
        raise ValueError(f"authority missing: {path}")
    size, digest = expected
    actual = (path.stat().st_size, sha256_path(path))
    if actual != (size, digest):
        raise ValueError(f"authority identity changed: {path}: {actual} != {(size, digest)}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


def artifact(path: Path, role: str) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "path": path.relative_to(OUT).as_posix(), "role": role, "sha256": sha256_path(path)}


def source_evidence(path: Path, role: str) -> dict[str, Any]:
    return {
        "bytes": path.stat().st_size,
        "locator": path.relative_to(OWNER_ROOT).as_posix(),
        "locator_base": "owner_root",
        "role": role,
        "sha256": sha256_path(path),
    }


def search_text(*values: str | None) -> str:
    joined = " ".join(value for value in values if value)
    normalized = unicodedata.normalize("NFKC", joined).casefold()
    normalized = re.sub(r"[^0-9a-zà-öø-ÿā-ž]+", " ", normalized, flags=re.IGNORECASE)
    return " ".join(normalized.split())


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class HeadingIndex(HTMLParser):
    """Map generated semantic element IDs to the first heading inside them."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []
        self.active: dict[str, Any] | None = None
        self.titles: dict[str, str] = {}
        self.all_ids: set[str] = set()
        self.id_counts: defaultdict[str, int] = defaultdict(int)
        self.exercise_subparts: dict[str, dict[str, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        element_id = attr.get("id")
        if element_id:
            self.all_ids.add(element_id)
            self.id_counts[element_id] += 1
        classes = set((attr.get("class") or "").split())
        if tag == "li" and "exercise-subpart" in classes:
            if not element_id:
                raise ValueError("exercise subpart without stable HTML ID")
            parent_id = attr.get("data-parent-exercise") or next(
                (
                    ancestor_id
                    for _, ancestor_id in reversed(self.stack)
                    if ancestor_id and re.fullmatch(r"o004\.petrunin\.ex\.ch\d{2}\.\d{3}", ancestor_id)
                ),
                None,
            )
            if not parent_id:
                raise ValueError(f"exercise subpart lacks parent binding: {element_id}")
            self.exercise_subparts[element_id] = {
                "parent_id": parent_id,
                "source_label": attr.get("data-source-id") or attr.get("data-synthetic-source-anchor") or "",
            }
        self.stack.append((tag, element_id))
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"} and self.active is None:
            targets: list[str] = []
            if element_id:
                targets.append(element_id)
            for ancestor_tag, ancestor_id in reversed(self.stack[:-1]):
                if ancestor_id and ancestor_tag in {"section", "article", "div"}:
                    targets.append(ancestor_id)
                    break
            self.active = {"tag": tag, "targets": targets, "text": []}

    def handle_data(self, data: str) -> None:
        if self.active is not None:
            self.active["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.active is not None and tag == self.active["tag"]:
            title = " ".join("".join(self.active["text"]).split())
            for target in self.active["targets"]:
                self.titles.setdefault(target, title)
            self.active = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def file_fact(source_path: str) -> dict[str, Any]:
    source = UPSTREAM / source_path
    target = TARGET / source_path
    if not source.is_file() or not target.is_file():
        raise ValueError(f"source/target closure missing: {source_path}")
    return {
        "source_bytes": source.stat().st_size,
        "source_path": source.relative_to(C100_ROOT).as_posix(),
        "source_sha256": sha256_path(source),
        "target_bytes": target.stat().st_size,
        "target_path": target.relative_to(C100_ROOT).as_posix(),
        "target_sha256": sha256_path(target),
    }


def structure_parent(unit_id: str) -> str | None:
    if re.fullmatch(r"o004\.petrunin\.(?:preface|ch\d{2})", unit_id):
        return None
    match = re.fullmatch(r"(o004\.petrunin\.ch\d{2})\.(?:s\d{2}|intro)", unit_id)
    if match:
        return match.group(1)
    match = re.fullmatch(r"(o004\.petrunin\.ch\d{2}\.s\d{2})\.[^.]+", unit_id)
    if match:
        return match.group(1)
    raise ValueError(f"cannot derive structural parent: {unit_id}")


def chapter_unit_from_id(value: str) -> str:
    match = re.search(r"\.ch(\d{2})\.", value)
    if not match:
        raise ValueError(f"cannot derive chapter from ID: {value}")
    return f"o004.petrunin.ch{match.group(1)}"


def solution_manifest_path(chapter: int) -> Path:
    return SOLUTIONS / ("manifest.json" if chapter == 1 else f"manifest-chapter{chapter:02d}.json")


def validate_frozen_package() -> dict[str, Any]:
    """Validate committed C100 projection bytes when the owner tree is absent.

    The central source release deliberately carries the compact, hash-bound
    derived package rather than the multi-repository owner corpus.  A clean
    checkout therefore validates the frozen projection and its declared input
    identities; an owner-adjacent checkout rebuilds it from the primary bytes.
    """

    manifest_path = OUT / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("C100 owner tree and committed frozen pilot are both absent")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_counts = {
        "relations": 994,
        "rights_accessibility_documents": 1,
        "route_materialization_documents": 1,
        "search_documents": 939,
        "units": 939,
    }
    if manifest.get("dataset_id") != "pilot:c100-geometry:v2.1:0.1.0" or manifest.get("record_counts") != expected_counts:
        raise ValueError("committed C100 frozen-pilot identity/counts changed")
    declared = {row["path"]: row for row in manifest.get("files", [])}
    expected_files = {
        "relations.jsonl",
        "rights_accessibility.json",
        "route_materialization.json",
        "search.jsonl",
        "units.jsonl",
    }
    if set(declared) != expected_files:
        raise ValueError("committed C100 frozen-pilot inventory changed")
    for relative, fact in declared.items():
        path = OUT / relative
        if not path.is_file() or (path.stat().st_size, sha256_path(path)) != (fact["bytes"], fact["sha256"]):
            raise ValueError(f"committed C100 frozen-pilot artifact changed: {relative}")
    return manifest


def build() -> dict[str, Any]:
    if not C100_ROOT.exists():
        return validate_frozen_package()
    for key, path in AUTHORITIES.items():
        require_identity(path, EXPECTED[key])
    for chapter in range(1, 21):
        require_identity(solution_manifest_path(chapter), SOLUTION_MANIFEST_EXPECTED[chapter])
        require_identity(SOLUTIONS / f"chapter{chapter:02d}-solutions.tex", SOLUTION_TEX_EXPECTED[chapter])

    publication = json.loads(PUBLICATION_RECEIPT.read_text(encoding="utf-8"))
    accessible_receipt = json.loads((ACCESSIBLE / "receipt.json").read_text(encoding="utf-8"))
    if publication.get("published", {}).get("record_id") not in {22102628, "22102628"}:
        raise ValueError("C100 publication receipt is not the complete open-course record")
    if accessible_receipt.get("status") != "pass" or accessible_receipt.get("scope", {}).get("excluded") != "none; complete source-book semantic scope through EOF":
        raise ValueError("C100 accessible receipt is not the complete passing reader")
    solution_receipt = json.loads(SOLUTION_RECEIPT.read_text(encoding="utf-8"))
    solution_output = solution_receipt.get("output", {})
    if (
        solution_receipt.get("status") != "PASS_ADMITTED"
        or solution_receipt.get("coverage", {}).get("complete_source_exercise_solutions") != 253
        or solution_output.get("pages") != 331
        or (solution_output.get("bytes"), solution_output.get("sha256")) != EXPECTED["solution_pdf"]
    ):
        raise ValueError("C100 cumulative 253-solution receipt is not the final passing authority")

    parser = HeadingIndex()
    parser.feed((ACCESSIBLE / "index.html").read_text(encoding="utf-8"))
    structure_rows = csv_rows(C100_BACKEND / "unit-order-v0.csv")
    exercise_rows = csv_rows(C100_BACKEND / "exercise-hints-v0.csv")
    if len(structure_rows) != 154 or len(exercise_rows) != 266:
        raise ValueError("C100 native unit/exercise closure changed")
    if len(parser.exercise_subparts) != 32:
        raise ValueError(f"C100 semantic exercise-subpart closure changed: {len(parser.exercise_subparts)}")
    exercise_by_id = {row["exercise_id"]: row for row in exercise_rows}
    if len(exercise_by_id) != 266:
        raise ValueError("C100 exercise IDs are duplicated")
    indexed_subpart_ids = set(parser.exercise_subparts) & set(exercise_by_id)
    missing_subpart_ids = set(parser.exercise_subparts) - set(exercise_by_id)
    if len(indexed_subpart_ids) != 13 or len(missing_subpart_ids) != 19:
        raise ValueError("C100 owner-indexed/new semantic subpart partition changed")
    for subpart_id in indexed_subpart_ids:
        if not exercise_by_id[subpart_id]["exercise_kind"].endswith("exercise-subpart"):
            raise ValueError(f"owner-indexed semantic subpart kind mismatch: {subpart_id}")
    hint_rows: dict[str, dict[str, str]] = {}
    hint_orders: dict[str, int] = {}
    for row in exercise_rows:
        if row["hint_id"]:
            hint_rows.setdefault(row["hint_id"], row)
            hint_orders[row["hint_id"]] = min(hint_orders.get(row["hint_id"], 10**9), int(row["order"]))
    if len(hint_rows) != 247:
        raise ValueError("C100 unique hint closure changed")

    required_ids = {row["unit_id"] for row in structure_rows}
    required_ids.update(row["exercise_id"] for row in exercise_rows)
    required_ids.update(missing_subpart_ids)
    required_ids.update(hint_rows)
    anchor_count_failures = {
        unit_id: parser.id_counts.get(unit_id, 0)
        for unit_id in sorted(required_ids)
        if parser.id_counts.get(unit_id, 0) != 1
    }
    if anchor_count_failures:
        raise ValueError(f"semantic HTML anchor one-to-one closure failed: {list(anchor_count_failures.items())[:10]}")

    facts = {path: file_fact(path) for path in sorted({row["source_path"] for row in structure_rows} | {row["exercise_source"] for row in exercise_rows} | {row["hint_source"] for row in exercise_rows if row["hint_source"]})}
    catalog = json.loads((C100_BACKEND / "catalog-v0.json").read_text(encoding="utf-8"))
    catalog_units = {row["id"]: row for row in catalog["records"] if row.get("entity_type") == "unit"}
    top_level = ["o004.petrunin.preface"] + [f"o004.petrunin.ch{number:02d}" for number in range(1, 21)]
    expected_catalog_unit_ids = set(top_level) | {"o004.petrunin.front-ch01"}
    if set(catalog_units) != expected_catalog_unit_ids:
        raise ValueError("C100 owner catalog top-level identity set changed")
    catalog_rights = [row for row in catalog["records"] if row.get("entity_type") == "rights"]
    expected_rights_ids = {
        "rights-petrunin-body-cc-by-sa-4.0",
        "rights-p22-cover-excluded",
        "rights-fiziko-gpl-3.0-or-later",
        "rights-mppics-macros-unresolved",
        "rights-id-terminology-witness-pdfs-internal-only",
        "rights-h2checkers-public-domain",
    }
    if {row["id"] for row in catalog_rights} != expected_rights_ids or len(catalog_rights) != 6:
        raise ValueError("C100 owner-native rights component set changed")

    main_exercise_rows = [row for row in exercise_rows if row["exercise_id"] not in parser.exercise_subparts]
    if len(main_exercise_rows) != 253:
        raise ValueError("C100 parent-exercise closure changed")
    main_by_chapter_and_label: defaultdict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    for row in main_exercise_rows:
        chapter_match = re.search(r"\.ch(\d{2})\.", row["exercise_id"])
        if not chapter_match:
            raise ValueError(f"cannot derive exercise chapter: {row['exercise_id']}")
        main_by_chapter_and_label[(int(chapter_match.group(1)), row["source_label"])].append(row)

    solution_records: list[dict[str, Any]] = []
    solution_manifest_paths: list[Path] = []
    solution_tex_paths: list[Path] = []
    for chapter in range(1, 21):
        manifest_path = solution_manifest_path(chapter)
        solution_manifest_paths.append(manifest_path)
        solution_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        solution_tex = SOLUTIONS / f"chapter{chapter:02d}-solutions.tex"
        solution_tex_paths.append(solution_tex)
        declared_file = solution_manifest.get("solution_file") or solution_manifest.get("component_file")
        if isinstance(declared_file, dict):
            declared_path = C100_ROOT / declared_file["path"]
            if (declared_file.get("bytes"), declared_file.get("sha256")) != SOLUTION_TEX_EXPECTED[chapter]:
                raise ValueError(f"solution manifest file identity mismatch: chapter {chapter}")
        elif isinstance(declared_file, str):
            declared_path = C100_ROOT / declared_file if "/" in declared_file else SOLUTIONS / declared_file
            declared_bytes = solution_manifest.get("solution_file_bytes")
            declared_sha = solution_manifest.get("solution_file_sha256")
            if declared_bytes is not None and declared_bytes != SOLUTION_TEX_EXPECTED[chapter][0]:
                raise ValueError(f"solution manifest byte claim mismatch: chapter {chapter}")
            if declared_sha is not None and declared_sha != SOLUTION_TEX_EXPECTED[chapter][1]:
                raise ValueError(f"solution manifest hash claim mismatch: chapter {chapter}")
        else:
            raise ValueError(f"solution manifest lacks component file: chapter {chapter}")
        if declared_path.resolve() != solution_tex.resolve():
            raise ValueError(f"solution manifest resolves to unexpected file: chapter {chapter}")

        chapter_exercises = solution_manifest.get("exercises")
        if not isinstance(chapter_exercises, list) or not chapter_exercises:
            raise ValueError(f"solution manifest exercise closure missing: chapter {chapter}")
        for fallback_ordinal, exercise in enumerate(chapter_exercises, 1):
            ordinal = int(exercise.get("sequence") or exercise.get("ordinal") or fallback_ordinal)
            stable_id = exercise.get("stable_id")
            source_labels = exercise.get("source_labels") or []
            source_label = exercise.get("source_topology_id") or exercise.get("source_local_label") or (source_labels[0] if source_labels else None)
            if not isinstance(stable_id, str) or not re.fullmatch(rf"o004-c100-sol-ch{chapter:02d}-ex\d{{3}}", stable_id):
                raise ValueError(f"solution stable ID mismatch: chapter {chapter}, ordinal {ordinal}")
            candidates = main_by_chapter_and_label.get((chapter, source_label), []) if isinstance(source_label, str) else []
            if source_label == "__unlabeled_ch09_ex005_video":
                candidates = main_by_chapter_and_label.get((chapter, ""), [])
            if len(candidates) != 1:
                raise ValueError(f"solution-to-exercise crosswalk is not one-to-one: {stable_id}: {source_label}: {len(candidates)}")
            mapped_exercise = candidates[0]
            solution_records.append({
                "chapter": chapter,
                "exercise": exercise,
                "exercise_id": mapped_exercise["exercise_id"],
                "manifest_path": manifest_path,
                "manifest_sha256": SOLUTION_MANIFEST_EXPECTED[chapter][1],
                "ordinal": ordinal,
                "solution_file": solution_tex,
                "solution_file_bytes": SOLUTION_TEX_EXPECTED[chapter][0],
                "solution_file_sha256": SOLUTION_TEX_EXPECTED[chapter][1],
                "source_label": source_label,
                "stable_id": stable_id,
            })
    if (
        len(solution_records) != 253
        or len({row["stable_id"] for row in solution_records}) != 253
        or {row["exercise_id"] for row in solution_records} != {row["exercise_id"] for row in main_exercise_rows}
    ):
        raise ValueError("C100 253-solution crosswalk does not exactly cover parent exercises")

    units: list[dict[str, Any]] = []
    search_rows: list[dict[str, Any]] = []

    def add_unit(unit: dict[str, Any], aliases: Iterable[str] = ()) -> None:
        units.append(unit)
        search_rows.append({
            "course_id": "C100",
            "learner_url": unit["learner_route"]["url"],
            "locale": "id-ID",
            "native_unit_kind": unit["native_unit_kind"],
            "order_key": unit["order_key"],
            "record_type": "search_document",
            "search_text": search_text("geometri bidang euklides afin proyektif hiperbolik sferis", unit["title"], unit["stable_unit_id"], *aliases),
            "stable_unit_id": unit["stable_unit_id"],
            "title": unit["title"],
        })

    for row in structure_rows:
        unit_id = row["unit_id"]
        order = int(row["order"])
        file = facts[row["source_path"]]
        catalog_row = catalog_units.get(unit_id)
        catalog_binding_state = "unit_order_authority_only; owner_catalog_is_top_level_granular"
        if unit_id in top_level and catalog_row is None:
            raise ValueError(f"selected C100 top-level unit is absent from owner catalog: {unit_id}")
        if catalog_row:
            catalog_binding_state = "catalog_hashes_match_live_owner_files"
            for side in ("source", "target"):
                expected = catalog_row.get(f"{side}_sha256")
                if expected and expected != file[f"{side}_sha256"]:
                    known_stale_inversion_source = (
                        unit_id == "o004.petrunin.ch10"
                        and side == "source"
                        and expected == "105a29420bf4fb336b9d277aa6edbd86d3472f9511a9178f9eec0173da4d361e"
                        and file["source_sha256"] == "638839445fe457593ba453b0a8020194063d650cccc33107a9865094b727cab7"
                    )
                    if not known_stale_inversion_source:
                        raise ValueError(f"catalog {side} binding failed: {unit_id}")
                    catalog_binding_state = "single_known_stale_catalog_source_hash; live frozen source bytes retained"
        title = parser.titles.get(unit_id) or row["source_local_id"] or unit_id
        add_unit({
            **file,
            "course_id": "C100",
            "edition_id": "o004-petrunin-current-0b0858e",
            "learner_route": {
                "anchor": unit_id,
                "local_evidence_locator": "accessible/id-ID/index.html",
                "local_evidence_sha256": EXPECTED["html"][1],
                "route_state": "central_exact_owner_html_materialized_for_release",
                "url": f"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/#{unit_id}",
            },
            "locale": "id-ID",
            "native_locator": {
                "catalog_binding_state": catalog_binding_state,
                "catalog_source_sha256": catalog_row.get("source_sha256") if catalog_row else None,
                "catalog_target_sha256": catalog_row.get("target_sha256") if catalog_row else None,
                "owner_catalog_id": unit_id,
                "source_local_id": row["source_local_id"] or None,
            },
            "native_unit_id": unit_id,
            "native_unit_kind": row["entity_kind"],
            "order_index": order,
            "order_key": f"s{order:04d}",
            "record_type": "unit",
            "rights_component_id": "rights-petrunin-body-cc-by-sa-4.0",
            "schema_id": SCHEMA_ID,
            "stable_unit_id": unit_id,
            "title": title,
            "translation_state": row["translation_state"],
        }, [row["source_local_id"], row["source_path"]])

    for row in exercise_rows:
        exercise_id = row["exercise_id"]
        order = int(row["order"])
        file = facts[row["exercise_source"]]
        title = f"Latihan {exercise_id.rsplit('.', 1)[-1]}"
        if row["source_label"]:
            title += f" — {row['source_label']}"
        add_unit({
            **file,
            "course_id": "C100",
            "edition_id": "o004-petrunin-current-0b0858e",
            "learner_route": {
                "anchor": exercise_id,
                "local_evidence_locator": "accessible/id-ID/index.html",
                "local_evidence_sha256": EXPECTED["html"][1],
                "route_state": "central_exact_owner_html_materialized_for_release",
                "url": f"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/#{exercise_id}",
            },
            "locale": "id-ID",
            "native_locator": {"source_label": row["source_label"] or None, "used_later": row["used_later"].casefold() == "true"},
            "native_unit_id": exercise_id,
            "native_unit_kind": row["exercise_kind"],
            "order_index": 10000 + order,
            "order_key": f"x{order:04d}",
            "record_type": "unit",
            "rights_component_id": "rights-petrunin-body-cc-by-sa-4.0",
            "schema_id": SCHEMA_ID,
            "stable_unit_id": exercise_id,
            "title": title,
            "translation_state": row["status"],
        }, [row["source_label"], row["exercise_kind"]])

    for subpart_id in sorted(missing_subpart_ids):
        subpart = parser.exercise_subparts[subpart_id]
        parent_row = exercise_by_id.get(subpart["parent_id"])
        if parent_row is None:
            raise ValueError(f"new semantic subpart parent is absent from owner index: {subpart_id}")
        parent_order = int(parent_row["order"])
        suffix = subpart_id.rsplit(".", 1)[-1]
        file = facts[parent_row["exercise_source"]]
        add_unit({
            **file,
            "course_id": "C100",
            "edition_id": "o004-petrunin-current-0b0858e",
            "learner_route": {
                "anchor": subpart_id,
                "local_evidence_locator": "accessible/id-ID/index.html",
                "local_evidence_sha256": EXPECTED["html"][1],
                "route_state": "central_exact_owner_html_materialized_for_release",
                "url": f"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/#{subpart_id}",
            },
            "locale": "id-ID",
            "native_locator": {
                "index_gap_state": "present_in_terminal_semantic_HTML_but_absent_from_owner_exercise-hints-v0.csv",
                "parent_exercise_id": subpart["parent_id"],
                "source_label": subpart["source_label"],
            },
            "native_unit_id": subpart_id,
            "native_unit_kind": "exercise-subpart",
            "order_index": 1000000 + parent_order * 100 + ord(suffix[0]),
            "order_key": f"x{parent_order:04d}.sub.{suffix}",
            "record_type": "unit",
            "rights_component_id": "rights-petrunin-body-cc-by-sa-4.0",
            "schema_id": SCHEMA_ID,
            "stable_unit_id": subpart_id,
            "title": f"Bagian {suffix} — Latihan {subpart['parent_id'].rsplit('.', 1)[-1]}",
            "translation_state": "translated-admitted-in-terminal-semantic-reader",
        }, [subpart["source_label"], subpart["parent_id"], "subbagian latihan"])

    for hint_id, row in sorted(hint_rows.items(), key=lambda item: (hint_orders[item[0]], item[0])):
        order = hint_orders[hint_id]
        file = facts[row["hint_source"]]
        title = f"Petunjuk {hint_id.rsplit('.', 1)[-1]}"
        add_unit({
            **file,
            "course_id": "C100",
            "edition_id": "o004-petrunin-current-0b0858e",
            "learner_route": {
                "anchor": hint_id,
                "local_evidence_locator": "accessible/id-ID/index.html",
                "local_evidence_sha256": EXPECTED["html"][1],
                "route_state": "central_exact_owner_html_materialized_for_release",
                "url": f"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/#{hint_id}",
            },
            "locale": "id-ID",
            "native_locator": {"shared_hint": sum(1 for item in exercise_rows if item["hint_id"] == hint_id) > 1},
            "native_unit_id": hint_id,
            "native_unit_kind": "hint",
            "order_index": 20000 + order,
            "order_key": f"h{order:04d}:{hint_id}",
            "record_type": "unit",
            "rights_component_id": "rights-petrunin-body-cc-by-sa-4.0",
            "schema_id": SCHEMA_ID,
            "stable_unit_id": hint_id,
            "title": title,
            "translation_state": "admitted",
        })

    for solution in sorted(solution_records, key=lambda row: (row["chapter"], row["ordinal"], row["stable_id"])):
        exercise = solution["exercise"]
        title = (
            exercise.get("title_id")
            or exercise.get("source_title")
            or exercise.get("title")
            or f"Solusi Latihan {solution['ordinal']:03d}"
        )
        add_unit({
            "course_id": "C100",
            "edition_id": "o004-petrunin-current-0b0858e",
            "learner_route": {
                "anchor": None,
                "local_evidence_locator": "solutions/id-ID/output/pdf/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf",
                "local_evidence_sha256": EXPECTED["solution_pdf"][1],
                "route_state": "central_exact_owner_solution_pdf_materialized_course_level_fallback_no_named_destination",
                "url": "https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf",
            },
            "locale": "id-ID",
            "native_locator": {
                "mapped_exercise_id": solution["exercise_id"],
                "owner_manifest_path": solution["manifest_path"].relative_to(C100_ROOT).as_posix(),
                "owner_manifest_sha256": solution["manifest_sha256"],
                "solution_anchor_in_tex": exercise.get("solution_anchor"),
                "source_label": solution["source_label"],
            },
            "native_unit_id": solution["stable_id"],
            "native_unit_kind": "independent_solution",
            "order_index": 3000000 + solution["chapter"] * 1000 + solution["ordinal"],
            "order_key": f"z{solution['chapter']:02d}.{solution['ordinal']:03d}",
            "record_type": "unit",
            "rights_component_id": "rights-c100-independent-solutions-cc-by-sa-4.0",
            "schema_id": SCHEMA_ID,
            "solution_source_bytes": solution["solution_file_bytes"],
            "solution_source_path": solution["solution_file"].relative_to(C100_ROOT).as_posix(),
            "solution_source_sha256": solution["solution_file_sha256"],
            "source_provenance_state": "independently_authored_id-ID_solution; no upstream solution prose",
            "stable_unit_id": solution["stable_id"],
            "title": f"Solusi Bab {solution['chapter']:02d} — {title}",
            "translation_state": "complete-published-terminal-cumulative-receipt",
        }, [solution["source_label"], solution["exercise_id"], "solusi latihan"])

    if len(units) != 939 or len({row["stable_unit_id"] for row in units}) != 939:
        raise ValueError("C100 materialized stable-unit closure changed")

    relations: list[dict[str, Any]] = []

    def relation(from_id: str, relation_type: str, to_id: str, evidence: dict[str, Any], strength: str = "hard") -> None:
        relations.append({
            "course_id": "C100",
            "evidence": evidence,
            "from_id": from_id,
            "record_type": "relation",
            "relation_type": relation_type,
            "schema_id": SCHEMA_ID,
            "strength": strength,
            "to_id": to_id,
        })

    for row in structure_rows:
        parent = structure_parent(row["unit_id"])
        if parent:
            relation(row["unit_id"], "part_of", parent, {"derivation": "owner unit-order-v0 hierarchy", "source_path": row["source_path"]})
    for row in exercise_rows:
        if row["exercise_id"] in parser.exercise_subparts:
            relation(
                row["exercise_id"],
                "part_of_exercise",
                parser.exercise_subparts[row["exercise_id"]]["parent_id"],
                {"owner_order": int(row["order"]), "source_label": row["source_label"] or None},
            )
        else:
            chapter = chapter_unit_from_id(row["exercise_id"])
            relation(chapter, "has_exercise", row["exercise_id"], {"owner_order": int(row["order"]), "source_label": row["source_label"] or None})
        if row["hint_id"]:
            relation(row["exercise_id"], "guided_by", row["hint_id"], {"owner_status": row["status"], "hint_source": row["hint_source"]})
    for subpart_id in sorted(missing_subpart_ids):
        subpart = parser.exercise_subparts[subpart_id]
        parent_row = exercise_by_id[subpart["parent_id"]]
        relation(
            subpart_id,
            "part_of_exercise",
            subpart["parent_id"],
            {"derivation": "terminal semantic HTML containment", "source_label": subpart["source_label"]},
        )
        if parent_row["hint_id"]:
            relation(
                subpart_id,
                "guided_by",
                parent_row["hint_id"],
                {"derivation": "terminal semantic HTML inherited parent hint", "parent_exercise_id": subpart["parent_id"]},
            )
    for solution in solution_records:
        relation(
            solution["stable_id"],
            "solves",
            solution["exercise_id"],
            {
                "owner_manifest_path": solution["manifest_path"].relative_to(C100_ROOT).as_posix(),
                "owner_manifest_sha256": solution["manifest_sha256"],
                "source_label": solution["source_label"],
            },
        )
    for left, right in zip(top_level, top_level[1:]):
        relation(left, "next", right, {"derivation": "owner unit-order-v0 top-level order"})
    for prerequisite, successor in CHAPTER_DEPENDENCIES:
        relation(
            f"o004.petrunin.ch{successor:02d}",
            "depends_on",
            f"o004.petrunin.ch{prerequisite:02d}",
            {"derivation": "author dependency graph in translated preface", "graph_edge": f"{prerequisite}->{successor}"},
        )
    relations.sort(key=lambda row: (row["relation_type"], row["from_id"], row["to_id"], canonical_json(row["evidence"])))
    if len(relations) != 994:
        raise ValueError(f"C100 relation closure changed: {len(relations)}")
    relation_endpoints = {row["from_id"] for row in relations} | {row["to_id"] for row in relations}
    external_relation_endpoints = sorted(relation_endpoints - {row["stable_unit_id"] for row in units})
    if external_relation_endpoints:
        raise ValueError("C100 relation graph must close entirely over its 939 stable units")

    visual = accessible_receipt["visual_browser_readability_qa"]
    rights_accessibility = {
        "accessibility": {
            "accessible_figure_surfaces": visual["complete_reader"]["accessible_figures"],
            "exercise_parent_units": 253,
            "exercise_subpart_units": 32,
            "exercise_units": 285,
            "hint_units": 247,
            "mathml_nodes": visual["math"]["mathml_nodes"],
            "reader_html_bytes": EXPECTED["html"][0],
            "reader_html_sha256": EXPECTED["html"][1],
            "reader_style_bytes": EXPECTED["style"][0],
            "reader_style_sha256": EXPECTED["style"][1],
            "solution_pdf_bytes": EXPECTED["solution_pdf"][0],
            "solution_pdf_pages": 331,
            "solution_pdf_sha256": EXPECTED["solution_pdf"][1],
            "solution_units": 253,
            "state": "complete semantic HTML/EPUB; exact local bytes and bounded desktop/narrow browser QA pass",
            "visible_tex_fallbacks": visual["math"]["visible_tex_fallbacks"],
        },
        "course_id": "C100",
        "rights": {
            "components": [
                {
                    **row,
                    "materialized_component_bytes_in_backend": False,
                    "projection_note": "owner-native rights metadata projected without component payload",
                }
                for row in sorted(catalog_rights, key=lambda item: item["id"])
            ] + [
                {
                    "applies_to": "253 independently authored Indonesian solutions and mastery metadata",
                    "id": "rights-c100-independent-solutions-cc-by-sa-4.0",
                    "license": "CC BY-SA 4.0",
                    "materialized_component_bytes_in_backend": False,
                    "materialized_in_central_learner_route": True,
                    "non_endorsement": "not written, reviewed, or endorsed by the source-book author",
                    "state": "complete cumulative solution PDF is byte-exact and separately addressable; stable solution metadata contains no solution prose",
                },
                {
                    "applies_to": "separately licensed Clemens/Snapp advanced workbook and its media",
                    "id": "rights-c100-advanced-workbook-separated",
                    "materialized_component_bytes_in_backend": False,
                    "materialized_in_pilot_or_reader": False,
                    "state": "excluded from the CC BY-SA main-course route; preserved only in its separate lineage",
                }
            ],
            "state": "the central reader contains only the complete CC BY-SA main-course surface; no separately licensed workbook bytes are copied",
        },
        "schema_id": SCHEMA_ID,
    }
    route_materialization = {
        "course_id": "C100",
        "expected_public_url": "https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/",
        "local_materialization": {
            "html": {"bytes": EXPECTED["html"][0], "sha256": EXPECTED["html"][1]},
            "solution_pdf": {"bytes": EXPECTED["solution_pdf"][0], "pages": 331, "sha256": EXPECTED["solution_pdf"][1]},
            "style": {"bytes": EXPECTED["style"][0], "sha256": EXPECTED["style"][1]},
            "state": "byte-exact owner reader and complete solution PDF copied by the central route builder; public-byte readback is a release gate",
        },
        "observation_state": "local_only",
        "recorded_at": RECORDED_AT,
        "owner_publication": {
            "concept_doi": "10.5281/zenodo.22044357",
            "version_doi": "10.5281/zenodo.22102628",
            "publication_receipt_sha256": EXPECTED["publication_receipt"][1],
        },
        "schema_id": SCHEMA_ID,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT / "units.jsonl", units)
    write_jsonl(OUT / "relations.jsonl", relations)
    write_jsonl(OUT / "search.jsonl", search_rows)
    write_json(OUT / "rights_accessibility.json", rights_accessibility)
    stale_route_readback = OUT / "route_readback.json"
    if stale_route_readback.exists():
        stale_route_readback.unlink()
    write_json(OUT / "route_materialization.json", route_materialization)
    files = [
        artifact(OUT / "relations.jsonl", "evidence_bound_relations"),
        artifact(OUT / "rights_accessibility.json", "rights_accessibility_summary"),
        artifact(OUT / "route_materialization.json", "learner_route_materialization_evidence"),
        artifact(OUT / "search.jsonl", "compact_search_shard"),
        artifact(OUT / "units.jsonl", "stable_unit_registry"),
    ]

    input_authority = [
        source_evidence(AUTHORITIES[key], role)
        for key, role in (
            ("publication_receipt", "complete_open_course_publication_receipt"),
            ("receipt", "complete_semantic_reader_receipt"),
            ("validator", "complete_semantic_reader_validation_report"),
            ("manifest", "owner_accessible_manifest"),
            ("html", "owner_semantic_html_reader"),
            ("style", "owner_semantic_html_stylesheet"),
            ("catalog", "owner_native_catalog"),
            ("schema", "owner_native_catalog_schema"),
            ("unit_order", "owner_native_unit_order"),
            ("exercise_hints", "owner_native_exercise_hint_index"),
            ("solution_receipt", "terminal_253_solution_cumulative_receipt"),
            ("solution_pdf", "complete_253_solution_learner_pdf"),
        )
    ]
    for source_path in sorted(facts):
        input_authority.append(source_evidence(UPSTREAM / source_path, f"frozen_source:{source_path}"))
        input_authority.append(source_evidence(TARGET / source_path, f"admitted_target:{source_path}"))
    for chapter, (manifest_path, solution_path) in enumerate(zip(solution_manifest_paths, solution_tex_paths), 1):
        input_authority.append(source_evidence(manifest_path, f"solution_manifest:chapter{chapter:02d}"))
        input_authority.append(source_evidence(solution_path, f"solution_component:chapter{chapter:02d}"))

    manifest = {
        "canonical_serialization": "UTF-8; JSON objects sorted by key; JSONL LF with trailing newline",
        "course_id": "C100",
        "dataset_id": "pilot:c100-geometry:v2.1:0.1.0",
        "files": files,
        "input_authority": input_authority,
        "limitations": [
            "The v2.1 pilot contains metadata, hashes, and relations only; textbook prose is not copied into backend records.",
            "The exact semantic HTML reader is a separate learner-facing route and remains CC BY-SA 4.0 with attribution, change notice, ShareAlike, and non-endorsement.",
            "The separately licensed Clemens/Snapp advanced workbook is excluded from this pilot, reader route, and release lineage.",
            "Static Indonesian figure descriptions are available; the source MPS/EPS artwork is not embedded in the semantic reader.",
            "The older per-unit catalog QA labels are retained as historical native metadata; the final complete-reader receipt and publication receipt are the terminal admission authorities.",
            "The native catalog's Chapter 10 source hash is stale against the live frozen-commit directory; both values are preserved explicitly, while the live file hash and admitted target hash drive this pilot.",
            "The 253 solution units resolve to one exact 331-page course-level PDF because that PDF has no named per-solution destinations; the stable solution-to-exercise crosswalk remains exact and independent of page guesses.",
            "A checkout adjacent to the owner corpus rebuilds this projection from primary authorities. The standalone central source release validates the committed compact package and its declared hashes; it does not claim to contain the full owner corpus.",
        ],
        "materialization_scope": "compact structure, complete exercise/subpart, hint, solution-crosswalk, relation, search, rights/accessibility, and learner-route projections; no textbook prose and no solution prose",
        "native_backend_contribution": {
            "accessibility": "7,646 MathML nodes and 213 accessible figure surfaces are summarized by exact hashes without payload duplication",
            "exercise_hint_topology": "253 parent exercises, all 32 semantic subparts (13 native-indexed plus 19 terminal-reader additions), 247 unique hints, and exact parent/hint relations",
            "identity_and_order": "154 owner-native structural units, 285 exercise surfaces, 247 hints, and 253 independent solution identities",
            "route": "686 reader-addressable structure/exercise/hint units have exact semantic-reader anchors; 253 solution units resolve truthfully to the exact course-level solution PDF",
            "solution_crosswalk": "253 independently authored solutions map one-to-one to all 253 parent exercises through 20 exact chapter manifests",
            "source_target_binding": "all 22 unique source/target TeX file pairs are byte- and SHA-256-bound",
        },
        "owner_tree_mode": "read_only",
        "standalone_replay_mode": "committed_hash_bound_projection_validation_when_owner_corpus_is_not_adjacent",
        "relation_endpoint_policy": {
            "external_endpoint_count": 0,
            "external_endpoint_sha256": hashlib.sha256(canonical_json([]).encode("utf-8")).hexdigest(),
            "mode": "internal_only",
        },
        "record_counts": {
            "relations": len(relations),
            "rights_accessibility_documents": 1,
            "route_materialization_documents": 1,
            "search_documents": len(search_rows),
            "units": len(units),
        },
        "recorded_at": RECORDED_AT,
        "schema_id": SCHEMA_ID,
        "uncertain_field_contracts": [
            {"field": "learner_route.route_state", "decision": "the central release receipt must upgrade local exact-byte materialization to anonymous public-byte readback"},
            {"field": "figure payload", "decision": "retain the owner-authored Indonesian static description and do not invent or import unlicensed artwork"},
        ],
    }
    write_json(OUT / "manifest.json", manifest)
    return manifest


def main() -> None:
    manifest = build()
    print(canonical_json({"course_id": "C100", "record_counts": manifest["record_counts"], "result": "pass"}))


if __name__ == "__main__":
    main()
