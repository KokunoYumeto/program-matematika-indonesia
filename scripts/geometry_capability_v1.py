"""C100 native capability projection with a removable central navigation shell."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/geometry-capability-v1')
PILOT = Path('backend/v2.1/pilots/c100-geometry')
READER = Path('docs/id-ID/courses/C100/reader/index.html')
READER_STYLE = Path('docs/id-ID/courses/C100/reader/style.css')
SOLUTION_PDF = Path('docs/id-ID/courses/C100/solutions/SOLUSI_DAN_PENGUASAAN_ID_BAB01_20.pdf')
READER_URL = 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/'
SITE_URL = 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/geometry/'
NATIVE_PATHS = ['backend/catalog-v0.json', 'backend/schema-v0.json',
                'backend/unit-order-v0.csv', 'backend/exercise-hints-v0.csv',
                'backend/figure-descriptions-id-v0.csv', '00_control/TERMINOLOGY.csv']
NATIVE_PATHS += [f'backend/concepts-ch{n:02d}-id-v0.csv' for n in range(1, 21)]
PROGRAM_NAVIGATION = ('\n<nav data-program-navigation="v1" aria-label="Navigasi program">'
                      '<a data-program-home href="../../../../id/#course-C100">← Kembali ke Program Matematika</a></nav>')
PROGRAM_RETURN = ('<p data-program-return><a data-program-home href="../../../../id/#course-C100">'
                  '← Kembali ke Program Matematika</a></p>\n')


def reader_source_projection(data):
    """Remove only the documented central shell before checking frozen source bytes."""
    text = data.decode('utf-8')
    assert text.count(PROGRAM_NAVIGATION) == 1
    assert text.count(PROGRAM_RETURN) == 1
    return text.replace(PROGRAM_NAVIGATION, '', 1).replace(PROGRAM_RETURN, '', 1).encode('utf-8')


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def fact(path, data):
    return {'path': str(path).replace('\\', '/'), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def load_json(path):
    return json.loads(path.read_bytes())


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.figures = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
            if tag == 'figure':
                self.figures.add(attrs['id'])


def freeze_native(native_root):
    """Create once. Replay never re-imports or silently advances the frozen source."""
    destination = ROOT / BASE / 'input'
    assert not destination.exists(), 'Frozen input already exists; do not re-import it.'
    native_root = Path(native_root).resolve()
    manifest = load_json(ROOT / PILOT / 'manifest.json')
    bindings = []
    for item in manifest['input_authority']:
        assert item['locator_base'] == 'owner_root'
        relative = Path(item['locator'])
        assert relative.parts[0] == native_root.name
        relative = Path(*relative.parts[1:])
        assert '..' not in relative.parts and not relative.is_absolute()
        data = (native_root / relative).read_bytes()
        identity = fact(relative, data)
        assert identity['bytes'] == item['bytes'] and identity['sha256'] == item['sha256'], relative
        bindings.append(identity)
    assert len(bindings) == 96
    pending = {}
    for relative in NATIVE_PATHS:
        data = (native_root / relative).read_bytes()
        # Public metadata must not accidentally export local account paths.
        assert not re.search(rb'(?i)(?:["\s][A-Z]:[\\/]|users[\\/])', data), relative
        private_name = Path.home().name.encode('utf-8').lower()
        assert not re.search(rb'\b' + re.escape(private_name) + rb'\b', data.lower()), relative
        pending[relative] = data
    lock = {'contract': 'geometry-native-intake/1', 'native_folder': native_root.name,
            'native_files': [fact(p, b) for p, b in pending.items()],
            'existing_pilot_native_bindings': bindings,
            'central_dependencies': [fact(p, (ROOT / p).read_bytes()) for p in
                                     [PILOT / 'manifest.json', PILOT / 'units.jsonl', PILOT / 'relations.jsonl',
                                      PILOT / 'rights_accessibility.json', READER]],
            'scope': 'Complete native metadata inputs; existing reader and pilot remain separate unchanged dependencies.'}
    for relative, data in pending.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (destination / 'source-lock.json').write_bytes(encoded(lock))
    return lock


def read_inputs(root=ROOT):
    folder = root / BASE / 'input'
    lock = load_json(folder / 'source-lock.json')
    assert lock['contract'] == 'geometry-native-intake/1'
    assert [x['path'] for x in lock['native_files']] == NATIVE_PATHS
    for expected in lock['native_files']:
        assert fact(expected['path'], (folder / expected['path']).read_bytes()) == expected, expected['path']
    for expected in lock['central_dependencies']:
        data = (root / expected['path']).read_bytes()
        if Path(expected['path']) == READER:
            data = reader_source_projection(data)
        assert fact(expected['path'], data) == expected, expected['path']
    # Independently bind companion assets to the already locked pilot's facts.
    accessibility=load_json(root / PILOT / 'rights_accessibility.json')['accessibility']
    for path,prefix in [(READER_STYLE,'reader_style'),(SOLUTION_PDF,'solution_pdf')]:
        identity=fact(path,(root/path).read_bytes())
        assert identity['bytes']==accessibility[prefix+'_bytes']
        assert identity['sha256']==accessibility[prefix+'_sha256']
    def rows(relative):
        return list(csv.DictReader(io.StringIO((folder / relative).read_text(encoding='utf-8-sig'))))
    return {'lock': lock, 'catalog': load_json(folder / 'backend/catalog-v0.json'),
            'concepts': [(f'backend/concepts-ch{n:02d}-id-v0.csv', row)
                         for n in range(1, 21) for row in rows(f'backend/concepts-ch{n:02d}-id-v0.csv')],
            'terms': rows('00_control/TERMINOLOGY.csv'),
            'figures': rows('backend/figure-descriptions-id-v0.csv'),
            'exercise_rows': rows('backend/exercise-hints-v0.csv'),
            'unit_order': rows('backend/unit-order-v0.csv'),
            'units': [json.loads(line) for line in (root / PILOT / 'units.jsonl').read_text('utf-8').splitlines()],
            'relations': [json.loads(line) for line in (root / PILOT / 'relations.jsonl').read_text('utf-8').splitlines()],
            'rights_accessibility': load_json(root / PILOT / 'rights_accessibility.json'),
            'reader': (root / READER).read_text('utf-8')}


def index_unique(items, key):
    result = {item[key]: item for item in items}
    assert len(result) == len(items), f'Duplicate {key}'
    return result


def build_model(source):
    units = index_unique(source['units'], 'stable_unit_id')
    assert len(units) == 939
    anchors = Anchors()
    anchors.feed(source['reader'])
    concepts = []
    concept_ids = {row['concept_id'] for _, row in source['concepts']}
    assert len(concept_ids) == len(source['concepts']) == 491
    for path, row in source['concepts']:
        first = units.get(row['first_unit_id'])
        prereqs = [x.strip() for x in row['prerequisite_concept_ids'].split(';') if x.strip()]
        reading = first['learner_route']['url'] if first else None
        fallback = [r for r in source['catalog']['relations'] if r['type'] == 'contains'
                    and r['to'] == row['first_unit_id'] and r['from'] in units]
        if first is None and len(fallback) == 1:
            reading = units[fallback[0]['from']]['learner_route']['url']
        if first:
            assert first['learner_route']['anchor'] in anchors.ids
        concepts.append({'id': row['concept_id'], 'native': row, 'source_file': path,
                         'reading': reading, 'reading_state': ('exact_native_unit' if first else
                                      'chapter_fallback' if reading else 'unmapped_native_unit'),
                         'fallback_evidence': fallback if first is None else [],
                         'prerequisites': [{'id': p, 'resolved': p in concept_ids} for p in prereqs]})
    terms = [{'id': row['term_id'], 'native': row} for row in source['terms']]
    index_unique(terms, 'id')
    assert len(terms) == 432
    figures = [{'id': row['asset_id'], 'native': row,
                'reading': READER_URL + '#' + row['asset_id'] if row['asset_id'] in anchors.figures else None,
                'reading_state': 'exact_figure_description' if row['asset_id'] in anchors.figures else 'not_present_in_reader'}
               for row in source['figures']]
    index_unique(figures, 'id')
    assert len(figures) == 214
    exercise_rows = index_unique(source['exercise_rows'], 'exercise_id')
    for rel in source['relations']:
        assert rel['from_id'] in units and rel['to_id'] in units, rel
    exercises = []
    for unit in source['units']:
        if 'exercise' not in unit['native_unit_kind']:
            continue
        uid = unit['stable_unit_id']
        assert unit['learner_route']['anchor'] in anchors.ids
        supports = []
        parents = []
        for rel in source['relations']:
            if rel['relation_type'] == 'guided_by' and rel['from_id'] == uid:
                target = units[rel['to_id']]
                supports.append({'kind': 'hint', 'unit': target, 'relation': rel})
            if rel['relation_type'] == 'solves' and rel['to_id'] == uid:
                target = units[rel['from_id']]
                supports.append({'kind': 'independently_authored_solution', 'unit': target, 'relation': rel})
            if rel['relation_type'] == 'part_of_exercise' and rel['from_id'] == uid:
                parents.append(rel['to_id'])
        match = re.search(r'\.ch(\d{2})', uid)
        exercises.append({'id': uid, 'unit': unit, 'native_exercise_row': exercise_rows.get(uid),
                          'chapter': match.group(1) if match else '', 'parents': parents,
                          'support': supports, 'support_state': 'linked_support' if supports else 'no_direct_support_recorded',
                          'learner_url': SITE_URL + 'C100.html#' + uid})
    assert len(exercises) == 285
    records = source['catalog']['records']
    index_unique(records, 'id')
    universe = set(units) | concept_ids | {r['id'] for r in records} | {t['id'] for t in terms} | {f['id'] for f in figures}
    for rel in source['catalog']['relations']:
        assert rel['from'] in universe and rel['to'] in universe, rel
    for concept in concepts:
        concept['lexical_term_matches'] = [t['id'] for t in terms
            if (t['native']['source_term'], t['native']['preferred_id_ID']) ==
               (concept['native']['source_term'], concept['native']['preferred_id_ID'])]
    for figure in figures:
        figure['native_illustrates_relations'] = [r for r in source['catalog']['relations']
                                                 if r['type'] == 'illustrates' and r['from'] == figure['id']]
    corrections = [r for r in records if r['entity_type'] == 'correction']
    record_types = Counter(r['entity_type'] for r in records)
    counts = {'stable_units': len(units), 'exercise_surfaces': len(exercises),
              'parent_exercises': sum(not e['parents'] for e in exercises),
              'concepts': len(concepts), 'terms': len(terms), 'figure_records': len(figures),
              'figures_in_reader': sum(f['reading'] is not None for f in figures),
              'corrections': len(corrections), 'relations': len(source['relations']),
              'unmapped_concept_readings': sum(c['reading'] is None for c in concepts),
              'chapter_fallback_readings': sum(c['reading_state'] == 'chapter_fallback' for c in concepts),
              'unresolved_prerequisites': sum(not p['resolved'] for c in concepts for p in c['prerequisites']),
              'concept_statuses': dict(Counter(c['native']['status'] for c in concepts))}
    return {'contract': 'geometry-learning-capability/1', 'role': 'C100', 'locale': 'id-ID',
            'native_edition': next(r for r in records if r['id'] == 'o004-petrunin-current-0b0858e'),
            'counts': counts, 'concepts': concepts, 'terms': terms, 'figures': figures,
            'exercises': exercises, 'corrections': corrections,
            'chapter_dependencies': [r for r in source['relations'] if r['relation_type'] == 'depends_on'],
            'chapters': [u for u in source['units'] if u['native_unit_kind'] == 'chapter'],
            'rights_accessibility': source['rights_accessibility'],
            'native_record_counts': dict(record_types),
            'projection_policy': {'native_metadata_inputs': 'exact complete bytes frozen; no native field rewritten',
                                  'concept_term_figure_rows': 'all CSV fields retained inside native',
                                  'exercise_units_support_and_relations': 'complete pilot records retained for selected exercise/support surfaces',
                                  'catalog': 'complete catalog retained in frozen input; corrections projected whole; other kinds not equated to CSV completeness',
                                  'roundtrip': 'no general native-format roundtrip or full production replay claimed'},
            'limitations': ['Concept prerequisite links are native editorial metadata, not a validated learning assessment.',
                            'Mapped-pending-qa and unresolved prerequisite IDs remain explicit; no silent approval.',
                            '253 independently authored solutions share one complete PDF; no exact solution-page claim.',
                            'Source figures are description surfaces; no new visual or assistive-technology certification.',
                            'The separate Clemens/Snapp workbook is not merged into this main-course metadata profile.']}
