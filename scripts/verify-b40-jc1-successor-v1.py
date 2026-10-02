"""Check exact native-unit preservation across the public B40 successor.

Only the named historical Git objects and current reader files are read.
No historical source is executed and no mathematical correctness is inferred.
"""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "ca22420a8d8de81b0237eb12f07da183b4e57a29"
PREFIX = "docs/en/readers/hefferon-linear-algebra/"
OLD_MANIFEST = "26a998effd54d16dcc4865ecdc199e5c94a6599ea464e48ad83c665293544031"
NEW_MANIFEST = "d2e20590a9ea03148979c33a921b17547cffe06ae11cc40183af092c68257653"


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def old(path):
    require(path.startswith(PREFIX) and ".." not in Path(path).parts, "Unexpected historical path")
    return subprocess.check_output(["git", "show", BASE + ":" + path], cwd=ROOT)


def span(unit, body):
    surface = unit["surface"]
    value = body[surface["byte_start"]:surface["byte_end"]]
    require(len(value) == surface["bytes"] and digest(value) == surface["sha256"],
            "Native unit no longer matches its exact rendered span: " + unit["unit_id"])
    return value


def verify_pair(previous, current, old_body, new_body):
    left, right = copy.deepcopy(previous), copy.deepcopy(current)
    left.pop("surface"); right.pop("surface")
    require(left == right, "Native unit identity, source or kind changed")
    require(span(previous, old_body) == span(current, new_body), "Native unit body changed")


def validate():
    before = old(PREFIX + "READER_MANIFEST.json")
    after = (ROOT / PREFIX / "READER_MANIFEST.json").read_bytes()
    require(digest(before) == OLD_MANIFEST and digest(after) == NEW_MANIFEST, "Unexpected edition identity")
    previous, current = json.loads(before), json.loads(after)
    require(len(previous["sections"]) == 33 and len(current["sections"]) == 34, "Unexpected scope")
    require([r["section"] for r in current["sections"][:-1]] == [r["section"] for r in previous["sections"]],
            "Predecessor section order changed")
    preserved, refreshed = 0, 0
    for left, right in zip(previous["sections"], current["sections"]):
        old_index_raw = old(PREFIX + left["public_index"]["path"])
        new_index_raw = (ROOT / PREFIX / right["public_index"]["path"]).read_bytes()
        old_body = old(PREFIX + left["reader"]["path"])
        new_body = (ROOT / PREFIX / right["reader"]["path"]).read_bytes()
        for data, fact in [(old_index_raw, left["public_index"]), (new_index_raw, right["public_index"]),
                           (old_body, left["reader"]), (new_body, right["reader"])]:
            require(len(data) == fact["bytes"] and digest(data) == fact["sha256"], "Edition file differs from manifest")
        old_index, new_index = json.loads(old_index_raw), json.loads(new_index_raw)
        require(len(old_index["units"]) == len(new_index["units"]), "Predecessor units lost or added")
        for key in ["source_context_contract", "external_reference_bindings", "source_notes", "editorial_notes", "exercises"]:
            require(old_index.get(key) == new_index.get(key), "Native context changed: " + key)
        for old_unit, new_unit in zip(old_index["units"], new_index["units"]):
            verify_pair(old_unit, new_unit, old_body, new_body)
            preserved += 1
            refreshed += old_unit["surface"] != new_unit["surface"]
    added = current["sections"][-1]
    require(added["section"] == "jc1" and added["units"] == 15, "Unexpected added section")
    index = json.loads((ROOT / PREFIX / added["public_index"]["path"]).read_bytes())
    body = (ROOT / PREFIX / added["reader"]["path"]).read_bytes()
    source = (ROOT / PREFIX / "sources/jc1.tex").read_bytes()
    require(digest(source) == added["complete_original_source"]["sha256"], "New source identity changed")
    require(len(index["units"]) == 15, "New native-unit scope differs")
    for unit in index["units"]:
        span(unit, body)
        for fragment in unit["source_fragments"]:
            require(fragment["path"] == "src/jc/jc1.tex", "Unexpected source fragment")
            require(digest(source[fragment["byte_start"]:fragment["byte_end"]]) == fragment["sha256"],
                    "New unit source fragment changed")
    require(preserved == 2577, "Wrong preserved-unit count")
    return {"schema": "b40-jc1-exact-successor-verification/1", "state": "pass",
            "base_commit": BASE, "old_manifest_sha256": OLD_MANIFEST, "new_manifest_sha256": NEW_MANIFEST,
            "previous_sections_preserved": 33, "previous_native_units_preserved": preserved,
            "rendered_locations_refreshed": refreshed, "added_source_bound_native_units": 15,
            "total_native_units": 2592, "historical_receipts_unchanged": True,
            "independent_mathematical_review": False, "whole_book_complete": False}


if __name__ == "__main__":
    result = validate()
    target = ROOT / "backend/authority/b40-jc1-successor-validation-v1.json"
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result))
