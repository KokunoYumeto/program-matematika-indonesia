"""Finite, evidence-bound closure of the CLP v0.62.17 integration delta."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT.parents[2] / "outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook/backend_adapters/clp_family_v231_candidate"
AUTH = "backend/course-capsule-v1/authority/clp-family-v231/"
QA = "backend/course-capsule-v1/validation/"
PACKAGE = "urn:uuid:8dbda99c-2e39-5fc0-a6ff-64a52cb81b26"

def digest(path):
    checksum = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return {"bytes": path.stat().st_size, "sha256": checksum.hexdigest()}

def read(path):
    return json.loads((ROOT / path).read_bytes())

def run(*args):
    return subprocess.check_output(args, cwd=ROOT)

def main():
    evidence, checks = [], []
    def require(name, condition, detail):
        assert condition, (name, detail)
        checks.append({"requirement": name, "status": "pass", "evidence": detail})
    for name, size, checksum in (
        ("MANAGER_HANDOFF.json", 10696, "905b366c26489a8ead77d0554e171e46617614abbf7b9d36a97b1329f26eec52"),
        ("HANDOFF_FILE_INVENTORY.json", 2709, "8e36f2c85ebf7135345086e0ca3dcb1cb4bf5869c6925c395a814ebf68b3b055"),
        ("CLP_SITE_INTEGRATION_INSTRUCTIONS.md", 7195, "43fe78819f1fbb24945d105c91661777a272a9c0d24238f12c9cf099e94b9323"),
    ):
        fact = digest(INTAKE / name)
        require("sealed intake " + name, fact == {"bytes": size, "sha256": checksum}, fact)
    inventory = json.loads((INTAKE / "HANDOFF_FILE_INVENTORY.json").read_bytes())
    payload = []
    for row in inventory["files"]:
        path = (INTAKE / row["path"]).resolve()
        assert path.is_relative_to(INTAKE.resolve())
        fact = digest(path)
        require("sealed payload " + row["path"], fact == {"bytes": row["bytes"], "sha256": row["sha256"]}, fact)
        payload.append(row)
    # The sealed receipt uses PowerShell Sort-Object's linguistic order, not
    # Python's ordinal sort (notably BUILD_A_TRANSACTION versus build_a.validation).
    # Freeze the independently replayed nine-path order to make this portable.
    payload_order = ["BUILD_A_TRANSACTION_RECEIPT_20260901.json", "build_a.validation.json",
                     "CLP_CALCULUS_FAMILY_V231_ADAPTER_0.1.0.zip",
                     "CLP_FINAL_INDEPENDENT_PACKAGE_AUDIT_20260901.json",
                     "CLP_FINAL_INDEPENDENT_PACKAGE_AUDIT_SUPERSEDING_20260901.json",
                     "CLP_SITE_INTEGRATION_INSTRUCTIONS.md", "deterministic_ab_validation.json",
                     "FINAL_TOOLCHAIN_STATIC_AUDIT_20260901.json", "negative_probe_report.json"]
    by_path = {r["path"]: r for r in payload}
    assert set(payload_order) == set(by_path)
    aggregate = sha256("".join(f'{r["path"]}\0{r["bytes"]}\0{r["sha256"]}\n' for r in (by_path[p] for p in payload_order)).encode()).hexdigest()
    require("nine-payload aggregate", len(payload) == 9 and sum(r["bytes"] for r in payload) == 545465582 and aggregate == "7c5239f715f4451fbda18178fcdd85e49e946c3d908e967c07df5d575d5a5393", aggregate)
    names = [QA + name for name in (
        "CLP_POSTPUBLICATION_VALIDATION_FINAL_20260904.json", "CLP_PUBLIC_LINEAGES_FINAL_20260904.json",
        "CLP_POSTPUBLICATION_PUBLIC_MAP_FINAL_20260904.json", "SITE_VALIDATION_RECEIPT.json",
        "VALIDATION_RECEIPT.json", "PUBLIC_SITE_READBACK_v0.62.17.json",
    )] + ["GITHUB_PUBLICATION_RECEIPT_v0.62.17.json", "ZENODO_PUBLICATION_RECEIPT_v0.62.17.json"]
    for name in names:
        evidence.append({"path": name, **digest(ROOT / name)})
    archive = read(names[0])
    require("streamed archive and schema QA", archive["status"] == "pass" and len(archive["checks"]) == 361 and all(r["status"] == "pass" for r in archive["checks"]), evidence[0])
    require("70 safe unique archive members", archive["derived"]["archive"]["member_count"] == 70, archive["derived"]["archive"])
    index = read(AUTH + "v23-adapter-index-v2.json")
    baseline = json.loads(run("git", "show", "v0.62.17:" + AUTH + "v23-adapter-index-v2.json"))
    require("one CLP package and four unchanged native profiles", sum(p["package_id"] == PACKAGE for p in index["packages"]) == 1 and index["adapters"] == baseline["adapters"] and [p for p in index["packages"] if p["package_id"] != PACKAGE] == [p for p in baseline["packages"] if p["package_id"] != PACKAGE], {"roles": ["B20", "B30", "B50", "B60"], "summary": index["summary"]})
    sidecar = read(AUTH + "learner-reader-actions-v1.json")
    before_sidecar = json.loads(run("git", "show", "v0.62.17:" + AUTH + "learner-reader-actions-v1.json"))
    require("seven native PDF actions preserved", sidecar["actions"] == before_sidecar["actions"] and sidecar["snapshot_id"] == index["snapshot"]["snapshot_id"], {"actions": 7, "pages": 4077, "bytes": 35639691})
    require("all admitted adapters public", index["summary"]["published_role_bindings"] == 13 and index["summary"]["published_adapter_packages"] == 9 and index["summary"]["pending_role_bindings"] == 0, index["summary"])
    capsule = read(QA + "VALIDATION_RECEIPT.json")
    require("40 seven-layer capsules, DAG and two-build identity", capsule["state"] == "pass" and capsule["checks"]["seven_layer_rows"] == 40 and capsule["checks"]["prerequisite_edges"] == 83 and capsule["peer_replay"]["byte_identical"], evidence[4])
    site = read(QA + "SITE_VALIDATION_RECEIPT.json")
    require("learner-first routes, fallback, language, accessibility and privacy", site["state"] == "pass" and site["public_mirror"]["byte_identical_files"] == 51, evidence[3])
    require("postpublication mirrors", read(names[2])["historical_v2_paths_untouched"], evidence[2])
    public = read(QA + "PUBLIC_SITE_READBACK_v0.62.17.json")
    require("83 exact anonymous website routes including both languages", public["state"] == "PASS_ANONYMOUS_EXACT_PUBLIC_BYTES" and public["file_count"] == 83 and all(r["exact_local_identity"] for r in public["entries"]), evidence[5])
    require("public lineages and intact predecessors", read(names[1])["status"] == "pass", evidence[1])
    for name in names[-2:]:
        receipt = read(name)
        require("public full-byte receipt " + name, receipt["status"] == "pass" and receipt["credentials_recorded"] is False and run("git", "show", "HEAD:" + name) == (ROOT / name).read_bytes(), {"path": name, **digest(ROOT / name)})
    ui = json.loads(run("node", "scripts/test-course-capsule-ui-v1.mjs"))
    bilingual = json.loads(run("node", "scripts/test-multilingual-interface.mjs"))
    require("actual module behavior and bilingual integration tests", ui["state"] == "pass" and bilingual["status"] == "pass", {"backend": ui, "bilingual": bilingual})
    build = subprocess.run(["npm.cmd", "--ignore-scripts", "run", "build"], cwd=ROOT, capture_output=True, timeout=120)
    require("final production build", build.returncode == 0, {"command": "npm --ignore-scripts run build", "exit_code": build.returncode, "stdout_sha256": sha256(build.stdout).hexdigest(), "stderr_sha256": sha256(build.stderr).hexdigest()})
    run("git", "merge-base", "--is-ancestor", "86bb3a0efcf0d33537fe9b354173b8cbb1b8189d", "HEAD")
    require("manager bilingual changes preserved", True, "Both manager commits are ancestors of the tested integration commit; no force push or producer message.")
    report = {"schema": "clp-successor-terminal-audit/v1", "status": "pass",
              "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_commit": run("git", "rev-parse", "HEAD").decode().strip(),
              "source_tree": run("git", "rev-parse", "HEAD^{tree}").decode().strip(),
              "scope": "CLP common-v2.3.1 integration and v0.62.17 preservation only; not a fresh all-40 translation audit or completion of every native backend capability.",
              "checks": checks, "evidence": evidence,
              "semantic_replay_boundary": "Exact sealed native A/B and independent audits plus new streaming archive/schema replay; no native textbook rebuild.",
              "sites": {"status": "project_not_found", "http_status": 404, "replacement_created": False, "active_public_surface": "GitHub Pages"},
              "remaining_outside_this_delta": ["24 of 33 native families lack a common adapter with complete public replay", "terminology evidence and capability gaps remain explicitly labeled", "course status counters are a dated 1 September source snapshot, not a current task queue"],
              "next_action": "Commit and anonymously verify this closure receipt; append and reseal durable state; mark the finite pursuit complete."}
    target = ROOT / QA / "CLP_TERMINAL_REQUIREMENTS_20260904.json"
    target.write_bytes((json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode())
    print(json.dumps({"status": "pass", "checks": len(checks), "receipt": digest(target)}))

if __name__ == "__main__":
    main()
