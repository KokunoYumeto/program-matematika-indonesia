"""Expose exact D70 metadata reproducibility; do not upgrade full-native claims."""
from __future__ import annotations
import copy
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'backend/course-capsule-v1/adapters/d70-native-replay-v1'
SITE = 'docs/backend/d70-replay'
SOURCE_NAME = '05_o013-sumber-backend-1.0.0.zip'

LIMITATION_TRANSLATIONS = [
    ("This adapter contains metadata, evidence, route text, diagnostics, and edition-original mastery only; it copies no native book body, formula, TeX, PDF, or source archive.",
     "Adapter ini hanya memuat metadata, bukti, teks rute, diagnostik, serta bahan penguasaan yang dibuat khusus untuk edisi ini; tidak ada isi buku asli, rumus, TeX, PDF, atau arsip sumber yang disalin."),
    ("P01-P06 map only to the Li component because the native route does not identify exact Li unit roots for them.",
     "P01-P06 hanya dipetakan ke komponen Li karena rute asli tidak mengidentifikasi simpul awal unit Li yang tepat untuk keenam bagian tersebut."),
    ("The CRing component is six exact selected spans, not the complete CRing work.",
     "Komponen CRing memuat enam rentang terpilih yang batasnya ditetapkan secara persis, bukan seluruh karya CRing."),
    ("Duncan's six external assignment sheets, 49 problems, and partial solution are outside the pinned CC BY repository and remain excluded.",
     "Enam lembar tugas eksternal Duncan, 49 soal, dan solusi parsial berada di luar repositori CC BY yang telah dipatok versinya dan tetap tidak disertakan."),
    ("The source components provide no answers or solutions; the eight mastery answers are separately attributed edition-original material.",
     "Komponen sumber tidak menyediakan jawaban atau solusi; delapan jawaban penguasaan adalah bahan asli edisi ini dengan atribusi tersendiri."),
    ("Generated HTML is metadata navigation, not a converted native semantic reader.",
     "HTML yang dihasilkan adalah navigasi metadata, bukan pembaca semantik asli yang telah dikonversi."),
    ("No native EPUB, MathML, tagged PDF, complete ToUnicode, WCAG conformance, or assistive-technology user test is claimed.",
     "Tidak ada klaim mengenai EPUB asli, MathML asli, PDF bertag, pemetaan ToUnicode yang lengkap, kepatuhan WCAG, atau pengujian oleh pengguna teknologi pendukung."),
    ("Li whole-reader byte replay and all PDF byte replay remain unproven; the full native roundtrip is therefore false.",
     "Reproduksi seluruh pembaca Li maupun seluruh PDF dengan byte yang persis sama belum terbukti; karena itu, proses bolak-balik seluruh lapisan asli belum terbukti berhasil (full_native_roundtrip: false)."),
]


