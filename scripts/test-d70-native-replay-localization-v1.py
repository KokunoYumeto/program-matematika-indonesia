"""Check each localized limitation's exact source/target identity and claim scope."""
import copy
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d70-native-replay-v1'
SITE = ROOT / 'docs/backend/d70-replay'
SOURCE = ROOT / 'backend/course-capsule-v1/adapters/d70-capability-v1/data/capabilities.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate(ledger):
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes)
    assert ledger['locale'] == 'id'
    assert ledger['source']['sha256'] == digest(source_bytes)
    assert ledger['source']['bytes'] == len(source_bytes)
    for key in ['mathematical_content_modified', 'native_terminology_canon_review', 'whole_surface_localization_claimed', 'human_review_required_to_continue']:
        assert ledger[key] is False
    rows = ledger['choices']
    assert len(rows) == len(source['limitations']) == 8
    assert len({row['id'] for row in rows}) == 8
    references = {row['id']: row for row in ledger['consulted_references']}
    assert len(references) == 2
    assert all(row['consulted_at'] == '2026-09-30' and row['url'].startswith('https://www.w3.org/WAI/') and row['limitation'] for row in references.values())
    review = (SITE / 'limitations-review.id.html').read_text(encoding='utf-8')
    assert '<html lang="id">' in review
    assert review.count('<blockquote lang="en">') == 8
    assert 'gpt-6.1-sol' in review and 'tingkat upaya Ultra' in review
    for index, row in enumerate(rows, 1):
        assert row['source_text'] == source['limitations'][index - 1]
        assert row['source_sha256'] == digest(row['source_text'].encode('utf-8'))
        assert row['target_sha256'] == digest(row['target_text'].encode('utf-8'))
        assert row['target_text'] != row['source_text']
        assert len(row['target_segments']) == 2 and len(set(row['target_segments'])) == 2
        assert row['human_review_performed'] is False and row['confidence']['calibrated_probability'] is False
        assert row['rationale'] and row['attestation_scope'] and row['rejected_alternatives']
        assert set(row['consulted_passages']).issubset(references)
        for segment in row['target_segments']:
            name, fragment = segment.split('#')
            assert name in ['docs/backend/d70/D70.html', 'docs/backend/d70/D70-pengajar.html']
            assert fragment == f'd70-batas-{index:02}'
            text = (ROOT / name).read_text(encoding='utf-8')
            assert text.count(f'<li id="{fragment}">{html.escape(row["target_text"])}</li>') == 1
            assert '<li>' + html.escape(row['source_text']) + '</li>' not in text
            assert 'id="d70-batas-review"' in text
        assert html.escape(row['source_text']) in review and html.escape(row['target_text']) in review
    assert 'P01-P06' in rows[1]['target_text']
    assert 'enam' in rows[2]['target_text']
    assert '49' in rows[3]['target_text'] and 'CC BY' in rows[3]['target_text']
    assert 'delapan' in rows[4]['target_text']
    assert all(term in rows[6]['target_text'] for term in ['EPUB', 'MathML', 'PDF', 'ToUnicode', 'WCAG', 'teknologi pendukung'])
    assert set(rows[6]['consulted_passages']) == set(references)
    assert 'belum terbukti' in rows[7]['target_text'] and 'full_native_roundtrip: false' in rows[7]['target_text']


ledger = json.loads((BASE / 'metadata-localization-choices.id.json').read_bytes())
assert (BASE / 'metadata-localization-choices.id.json').read_bytes() == (SITE / 'metadata-localization-choices.id.json').read_bytes()
validate(ledger)
negative = []
for name, change in [
    ('false_whole_surface_claim', lambda x: x.update(whole_surface_localization_claimed=True)),
    ('fabricated_mathematical_canon_review', lambda x: x.update(native_terminology_canon_review=True)),
    ('missing_occurrence_mapping', lambda x: x['choices'][0]['target_segments'].pop()),
    ('altered_source_scope', lambda x: x['choices'][2].update(source_text='The whole CRing work.')),
    ('invented_human_review', lambda x: x['choices'][0].update(human_review_performed=True)),
]:
    corrupted = copy.deepcopy(ledger)
    change(corrupted)
    try:
        validate(corrupted)
    except AssertionError:
        negative.append(name)
    else:
        raise AssertionError('Invalid localization evidence accepted: ' + name)
print(json.dumps({'state': 'pass', 'localized_choices': 8, 'exact_public_occurrences': 16,
                  'source_target_hashes_verified': True, 'rejection_cases': negative,
                  'native_terminology_canon_review': False, 'whole_surface_localization_claimed': False}))
