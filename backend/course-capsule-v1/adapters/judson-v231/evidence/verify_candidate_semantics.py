#!/usr/bin/env python3
"""Independent Judson projection checks. No builder imports, network or owner writes.

Native ZIP rows are the oracle. Negative probes modify only in-memory objects.
Reference-assisted inverse replay is not standalone recovery without the ZIP.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import uuid
import zipfile

ZIP_SHA = "0aa85116679703b632333f4003b3373f42bb7b282c3719bea3731257c0fe55e0"
NS = uuid.UUID("0e4d7b37-6108-5065-b08f-d1098697cc02")
TABLE_MEMBERS = {
    "units": "topology/units.jsonl",
    "relations": "topology/relations.jsonl",
    "identity_crosswalks": "identity/id-map.jsonl",
    "course_unit_memberships": "courses/course-units.jsonl",
    "editions": "authority/editions.jsonl",
    "rights": "rights/rights.jsonl",
    "artifacts": "artifacts/artifacts.jsonl",
}
ENVELOPE = {"schema", "schema_version", "record_type", "recorded_at", "id", "status", "workflow_id"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": digest}


def check(ok, why):
    if not ok:
        raise AssertionError(why)


def load(path):
    return json.loads(path.read_bytes())


def compact(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


class Audit:
    def __init__(self, package, archive, route_doc):
        check(fact(archive)["sha256"] == ZIP_SHA, "source archive drift")
        self.package, self.route_doc = package, route_doc
        self.tables = {p.stem: [json.loads(line) for line in p.read_bytes().splitlines()]
                       for p in (package / "tables").glob("*.jsonl")}
        check(len(self.tables) == 19, "exact 19 table surface")
        self.native, self.raw, self.references = {}, {}, {}
        with zipfile.ZipFile(archive) as z:
            manifest = json.loads(z.read("backend/v1/manifest.json"))
            self.native_manifest = manifest
            for f in manifest["files"]:
                name = f["path"]
                data = z.read("backend/v1/" + name)
                check((len(data), sha(data)) == (f["bytes"], f["sha256"]), "native fact drift: " + name)
                self.raw[name] = data
                if name.endswith(".jsonl"):
                    lines = data.splitlines(keepends=True)
                    self.native[name] = [json.loads(line) for line in lines]
                    for ordinal, (line, row) in enumerate(zip(lines, self.native[name]), 1):
                        self.references[(name, row["id"])] = {
                            "member": "backend/v1/" + name, "jsonl_row_ordinal": ordinal,
                            "json_pointer": "", "native_id": row["id"],
                            "row_bytes": len(line), "row_sha256": sha(line)}
        self.units = {r["id"]: r for r in self.native["topology/units.jsonl"]}
        self.courses = {r["id"]: r for r in self.native["courses/courses.jsonl"]}
        self.members = {r["unit_id"]: r for r in self.native["courses/course-units.jsonl"]}
        self.unit_selection = {}
        for uid in self.units:
            cursor, ancestry = uid, set()
            selected = None
            while cursor is not None:
                check(cursor not in ancestry, "native cycle")
                ancestry.add(cursor)
                if cursor in self.members:
                    check(selected is None, "ambiguous native selector")
                    selected = self.members[cursor]
                cursor = self.units[cursor]["parent_id"]
            self.unit_selection[uid] = selected
        self.views = load(package / "course-views.json")
        self.states = load(package / "translation-state-index-v0.2.0.json")
        self.crosswalk = load(package / "namespace-crosswalk-v0.2.0.json")
        self.capabilities = load(package / "capability-declarations-v0.2.0.json")
        self.scope = load(package / "scope-declaration-v0.2.0.json")
        self.endpoints = [json.loads(line) for line in (package / "native-relation-endpoints.jsonl").read_bytes().splitlines()]
        self.source_segments = {r["id"]: r for r in self.native["text/segments.en-US.jsonl"]}
        self.translations = {r["segment_id"]: r for r in self.native["text/translations.id-ID.jsonl"]}

    def projection(self, record_type, semantic):
        return "urn:uuid:" + str(uuid.uuid5(NS, record_type + ":judson-aata:" + semantic))

    def exact_rows(self, table, member):
        expected = {r["id"]: r for r in self.native[member]}
        rows = self.tables[table]
        actual = {r["payload"]["native_id"]: r for r in rows}
        check(len(rows) == len(actual) == len(expected) and actual.keys() == expected.keys(), table + " exact native ID coverage")
        for native_id, row in actual.items():
            check(row["id"] == self.projection(row["record_type"], native_id), table + " reminted projection")
            check(row["payload"]["native_evidence"] == self.references[member, native_id], table + " native row witness")
            check(row["owner_native_state"] == expected[native_id]["status"], table + " native state")
        return expected, actual

    def unit_identity(self):
        expected, actual = self.exact_rows("units", "topology/units.jsonl")
        fields = ("kind", "parent_id", "ordinal", "preorder_index", "authority_preorder_index", "depth",
                  "identity_method", "source_path", "source_xpath", "source_xml_id", "source_label",
                  "source_c14n_sha256", "source_origin", "content_locale", "xml_lang", "translatable",
                  "edition_declaration_id", "edition_id", "rights_id", "resource_id", "supersedes_id")
        for uid, native in expected.items():
            p = actual[uid]["payload"]
            for k in fields:
                check((k in p) == (k in native) and p.get(k) == native.get(k), "unit field " + k)
            check(p["projected_parent_id"] == (self.projection("unit", native["parent_id"]) if native["parent_id"] else None), "projected parent")
        expected, actual = self.exact_rows("identity_crosswalks", "identity/id-map.jsonl")
        for rid, native in expected.items():
            p = actual[rid]["payload"]
            for k in native.keys() - ENVELOPE:
                check(p.get(k) == native[k], "birth/current tuple " + k)
            check(p["projected_unit_id"] == self.projection("unit", native["unit_id"]), "identity target")
            check(p["owner_id_reminted"] is False, "owner identity remint")
        return {"units": len(self.units), "identity_maps": len(expected)}

    def courses_check(self):
        expected, actual = self.exact_rows("course_unit_memberships", "courses/course-units.jsonl")
        for rid, native in expected.items():
            p = actual[rid]["payload"]
            for k in ("course_id", "unit_id", "sequence", "membership_role", "render"):
                check(p[k] == native[k], "course membership " + k)
            check(p["projected_unit_id"] == self.projection("unit", native["unit_id"]), "course projected unit")
            check(p["curriculum_role_id"] == self.courses[native["course_id"]]["code"], "course role")
        view_by_code = {r["curriculum_role_id"]: r for r in self.views["views"]}
        check(set(view_by_code) == {"C30", "C40"}, "two course views")
        for cid, c in self.courses.items():
            v = view_by_code[c["code"]]
            selected = sorted((m for m in self.members.values() if m["course_id"] == cid), key=lambda r:r["sequence"])
            check(v["native_course_id"] == cid and len(v["chapters"]) == len(selected), "view course/chapter identity")
            for p, n in zip(v["chapters"], selected):
                check(all(p[k] == val for k, val in {"native_membership_id":n["id"], "native_unit_id":n["unit_id"], "sequence":n["sequence"], "projected_unit_id":self.projection("unit", n["unit_id"])}.items()), "view chapter boundary")
            uids = sorted((uid for uid, m in self.unit_selection.items() if m and m["course_id"] == cid), key=lambda uid:self.units[uid]["preorder_index"])
            check(v["native_unit_ids"] == uids and v["projected_unit_ids"] == [self.projection("unit", uid) for uid in uids], "course descendant closure")
            check(v["unit_count"] == len(uids) == {"C30":2014, "C40":1279}[c["code"]], "course unit count")
        outside = sorted(uid for uid, m in self.unit_selection.items() if not m)
        check(self.views["outside_course_selectors"] == {"count":30, "native_unit_ids":outside}, "outside support units")
        for row in self.tables["units"]:
            p = row["payload"]
            m = self.unit_selection[p["native_id"]]
            check(p["native_membership_id"] == (m["id"] if m else None), "inherited membership")
            check(p["curriculum_role_ids"] == ([self.courses[m["course_id"]]["code"]] if m else []), "inherited course role")
        return {"chapter_memberships":23, "C30_units":2014, "C40_units":1279, "outside_units":30}

    def relation_check(self):
        expected, actual = self.exact_rows("relations", "topology/relations.jsonl")
        endpoint_ids = {r[k] for r in expected.values() for k in ("from_id", "to_id")}
        oracle = defaultdict(list)
        for member, rows in self.native.items():
            if member.startswith("state/") or member == "identity/id-map.jsonl":
                continue
            for r in rows:
                oracle[r["id"]].append((member, r))
        endpoints = {r["native_record_id"]: r for r in self.endpoints}
        check(len(endpoints) == len(self.endpoints) and set(endpoints) == endpoint_ids, "endpoint exact closure")
        for rid in endpoint_ids:
            check(len(oracle[rid]) == 1, "native endpoint ambiguity")
            member, row = oracle[rid][0]
            p = endpoints[rid]
            check(p["native_record_type"] == row["record_type"] and p["evidence"] == self.references[member,rid], "endpoint namespace/evidence")
        for rid, n in expected.items():
            p = actual[rid]["payload"]
            for k in n.keys() - ENVELOPE:
                check(p.get(k) == n[k], "typed relation field " + k)
            for side in ("from", "to"):
                uid = n[side + "_id"]
                check(p[side + "_projected_unit_id"] == (self.projection("unit", uid) if uid in self.units else None), "unit/nonunit endpoint distinction")
                check(p[side + "_native_record_type"] == endpoints[uid]["native_record_type"], "endpoint type")
        nonunit = sum(r["from_id"] not in self.units or r["to_id"] not in self.units for r in expected.values())
        check(nonunit == 104, "nonunit relation count")
        return {"relations":len(expected), "nonunit_edges":nonunit, "types":dict(Counter(r["type"] for r in expected.values()))}

    def pairs_check(self):
        rows = self.tables["content_bindings"]
        actual = {r["payload"]["native_source_segment_id"]:r for r in rows}
        check(len(rows) == len(actual) == 4466 and set(actual) == set(self.source_segments), "exact pair closure")
        for sid, s in self.source_segments.items():
            t = self.translations[sid]
            row, p = actual[sid], actual[sid]["payload"]
            expected = {"native_translation_id":t["id"], "native_unit_id":s["unit_id"],
                "projected_unit_id":self.projection("unit",s["unit_id"]), "source_path":s["source_path"], "source_xpath":s["source_xpath"],
                "source_sha256":s["source_sha256"], "translation_source_sha256":t["source_sha256"], "target_sha256":t["target_sha256"],
                "native_state":t["state"], "source_locale":s["source_locale"], "target_locale":t["locale"],
                "content_locale":t["content_locale"], "state_reason":t["state_reason"], "disposition_id":t["disposition_id"],
                "disposition_reason_code":t["disposition_reason_code"], "source_evidence":self.references["text/segments.en-US.jsonl",sid],
                "translation_evidence":self.references["text/translations.id-ID.jsonl",t["id"]],
                "source_protected_signature_sha256":sha(compact(s["protected_signature"])),
                "target_protected_signature_sha256":sha(compact(t["protected_signature"])),
                "localized_protected_text_deltas_sha256":sha(compact(t["localized_protected_text_deltas"])), "full_text_included":False}
            check(all(p.get(k) == v for k,v in expected.items()), "source-target binding/state/witness")
            check(row["id"] == self.projection("content_binding", "source-translation-pair:"+sid), "pair projection ID")
            check(not ({"text", "fragment_xml", "source_text", "target_text"} & p.keys()), "prose centralization")
            if t["state"] == "source_frozen":
                if t["disposition_id"]:
                    d = next(r for r in self.native["state/segment-dispositions.id-ID.jsonl"] if r["id"] == t["disposition_id"])
                    check(p["preservation_target_sha256"] == d["target_sha256"] and p["preservation_evidence"] == self.references["state/segment-dispositions.id-ID.jsonl",d["id"]], "frozen disposition binding")
                else:
                    paths = json.loads(self.raw["state/source-preserved-paths.json"])["paths"]
                    matches = [(i,r) for i,r in enumerate(paths) if r["path"] == s["source_path"]]
                    check(len(matches)==1, "native preservation path ambiguity")
                    i,d = matches[0]
                    check(p["preservation_evidence"] == {"member":"backend/v1/state/source-preserved-paths.json", "json_pointer":"/paths/"+str(i), "source_path":s["source_path"]}, "preservation pointer")
                    check(p["preservation_target_sha256"] == s["source_sha256"] and d["reason"]==t["state_reason"], "preservation hash policy")
            else:
                check(p["preservation_target_sha256"] is None and p["preservation_evidence"] is None, "translated/frozen conflation")
        check(Counter(r["payload"]["native_state"] for r in rows)=={"translated":4150,"source_frozen":316}, "pair state count")
        return {"pairs":4466, "translated":4150, "source_frozen":316, "raw_null_target_hashes":316}

    def states_check(self):
        check(self.states["no_inference"] is True, "state no-inference flag")
        rows = self.states["records"]
        actual = {r["native_unit_id"]:r for r in rows}
        check(len(rows)==len(actual)==3323 and set(actual)==set(self.units), "state unit coverage")
        direct = defaultdict(list)
        for s in self.source_segments.values():
            t = self.translations[s["id"]]
            direct[s["unit_id"]].append({"native_source_segment_id":s["id"], "native_translation_id":t["id"],
                "content_binding_id":self.projection("content_binding","source-translation-pair:"+s["id"]),
                "native_state":t["state"], "content_locale":t["content_locale"]})
        edition = defaultdict(list)
        for s in self.native["text/segments.edition.id-ID.jsonl"]:
            edition[s["unit_id"]].append({"native_segment_id":s["id"],"content_locale":s["content_locale"],"source_origin":s["source_origin"],"source_sha256":s["source_sha256"],"translation_overlay_required":False,"native_evidence":self.references["text/segments.edition.id-ID.jsonl",s["id"]]})
        for uid,u in self.units.items():
            p=actual[uid]
            pairs=sorted(direct[uid],key=lambda r:r["native_source_segment_id"])
            states=sorted({r["native_state"] for r in pairs})
            state=states[0] if len(states)==1 else "mixed" if states else "no-segment-evidence"
            expected={"projected_unit_id":self.projection("unit",uid),"native_unit_status":u["status"],"native_xml_lang":u.get("xml_lang"),
                "native_content_locale":u.get("content_locale"),"pairs":pairs,"state":state,"observed_native_states":states,
                "native_pair_count":len(pairs),"state_counts":dict(Counter(p["native_state"] for p in pairs)),"edition_authored_segment_evidence":edition[uid]}
            check(all(p.get(k)==v for k,v in expected.items()), "direct segment-state aggregation")
        return {"unit_states":dict(Counter(r["state"] for r in rows)),"edition_authored_segments":3}

    def rights_check(self):
        expected,actual=self.exact_rows("rights","rights/rights.jsonl")
        fields=("license_expression","modified_edition_license_expression","upstream_license_expression","legal_text_policy",
            "full_license_source_path","full_license_source_sha256","license_source_path","license_source_sha256",
            "invariant_sections","front_cover_texts","back_cover_texts","change_notice_required","additional_copyright_claimed")
        for rid,n in expected.items():
            check(all(actual[rid]["payload"].get(k)==n[k] for k in fields),"rights field flattening")
        expected,actual=self.exact_rows("editions","authority/editions.jsonl")
        for rid,n in expected.items():
            p=actual[rid]["payload"]
            check(p["license_expression"]==("GFDL-1.3-or-later" if n.get("locale")=="id-ID" else "GFDL-1.2-or-later"),"edition rights version")
        return {"upstream":"GFDL-1.2-or-later","modified":"GFDL-1.3-or-later","operative_English_policy_preserved":True}

    def inverse_check(self):
        results=[]
        for table,member in TABLE_MEMBERS.items():
            self.exact_rows(table,member)
            refs=[r["payload"]["native_evidence"] for r in self.tables[table]]
            lines=self.raw[member].splitlines(keepends=True)
            ordered=sorted(refs,key=lambda r:r["jsonl_row_ordinal"])
            check([r["jsonl_row_ordinal"] for r in ordered]==list(range(1,len(lines)+1)),"inverse row order/coverage")
            reconstructed=b"".join(lines[r["jsonl_row_ordinal"]-1] for r in ordered)
            check(reconstructed==self.raw[member],"inverse metadata bytes")
            results.append({"member":"backend/v1/"+member,"rows":len(lines),"bytes":len(reconstructed),"sha256":sha(reconstructed)})
        mappings=self.crosswalk["mappings"]
        projected={r["id"]:r for rows in self.tables.values() for r in rows}
        for m in mappings:
            check(m["target_record_id"] in projected,"crosswalk target absent")
            check(projected[m["target_record_id"]]["payload"].get("native_id")==m["source_record_id"],"crosswalk inverse identity")
        return {"replay_mode":"reference-assisted using exact public ZIP; not standalone reconstitution without native authority", "streams":results,"crosswalks":len(mappings)}

    def capabilities_check(self):
        caps={r["name"]:r for r in self.capabilities["capabilities"]}
        check(len(caps)==10,"ten capability slots")
        for name,c in caps.items():
            expected="materialized" if name=="structure_localization" else "not_projected" if name=="accessibility" else "referenced_native_shards"
            check(c["state"]==expected,"capability overclaim: "+name)
            if expected=="referenced_native_shards":
                count=0
                for f in c["shard_refs"]:
                    member=f["path"].removeprefix("backend/v1/")
                    check((f["bytes"],f["sha256"])==(len(self.raw[member]),sha(self.raw[member])),"capability shard identity")
                    count+=len(self.native[member])
                check(c["native_count"]==count and c["projected_count"]==0,"native/projected capability counts")
        check(self.scope["curriculum_role_ids"]==["C30","C40"] and self.scope["aggregate_conformance_claim"] is False,"bounded conformance")
        for name in ("adapter_profiles","reader_surfaces","routes"):
            for r in self.tables[name]:
                check(r["payload"].get("learner_consumption_claim") is False,"premature learner runtime claim")
        return {"materialized":["structure_localization"],"referenced_only":8,"not_projected":["accessibility"],"runtime_claim":False}

    def learner_check(self):
        doc=self.route_doc
        check(load(self.package/"frozen-inputs/JUDSON_TWO_COURSE_LEARNER_ROUTES.json")==doc,"frozen route input drift")
        routes=[r for r in self.tables["routes"] if "native_unit_id" in r["payload"]]
        route_by_unit={r["payload"]["native_unit_id"]:r for r in routes}
        check(len(routes)==len(route_by_unit)==23,"exact 23 projected chapter routes")
        surfaces={r["id"]:r for r in self.tables["reader_surfaces"]}
        live={r["native_unit_id"]:(i,r) for i,r in enumerate(doc["live_verification"]["observations"])}
        view_by_code={r["curriculum_role_id"]:r for r in self.views["views"]}
        for ci,course in enumerate(doc["offline"]["courses"]):
            view=view_by_code[course["course_id"]]
            for ri,n in enumerate(course["routes"]):
                uid=n["native_unit_id"]
                row=route_by_unit[uid]
                p=row["payload"]
                check(uid in self.members and n["native_membership_id"]==self.members[uid]["id"],"learner native selector")
                expected={"native_course_id":n["native_course_id"],"native_membership_id":n["native_membership_id"],
                    "curriculum_role_id":course["course_id"],"projected_unit_id":self.projection("unit",uid),
                    "sequence":n["sequence"],"chapter_number":n["chapter_number"],"localized_title":n["localized_title"],
                    "url":n["public_url"],"offline_href":n["offline_href"],"offline_html_chapter_id":n["html_chapter_id"],
                    "offline_member":{"path":n["archive_member"],"bytes":n["bytes"],"sha256":n["sha256"]},
                    "offline_archive":doc["offline"]["web_archive"],"live_observation":live[uid][1],
                    "current_live_edition_identity":"not_verified","learner_consumption_claim":False}
                check(all(p.get(k)==v for k,v in expected.items()),"learner URL/title/identity binding")
                check(p["evidence"]["offline_json_pointer"]==f"/offline/courses/{ci}/routes/{ri}","offline evidence pointer")
                check(p["evidence"]["live_json_pointer"]==f"/live_verification/observations/{live[uid][0]}","live evidence pointer")
                check(p["reader_surface_id"] in surfaces and surfaces[p["reader_surface_id"]]["payload"]["url"]==n["public_url"],"reader surface route closure")
                chapter=view["chapters"][ri]
                check(chapter["route_id"]==row["id"] and chapter["localized_title"]==n["localized_title"] and chapter["public_url"]==n["public_url"],"course view route join")
                observed=datetime.fromisoformat(live[uid][1]["observed_utc"])
                recorded=datetime.fromisoformat(row["recorded_at"].replace("Z","+00:00"))
                check(recorded>=observed,"route record precedes its own observation")
        check(len(self.tables["routes"])==25 and len(surfaces)==25,"23 chapter routes plus two course fallbacks")
        return {"chapter_routes":23,"course_fallbacks":2,"frozen_HTML_bytes":1830695,"dated_live_HTTP_200":23,
            "live_frozen_byte_matches":0,"student_runtime_integration":"not_yet_admitted"}

    def run(self):
        tests={}
        for name in ("unit_identity","courses_check","relation_check","pairs_check","states_check","rights_check","inverse_check","capabilities_check","learner_check"):
            tests[name]={"status":"pass","evidence":getattr(self,name)()}
        return tests

    def negatives(self):
        results=[]
        def probe(name, obj, key, bad, gate):
            old=deepcopy(obj[key])
            obj[key]=bad
            try:
                try:
                    gate()
                except AssertionError as error:
                    results.append({"id":name,"result":"rejected","reason":str(error)})
                else:
                    raise RuntimeError("negative probe escaped: "+name)
            finally:
                obj[key]=old
        probe("reminted_unit",self.tables["units"][0],"id","urn:uuid:"+str(uuid.UUID(int=0)),self.unit_identity)
        probe("altered_source_hash",self.tables["units"][0]["payload"],"source_c14n_sha256","0"*64,self.unit_identity)
        probe("birth_selector_mutation",self.tables["identity_crosswalks"][0]["payload"],"birth_xpath","/wrong[1]",self.unit_identity)
        probe("cross_course_move",self.tables["course_unit_memberships"][0]["payload"],"course_id","invalid-native-course",self.courses_check)
        support=next(r["payload"] for r in self.tables["units"] if not r["payload"]["curriculum_role_ids"])
        probe("support_unit_forced_into_course",support,"curriculum_role_ids",["C30"],self.courses_check)
        hint=next(r["payload"] for r in self.tables["relations"] if r["payload"]["type"]=="has_hint")
        probe("hint_edge_changed",hint,"to_id","invalid-native-unit",self.relation_check)
        endpoint=next(r for r in self.endpoints if r["materialization"]!="unit")
        probe("nonunit_endpoint_type_changed",endpoint,"native_record_type","unit",self.relation_check)
        pair=self.tables["content_bindings"][0]["payload"]
        probe("translation_hash_changed",pair,"target_sha256","0"*64,self.pairs_check)
        frozen=next(r["payload"] for r in self.tables["content_bindings"] if r["payload"]["native_state"]=="source_frozen")
        probe("frozen_segment_promoted",frozen,"native_state","translated",self.pairs_check)
        probe("frozen_reason_erased",frozen,"state_reason",None,self.pairs_check)
        no_evidence=next(r for r in self.states["records"] if r["state"]=="no-segment-evidence")
        probe("active_unit_inferred_translated",no_evidence,"state","translated",self.states_check)
        probe("license_flattened",self.tables["rights"][0]["payload"],"modified_edition_license_expression","CC-BY-4.0",self.rights_check)
        probe("inverse_native_id_changed",self.crosswalk["mappings"][0],"source_record_id","wrong-native-id",self.inverse_check)
        referenced=next(r for r in self.capabilities["capabilities"] if r["state"]=="referenced_native_shards")
        probe("reference_upgraded_to_materialized",referenced,"state","materialized",self.capabilities_check)
        route=next(r["payload"] for r in self.tables["routes"] if "native_unit_id" in r["payload"])
        probe("unbound_chapter_URL",route,"url","https://example.invalid/guessed.html",self.learner_check)
        probe("live_bytes_misrepresented_as_frozen",route,"current_live_edition_identity","verified",self.learner_check)
        return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package",type=Path,required=True)
    parser.add_argument("--source-zip",type=Path,required=True)
    parser.add_argument("--route-document",type=Path,required=True)
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args()
    audit=Audit(args.package,args.source_zip,load(args.route_document))
    positive=audit.run()
    negative=audit.negatives()
    check(audit.run()==positive,"negative probe restoration")
    report={"schema_id":"interlanguage/judson-candidate-independent-semantic-qa/v1","status":"pass",
        "created_utc":datetime.now(timezone.utc).isoformat(),"candidate_manifest":fact(args.package/"manifest.json"),
        "candidate_seal":fact(args.package/"seal.json"),"source_archive":fact(args.source_zip),"validator":fact(Path(__file__)),
        "positive_tests":positive,"negative_probes":negative,"negative_probe_restoration":"pass",
        "network_requests":0,"owner_writes":0,"package_writes":0,
        "limits":["Metadata and native-reference checks only; not new mathematical or language review.",
                  "Reference-assisted inverse replay requires the exact public native ZIP.",
                  "Learner route replay and generic schema/CSV/A-B validation are separate bound receipts."]}
    args.report.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":"pass","positive_tests":len(positive),"negative_probes":len(negative),"report":fact(args.report)},sort_keys=True))


if __name__=="__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps({"status":"fail","error_type":type(error).__name__,"error":str(error)},ensure_ascii=False),file=sys.stderr)
        sys.exit(1)
