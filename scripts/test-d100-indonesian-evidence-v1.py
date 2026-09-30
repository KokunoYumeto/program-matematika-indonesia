"""Two complete native-input replays and isolated record-validation negatives."""
from copy import deepcopy
import json
from pathlib import Path
from d100_indonesian_evidence_v1 import ROOT, BASE, build, encoded, fact, validate_record


def main():
    native = ROOT.parent / 'algebraic-geometry-bridge-id'
    first, second = build(native), build(native)
    assert first == second
    for name, data in first.items():
        assert (ROOT / BASE / name).read_bytes() == data, name
    witnesses = [json.loads(line) for line in first['metadata-witnesses.jsonl'].splitlines()]
    term = next(json.loads(row['native_record']) for row in witnesses
                if json.loads(row['native_record'])['entity_class'] == 'term')
    cases = []
    for name, key, value in [('english_record','language','en'),
                             ('unidentified_record','stable_id',''),
                             ('wrong_schema','schema','other')]:
        row = deepcopy(term)
        row[key] = value
        cases.append((name,row))
    wrong = deepcopy(term)
    wrong['payload']['target_language'] = 'en'
    cases.append(('english_payload_despite_id_envelope',wrong))
    blank = deepcopy(term)
    blank['payload']['preferred_target'] = ''
    cases.append(('missing_target_term',blank))
    for name, row in cases:
        try:
            validate_record(row)
        except ValueError:
            continue
        raise AssertionError('Accepted ' + name)
    receipt = {'schema':'d100-indonesian-evidence-replay/1','state':'pass',
               'native_stream_replays':2,'byte_identical':True,
               'files':[fact(name,data) for name,data in sorted(first.items())],
               'negative_fixtures':[name for name,_ in cases],
               'semantic_canon_review':'not_established'}
    (ROOT / BASE / 'replay.json').write_bytes(encoded(receipt,True))
    print(json.dumps({'state':'pass','native_replays':2,'negative_fixtures':len(cases)}))


if __name__ == '__main__':
    main()
