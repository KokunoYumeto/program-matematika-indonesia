#!/usr/bin/env python3
"""Read-only, network-free replay of Judson's real two-course chapter routes.

Usage:
  python replay_judson_two_course_learner_routes.py --web-zip WEB.zip \
    --native-backend extracted-source/backend/v1 --release-manifest RELEASE_MANIFEST.json \
    --check JUDSON_TWO_COURSE_LEARNER_ROUTES.json

Without --check, emit the deterministic offline object to stdout. Live observations
in the route document are historical observations, never re-asserted by this tool.
Only the 23 localized chapter titles are copied; no chapter prose is exported.
"""
import argparse
import csv
import hashlib
import io
import json
import posixpath
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

WEB_NAME = "ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2_WEB.zip"
WEB_BYTES = 27339920
WEB_SHA = "cb27ec5671b7e2378da0754a607125b43367ba6eca473d3dc11afd307313a7c1"
RELEASE_SHA = "19edcfb1223be1a5b416598e0a3224bb99df91dbff8929ea853cb8b31e3365ee"
BACKEND_SHA = "4294d16f96ea7fa405d6841e308e7c90c08152a2c7eb6cefe45a44e5b705bcd1"
PUBLIC_BASE = "https://kokunoyumeto.github.io/abstract-algebra-theory-and-applications-id/"
INPUTS = {
    "courses/courses.jsonl": (1176, "9723e8020b4407c7b14a077ddfb475cfc47eae3666c8bfcd3d17d682ffef4982"),
    "courses/course-units.jsonl": (9896, "8cdffd21c7867cc91da9d6c00f68d9e8e585d74777ef8ca15f7bc108f424000d"),
    "topology/units.jsonl": (3013695, "c3ec8fd2f36566e3f4d02a1549b1b768170305737fff7985f7770760168f4140"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(name, data):
    return {"name": name, "bytes": len(data), "sha256": sha(data)}


def require(condition, message):
    if not condition:
        raise ValueError(message)


class HTMLFacts(HTMLParser):
    """Find actual local hrefs and chapter section/header facts."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = set()
        self.chapter_ids = []
        self.h1_depth = 0
        self.capture = None
        self.capture_depth = 0
        self.title_parts = []
        self.number_parts = []
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "a" and "href" in attrs:
            value = urlsplit(attrs["href"])
            if not value.scheme and not value.netloc and value.path:
                self.hrefs.add(unquote(value.path))
        if tag == "section" and "chapter" in classes:
            self.chapter_ids.append(attrs.get("id"))
        self.depth += 1
        if tag == "h1":
            self.h1_depth = self.depth
        if self.h1_depth and tag == "span":
            if "title" in classes:
                self.capture, self.capture_depth = "title", self.depth
            elif "codenumber" in classes:
                self.capture, self.capture_depth = "number", self.depth

    def handle_endtag(self, tag):
        if self.capture and self.depth == self.capture_depth:
            self.capture = None
        if tag == "h1":
            self.h1_depth = 0
        self.depth = max(0, self.depth - 1)

    def handle_data(self, data):
        if self.capture == "title":
            self.title_parts.append(data)
        elif self.capture == "number":
            self.number_parts.append(data)


def parse_html(data):
    parser = HTMLFacts()
    parser.feed(data.decode("utf-8"))
    return parser


def derive(web_zip, native_backend, release_manifest):
    release_data = release_manifest.read_bytes()
    require(sha(release_data) == RELEASE_SHA, "release manifest hash mismatch")
    release = json.loads(release_data)
    web_info = next(row for row in release["artifacts"] if row["name"] == WEB_NAME)
    require((web_info["bytes"], web_info["sha256"]) == (WEB_BYTES, WEB_SHA), "WEB release binding mismatch")
    require(web_zip.stat().st_size == WEB_BYTES, "WEB archive size mismatch")
    with web_zip.open("rb") as stream:
        require(hashlib.file_digest(stream, "sha256").hexdigest() == WEB_SHA, "WEB archive hash mismatch")
    manifest_data = (native_backend / "manifest.json").read_bytes()
    require(sha(manifest_data) == BACKEND_SHA == release["backend_manifest_sha256"], "native manifest mismatch")
    manifest = json.loads(manifest_data)
    declared = {row["path"]: row for row in manifest["files"]}
    inputs, rows = [], {}
    for name, (length, digest) in INPUTS.items():
        data = (native_backend / name).read_bytes()
        require((len(data), sha(data)) == (length, digest), "native input mismatch: " + name)
        require((declared[name]["bytes"], declared[name]["sha256"]) == (length, digest), "native manifest binding: " + name)
        inputs.append(identity(name, data))
        rows[name] = [json.loads(line) for line in data.decode("utf-8").splitlines() if line]
    units = {row["id"]: row for row in rows["topology/units.jsonl"]}
    require(len(units) == 3323, "unit identity count")
    courses = {row["code"]: row for row in rows["courses/courses.jsonl"]}
    require(set(courses) == {"C30", "C40"}, "course selectors")
    members = rows["courses/course-units.jsonl"]
    require(len(members) == 23 and len({row["unit_id"] for row in members}) == 23, "nonduplicating 23-chapter membership")
    with zipfile.ZipFile(web_zip) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)) == 1088, "WEB entry inventory uniqueness/count")
        package_data = archive.read("PACKAGE_MANIFEST.csv")
        require(sha(package_data) == release["reader_trees"]["web"]["package_manifest_sha256"], "WEB package manifest mismatch")
        package = {row["path"]: row for row in csv.DictReader(io.StringIO(package_data.decode("utf-8")))}
        mapping_data = archive.read(".mapping.json")
        mapping = json.loads(mapping_data)
        page_ids = {item for values in mapping.values() for item in values}
        toc_data = archive.read("aata-toc.html")
        toc = parse_html(toc_data)
        chapter_units = {units[row["unit_id"]]["source_xml_id"]: units[row["unit_id"]] for row in members}
        actual_pages = {}
        # Iterate existing ZIP names and actual TOC hrefs; do not invent paths
        # by appending an extension to the native source ID.
        for name in names:
            stem, suffix = posixpath.splitext(posixpath.basename(name))
            if suffix != ".html" or stem not in chapter_units or name not in toc.hrefs:
                continue
            data = archive.read(name)
            facts = parse_html(data)
            require(facts.chapter_ids == [stem], "chapter section ID: " + name)
            require(stem in page_ids, "PreTeXt page mapping: " + name)
            title = " ".join("".join(facts.title_parts).split())
            number = "".join(facts.number_parts).strip()
            require(title and number.isdigit(), "localized chapter heading: " + name)
            require((len(data), sha(data)) == (int(package[name]["bytes"]), package[name]["sha256"]), "HTML manifest binding: " + name)
            require(stem not in actual_pages, "ambiguous chapter route")
            actual_pages[stem] = {
                "chapter_number": int(number),
                "localized_title": title,
                "archive_member": name,
                "bytes": len(data),
                "sha256": sha(data),
                "offline_href": name,
                "public_url": urljoin(PUBLIC_BASE, name),
                "html_chapter_id": stem,
                "toc_href": name,
                "page_mapping_member": ".mapping.json",
            }
        require(set(actual_pages) == set(chapter_units), "all native chapter IDs resolve to real ZIP/TOC routes")
        result_courses = []
        for code in ("C30", "C40"):
            course = courses[code]
            selected = sorted((row for row in members if row["course_id"] == course["id"]), key=lambda row: row["sequence"])
            require([row["sequence"] for row in selected] == list(range(1, len(selected) + 1)), "course sequence")
            require(len(selected) == {"C30": 15, "C40": 8}[code], "course chapter count")
            routes = []
            for membership in selected:
                unit = units[membership["unit_id"]]
                require(unit["kind"] == "chapter", "membership must select canonical chapter")
                routes.append({
                    "native_course_id": course["id"],
                    "native_membership_id": membership["id"],
                    "native_unit_id": unit["id"],
                    "sequence": membership["sequence"],
                    "native_source_path": unit["source_path"],
                    **actual_pages[unit["source_xml_id"]],
                })
            result_courses.append({"course_id": code, "native_course_id": course["id"], "localized_title": course["title"], "chapter_count": len(routes), "routes": routes})
    return {
        "schema": "judson-two-course-learner-routes-offline/v1",
        "locale": "id-ID",
        "native_edition": "2026.08.22.2",
        "record_id": 22062449,
        "source_release_manifest": identity("RELEASE_MANIFEST.json", release_data),
        "native_backend_manifest": identity("backend/v1/manifest.json", manifest_data),
        "native_inputs": inputs,
        "web_archive": {"name": WEB_NAME, "bytes": WEB_BYTES, "sha256": WEB_SHA, "public_url": "https://zenodo.org/records/22062449/files/" + WEB_NAME + "?download=1"},
        "web_package_manifest": identity("PACKAGE_MANIFEST.csv", package_data),
        "toc": identity("aata-toc.html", toc_data),
        "page_mapping": identity(".mapping.json", mapping_data),
        "public_base_url": PUBLIC_BASE,
        "public_base_source": "v0.62.13 course capsules C30/C40 /layers/learner/primary/url",
        "derivation": "native course membership -> canonical chapter unit/XML ID -> existing WEB member and actual TOC href -> matching chapter section ID and localized h1 title; all member bytes match WEB package manifest",
        "courses": result_courses,
        "chapter_routes": 23,
        "duplicated_chapters": 0,
        "copied_chapter_prose": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--web-zip", type=Path, required=True)
    parser.add_argument("--native-backend", type=Path, required=True)
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    result = derive(args.web_zip, args.native_backend, args.release_manifest)
    if args.check:
        recorded = json.loads(args.check.read_text(encoding="utf-8"))
        require(recorded["offline"] == result, "recorded offline routes differ from deterministic replay")
        output = {"result": "pass", "course_counts": {"C30": 15, "C40": 8}, "chapter_routes": 23, "offline_bytes_verified": sum(route["bytes"] for course in result["courses"] for route in course["routes"]), "network_requests": 0, "live_observations_reasserted": False, "offline_canonical_sha256": sha((json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))}
    else:
        output = result
    print(json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"result": "fail", "error_type": type(exc).__name__, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        sys.exit(1)

