"""Build a source-preserving, bilingual D110 study/teaching selector."""
from collections import Counter
import argparse
import hashlib
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'backend/course-capsule-v1/adapters/d110-surface-v1'
LICENSES = {
    'LICENSE-APACHE-2.0.txt': 'b40930bbcf80744c86c46a12bc9da056641d722716c378f5659b9e555ef833e1',
    'LICENSE-CC-BY-4.0.txt': '9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()


def load():
    body = (BASE / 'input/source-lock.json').read_bytes()
    lock = json.loads(body)
    assert lock['schema'] == 'd110-consumer-input/1'
    files = {}
    for f in lock['files']:
        assert '/' not in f['path'] and '\\' not in f['path'] and '..' not in f['path']
        b = (BASE / 'input' / f['path']).read_bytes()
        assert (len(b), sha(b)) == (f['bytes'], f['sha256']), f['path']
        files[f['path']] = [json.loads(line) for line in b.decode().splitlines()] if f['path'].endswith('.jsonl') else json.loads(b)
    authority = lock['admission_authority']
    b = (ROOT / authority['path']).read_bytes()
    assert (len(b), sha(b)) == (authority['bytes'], authority['sha256'])
    files['identity'] = {'path': 'input/source-lock.json', 'bytes': len(body), 'sha256': sha(body)}
    files['lock'] = lock
    return files


def project(data):
    native, assets, relations = data['unit.jsonl'], data['asset.jsonl'], data['relation.jsonl']
    witness, texts = data['reader-witness.json'], data['solution-witness.json']
    assert witness['schema'] == 'd110-reader-witness/1' and witness['public_verified'] is True
    assert witness['readers'] == {
        'id': 'https://kokunoyumeto.github.io/mathematics-in-lean-id/',
        'en': 'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/D110/'}
    by_id = {u['record_id']: u for u in native}
    assert len(by_id) == len(native)
    rights = {r['record_id'] for r in data['rights.jsonl']}
    asset_by_id = {a['record_id']: a for a in assets}
    assert len(asset_by_id) == len(assets)
    solution_texts = {r['id']: r['texts'] for r in texts['units']}
    assert len(solution_texts) == len(texts['units'])
    pages = {p['url']: p for p in witness['pages']}
    assert len(pages) == 26
    chapters = [u for u in native if u['data']['unit_type'] == 'chapter']
    sections = [u for u in native if u['data']['unit_type'] == 'section']
    assert set(witness['routes']) == {u['record_id'] for u in chapters + sections}
    for ident, routes in witness['routes'].items():
        assert set(routes) == {'id', 'en'}
        for lang, r in routes.items():
            assert r['state'] == 'verified_heading' and r['url'].startswith(witness['readers'][lang])
            url, fragment = r['url'].split('#')
            assert fragment == r['anchor'] and fragment and url in pages
            assert r['page_sha256'] == pages[url]['sha256']
            assert len([h for h in pages[url]['headings'] if h['anchor'] == fragment]) == 1

    def ancestors(u):
        result, seen = [], {u['record_id']}
        while u['parent_id'] in by_id:
            u = by_id[u['parent_id']]
            assert u['record_id'] not in seen, 'Parent cycle'
            seen.add(u['record_id'])
            result.append(u)
        assert u['parent_id'] == 'urn:mil:course:mathematics-in-lean'
        return result

    result = []
    for u in native:
        ident, d = u['record_id'], u['data']
        lineage = [u, *ancestors(u)]
        chapter = next((p for p in lineage if p['data']['unit_type'] == 'chapter'), None)
        section = next((p for p in lineage if p['data']['unit_type'] == 'section'), None)
        nearest = section or chapter
        routes, title = {}, {}
        for lang in ('id', 'en'):
            if nearest:
                r = witness['routes'][nearest['record_id']][lang]
                routes[lang] = {**r, 'state': 'exact_heading' if ident == nearest['record_id'] else 'enclosing_section',
                                'bound_unit_id': nearest['record_id'], 'code_equivalence_claimed': False}
            else:
                routes[lang] = {'url': witness['readers'][lang], 'anchor': None, 'state': 'book_context', 'code_equivalence_claimed': False}
            title[lang] = witness['routes'][ident][lang]['title'] if ident in witness['routes'] else u['source_local_id']
        assert u['rights_id'] in rights, f'Unknown rights {ident}'
        code = None
        if d.get('code_asset_id'):
            a = asset_by_id[d['code_asset_id']]
            assert a['data']['asset_type'] in ('embedded_lean_code', 'literalinclude_lean_code')
            ad = a['data']
            for side in ('source', 'target'):
                assert sha(ad[f'{side}_text'].encode()) == ad[f'{side}_text_sha256'], f'Code drift: {ident}'
            code = {'id': ad['target_text'], 'en': ad['source_text'],
                    'sha256': {'id': ad['target_text_sha256'], 'en': ad['source_text_sha256']},
                    'asset_id': a['record_id'], 'scope': 'shared_learner_code_block',
                    'source_asset_identity': {'id': a['record_id'], 'canonical_record_sha256': sha(encoded(a))}}
        elif ident in solution_texts:
            snippets = solution_texts[ident]
            if snippets:
                code = {'sha256': {}, 'scope': 'source_solution_or_support_fragment', 'witness': {}}
                for lang, key in [('id', 'target_text_sha256'), ('en', 'source_text_sha256')]:
                    s = snippets.get(lang)
                    if s and s['state'] in ('exact_hash_span', 'exact_hash_projection'):
                        assert s['sha256'] == d[key] == sha(s['text'].encode()), f'Solution drift: {ident}'
                        code[lang], code['sha256'][lang], code['witness'][lang] = s['text'], s['sha256'], s
                    else:
                        code[lang] = None
        result.append({'id': ident, 'kind': d['unit_type'], 'practice': d.get('is_exercise') is True,
                       'chapter_id': chapter['record_id'] if chapter else '',
                       'section_id': section['record_id'] if section else '', 'title': title,
                       'reader_routes': routes, 'source_locator': u['source_locator'],
                       'source_locator_scope': 'original_authoring_witness_not_current_target_lines',
                       'rights_ids': [u['rights_id']], 'concept_ids': u['concept_ids'],
                       'code': code, 'supports': [], 'supporting': [],
                       'companion': bool(d.get('no_exercise_declaration')), 'source_record': u})
    projected = {u['id']: u for u in result}
    support_rows = [r for r in relations if r['data']['relation_type'] in ('solves', 'supports')]
    assert len(support_rows) == len({r['record_id'] for r in support_rows})
    for r in support_rows:
        d = r['data']
        source, target = projected[d['subject_id']], projected[d['object_id']]
        assert source['kind'] == ('solution' if d['relation_type'] == 'solves' else 'solution_support')
        if d['relation_type'] == 'solves':
            sd = source['source_record']['data']
            # Two native source solutions explain demonstrations, not exercises.
            assert (sd.get('exercise_id') or sd.get('source_unit_id')) == target['id']
            if sd.get('target_is_exercise') is not None:
                assert sd['target_is_exercise'] == target['practice']
            assert (d.get('exercise_id') or d.get('source_unit_id')) == target['id']
            assert d.get('solution_id', source['id']) == source['id']
        else:
            assert target['kind'] == 'solution'
            assert source['source_record']['data']['supported_solution_id'] == target['id']
            assert d['support_id'] == source['id'] and d['solution_id'] == target['id']
        target['supports'].append({'relation_id': r['record_id'], 'id': source['id'], 'target_id': target['id'],
                                   'kind': d['relation_type'], 'source_record': r})
        target['supporting'].append(source['id'])
    for u in result:
        if u['practice']:
            assert u['code'] and u['code']['scope'] == 'shared_learner_code_block'
            d = u['source_record']['data']
            if d.get('solution_id'):
                assert d['solution_id'] in u['supporting']
            for ident in d.get('solution_ids', []):
                assert ident in u['supporting']
    kinds = Counter(u['kind'] for u in result)
    counts = {'units': len(result), 'kinds': dict(kinds), 'chapters': len(chapters), 'sections': len(sections),
              'practice_flags': sum(u['practice'] for u in result),
              'practice_with_solution_relation': sum(u['practice'] and bool(u['supports']) for u in result),
              'practice_without_solution_relation': sum(u['practice'] and not u['supports'] for u in result),
              'solves_edges': sum(r['data']['relation_type'] == 'solves' for r in support_rows),
              'supports_edges': sum(r['data']['relation_type'] == 'supports' for r in support_rows),
              'solution_fragments_with_both_texts': sum(u['kind'] in ('solution', 'solution_support') and bool(u['code']) and bool(u['code'].get('id')) and bool(u['code'].get('en')) for u in result)}
    assert (counts['units'], counts['practice_flags'], counts['practice_without_solution_relation'], counts['solves_edges'], counts['supports_edges'], counts['solution_fragments_with_both_texts']) == (2177, 243, 6, 324, 6, 330)
    chapter_list = [{'id': u['record_id'], 'title': projected[u['record_id']]['title']} for u in chapters]
    section_list = [{'id': u['record_id'], 'chapter_id': u['parent_id'], 'title': projected[u['record_id']]['title'],
                     'routes': projected[u['record_id']]['reader_routes']} for u in sections]
    return {'schema': 'd110-study-map/1', 'course_id': 'D110', 'input_identity': data['identity'],
            'counts': counts, 'chapters': chapter_list, 'sections': section_list, 'units': result,
            'rights': data['rights.jsonl'], 'relations': relations, 'reader_witness': witness,
            'solutions_generated': False, 'lean_compilation_performed': False,
            'limitations': {
                'id': ['Bahasa Indonesia dan English tersedia untuk antarmuka, bacaan, dan cuplikan kode sumber. Ini bukan penulisan ulang dalam bahasa sehari-hari.',
                       'Pembaca Inggris memakai revisi berbeda. Tautan bab/bagian memberi konteks bacaan, bukan bukti kesamaan setiap deklarasi kode.',
                       '243 unit ditandai sebagai latihan oleh sumber; beberapa merupakan contoh pengajaran. Enam tidak mempunyai relasi solusi tercatat.',
                       'Solusi dapat mengisi satu lubang bukti atau memberi alternatif. Banyaknya solusi bukan banyaknya latihan yang selesai.',
                       'Kode latihan dapat berupa satu blok bersama untuk beberapa ID. Nomor baris sumber bukan nomor baris terjemahan.',
                       'Rencana memuat pilihan, asal sumber, dan tautan. Buku lengkap tidak disertakan untuk dibaca luring. Tidak ada kode Lean yang dijalankan.'],
                'en': ['Indonesian and English interfaces, reading contexts and original code snippets are available. This is not an everyday-English rewrite.',
                       'The English reader uses a different revision. Chapter/section links give reading context, not proof of equivalence for each code declaration.',
                       '243 units carry the native exercise flag; some are teaching examples. Six have no recorded solution relation.',
                       'Solutions may fill one proof hole or give an alternative. Solution counts are not counts of completed exercises.',
                       'An exercise snippet may be a shared block for several IDs. Source line numbers are not translated-file line numbers.',
                       'Plans contain selections, provenance and links, not a complete offline book. No Lean code is executed.']}}


def render(m, lang, teacher):
    def t(id_text, en_text):
        return escape(en_text if lang == 'en' else id_text)
    suffix = '.en' if lang == 'en' else ''
    mode = 'teacher' if teacher else 'index'
    title = t('Matematika dalam Lean · Pilihan belajar dan mengajar', 'Mathematics in Lean · Study and teaching plans')
    readings = ''.join(f'<li><a href="{escape(s["routes"][lang]["url"])}">{escape(s["title"][lang])}</a></li>' for s in m['sections'])
    limits = ''.join(f'<li>{escape(text)}</li>' for text in m['limitations'][lang])
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'"><title>D110 · {title}</title><link rel="stylesheet" href="d110.css"><script defer src="data.js"></script><script defer src="d110-ui.js"></script></head><body data-language="{lang}" data-mode="{'teacher' if teacher else 'learner'}"><a href="#main">{t('Langsung ke isi','Skip to content')}</a><nav><a href="{mode}.html">Bahasa Indonesia</a> · <a href="{mode}.en.html">English</a> · <a href="{'index' if teacher else 'teacher'}{suffix}.html">{t('Untuk pelajar' if teacher else 'Untuk pengajar','For learners' if teacher else 'For teachers')}</a> · <a href="https://kokunoyumeto.github.io/program-matematika-indonesia/{lang}/#course-D110">{t('Program matematika','Mathematics program')}</a></nav><main id="main"><header><h1>D110 · {title}</h1><p>{t('Pilih bagian, blok kode, dan latihan. Simpan rencana dengan ID sumber dan relasi solusi yang tetap utuh.','Choose sections, code blocks and exercises. Save a plan with its original IDs and solution relationships intact.')}</p><p>13 {t('bab','chapters')} · 43 {t('bagian','sections')} · 243 {t('unit bertanda latihan','exercise-marked units')}</p></header><details><summary>{t('Daftar bacaan lengkap — juga berfungsi tanpa JavaScript','All readings — also works without JavaScript')}</summary><ol>{readings}</ol></details><section aria-labelledby="choose"><h2 id="choose">{t('Susun pilihan Anda','Build your selection')}</h2><div class="filters"><label for="search">{t('Cari judul atau ID','Search title or ID')}</label><input id="search" type="search"><label for="kind">{t('Jenis','Kind')}</label><select id="kind"><option value="">{t('Semua jenis','All kinds')}</option><option value="practice">{t('Bertanda latihan','Exercise-marked')}</option></select><label for="chapter">{t('Bab','Chapter')}</label><select id="chapter"><option value="">{t('Semua bab','All chapters')}</option></select></div><div class="actions"><button id="select-page">{t('Pilih halaman hasil ini','Select this results page')}</button><button id="clear">{t('Hapus pilihan','Clear selection')}</button><button id="export" disabled>{t('Simpan JSON','Save JSON')}</button><button id="export-text" disabled>{t('Simpan teks','Save text')}</button><span id="selection" role="status"></span></div><p id="results-status" role="status" aria-live="polite"></p><div id="unit-list"></div><div class="actions"><button id="previous">{t('Sebelumnya','Previous')}</button><button id="next">{t('Berikutnya','Next')}</button></div><noscript><p>{t('Daftar bacaan di atas tetap tersedia. Pencarian dan ekspor pilihan memerlukan JavaScript.','The reading list above remains available. Searching and selected-plan export require JavaScript.')}</p></noscript></section><section><h2>{t('Cakupan dan batas','Scope and limits')}</h2><ul>{limits}</ul><p>{t('Kode: Apache-2.0; teks buku: CC BY 4.0. Catatan komponen asli dipertahankan.','Code: Apache-2.0; book text: CC BY 4.0. Original component notices are retained.')}</p><a href="learning-map.json">{t('Data dan catatan sumber','Data and source records')}</a> · <a href="validation.json">{t('Hasil pemeriksaan struktur','Structural validation')}</a></section><footer><p>{t('Kode antarmuka dan pemetaan dibuat oleh OpenAI Codex — GPT-6 Astra, Ultra effort. Ini bukan atribusi penerjemahan buku atau pemeriksaan manusia.','Interface code and mapping produced by OpenAI Codex — GPT-6 Astra, Ultra effort. This does not attribute the original book translation or claim human review.')}</p><p><a href="LICENSE-APACHE-2.0.txt">Apache-2.0</a> · <a href="LICENSE-CC-BY-4.0.txt">CC BY 4.0</a> · <a href="https://github.com/KokunoYumeto/program-matematika-indonesia/tree/main/backend/course-capsule-v1/adapters/d110-surface-v1">{t('Kode dan petunjuk reproduksi','Code and reproduction instructions')}</a></p></footer></main></body></html>\n'''


def build(out=None):
    m = project(load())
    out = out or BASE / 'portable'
    out.mkdir(parents=True, exist_ok=True)
    ui = {key: value for key, value in m.items() if key not in ('relations', 'rights', 'reader_witness')}
    outputs = {'learning-map.json': encoded(m), 'data.js': ('globalThis.D110_DATA=' + json.dumps(ui, ensure_ascii=False, separators=(',', ':')) + ';\n').encode()}
    for lang in ('id', 'en'):
        for teacher in (False, True):
            name = ('teacher' if teacher else 'index') + ('.en' if lang == 'en' else '') + '.html'
            outputs[name] = render(m, lang, teacher).encode()
    for name in ('d110-ui.js', 'd110.css'):
        outputs[name] = (ROOT / 'scripts/d110-surface' / name).read_bytes()
    for name, expected in LICENSES.items():
        body = (BASE / 'input' / name).read_bytes()
        assert sha(body) == expected, name
        outputs[name] = body
    report = {'schema': 'd110-consumer-build/1', 'state': 'pass', 'counts': m['counts'],
              'input_identity': m['input_identity'], 'scope': 'source mapping and deterministic generation; not browser/publication verification',
              'outputs': [{'path': p, 'bytes': len(b), 'sha256': sha(b)} for p, b in outputs.items()]}
    outputs['validation.json'] = encoded(report)
    for path, body in outputs.items():
        (out / path).write_bytes(body)
    return m, outputs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-root', type=Path)
    args = parser.parse_args()
    m, _ = build(args.output_root)
    print(json.dumps({'state': 'pass', 'counts': m['counts']}, ensure_ascii=False))
