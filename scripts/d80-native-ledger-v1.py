"""Read-only native D80 ledger consumer; reversible metadata, not a book rebuild."""
import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('backend/course-capsule-v1/adapters/d80-native-ledger-v1')
OLD = Path('backend/course-capsule-v1/adapters/d80-capability-v1')
SITE = Path('docs/backend/d80/native-ledger')
ROLES = ('native_units', 'segment_ledger_reference', 'term_ledger_reference',
         'figure_alt_ledger_reference', 'source_correction_ledger_reference',
         'terminology_control_reference', 'diagram_override_ledger_reference', 'source_scope_authority')
EXPECTED = {'segments':6347, 'terms':511, 'corrections':73, 'diagrams':829}

def require(value, message):
    if not value:
        raise ValueError(message)

def identity(data):
    return {'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()}

def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()

def lines(raw):
    return [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]

def csv_rows(raw):
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline='')))

def safe_path(value):
    path = Path(value)
    require(not path.anchor and not path.is_absolute() and '..' not in path.parts and '\\' not in value and ':' not in value,
            'Unsafe relative source path')
    return path

def intake(native, root=ROOT):
    destination = root/BASE
    require(not (destination/'source-lock.json').exists(), 'Intake already frozen; do not replace')
    source_lock = json.loads((root/OLD/'input/source-lock.json').read_bytes())
    by_role = {row['role']:row for row in source_lock['inputs']}
    payload, entries = {}, []
    for role in ROLES:
        entry = by_role[role]
        relative = safe_path(entry['path'])
        raw = (native/relative).read_bytes()
        require(identity(raw) == {key:entry[key] for key in ('bytes','sha256')}, 'Pinned native input changed: '+role)
        payload['input/'+relative.as_posix()] = raw
        entries.append({'role':role, 'path':'input/'+relative.as_posix(), 'native_path':relative.as_posix(), **identity(raw)})
    authorities = []
    for name in ('data/units.jsonl','data/routes.jsonl','data/ledger-references.json','input/source-lock.json'):
        raw = (root/OLD/name).read_bytes()
        authorities.append({'path':(OLD/name).as_posix(), **identity(raw)})
    lock = {'schema':'d80-native-ledger-source-lock/1','course_id':'D80','inputs':entries,'authorities':authorities,
            'native_repository':source_lock['native_repository'], 'reader':source_lock['corrected_reader'],
            'license':'CC-BY-4.0', 'source_author':'Wen-Wei Li',
            'native_translation_provenance':'OpenAI Codex gpt-5.6-sol, Ultra',
            'integration_provenance':'OpenAI Codex gpt-6-astra, Ultra', 'book_bodies_copied':False}
    for name, raw in payload.items():
        target = destination/name
        target.parent.mkdir(parents=True, exist_ok=True)
        require(not target.exists(), 'Existing intake member')
        target.write_bytes(raw)
    (destination/'source-lock.json').write_bytes(encode(lock))
    return lock

def load(root=ROOT):
    lock = json.loads((root/BASE/'source-lock.json').read_bytes())
    require(lock['schema'] == 'd80-native-ledger-source-lock/1' and lock['course_id'] == 'D80', 'Wrong input scope')
    raw = {}
    require([row['role'] for row in lock['inputs']] == list(ROLES), 'Native ledger set/order differs')
    original = json.loads((root/OLD/'input/source-lock.json').read_bytes())
    original_inputs = {row['role']:row for row in original['inputs']}
    for row in lock['inputs']:
        source = original_inputs[row['role']]
        require(row['native_path'] == safe_path(source['path']).as_posix() and
                row['path'] == 'input/'+row['native_path'] and
                all(row[k] == source[k] for k in ('bytes','sha256')), 'Native pin differs from original authority')
        data = (root/BASE/safe_path(row['path'])).read_bytes()
        require(identity(data) == {key:row[key] for key in ('bytes','sha256')}, 'Native bytes changed: '+row['role'])
        raw[row['role']] = data
    expected_authorities = {(OLD/name).as_posix() for name in ('data/units.jsonl','data/routes.jsonl','data/ledger-references.json','input/source-lock.json')}
    require(len(lock['authorities']) == 4 and {row['path'] for row in lock['authorities']} == expected_authorities, 'Authority inventory differs')
    for row in lock['authorities']:
        require(identity((root/safe_path(row['path'])).read_bytes()) == {key:row[key] for key in ('bytes','sha256')}, 'Central authority changed')
    return lock, raw

