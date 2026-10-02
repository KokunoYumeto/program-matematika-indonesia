"""Replay the shipped D20 metadata consumer offline, without producer caches."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import shutil

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("d20_package_replay", ROOT / "scripts/d20-native-ledger-v1.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-plan', type=Path)
    args = parser.parse_args()
    expected = json.loads((ROOT / m.BASE / "tests.json").read_bytes())
    with tempfile.TemporaryDirectory(prefix="d20-offline-consumer-") as temporary:
        replay_root = ROOT
        if args.package_plan:
            manifest = json.loads(args.package_plan.read_bytes())
            included = {row['path']: row for row in manifest['files']}
            lock = json.loads((ROOT / m.BASE / 'source-lock.json').read_bytes())
            required = [m.BASE / name for name in ['source-lock.json', 'intake-audit.json', 'intake-seal.json']]
            required += [Path(row['path']) for row in lock['inputs']]
            required += [m.BASE / 'input' / (Path(row['path']).stem + '.jsonl') for row in lock['source_tables']]
            required += [m.SITE / name for name in ['ledger-ui.js', 'ledger.css']]
            replay_root = Path(temporary) / 'isolated-package-inputs'
            for path in required:
                assert path.as_posix() in included, 'Missing D20 package dependency: ' + path.as_posix()
                row = included[path.as_posix()]
                assert m.fact((ROOT / path).read_bytes()) == {k: row[k] for k in ['bytes', 'sha256']}
                target = replay_root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
        projection, first = m.build(replay_root, Path(temporary) / "first")
        _, second = m.build(replay_root, Path(temporary) / "second")
        assert first == second == expected["outputs"], "D20 metadata replay differs"
        for name, identity in first.items():
            assert m.fact((ROOT / m.BASE / "site" / name).read_bytes()) == identity
        assert len([row for row in projection["rows"] if row["kind"] == "segments"]) == 2196
        assert projection["semantic_canon_review"] is False
        assert projection["native_book_rebuilt"] is False
    print(json.dumps({"state": "pass", "outputs_reproduced": len(first),
                      "isolated_package_plan_checked": bool(args.package_plan),
                      "network_used": False, "producer_archives_required": False,
                      "native_book_rebuilt": False, "semantic_canon_review": False}))


if __name__ == "__main__":
    main()
