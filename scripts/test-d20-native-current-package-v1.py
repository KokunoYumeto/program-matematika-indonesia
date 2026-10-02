"""Replay the shipped D20 metadata consumer offline, without producer caches."""
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("d20_package_replay", ROOT / "scripts/d20-native-ledger-v1.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def main():
    expected = json.loads((ROOT / m.BASE / "tests.json").read_bytes())
    with tempfile.TemporaryDirectory(prefix="d20-offline-consumer-") as temporary:
        projection, first = m.build(ROOT, Path(temporary) / "first")
        _, second = m.build(ROOT, Path(temporary) / "second")
        assert first == second == expected["outputs"], "D20 metadata replay differs"
        for name, identity in first.items():
            assert m.fact((ROOT / m.BASE / "site" / name).read_bytes()) == identity
        assert len([row for row in projection["rows"] if row["kind"] == "segments"]) == 2196
        assert projection["semantic_canon_review"] is False
        assert projection["native_book_rebuilt"] is False
    print(json.dumps({"state": "pass", "outputs_reproduced": len(first),
                      "network_used": False, "producer_archives_required": False,
                      "native_book_rebuilt": False, "semantic_canon_review": False}))


if __name__ == "__main__":
    main()