def project(root=ROOT):
    lock, raw = load(root)
    unit_rows = lines((root/OLD/'data/units.jsonl').read_bytes())
    units = {row['unit_id']:row for row in unit_rows if row['unit_type'] == 'translated_source_unit'}
    require(len(units) == 146, 'Native unit scope differs')
    native_units = lines(raw['native_units'])
    require(len(native_units) == 146 and {row['unit_id'] for row in native_units} == set(units), 'Native/central unit identities differ')
    route_rows = lines((root/OLD/'data/routes.jsonl').read_bytes())
    routes = {row['unit_id']:row for row in route_rows if row['unit_id'] in units}
    require(sum(row['unit_id'] in units for row in route_rows) == 146 and set(routes) == set(units), 'Missing or duplicate unit route')
    for uid, route in routes.items():
        require(route['target_url'] == lock['reader']['url']+'#'+route['target_anchor'], 'Foreign or imprecise reader URL')
        require(route['reader_head'] == lock['reader']['head'], 'Reader edition changed')
    by_target = {row['translation_target']['path']:uid for uid,row in units.items()}
    require(len(by_target) == 146, 'Ambiguous target path')
    controls = csv_rows(raw['terminology_control_reference'])
    control = {row['concept_id']:row for row in controls}
    require(len(control) == len(controls) == 511, 'Duplicate/missing terminology controls')
    overrides = json.loads(raw['diagram_override_ledger_reference'])['overrides']
    override = {row['diagram_id']:row for row in overrides}
    require(len(override) == len(overrides) == 13, 'Diagram override identities differ')
    rows = []
    def add(kind, rid, native, uid, scope, flags, related=None):
        require(uid is None or uid in units, 'Unresolved exact unit identity: '+str(uid))
        link = [] if uid is None else [{'unit_id':uid,'title':units[uid]['title_id'],'url':routes[uid]['target_url']}]
        rows.append({'kind':kind,'id':rid,'native':native,'unit_ids':[] if uid is None else [uid],
                     'unit_links':link,'discovery_scope':scope,'flags':flags,'related_native':related or {}})
    for row in lines(raw['segment_ledger_reference']):
        precision = row.get('source_span_precision','exact_source_span')
        require(precision in ('exact_source_span','unit_slice'), 'Unknown segment precision')
        add('segments',row['segment_id'],row,row['unit_id'],'exact_native_unit',[precision])
    for row in csv_rows(raw['term_ledger_reference']):
        peer = control[row['concept_id']]
        flags = ['canon_not_independently_checked']
        if row['status'] == 'provisional': flags.append('provisional')
        if row['preferred_id'] != peer['o013_o014_preferred_id']: flags.append('term_disagreement')
        recorded_uid = peer.get('first_o014_unit') or None
        uid = recorded_uid if recorded_uid in units else None
        scope = 'recorded_first_introduction_not_all_occurrences'
        if uid is None:
            flags.append('unmapped_unit')
            scope = 'unresolved_recorded_first_introduction' if recorded_uid else 'no_first_introduction_recorded'
        add('terms',row['concept_id'],row,uid,scope,flags,{'terminology_control':peer})
    for row in csv_rows(raw['source_correction_ledger_reference']):
        uid = by_target.get(row['target_path'])
        add('corrections',row['correction_id'],row,uid,'exact_target_file' if uid else 'no_exact_unit_join',
            [row['status']]+([] if uid else ['unmapped_unit']))
    for row in csv_rows(raw['figure_alt_ledger_reference']):
        uid = by_target.get('source/id-ID/'+row['unit_filename'])
        require(uid is not None, 'Unmapped diagram target')
        related = {'reader_override':override[row['diagram_id']]} if row['diagram_id'] in override else {}
        add('diagrams',row['diagram_id'],row,uid,'exact_target_file',['reader_override'] if related else [],related)
    require(len({(row['kind'],row['id']) for row in rows}) == len(rows), 'Duplicate ledger ID')
    counts = {kind:sum(row['kind'] == kind for row in rows) for kind in EXPECTED}
    require(counts == EXPECTED, 'Ledger counts differ')
    flag_counts = {flag:sum(flag in row['flags'] for row in rows) for flag in ('unit_slice','exact_source_span','provisional','term_disagreement','reader_override','unmapped_unit')}
    require({k:flag_counts[k] for k in ('unit_slice','exact_source_span','provisional','term_disagreement','reader_override')} ==
            {'unit_slice':1736,'exact_source_span':4611,'provisional':88,'term_disagreement':2,'reader_override':13}, 'Native distinctions collapsed')
    require(next(row for row in rows if row['id'] == 'O014-O001')['native']['status'] == 'observed_not_modified_pending_consolidated_review', 'Pending correction promoted')
    require({row['id'] for row in rows if 'term_disagreement' in row['flags']} == {'math.homological.cup_product','math.set_theory.regular_small_cardinal'}, 'Term disagreement identities differ')
    projection = {'schema':'d80-native-ledger-projection/1','course_id':'D80','rows':rows,
                  'summary':{'visible_records':len(rows),'native_records':8430,'counts':counts,'flags':flag_counts},
                  'units':[{'id':uid,'title':u['title_id'],'sequence':u['sequence']} for uid,u in units.items()],
                  'native_records_changed':False,'book_bodies_copied':False,'semantic_canon_approval':False,'native_book_rebuilt':False,
                  'reading_language':'id-ID','source_lock':identity((root/BASE/'source-lock.json').read_bytes()),
                  'provenance':{'model':'OpenAI Codex gpt-6-astra','effort':'Ultra','work':'Metadata integration, interface and deterministic QA'}}
    return projection, lock, raw