def localize_limitations():
    source_path = 'backend/course-capsule-v1/adapters/d70-capability-v1/data/capabilities.json'
    source = load(source_path)
    assert source['limitations'] == [row[0] for row in LIMITATION_TRANSLATIONS], 'Limitation source changed; review exact meanings before localization'
    surfaces = ['docs/backend/d70/D70.html', 'docs/backend/d70/D70-pengajar.html']
    choices = []
    for index, (original, target) in enumerate(LIMITATION_TRANSLATIONS, 1):
        choices.append({'id': f'D70:UI:LIMITATION:{index:02}', 'source_segment': source_path + f'#/limitations/{index - 1}',
            'source_text': original, 'source_sha256': hashlib.sha256(original.encode('utf-8')).hexdigest(),
            'target_text': target, 'target_sha256': hashlib.sha256(target.encode('utf-8')).hexdigest(),
            'target_segments': [path + f'#d70-batas-{index:02}' for path in surfaces],
            'choice_rule': 'metadata-scope-preservation-v1',
            'rationale': 'Pertahankan semua batas cakupan, angka, nama komponen, penyangkalan klaim, dan status bukti; jangan mengubah bahan matematika atau memperluas hasil pengujian.',
            'consulted_passages': ['W3C-ID-WAI-ARIA', 'W3C-ID-ACCESSIBILITY-COMPONENTS'] if index in [6, 7] else [],
            'attestation_scope': 'Istilah aksesibilitas didukung dua teks teknis Indonesia yang benar-benar dibaca; bagian lain merupakan pelokalan prosa metadata, bukan bukti istilah matematika.' if index == 7 else 'Perbandingan langsung terhadap prosa metadata sumber; tidak diklaim sebagai pengesahan istilah matematika oleh kanon.',
            'rejected_alternatives': ['teknologi bantu: tidak dipilih karena dua sumber yang dibaca menggunakan teknologi pendukung'] if index == 7 else ['Menghapus kata belum, pengecualian, atau batas angka: ditolak karena akan memperluas klaim sumber.'],
            'confidence': {'label': 'tinggi untuk kesetiaan batas metadata', 'reason': 'Seluruh butir dibandingkan dengan teks sumber persis; klaim negatif, angka, dan pengenal dipertahankan.', 'calibrated_probability': False},
            'human_review_performed': False})
    references = [
        {'id': 'W3C-ID-WAI-ARIA', 'url': 'https://www.w3.org/WAI/standards-guidelines/id',
         'locator': 'Aplikasi Internet yang Kaya dan Aksesibel (WAI-ARIA), paragraf pembuka; Pedoman Aksesibilitas Konten Web (WCAG) 2',
         'consulted_at': '2026-09-30', 'translation_updated': '2024-03-18',
         'exact_terms_consulted': ['teknologi pendukung', 'pembaca layar', 'Pedoman Aksesibilitas Konten Web'],
         'limitation': 'Terjemahan sukarela yang diperingatkan oleh W3C; versi Inggris diperbarui kemudian. Bukti penggunaan teknis, bukan standar normatif berbahasa Indonesia atau pengesahan matematika.'},
        {'id': 'W3C-ID-ACCESSIBILITY-COMPONENTS', 'url': 'https://www.w3.org/WAI/fundamentals/accessibility-principles/id',
         'locator': 'Standar aksesibilitas web, daftar komponen dan paragraf Lebih lanjut tentang standar aksesibilitas web',
         'consulted_at': '2026-09-30', 'translation_updated': '2023-12-07',
         'exact_terms_consulted': ['teknologi pendukung', 'pembaca layar'],
         'limitation': 'Terjemahan sukarela berstatus draf; versi Inggris diperbarui kemudian. Tidak membuktikan kepatuhan aksesibilitas D70.'},
    ]
    for path in surfaces:
        target_path = ROOT / path
        before = target_path.read_bytes()
        text = before.decode('utf-8')
        for index, (original, target) in enumerate(LIMITATION_TRANSLATIONS, 1):
            old = '<li>' + html.escape(original) + '</li>'
            replacement = f'<li id="d70-batas-{index:02}">' + html.escape(target) + '</li>'
            assert text.count(old) + text.count(replacement) == 1, 'Missing/ambiguous limitation occurrence: ' + path
            text = text.replace(old, replacement)
        review_link = ('<p id="d70-batas-review"><a href="../d70-replay/limitations-review.id.html">'
                       'Catatan pilihan bahasa dan batas bukti D70</a>. Pelokalan catatan batas: '
                       'OpenAI Codex — gpt-6.1-sol, tingkat upaya Ultra.</p>')
        if 'id="d70-batas-review"' not in text:
            assert text.count('</main>') == 1
            text = text.replace('</main>', review_link + '</main>')
        assert target_path.read_bytes() == before, 'Concurrent D70 surface edit'
        target_path.write_text(text, encoding='utf-8', newline='\n')
    ledger = {'schema': 'd70-ui-metadata-localization-choices/1', 'locale': 'id',
        'source': {'path': source_path, **fact(source_path)}, 'consulted_references': references, 'choices': choices,
        'mathematical_content_modified': False, 'native_terminology_canon_review': False,
        'whole_surface_localization_claimed': False, 'human_review_required_to_continue': False,
        'scope_note': 'Delapan batas metadata pada dua permukaan pusat; tidak mengklaim peninjauan seluruh istilah buku atau seluruh metadata native.'}
    save(BASE + '/metadata-localization-choices.id.json', ledger)
    save(SITE + '/metadata-localization-choices.id.json', ledger)
    parts = ['<!doctype html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
             '<title>D70 · Catatan pilihan bahasa untuk batas bukti</title><style>body{font:17px/1.6 system-ui;max-width:74ch;margin:auto;padding:24px;color:#183a35;background:#f5f5ed}a{color:#086b63}a:focus-visible{outline:3px solid #bd7519;outline-offset:3px}blockquote{margin:12px 0;padding:12px;background:#e5ece7}code{overflow-wrap:anywhere}</style></head><body><main>',
             '<nav aria-label="Navigasi D70"><a href="index.html">Petunjuk produksi ulang metadata</a> · <a href="../d70/D70-pengajar.html">Panduan pengajar</a> · <a href="../d70/D70.html">Rute pembelajar</a></nav>',
             '<h1>Catatan pilihan bahasa untuk batas bukti D70</h1><p>Delapan batas cakupan pada halaman pembelajar dan pengajar dilokalkan ke Bahasa Indonesia. Angka, pengenal, pengecualian, dan penyangkalan klaim tetap sama. Isi buku dan rumus tidak diubah. Ini bukan pengesahan kanon matematika atau audit lengkap semua metadata.</p>',
             '<p>Peninjauan manusia belum dilakukan dan tidak menjadi syarat untuk melanjutkan pekerjaan. Keputusan dapat ditinjau dan diperbaiki dengan bukti baru.</p><h2>Sumber bahasa yang benar-benar dibaca</h2><ul>']
    for row in references:
        parts.append('<li><a href="' + html.escape(row['url']) + '">' + html.escape(row['id']) + '</a>: ' + html.escape(row['locator']) + '. ' + html.escape(row['limitation']) + '</li>')
    parts.append('</ul><h2>Pemetaan setiap catatan</h2>')
    for row in choices:
        parts.append('<section id="' + row['id'] + '"><h3>' + row['id'] + '</h3><p>Teks sumber (Inggris):</p><blockquote lang="en">' + html.escape(row['source_text']) + '</blockquote><p>Hasil pelokalan: ' + html.escape(row['target_text']) + '</p><p>Alasan: ' + html.escape(row['rationale']) + '</p><p>Batas bukti penggunaan: ' + html.escape(row['attestation_scope']) + '</p><p>Alternatif yang ditolak: ' + html.escape('; '.join(row['rejected_alternatives'])) + '</p></section>')
    parts.append('<p><a href="metadata-localization-choices.id.json">Unduh catatan pilihan yang dapat dibaca mesin</a></p><footer>Pelokalan metadata dan catatan peninjauan: OpenAI Codex — gpt-6.1-sol, tingkat upaya Ultra.</footer></main></body></html>\n')
    (ROOT / SITE / 'limitations-review.id.html').write_text(''.join(parts), encoding='utf-8', newline='\n')


