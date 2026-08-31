#!/usr/bin/env python3
"""Seal exact manager-owned Judson evidence. Never publishes or edits a corpus."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
NAMES=[
    "NATIVE_AUTHORITY_CHECK.json","NATIVE_PUBLIC_REPLAY_RECEIPT.json","verify_native_authority.py",
    "JUDSON_TWO_COURSE_LEARNER_ROUTES.json","replay_judson_two_course_learner_routes.py","ROOT_LEARNER_ROUTE_REPLAY.json",
    "verify_candidate_semantics.py","SEMANTIC_QA_ROUTES2.json","verify_replay_boundaries.py","REPLAY_BOUNDARY_QA_ROUTES2.json",
    "ROOT_GENERIC_VALIDATION_ROUTES2.json","INDEPENDENT_DESIGN_REVIEW.json","CANDIDATE_HANDOFF_ROUTES2.json",
    "JUDSON_CONTRIBUTION_TO_GLOBAL_BACKEND.md","SEMANTIC_QA_REQUIREMENTS.json","seal_manager_handoff.py",
    "build-a-routes2/manifest.json","build-a-routes2/seal.json","build-a-routes2/PACKAGE_CHECKSUMS.sha256",
    "build-a-routes2/tools/build_judson_candidate.py","build-a-routes2/README.md"]


def fact(name):
    data=(ROOT/name).read_bytes()
    assert not re.search(rb"(?i)(?:[a-z]:[\\/]+Users[\\/]|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9]{20,}|access_token=[A-Za-z0-9]{10,})",data),"private path or credential pattern"
    return {"path":name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}


def doc(name):
    return json.loads((ROOT/name).read_bytes())


def main():
    facts=[fact(name) for name in NAMES]
    byname={f["path"]:f for f in facts}
    generic=doc("ROOT_GENERIC_VALIDATION_ROUTES2.json")
    semantic=doc("SEMANTIC_QA_ROUTES2.json")
    boundary=doc("REPLAY_BOUNDARY_QA_ROUTES2.json")
    learner=doc("ROOT_LEARNER_ROUTE_REPLAY.json")
    native=doc("NATIVE_PUBLIC_REPLAY_RECEIPT.json")
    candidate=doc("CANDIDATE_HANDOFF_ROUTES2.json")
    design=doc("INDEPENDENT_DESIGN_REVIEW.json")
    assert generic["status"]=="PASS" and generic["deterministic_ab"]["byte_identical"]
    assert generic["authorities"]=={"declared":40,"locally_replayed":40}
    assert generic["sidecars"]["csv"]=={"records":17745,"roundtrip":"pass","tables":19}
    assert generic["privacy"]["credential_or_local_path_hits"]==0
    assert semantic["status"]=="pass" and len(semantic["positive_tests"])==9
    assert len(semantic["negative_probes"])==16 and all(p["result"]=="rejected" for p in semantic["negative_probes"])
    assert semantic["candidate_manifest"]["sha256"]==byname["build-a-routes2/manifest.json"]["sha256"]==generic["manifest"]["sha256"]
    assert semantic["validator"]["sha256"]==byname["verify_candidate_semantics.py"]["sha256"]
    assert boundary["status"]=="pass" and len(boundary["negative_probes"])==2
    assert boundary["builder"]["sha256"]==byname["build-a-routes2/tools/build_judson_candidate.py"]["sha256"]
    assert boundary["validator"]["sha256"]==byname["verify_replay_boundaries.py"]["sha256"]
    assert design["scope"]["inspected_builder_sha256"]==boundary["builder"]["sha256"]
    assert design["overall"]["native_preservation_design_defects_identified"]==0
    assert learner["state"]=="PASS" and learner["output"]["chapter_routes"]==23
    assert learner["input_document"]["sha256"]==byname["JUDSON_TWO_COURSE_LEARNER_ROUTES.json"]["sha256"]
    assert learner["replayer"]["sha256"]==byname["replay_judson_two_course_learner_routes.py"]["sha256"]
    assert len(native["commands"])==4 and all(r["exit_code"]==0 for r in native["commands"])
    assert native["post_replay"]["original_archive_files"]==native["post_replay"]["exact_post_replay_matches"]==416
    assert not native["post_replay"]["failures"]
    assert candidate["each_final_build"]["full_tree_sha256"]==generic["deterministic_ab"]["tree_sha256"]
    facts_digest=hashlib.sha256("".join(f"{r['path']}\0{r['bytes']}\0{r['sha256']}\n" for r in sorted(facts,key=lambda x:x["path"])).encode()).hexdigest()
    report={
        "schema_id":"interlanguage/judson-manager-integration-handoff/v1",
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "state":"validated_candidate_ready_for_sole_integrator_not_admitted_or_published",
        "manager_thread_id":"01a01ec1-e685-70d0-b022-211396334723",
        "sole_shared_source_editor_and_publisher":"01a024cd-b2e1-7d73-ad14-ce00f16bfdbc",
        "write_boundary":"manager logbook/candidate only; no corpus-owner or shared hub mutation",
        "central_concept_doi":"10.5281/zenodo.22059707",
        "payload":candidate["each_final_build"],
        "payload_root":"build-a-routes2","deterministic_witness_root":"build-b-routes2",
        "package_id":generic["package_id"],"extension_version":generic["extension_version"],
        "files":facts,"file_identity_set_sha256":facts_digest,
        "file_identity_algorithm":"sha256(sorted path NUL bytes NUL sha256 LF)",
        "materialized_scope":candidate["materialized_scope"],
        "gates":{
            "native_public_package_replay":"four documented commands pass;416original files unchanged",
            "exact_generic_contract":"six unchanged schemas;40/40external facts;19JSONL/CSVpairs;17745records",
            "deterministic_build":"two independently generated 65-file trees byte-identical",
            "independent_semantics":"9positive checks;16negative probes rejected;original state restored",
            "fail_closed_replay_boundaries":"2negative probes pass, including synthetic wrong-hash fault injection",
            "learner_map":"23actual archived chapter routes plus2course fallbacks;root offline replay passes",
            "static_independent_review":"no preservation design defect in exact final builder;its A/B and inverse proof dependencies closed by separate root receipts",
            "privacy":"generic package zero hits;all standalone handoff files zero credential/private-profile path hits"},
        "learner_integration":{
            "join":"course-views.json views[].chapters[].route_id -> tables/routes.jsonl id",
            "show":"Indonesian chapter title, native order, online chapter action and exact downloadable offline WEB edition",
            "live_identity":"23datedHTTP200;0of23matchfrozenbytes;do not conflate accessible live site with exact frozen edition",
            "not_implemented_here":"central student UI consumption,descendantanchors,exerciseengine,masterytracking"},
        "integrator_next_actions":[
            "Recheck the exact payload/receipt identities and admit this additive C30/C40 adapter under the existing unchanged common contract.",
            "Join the two course selectors to their23bound chapter routes in the existing human-facing hub; independently test real UI/data joins without visible browser windows.",
            "Preserve the adapter, root replay/QA receipts and JUDSON_CONTRIBUTION_TO_GLOBAL_BACKEND.md as a substantive addition to the distributed-design findings in the existing central DOI/release lineage.",
            "Publish through the existing sole transaction lane and anonymously verify all newly released files. Do not duplicate or interrupt the already-owned v0.62.14 transaction; choose its appropriate substantive integration boundary.",
            "Return exact central admission/integration/publication receipt identities; tool delivery alone is not acceptance or public preservation."],
        "limits":[
            "No new corpus selection,owner replacement,translation,retranslation,authorcontact,Gitoperation,networkrequest or publication by this manager handoff.",
            "Reference-assisted inverse replay needs the exact native archive;not standalone reconstruction after deleting native inputs.",
            "No new Sageexecution,readerbuild,language/mathematical review,accessibilityconformance or curriculum-wide completion claim.",
            "Only finalroutes2 is an admission input;preliminarybuilds remain unadmitted and unchanged."],
        "goal_state":"active;bounded candidate validation is not completion of the entire curriculum goal",
        "signoff":"Codex on instructions of the user"}
    path=ROOT/"MANAGER_INTEGRATION_HANDOFF_20260831.json"
    assert not path.exists(),"a sealed manager handoff already exists; do not overwrite or dispatch twice"
    path.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":"pass","bound_files":len(facts),"handoff":fact(path.name)},sort_keys=True))


if __name__=="__main__":
    main()