def archive_metadata(lock, raw):
    items = {'source-lock.json':encode(lock), 'NOTICE.txt':(
        'Metadata asli D80 tidak diubah. Penulis sumber: Wen-Wei Li. Lisensi CC BY 4.0; atribusi dan perbedaan edisi tetap berlaku.\n'
        'Terjemahan asli: OpenAI Codex gpt-5.6-sol, Ultra. Integrasi metadata: OpenAI Codex gpt-6-astra, Ultra.\n'
        'Ini bukan buku lengkap, pengesahan kanon, atau reproduksi pembangunan buku.\n'
        'Unchanged D80 metadata; source author Wen-Wei Li, CC BY 4.0. Native translation: OpenAI Codex gpt-5.6-sol, Ultra.\n'
        'Metadata integration: OpenAI Codex gpt-6-astra, Ultra. Not a textbook archive, canon approval or native-book rebuild.\n').encode()}
    items.update({row['native_path']:raw[row['role']] for row in lock['inputs']})
    out = io.BytesIO()
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name, data in sorted(items.items()):
            info = zipfile.ZipInfo(name,(1980,1,1,0,0,0)); info.create_system=3; info.external_attr=0o100644 << 16; info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data,compresslevel=9)
    return out.getvalue()

def page(locale, summary):
    def t(a,b): return b if locale == 'en' else a
    title = t('D80 · Istilah, sumber, koreksi dan diagram','D80 · Terms, sources, corrections and diagrams')
    options = ''.join('<option value="'+k+'">'+t(a,b)+' ('+str(EXPECTED[k])+')</option>' for k,a,b in (
        ('terms','Istilah','Terms'),('segments','Lokasi sumber/terjemahan','Source/target locations'),('corrections','Koreksi','Corrections'),('diagrams','Deskripsi diagram','Diagram descriptions')))
    flags = ''.join('<option value="'+k+'">'+t(a,b)+'</option>' for k,a,b in (
        ('provisional','Istilah sementara','Provisional terminology'),('term_disagreement','Pilihan istilah berbeda','Conflicting term choices'),
        ('unit_slice','Sumber hanya pada tingkat unit','Unit-level source location only'),('reader_override','Deskripsi pengganti pada pembaca','Reader-only replacement'),
        ('unmapped_unit','Lokasi tanpa pemetaan unit eksak','Locator without an exact unit mapping'),
        ('observed_not_modified_pending_consolidated_review','Koreksi belum diterapkan','Correction not applied')))
    return ('<!doctype html><html lang="'+locale+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title>'
        '<link rel="stylesheet" href="ledger.css"><script src="data.js" defer></script><script src="ledger-ui.js" defer></script></head><body data-locale="'+locale+'">'
        '<a class="skip" href="#records">'+t('Langsung ke catatan','Skip to records')+'</a><main><nav><a href="../D80.html">'+t('Belajar','Study · Indonesian edition')+'</a> · '
        '<a href="../D80-pengajar.html">'+t('Mengajar','Teach · Indonesian edition')+'</a> · <a id="language" href="ledger'+('' if locale=='en' else '-en')+'.html" lang="'+('id' if locale=='en' else 'en')+'">'+('Bahasa Indonesia' if locale=='en' else 'English')+'</a></nav>'
        '<h1>'+title+'</h1><p>'+t('Cari catatan asli untuk unit yang sedang dipelajari atau diajarkan.','Find native records for the unit you are studying or teaching.')+'</p>'
        '<p class="notice">'+t('Catatan asli dikutip tanpa perubahan; sebagian berbahasa Inggris. Tautan buku menuju edisi Indonesia. Status aktif bukan bukti pengesahan kanon. Istilah sementara dan perbedaan antardaftar tetap ditampilkan.',
        'Native records are quoted unchanged; some are in English. Book links lead to the Indonesian edition. Active status is not canon approval. Provisional terms and disagreements remain visible.')+'</p>'
        '<p>'+t('4.611 lokasi sumber eksak; 1.736 lokasi hanya pada tingkat unit. Lokasi pengenalan pertama suatu istilah bukan daftar semua kemunculannya. Deskripsi diagram tidak menggantikan seluruh hubungan visual.',
        '4,611 exact source spans; 1,736 unit-level source locations. A term’s recorded first introduction is not its complete occurrence list. Diagram summaries do not replace every visual relation.')+'</p>'
        '<section class="filters"><label for="kind">'+t('Jenis catatan','Record type')+'</label><select id="kind">'+options+'</select>'
        '<label for="search">'+t('Cari kata atau ID','Search text or ID')+'</label><input id="search" type="search">'
        '<label for="unit">'+t('ID unit asli (opsional)','Exact native unit ID (optional)')+'</label><input id="unit" type="search">'
        '<label for="flag">'+t('Temuan','Finding')+'</label><select id="flag"><option value="">'+t('Semua','All')+'</option>'+flags+'</select></section>'
        '<p id="count" aria-live="polite"></p><section id="records" tabindex="-1"></section><p class="paging"><button id="previous">'+t('Sebelumnya','Previous')+'</button><button id="next">'+t('Berikutnya','Next')+'</button></p>'
        '<noscript>'+t('Unduh JSON atau ZIP di bawah untuk semua catatan.','Download the JSON or ZIP below for all records.')+'</noscript><h2>'+t('Unduhan','Downloads')+'</h2><ul>'
        '<li><a href="projection.json" download>'+t('Data pencarian lengkap (JSON)','Complete searchable data (JSON)')+'</a></li><li><a href="native-metadata.zip" download>'+t('Metadata asli tanpa perubahan (ZIP)','Unchanged native metadata (ZIP)')+'</a></li>'
        '<li><a href="source-lock.json">'+t('Identitas sumber dan lisensi','Source identities and licence')+'</a></li></ul><footer>'+t('Integrasi metadata, antarmuka dan pemeriksaan: ','Metadata integration, interface and checks: ')
        +'OpenAI Codex gpt-6-astra, Ultra. '+t('Tidak diklaim ada peninjauan manusia, pengesahan kanon, atau pembangunan ulang buku.','No human review, canon approval or native-book rebuild is claimed.')+'</footer></main></body></html>\n').encode()

def build(root=ROOT, destination=None):
    projection, lock, raw = project(root)
    files = {'projection.json':encode(projection), 'source-lock.json':encode(lock), 'native-metadata.zip':archive_metadata(lock,raw),
        'data.js':('globalThis.D80_NATIVE_LEDGER='+json.dumps(projection,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')+';\n').encode(),
        'ledger.html':page('id',projection['summary']), 'ledger-en.html':page('en',projection['summary']),
        'ledger-ui.js':(root/'scripts/d80-native-ui.js').read_bytes(),
        'ledger.css':(root/'docs/backend/d60/native-ledger/ledger.css').read_bytes()}
    destination = destination or root/BASE/'site'
    destination.mkdir(parents=True,exist_ok=True)
    for name, raw in files.items(): (destination/name).write_bytes(raw)
    return projection, {name:identity(raw) for name,raw in files.items()}

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--intake',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.intake: intake(args.intake)
    projection, files=build(destination=args.out)
    if args.out is None:
        (ROOT/SITE).mkdir(parents=True,exist_ok=True)
        for name in files: (ROOT/SITE/name).write_bytes((ROOT/BASE/'site'/name).read_bytes())
    print(json.dumps({'state':'pass','summary':projection['summary'],'outputs':files}),flush=True)