def load(path):
    return json.loads((ROOT / path).read_bytes())


def fact(path):
    data = (ROOT / path).read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def save(path, data):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def page(locale, validation, build):
    english = locale == 'en'
    name = 'index.en.html' if english else 'index.html'
    opposite = 'index.html' if english else 'index.en.html'
    title = 'D70: reproduce native metadata' if english else 'D70: bangun ulang metadata native'
    source = validation['source_archive']
    bundle = build['bundle']
    command = ('python -B scripts/replay-d70-native-metadata-v1.py --bundle D70_NATIVE_METADATA_REPLAY_V1.zip '
               '--source-archive ' + SOURCE_NAME + ' --work-dir replay-work --output replay-result.json')
    parts = [f'<!doctype html><html lang="{locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
             f'<title>{html.escape(title)}</title><style>body{{font:17px/1.6 system-ui;background:#f5f5ed;color:#183a35;margin:0}}main{{max-width:74ch;margin:auto;padding:24px}}a{{color:#086b63}}a:focus-visible{{outline:3px solid #bd7519;outline-offset:3px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;padding:16px;background:#e5ece7}}code{{overflow-wrap:anywhere}}dt{{font-weight:650}}dd{{margin:0 0 14px;overflow-wrap:anywhere}}li{{margin-bottom:12px}}</style></head><body><main>',
             f'<nav aria-label="{"Language" if english else "Bahasa"}"><a lang="{"id" if english else "en"}" hreflang="{"id" if english else "en"}" href="{opposite}">{"Bahasa Indonesia" if english else "English"}</a> · <a href="../d70/D70-pengajar.html">{"D70 teacher guide (Indonesian)" if english else "Panduan pengajar D70"}</a></nav>', f'<h1>{html.escape(title)}</h1>']
    parts.append('<p>' + ('Both native builders, Duncan and the six selected CRing spans, run from the exact source archive plus 26 additional frozen inputs. Two isolated executions of the packaged code reproduce all 13 shipped metadata artifacts byte for byte.' if english else 'Dua pembangun native, Duncan dan enam rentang CRing terpilih, dijalankan dari arsip sumber yang persis sama ditambah 26 input beku. Dua eksekusi terpisah atas kode dalam paket menghasilkan kembali seluruh 13 berkas metadata terbitan dengan byte yang sama.') + '</p>')
    parts.append('<h2>' + ('Run it yourself' if english else 'Jalankan sendiri') + '</h2><ol>')
    parts.append('<li><a href="D70_NATIVE_METADATA_REPLAY_V1.zip" download>' + ('Download the dependency and editable replay-source ZIP' if english else 'Unduh ZIP dependensi dan sumber replay yang dapat diedit') + '</a>. ' + ('Extract it; keep the original ZIP beside the extracted files.' if english else 'Ekstrak; simpan ZIP asli di samping berkas hasil ekstraksi.') + '</li>')
    parts.append('<li><a href="https://zenodo.org/api/records/22160944/files/' + SOURCE_NAME + '/content" download>' + ('Download the unchanged native source ZIP from its original public record' if english else 'Unduh ZIP sumber native yang tidak diubah dari rekaman publik aslinya') + '</a>. ' + ('Do not rename it. Native book sources remain in that lineage, not in the shared adapter.' if english else 'Jangan ubah namanya. Sumber buku native tetap berada pada lini rilis itu, bukan di dalam adapter bersama.') + '</li>')
    parts.append('<li>' + ('With Python 3.10 or later, run the command below from the extracted directory. No package installation, network connection during replay, translation model or TeX engine is required. Historical translation scripts are only evidence inputs and are not executed.' if english else 'Dengan Python 3.10 atau lebih baru, jalankan perintah berikut dari direktori hasil ekstraksi. Tidak perlu instalasi paket, jaringan saat replay, model penerjemahan atau mesin TeX. Skrip penerjemahan lama hanya menjadi input bukti dan tidak dijalankan.') + '</li></ol>')
    parts.append('<pre><code>' + html.escape(command) + '</code></pre><p>' + ('Expected result: state “pass”, 13 matching metadata artifacts. Inspect replay-result.json for each artifact and validator result.' if english else 'Hasil yang diharapkan: state “pass”, 13 berkas metadata cocok. Periksa replay-result.json untuk identitas setiap berkas dan hasil validator.') + '</p>')
    parts.append('<h2>' + ('Exact download identities' if english else 'Identitas unduhan yang persis') + '</h2><dl>')
    for label, identity in [('D70_NATIVE_METADATA_REPLAY_V1.zip', bundle), (SOURCE_NAME, source)]:
        parts.append('<dt>' + html.escape(label) + '</dt><dd>' + str(identity['bytes']) + ' ' + ('bytes' if english else 'byte') + '; SHA-256 <code>' + identity['sha256'] + '</code></dd>')
    parts.append('</dl><h2>' + ('What this does not prove' if english else 'Hal yang belum dibuktikan') + '</h2><p>' + ('This closes the metadata dependency gap, not reproduction of the full Li reader or all four PDFs. No new semantic terminology/canon review, tagged-PDF claim, screen-reader test or whole-program completion is implied. Native component rights, exact selected boundaries and translation credits are unchanged.' if english else 'Ini menutup celah dependensi metadata, bukan membuktikan produksi ulang seluruh pembaca Li atau keempat PDF. Tidak ada peninjauan semantik istilah/kanon baru, klaim PDF bertag, uji pembaca layar atau klaim bahwa seluruh program selesai. Hak komponen native, batas pilihan yang persis dan kredit penerjemahan tidak berubah.') + '</p>')
    parts.append('<p><a href="validation.json">' + ('Machine-readable execution evidence' if english else 'Bukti eksekusi yang dapat dibaca mesin') + '</a> · <a href="../coverage.html">' + ('All forty roles and remaining requirements' if english else 'Seluruh empat puluh peran dan kebutuhan tersisa') + '</a></p><footer><p>' + ('Dependency integration, instructions and verification: ' if english else 'Integrasi dependensi, petunjuk dan verifikasi: ') + 'OpenAI Codex — gpt-6.1-sol, Ultra effort.</p></footer></main></body></html>\n')
    return name, ''.join(parts).encode('utf-8')


