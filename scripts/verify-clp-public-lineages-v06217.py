"""Read-only public inventory replay against full-body publication receipts."""
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import json
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://github.com/KokunoYumeto/program-matematika-indonesia"
PINNED = {
    "GITHUB_PUBLICATION_RECEIPT_v0.62.17.json": (23105, "1a8d3733c1bda0094c9f30ab94cacf2bd67de213038c4a46f2c2f933b74e1f41"),
    "ZENODO_PUBLICATION_RECEIPT_v0.62.17.json": (35615, "b439eef9dcd23b6c39dcf902f04de7e22f30ad1de3189c6c8c50fefe3ec52738"),
}

def identity(data):
    return {"bytes": len(data), "sha256": sha256(data).hexdigest()}

class Assets(HTMLParser):
    def __init__(self, tag):
        super().__init__()
        self.tag, self.names, self.digests = tag, set(), {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        href = attrs.get("href", "")
        if tag == "a" and f"/releases/download/{self.tag}/" in href:
            self.names.add(unquote(href.rsplit("/", 1)[1]))
        if tag == "clipboard-copy":
            label = attrs.get("aria-label", "")
            prefix = "Copy to clipboard digest for "
            if label.startswith(prefix):
                self.digests[label[len(prefix):]] = attrs.get("value")

def main():
    session = requests.Session()
    session.trust_env = False
    session.auth = None
    session.headers.clear()
    session.headers["User-Agent"] = "PMI-Anonymous-CLP-Inventory-Replay/1.0"
    receipts = {}
    evidence = []
    for name, pin in PINNED.items():
        raw = (ROOT / name).read_bytes()
        fact = identity(raw)
        assert (fact["bytes"], fact["sha256"]) == pin, name
        receipts[name.split("_")[0]] = json.loads(raw)
        evidence.append({"path": name, **fact})
    old_path = ROOT / "GITHUB_PUBLICATION_RECEIPT_v0.62.16.json"
    old_raw = old_path.read_bytes()
    old = json.loads(old_raw)
    evidence.append({"path": old_path.name, **identity(old_raw)})
    github = []
    for version, expected in (
        ("v0.62.16", old["anonymous_asset_readback"]["entries"]),
        ("v0.62.17", receipts["GITHUB"]["anonymous_readback"]),
    ):
        url = f"{BASE}/releases/expanded_assets/{version}"
        response = session.get(url, timeout=(15, 45))
        response.raise_for_status()
        parser = Assets(version)
        parser.feed(response.text)
        assert parser.names == {row["name"] for row in expected}, version
        assert len(parser.names) == (112 if version == "v0.62.16" else 121)
        for row in expected:
            assert parser.digests.get(row["name"]) == "sha256:" + row["sha256"], row["name"]
        github.append({"version": version, "inventory_url": url,
                       "assets": len(expected), "all_names_and_sha256_digests_unchanged": True,
                       "byte_count_from_bound_full_body_receipt": sum(row["bytes"] for row in expected),
                       "inventory_response": identity(response.content)})
    zenodo = []
    for record_id in (22231858, 22303203):
        response = session.get(f"https://zenodo.org/api/records/{record_id}", timeout=(15, 45))
        response.raise_for_status()
        record = response.json()
        assert record["metadata"]["access_right"] == "open"
        assert len(record["files"]) == 100
        if record_id == 22303203:
            expected = {row["name"]: row for row in receipts["ZENODO"]["anonymous_readback"]}
            assert {row["key"] for row in record["files"]} == set(expected)
            assert all(row["size"] == expected[row["key"]]["bytes"] for row in record["files"])
            assert str(record["conceptrecid"]) == "22059707"
            assert record["metadata"]["version"] == "0.62.17"
        zenodo.append({"record_id": record_id, "access": "open", "file_count": 100,
                       "version": record["metadata"]["version"],
                       "total_bytes": sum(row["size"] for row in record["files"]),
                       "inventory": identity(response.content)})
    result = {"schema": "clp-public-lineage-recheck/v1", "status": "pass",
              "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "authentication": "none", "credentials_recorded": False,
              "scope": "Fresh public inventories/digests; full-body file checks are the exact pinned receipts, not repeated downloads.",
              "github_api_rate_limit_workaround": "Public expanded-assets HTML with exact per-file SHA-256 digests; no authentication or API retries.",
              "receipts": evidence, "github": github, "zenodo": zenodo,
              "native_clp_pdfs": receipts["ZENODO"]["clp_reader_route_readback"],
              "predecessor_full_inventory_preservation_receipt": receipts["ZENODO"]["predecessor"]}
    target = ROOT / "backend/course-capsule-v1/validation/CLP_PUBLIC_LINEAGES_FINAL_20260904.json"
    target.write_bytes((json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())
    print(json.dumps({"status": "pass", "github_assets": [112, 121], "zenodo_files": [100, 100], "receipt": identity(target.read_bytes())}))

if __name__ == "__main__":
    main()
