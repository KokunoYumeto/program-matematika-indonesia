#!/usr/bin/env python3
"""Bounded fail-closed tests; no network, corpus writes or duplicated archives."""
import argparse
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys


def fact(path):
    data=path.read_bytes()
    return {"name":path.name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--package",type=Path,required=True)
    ap.add_argument("--source-zip",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    builder=args.package/"tools/build_judson_candidate.py"
    sys.path.insert(0,str(builder.parent.resolve()))
    spec=importlib.util.spec_from_file_location("judson_frozen_boundary_test",builder)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results=[]

    class SyntheticArchive:
        def stat(self):
            return SimpleNamespace(st_size=module.ZIP_BYTES)

    with patch.object(module,"sha256_file",return_value="0"*64), patch.object(module.zipfile,"ZipFile",side_effect=AssertionError("must not open changed authority")):
        try:
            module.Native(SyntheticArchive())
        except RuntimeError as error:
            assert str(error)=="public SOURCE_BACKEND.zip bytes/hash mismatch"
            results.append({"test":"same_size_wrong_digest","result":"rejected_before_archive_read","method":"synthetic same-size stat and digest fault injection; real Native constructor"})
        else:
            raise AssertionError("wrong hash accepted")

    missing=args.report.parent/"nonexistent-replay-input-20260831"
    output=args.report.parent/"rejected-build-must-not-exist-20260831"
    assert not missing.exists() and not output.exists()
    with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
        try:
            module.build(SimpleNamespace(output=output,central_root=missing,source_zip=args.source_zip,route_evidence=None))
        except FileNotFoundError as error:
            assert Path(error.filename)==(missing/module.CONTRACT).resolve()
            assert not output.exists()
            results.append({"test":"missing_frozen_central_contract","result":"rejected_before_output_creation","method":"real builder, absent exact required contract; no fixture files created"})
        else:
            raise AssertionError("missing contract accepted")

    for name,expected in module.EXACT_TOOLS.items():
        f=fact(args.package/"tools"/name)
        assert (f["bytes"],f["sha256"])==expected
    for name,expected in module.EXACT_SCHEMAS.items():
        f=fact(args.package/"schema"/name)
        assert (f["bytes"],f["sha256"])==expected
    assert (args.package/module.ROUTE_INPUT).exists()
    for name,expected in module.CENTRAL_FACTS.items():
        f=fact(args.package/"frozen-central"/name)
        assert (f["bytes"],f["sha256"])==expected
    report={"schema_id":"interlanguage/judson-public-replay-boundary-qa/v1","status":"pass",
        "created_utc":datetime.now(timezone.utc).isoformat(),"builder":fact(builder),"validator":fact(Path(__file__)),
        "negative_probes":results,"unchanged_tools":2,"unchanged_schemas":6,"bundled_central_prerequisites":2,
        "bundled_route_prerequisite":fact(args.package/module.ROUTE_INPUT),
        "public_native_archive_required":True,"native_archive_copy_created":False,"network_requests":0,
        "test_fixture_files_created":0,"package_or_owner_writes":0,
        "scope":"fail-closed input boundaries and packaged prerequisite availability; native/build A-B replay is separate"}
    args.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"status":"pass","report":fact(args.report)},sort_keys=True))


if __name__=="__main__":
    main()