def main():
    validation, build = load(BASE + '/validation.json'), load(BASE + '/build/BUILD_RECEIPT.json')
    assert validation['state'] == build['state'] == 'pass'
    assert validation['packaged_sources_executed'] is True and validation['two_isolated_replays_identical'] is True
    assert len(validation['artifact_comparisons']) == 13 and all(row['matches_shipped_bytes'] for row in validation['artifact_comparisons'])
    assert len(validation['commands']) == 2 and all(row['exit_code'] == 0 for row in validation['commands'])
    for flag in ['producer_tree_required', 'fresh_tex_build', 'fresh_semantic_canon_review', 'whole_native_parity_proven', 'producer_files_modified']:
        assert validation[flag] is False
    assert validation['dependency_bundle'] == fact(build['bundle']['path'])
    assert {key: build['bundle'][key] for key in ['bytes', 'sha256']} == validation['dependency_bundle']
    public = ROOT / SITE
    public.mkdir(parents=True, exist_ok=True)
    for source, target in [(BASE + '/build/D70_NATIVE_METADATA_REPLAY_V1.zip', 'D70_NATIVE_METADATA_REPLAY_V1.zip'),
                           (BASE + '/validation.json', 'validation.json'), (BASE + '/build/BUILD_RECEIPT.json', 'BUILD_RECEIPT.json')]:
        (public / target).write_bytes((ROOT / source).read_bytes())
    for locale in ['id', 'en']:
        name, data = page(locale, validation, build)
        (public / name).write_bytes(data)
    localize_limitations()
    override_path = 'backend/course-capsule-v1/authority/integration-overrides-v1.json'
    override_raw = (ROOT / override_path).read_bytes()
    over = json.loads(override_raw)
    before = copy.deepcopy(over)
    evidence = [{'kind': kind, 'locator': BASE + '/' + name, **fact(BASE + '/' + name), 'verified_date': '2026-09-30'}
                for kind, name in [('d70_portable_native_metadata_replay', 'validation.json'),
                                   ('d70_metadata_replay_bundle', 'build/BUILD_RECEIPT.json')]]
    for capability in ['build', 'deterministic_replay']:
        existing = over['native_capabilities']['D70'][capability]
        assert existing['status'] == 'available_unverified', 'Do not silently replace a new full-native result'
        existing['evidence'] = [r for r in existing['evidence'] if r['kind'] not in {row['kind'] for row in evidence}] + evidence
    resources = over['educator_evidence']['D70']['resources']
    resources[:] = [row for row in resources if not row['id'].startswith('D70:native-metadata-replay-')]
    for locale, name in [('id', 'index.html'), ('en', 'index.en.html')]:
        resources.append({'id': 'D70:native-metadata-replay-' + locale,
            'title': 'D70 · Reproduce native metadata' if locale == 'en' else 'D70 · Bangun ulang metadata native',
            'resource_type': 'teacher-guide', 'status': 'verified',
            'url': 'https://kokunoyumeto.github.io/program-matematika-indonesia/backend/d70-replay/' + name,
            'scope': 'Two builders, 13 byte-identical metadata artifacts; no producer tree. Not whole-native/PDF replay or semantic canon review.' if locale == 'en' else 'Dua pembangun, 13 berkas metadata dengan byte yang sama; tanpa direktori pembuat buku. Bukan replay seluruh native/PDF atau audit kanon semantik.',
            **fact(SITE + '/' + name)})
    for key in before:
        left, right = copy.deepcopy(before[key]), copy.deepcopy(over[key])
        if key in ['native_capabilities', 'educator_evidence']:
            left.pop('D70', None)
            right.pop('D70', None)
        assert left == right, 'Unrelated override changed: ' + key
    assert (ROOT / override_path).read_bytes() == override_raw, 'Concurrent override edit'
    save(override_path, over)
    nav_path = 'backend/authority/central-reader-navigation-v1.json'
    nav_raw = (ROOT / nav_path).read_bytes()
    nav = json.loads(nav_raw)
    teacher_path = ROOT / 'docs/backend/d70/D70-pengajar.html'
    teacher_raw = teacher_path.read_bytes()
    teacher = teacher_raw.decode('utf-8')
    teacher = re.sub(r'<!-- D70-METADATA-REPLAY:START -->.*?<!-- D70-METADATA-REPLAY:END -->', '', teacher, flags=re.S)
    replay_links = ('<!-- D70-METADATA-REPLAY:START -->'
        '<section id="d70-metadata-replay"><h2>Bangun ulang metadata sumber</h2>'
        '<p>Dua pembangun metadata dapat dijalankan tanpa direktori pembuat buku. '
        'Paket memuat 26 input tambahan dan menghasilkan kembali 13 berkas metadata. '
        'Ini bukan produksi ulang seluruh pembaca Li atau keempat PDF.</p><p>'
        '<a lang="id" hreflang="id" href="../d70-replay/index.html">Petunjuk replay metadata — Bahasa Indonesia</a> · '
        '<a lang="en" hreflang="en" href="../d70-replay/index.en.html">Metadata replay instructions — English</a>'
        '</p></section><!-- D70-METADATA-REPLAY:END -->')
    assert teacher.count('</main>') == 1, 'Expected exact central D70 teacher surface'
    teacher = teacher.replace('</main>', replay_links + '</main>')
    assert teacher_path.read_bytes() == teacher_raw, 'Concurrent D70 teacher edit'
    teacher_path.write_text(teacher, encoding='utf-8', newline='\n')
    teacher_surfaces = [row for row in nav['course_surfaces'] if row['root'] == 'docs/backend/d70']
    assert len(teacher_surfaces) == 1
    teacher_documents = [row for row in teacher_surfaces[0]['documents'] if row['path'] == 'D70-pengajar.html']
    assert len(teacher_documents) == 1
    teacher_document = teacher_documents[0]
    teacher_document['related_course_surface_paths'] = list(dict.fromkeys(
        teacher_document.get('related_course_surface_paths', []) + [SITE + '/index.html', SITE + '/index.en.html', SITE + '/limitations-review.id.html']))
    learner_document = next(row for row in teacher_surfaces[0]['documents'] if row['path'] == 'D70.html')
    learner_document['related_course_surface_paths'] = list(dict.fromkeys(
        learner_document.get('related_course_surface_paths', []) + [SITE + '/limitations-review.id.html']))
    surface = {'root': SITE, 'locale': 'id', 'state': 'current-shared-corpus-capability', 'documents': []}
    for locale, name, opposite in [('id', 'index.html', 'index.en.html'), ('en', 'index.en.html', 'index.html')]:
        surface['documents'].append({'path': name, 'locale': locale, 'course_ids': ['D70'], 'contents_paths': [opposite],
                                     'related_course_surface_paths': ['docs/backend/d70/D70-pengajar.html']})
    surface['documents'].append({'path': 'limitations-review.id.html', 'locale': 'id', 'course_ids': ['D70'], 'contents_paths': ['index.html'],
                                 'related_course_surface_paths': ['docs/backend/d70/D70-pengajar.html', 'docs/backend/d70/D70.html']})
    nav['course_surfaces'] = [row for row in nav['course_surfaces'] if row['root'] != SITE] + [surface]
    nav['summary']['course_surface_roots'] = len(nav['course_surfaces'])
    nav['summary']['course_surface_html_documents'] = sum(len(row['documents']) for row in nav['course_surfaces'])
    nav['summary']['classified_html_documents'] = sum(nav['summary'][key] for key in ['reader_html_documents', 'gateway_html_documents', 'course_surface_html_documents', 'generic_html_documents'])
    nav['summary']['navigation_overlay_documents'] = sum(nav['summary'][key] for key in ['reader_html_documents', 'gateway_html_documents', 'course_surface_html_documents']) + sum(bool(row['navigation_required']) for row in nav['generic_surfaces'])
    assert (ROOT / nav_path).read_bytes() == nav_raw, 'Concurrent navigation edit'
    save(nav_path, nav)
    scope_path = 'backend/course-capsule-v1/authority/current-package-scope-v1.json'
    scope_raw = (ROOT / scope_path).read_bytes()
    scope = json.loads(scope_raw)
    needed = ['scripts/' + name for name in ['audit-d70-native-source-closure-v1.py', 'test-d70-native-source-closure-v1.py',
              'replay-d70-native-metadata-v1.py', 'build-d70-native-replay-v1.py', 'test-d70-native-replay-v1.py',
              'test-d70-native-replay-package-v1.py', 'test-d70-native-replay-localization-v1.py', 'test-d70-native-replay-browser-v1.cjs', 'admit-d70-native-replay-v1.py']]
    needed.append(BASE + '/browser-checks.json')
    needed.append('scripts/d70-native-replay-evidence-v1.mjs')
    needed += [BASE + '/metadata-localization-choices.id.json', SITE + '/metadata-localization-choices.id.json', SITE + '/limitations-review.id.html']
    needed += [BASE + '/' + name for name in ['validation.json', 'build/BUILD_RECEIPT.json', 'build/D70_NATIVE_METADATA_REPLAY_V1.zip']]
    needed += [SITE + '/' + name for name in ['index.html', 'index.en.html', 'validation.json', 'BUILD_RECEIPT.json', 'D70_NATIVE_METADATA_REPLAY_V1.zip']]
    scope['exact_files'] = list(dict.fromkeys(needed + scope['exact_files']))
    assert (ROOT / scope_path).read_bytes() == scope_raw, 'Concurrent package scope edit'
    save(scope_path, scope)
    print(json.dumps({'state': 'locally_admitted_pending_publication', 'role': 'D70', 'metadata_artifacts': 13,
                      'two_packaged_source_replays': True, 'other_role_overrides_unchanged': True,
                      'whole_native_parity_proven': False}))


if __name__ == '__main__':
    main()
