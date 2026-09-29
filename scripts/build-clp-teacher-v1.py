"""Build bilingual, offline CLP assignment planners from verified native metadata.

This consumer preserves source identity; it does not render or retranslate books.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/clp-teacher-v1'
PROFILES = {'CLP1': 'B20', 'CLP2': 'B30', 'CLP3': 'B50', 'CLP4': 'B60'}
COUNTS = {'B20': 695, 'B30': 596, 'B50': 497, 'B60': 410}
KINDS = ('question', 'hint', 'answer', 'solution')
VECTORS = {
    'B20': {'pretext:1:0:1:1': 75, 'pretext:1:1:1:1': 620},
    'B30': {'pretext:1:0:1:1': 14, 'pretext:1:1:1:1': 582},
    'B50': {'latex:1:0:1:1|xml:1:0:1:1': 319, 'latex:1:1:1:1|xml:1:1:1:1': 175,
            'latex:1:0:1:1|xml:1:1:1:1': 1, 'latex:1:0:1:1|xml:1:0:1:2': 1,
            'latex:1:1:1:1|xml:1:1:1:2': 1},
    'B60': {'pretext:1:0:1:1': 93, 'pretext:1:1:1:1': 306,
            'pretext:1:0:1:2': 1, 'pretext:1:1:1:2': 10},
}


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def load(base=BASE):
    lock = json.loads((base / 'input/source-lock.json').read_bytes())
    assert lock['path'] == 'native-exercises.json'
    b = (base / 'input' / lock['path']).read_bytes()
    assert len(b) == lock['bytes'] and sha(b) == lock['sha256'], 'Native input drift'
    return json.loads(b), lock


def load_navigation(base=BASE):
    lock = json.loads((base/'input/clp1-navigation-lock.json').read_bytes())
    raw = (base/'clp1-navigation.json').read_bytes()
    checks = (base/'clp1-navigation-validation.json').read_bytes()
    assert lock['schema'] == 'clp1-navigation-lock/1'
    assert lock['mapping'] == {'bytes':len(raw),'sha256':sha(raw)}
    assert lock['validation'] == {'bytes':len(checks),'sha256':sha(checks)}
    validation = json.loads(checks)
    assert validation['state'] == 'pass' and len(validation['source_pdf_replays']) == 2
    assert validation['independent_annotation_comparison']['matched_supports'] == 2010
    data = json.loads(raw)
    assert data['inputs']['native']['sha256'] == lock['native_sha256']
    assert validation['mapping'] == lock['mapping']
    return data, lock


def unique(items, key):
    out = {key(x): x for x in items}
    assert len(out) == len(items), 'Duplicate identity'
    return out


def compact_unit(u, profile):
    if profile == 'CLP1':
        source, target = u['source'], u['target']
        s = {'file': source['locator']['path'], 'path': source['locator']['xpath'],
             'content_sha256': source.get('content_sha256'), 'edition_id': source['edition_id']}
        t = {'files': target['locators'], 'file_sha256': target['file_sha256'],
             'alignment': target['alignment'], 'edition_id': target['edition_id']}
    else:
        s = {'file': u['source_file'], 'path': u['source_path'], 'locator': u['source_locator'],
             'content_sha256': u['source_content_sha256'], 'edition_id': u['source_edition_id']}
        t = {'file': u.get('target_file') or u['source_file'], 'path': u['target_path'],
             'locator': u['target_locator'], 'content_sha256': u['target_content_sha256'],
             'alignment': 'native-structural-path', 'edition_id': u['edition_id']}
    return {'id': u['id'], 'kind': u['unit_type'], 'source': s, 'target': t,
            'rights_id': u['rights_id'], 'translation_state': u['translation_state'],
            'parent_id': u.get('parent_id'), 'attributes': u.get('attributes', {}),
            'topology_state': u.get('topology_state'), 'topology_delta_id': u.get('topology_delta_id')}


def project(native, navigation=None):
    assert native['schema'] == 'clp-teacher-native-input/1' and native['zero_book_prose'] is True
    assert set(native['profiles']) == set(PROFILES)
    common = unique(native['common_exercises'], lambda r: (r['profile'], r['native_id']))
    assert len({r['id'] for r in common.values()}) == len(common)
    courses = []
    readers = unique(native['readers'], lambda c: c['course_id'])
    assert set(readers) == set(PROFILES.values())
    for profile, role in PROFILES.items():
        p = native['profiles'][profile]
        assert p['course_id'] == role
        units = unique(p['units'], lambda u: u['id'])
        rels = unique(p['relations'], lambda r: r['id'])
        questions = []
        if profile == 'CLP3':
            closure_by_id = unique(p['closures'], lambda c: c['id'])
            groups = defaultdict(list)
            for c in closure_by_id.values():
                assert c['closure_complete'] is True
                groups[c['semantic_exercise_id']].append(c)
            for ident, closures in groups.items():
                mapped = common[(profile, ident)]
                assert mapped['course_id'] == role
                assert set(mapped['surface_native_ids']) == {c['id'] for c in closures}
                assert len(closures) == 2 and {c['surface_kind'] for c in closures} == {'xml', 'latex'}
                surfaces = []
                for c in sorted(closures, key=lambda x: x['surface_kind']):
                    parent = units[c['parent_id']]
                    components = {kind: c[('statement' if kind == 'question' else kind) + '_ids'] for kind in KINDS}
                    target_components = {kind: c['target_' + ('statement' if kind == 'question' else kind) + '_ids'] for kind in KINDS}
                    for kind in KINDS:
                        assert len(components[kind]) == len(target_components[kind])
                    # Native relations are question -> support in CLP3, unlike CLP2/4.
                    support_edges = [r for r in rels.values() if r.get('source_id') == c['exercise_id']]
                    for kind, relkind in [('hint', 'hints'), ('answer', 'answers'), ('solution', 'solves')]:
                        assert sorted(r['target_id'] for r in support_edges if r['relation_type'] == relkind) == sorted(components[kind]), (profile, c['id'], kind)
                    surfaces.append({'format': c['surface_kind'], 'native_id': c['exercise_id'], 'target_native_id': c['target_exercise_id'],
                        'closure_id': c['id'], 'source': {'file': c['source_locator'], 'exercise_order': c['order'], 'content_sha256': c['source_content_sha256']},
                        'target': {'file': parent['target_path'], 'exercise_order': c['order'], 'content_sha256': c['target_content_sha256'], 'alignment': 'native-paired-surface'},
                        'rights_id': c['rights_id'], 'translation_state': c['translation_state'], 'components': components,
                        'target_components': target_components, 'relations': support_edges, 'delta_issue_ids': c['delta_issue_ids'],
                        'native_row_sha256': c['native_row_sha256']})
                xml = next(s for s in surfaces if s['format'] == 'xml')
                # The common contract counts surfaces that contain a component,
                # not the number of alternatives within those surfaces.
                totals = {f'{kind}_surface_count': sum(bool(s['components'][kind]) for s in surfaces) for kind in KINDS}
                assert mapped['qhas_state'] == totals
                questions.append({'id': mapped['id'], 'native_id': ident, 'section': xml['source']['file'],
                    'label': str(xml['source']['exercise_order']), 'surfaces': surfaces})
        else:
            q = {k: u for k, u in units.items() if u['unit_type'] == 'exercise'}
            supports = {k: {kind: [] for kind in KINDS} for k in q}
            edges = defaultdict(list)
            for r in rels.values():
                kind = r.get('relation_type', r.get('relation'))
                question, component = (r['source_id'], r['target_id']) if profile == 'CLP1' else (r['to_id'], r['from_id'])
                if question not in q:
                    assert profile == 'CLP4' and kind == 'solves', ('Unexpected non-exercise relation', profile, kind)
                    continue  # CLP4's worked examples are not exercise solutions.
                dest = {'has_hint': 'hint', 'has_answer': 'answer', 'has_solution': 'solution', 'question_for': 'question', 'hints': 'hint', 'answers': 'answer', 'solves': 'solution'}[kind]
                comp = units[component]
                assert comp['parent_id'] == question, ('Miswired native support', profile, r['id'])
                assert comp['unit_type'] == ('statement' if dest == 'question' else dest)
                supports[question][dest].append(compact_unit(comp, profile))
                edges[question].append(r)
            for ident, u in q.items():
                mapped = common[(profile, ident)]
                assert mapped['course_id'] == role
                question = compact_unit(u, profile)
                if profile in ('CLP1', 'CLP4'):
                    supports[ident]['question'] = [question]
                for kind in KINDS:
                    supports[ident][kind].sort(key=lambda x: x['id'])
                    assert len({x['id'] for x in supports[ident][kind]}) == len(supports[ident][kind])
                assert len(supports[ident]['question']) == 1
                assert len(supports[ident]['answer']) == 1 and len(supports[ident]['solution']) >= 1
                path = question['source']['path']
                group = re.search(r'exercisegroup\[(\d+)\]', path)
                local = re.search(r'/exercise\[(\d+)\]$', path)
                assert local, (profile, path)
                label = (group.group(1) + ' / ' if group else '') + local.group(1)
                questions.append({'id': mapped['id'], 'native_id': ident, 'section': question['source']['file'], 'label': label,
                    'surfaces': [{'format': 'pretext', **question, 'components': supports[ident], 'relations': sorted(edges[ident], key=lambda r: r['id'])}]})
        assert len(questions) == COUNTS[role]
        def natural(value):
            return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', value)]
        questions.sort(key=lambda x: (natural(x['section']), natural(x['label']), x['id']))
        vectors = Counter()
        for x in questions:
            vectors['|'.join(s['format'] + ':' + ':'.join(str(len(s['components'][k])) for k in KINDS) for s in x['surfaces'])] += 1
        assert dict(vectors) == VECTORS[role], ('Native component coverage changed', role, dict(vectors))
        courses.append({'course_id': role, 'profile': profile, 'archive': p['archive'], 'archive_filename': p['archive_filename'],
            'readers': readers[role],
            'source_members': p['members'], 'exercise_count': len(questions), 'section_count': len({x['section'] for x in questions}),
            'component_vectors': dict(sorted(vectors.items())), 'questions': questions})
    assert sum(c['exercise_count'] for c in courses) == len(common) == 2198
    model = {'schema': 'clp-teacher-selection/1', 'courses': courses, 'book_prose_copied': False,
        'integration_provenance': {'model': 'gpt-6-astra', 'effort': 'ultra', 'work': 'source-preserving planner integration; no book translation', 'primary_turn_context_utc': '2026-09-27T03:16:18.538Z'},
        'pdf_page_or_html_anchors_claimed': False, 'source_exercises': 2198, 'format_surfaces_are_not_extra_exercises': True,
        'limitations': {'id': 'Perencana tugas berdasarkan identitas sumber, bukan lembar soal siap cetak. Isi soal tetap berada dalam buku. Korpus beku ini mengikuti versi sumber edisi Bahasa Indonesia; antarmuka Inggris tidak menyatakan cakupan atau penomoran yang sama dengan edisi Inggris lainnya. CLP1 hanya memiliki pemetaan ke berkas terjemahan, bukan ke lokasi tiap soal. Nomor kelompok/lokal berasal dari struktur sumber dan belum tentu sama dengan nomor tercetak. Ketiadaan petunjuk berarti tidak tercatat dalam backend ini. Tidak ada klaim nomor halaman PDF atau jangkar pembaca HTML.',
                        'en': 'An assignment planner using source identities, not a printable worksheet. Exercise text remains in the books. This frozen corpus follows the Indonesian edition source snapshot; the English interface does not assert coverage or numbering of other English editions. CLP1 has translated-file alignment only, not per-exercise target locations. Group/local numbers describe the source structure and need not equal printed numbering. A missing hint means none is recorded in this backend. No PDF page or HTML reader anchors are claimed.'}}
    if navigation is not None:
        data, lock = navigation
        course = next(c for c in courses if c['course_id']=='B20')
        qmap = unique(data['questions'],lambda q:q['native_id'])
        assert set(qmap) == {q['native_id'] for q in course['questions']}
        reader = next(r for r in course['readers']['actions'] if r['role']=='problembook')
        assert reader['sha256'] == data['reader']['sha256'] and reader['url'] == data['reader']['url']
        for q in course['questions']:
            nav = qmap[q['native_id']]
            assert q['id'] == nav['common_id']
            surface = q['surfaces'][0]
            assert nav['source_content_sha256'] == surface['source']['content_sha256']
            assert nav['native_translation_state'] == surface['translation_state']
            for kind in ('hint','answer','solution'):
                assert {s['native_id'] for s in nav['supports'] if s['kind']==kind} == {s['id'] for s in surface['components'][kind]}
            q['navigation'] = nav
        course['navigation_identity'] = lock['mapping']
        course['navigation_reader'] = data['reader']
        course['limitations'] = {
            'id':'Perencana tugas dengan rujukan soal, bukan lembar soal siap cetak. Pemetaan tambahan CLP1 menghubungkan 695 soal, 620 petunjuk, 695 jawaban, dan 695 penyelesaian ke rentang sumber terjemahan dan halaman awal PDF Bahasa Indonesia yang diverifikasi. Identitas dan status historis backend asli tetap dipertahankan, termasuk 30 soal yang diterjemahkan dalam berkas induk. Nomor PDF bukan nomor halaman tercetak. Tautan membutuhkan jaringan; untuk membaca luring, unduh PDF secara terpisah dan gunakan nomor PDF yang ditampilkan. Tidak adanya petunjuk berarti tidak tercatat (75 soal). Ini pemeriksaan struktur dan navigasi, bukan peninjauan baru atas kebenaran matematika atau mutu terjemahan. Antarmuka Inggris tetap memakai buku Bahasa Indonesia; tidak menyatakan kesamaan nomor soal dengan edisi Inggris lain.',
            'en':'An assignment planner with exercise references, not a printable worksheet. The additive CLP1 mapping connects 695 questions, 620 hints, 695 answers and 695 solutions to verified translated-source spans and start pages in the Indonesian PDF. Native identities and historical states remain unchanged, including 30 questions translated in their parent files. PDF numbers are not printed page numbers. Links require a connection; for offline reading, download the PDF separately and use the displayed PDF page numbers. A missing hint means none is recorded (75 exercises). This checks structure and navigation, not mathematical correctness or translation quality anew. The English interface still uses the Indonesian book and does not assert coverage or numbering of other English editions.'}
        model['pdf_page_or_html_anchors_claimed'] = True
        model['pdf_navigation_courses'] = ['B20']
    return model


def render(course, lang, model):
    en = lang == 'en'
    limitations = course.get('limitations',model['limitations'])
    words = ({'title': 'CLP assignment planner', 'section': 'Source section', 'all': 'All sections', 'filter': 'Support filter', 'every': 'All exercises', 'hint': 'With a recorded hint', 'nohint': 'Without a recorded hint', 'multi': 'Multiple solutions on a surface', 'search': 'Search identifier or source path', 'select': 'Select visible exercises', 'clear': 'Clear selection', 'export': 'Download assignment JSON', 'import': 'Load assignment JSON', 'print': 'Print selection', 'back': 'Books and downloads', 'details': 'Source locations and support', 'choose': 'Select', 'sources': 'Source metadata (reusable)', 'offline': 'Works offline after downloading this directory. Books require separate downloads.'}
             if en else {'title': 'Perencana tugas CLP', 'section': 'Bagian sumber', 'all': 'Semua bagian', 'filter': 'Saring bantuan', 'every': 'Semua soal', 'hint': 'Dengan petunjuk tercatat', 'nohint': 'Tanpa petunjuk tercatat', 'multi': 'Beberapa penyelesaian pada satu format', 'search': 'Cari identitas atau jalur sumber', 'select': 'Pilih soal yang tampil', 'clear': 'Hapus pilihan', 'export': 'Unduh tugas JSON', 'import': 'Muat tugas JSON', 'print': 'Cetak pilihan', 'back': 'Buku dan unduhan', 'details': 'Lokasi sumber dan bantuan', 'choose': 'Pilih', 'sources': 'Metadata sumber (dapat digunakan kembali)', 'offline': 'Berfungsi luring setelah direktori ini diunduh. Buku perlu diunduh secara terpisah.'})
    role = course['course_id']
    choices = ''.join(f'<option value="{escape(s, quote=True)}">{escape(s)}</option>' for s in dict.fromkeys(q['section'] for q in course['questions']))
    payload = encoded({'model': {**course, 'schema': model['schema'], 'limitations': limitations, 'input_identity': model['input_identity']}, 'locale': lang, 'words': words}).decode().replace('<', '\\u003c').replace('&', '\\u0026')
    links = ' · '.join(f'<a href="{r}.teacher{ ".en" if en else "" }.html">{r}</a>' for r in PROFILES.values())
    reader = course['readers']
    original = reader['authoritative_original']
    book_links = f'<li><a lang="en" href="{escape(original["url"], quote=True)}">{("Original English books" if en else "Buku asli berbahasa Inggris")}</a></li>'
    for action in reader['actions']:
        names = {'textbook': ('Textbook', 'Buku teks'), 'problembook': ('Problems and solutions', 'Soal dan penyelesaian'), 'combined_textbook_problembook': ('Textbook, problems and solutions', 'Buku teks, soal, dan penyelesaian')}
        name = names[action['role']][0 if en else 1]
        book_links += f'<li><a lang="id" href="{escape(action["url"], quote=True)}">{name} · Bahasa Indonesia · PDF · {action["pages"]} {"pages" if en else "halaman"}</a> · <a href="{escape(action["evidence"]["locator"], quote=True)}">{"All source files" if en else "Semua berkas sumber"}</a></li>'
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{role} · {words['title']}</title><link rel="stylesheet" href="teacher.css"></head>
<body><a class="skip" href="#main">{'Skip to exercises' if en else 'Langsung ke soal'}</a><header><nav>{links}</nav><nav aria-label="{'Language' if en else 'Bahasa'}"><a lang="id" href="{role}.teacher.html">Bahasa Indonesia</a> · <a lang="en" href="{role}.teacher.en.html">English</a></nav><h1>{role} · {words['title']}</h1><p>{course['exercise_count']} {'distinct exercises' if en else 'soal berbeda'} · {course['section_count']} {'source sections' if en else 'bagian sumber'}</p>
<p>{escape(limitations[lang])}</p><p><a href="#books">{words['back']}</a> · <a href="{role}.teacher.json">{words['sources']}</a></p><details id="books"><summary>{words['back']}</summary><ul>{book_links}</ul></details></header>
<main id="main"><section class="controls"><label>{words['section']}<select id="section"><option value="">{words['all']}</option>{choices}</select></label><label>{words['filter']}<select id="support"><option value="">{words['every']}</option><option value="hint">{words['hint']}</option><option value="nohint">{words['nohint']}</option><option value="multi">{words['multi']}</option></select></label><label>{words['search']}<input type="search" id="search"></label>
<div class="actions"><button id="select-visible">{words['select']}</button><button id="clear">{words['clear']}</button><button id="export">{words['export']}</button><label class="import">{words['import']}<input type="file" id="import" accept="application/json,.json"></label><button id="print">{words['print']}</button></div></section>
<details id="exchange"><summary>{'Copy or paste assignment JSON' if en else 'Salin atau tempel JSON tugas'}</summary><p>{'Export also places the JSON here. Copy it manually if downloads are unavailable. Paste a saved assignment and load it to restore your selection.' if en else 'Ekspor juga menampilkan JSON di sini. Salin secara manual jika unduhan tidak tersedia. Tempel tugas yang disimpan, lalu muat untuk memulihkan pilihan.'}</p><button id="show-json">{'Show selected assignment JSON' if en else 'Tampilkan JSON tugas terpilih'}</button><label for="assignment-text">{'Assignment JSON' if en else 'JSON tugas'}</label><textarea id="assignment-text" rows="8" spellcheck="false"></textarea><button id="load-text">{'Load pasted assignment' if en else 'Muat tugas yang ditempel'}</button></details>
<p id="status" role="status" aria-live="polite"></p><p id="error" role="alert"></p><div id="exercises"></div><noscript>{'Enable JavaScript to select exercises, or use the linked JSON data.' if en else 'Aktifkan JavaScript untuk memilih soal, atau gunakan data JSON yang ditautkan.'}</noscript></main>
<footer><p>{words['offline']}</p><p>{'The original CLP authors are Joel Feldman, Andrew Rechnitzer and Elyse Yeager. Native rights identities are retained for every exercise; CC BY-NC-SA 4.0.' if en else 'Penulis asli CLP adalah Joel Feldman, Andrew Rechnitzer, dan Elyse Yeager. Identitas hak sumber dipertahankan pada setiap soal; CC BY-NC-SA 4.0.'}</p><p>{'Planner integration produced by OpenAI Codex — gpt-6-astra, Ultra effort. This is not a new translation or a claim of human review.' if en else 'Integrasi perencana dibuat oleh OpenAI Codex — gpt-6-astra, tingkat upaya Ultra. Ini bukan terjemahan baru atau klaim peninjauan manusia.'}</p></footer>
<script id="planner-data" type="application/json">{payload}</script><script src="teacher.js"></script></body></html>'''


def build(output, base=BASE):
    native, lock = load(base)
    model = project(native,load_navigation(base))
    model['input_identity'] = lock
    output.mkdir(parents=True, exist_ok=True)
    files = {}
    for course in model['courses']:
        role = course['course_id']
        files[f'{role}.teacher.json'] = encoded({**course, 'schema': model['schema'], 'limitations': course.get('limitations',model['limitations']), 'input_identity': lock})
        for lang in ('id', 'en'):
            files[f'{role}.teacher' + ('.en' if lang == 'en' else '') + '.html'] = render(course, lang, model).encode()
    files['teacher-map.json'] = encoded(model)
    for name in ('teacher.js', 'teacher.css'):
        files[name] = (base / 'ui' / name).read_bytes()
    for name, data in files.items():
        (output / name).write_bytes(data)
    receipt = {'schema': 'clp-teacher-build/1', 'state': 'built-not-admitted', 'exercise_count': model['source_exercises'], 'course_counts': {c['course_id']: c['exercise_count'] for c in model['courses']},
               'input_identity': lock, 'files': [{'path': n, 'bytes': len(b), 'sha256': sha(b)} for n, b in sorted(files.items())]}
    (output / 'teacher-build.json').write_bytes(encoded(receipt))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=BASE / 'site')
    args = parser.parse_args()
    result = build(args.output)
    print(json.dumps({'state': result['state'], 'exercises': result['exercise_count'], 'files': len(result['files'])}))
