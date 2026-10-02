"""Bind one real core-to-advanced reading route; no source-owner writes."""
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import time
import requests

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
LOG = WORKSPACE / 'outputs/01a01ec1-e685-70d0-b022-211396334723/curriculum_logbook'
OUT = ROOT / 'backend/cross-programme-v1/d80-prerequisite-route-v1.json'
PROVIDER = 'https://kokunoyumeto.github.io/methods-of-algebra-volume-2-en/'
CONSUMER = 'https://kokunoyumeto.github.io/open-mathematics-courses/courses/derived-categories-and-sheaf-operations/'
PINS = [
    ('chapter2-unit-021', 'definition-of-an-abelian-category', 8424,
     '86b85ff540c9859bb8172dd218a65a945cde870880fdd734928a342d5c2870b6',
     'Definition of an Abelian Category', 'Definisi kategori abelian'),
    ('chapter2-unit-023', 'some-diagram-lemmas', 24152,
     '65ce863946f2f3f4fa33f4aa088f59e6aa82ed8403e93f8939e1c269e6863a5d',
     'Some Diagram Lemmas', 'Beberapa lema diagram'),
    ('chapter3-unit-037', 'complexes-on-an-abelian-category', 13395,
     '206451f9e042699e30881d1f8a0085b95e626166dd56fb638286effec90ab759',
     'Complexes on an Abelian Category', 'Kompleks pada kategori abelian'),
]


def identity(raw):
    return {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()}


class Anchors(HTMLParser):
    def __init__(self, raw):
        super().__init__()
        self.ids = set()
        self.feed(raw.decode('utf8'))

    def handle_starttag(self, tag, attrs):
        value = dict(attrs).get('id')
        if value:
            self.ids.add(value)


def main():
    assert not OUT.exists(), 'Existing admission must be inspected, not overwritten'
    r42path = LOG / 'CROSS_PROGRAMME_R42_DEPENDENCY_INCREMENT_20261002.json'
    r42raw = r42path.read_bytes()
    assert identity(r42raw) == {'bytes': 60560, 'sha256': '16402aa02a6713d3bb00ffc96ce4868ae93db4bb18693983b0019d959afe3d9c'}
    route = json.loads(r42raw)['new_core_dependency']
    r43path = LOG / 'CROSS_PROGRAMME_R43_DEPENDENCY_DELTA_20261002.json'
    r43raw = r43path.read_bytes()
    assert identity(r43raw) == {'bytes': 114012, 'sha256': '40c5b39db6d1426326a1650aaa91f92c92493d2161ba80700ed2c398ec411223'}
    r43 = json.loads(r43raw)
    assert r43['existing_core_integration']['d80_consumer_source_unchanged']
    assert route['distinct_course_level_relationships'] == 1
    session = requests.Session()
    session.trust_env = False
    last = 0

    def fetch(url, expected):
        nonlocal last
        time.sleep(max(0, 2.1 - (time.monotonic() - last)))
        last = time.monotonic()
        response = session.get(url, timeout=(20, 45), allow_redirects=False)
        assert response.status_code == 200, f'Public HTTP {response.status_code}'
        raw = response.content
        assert identity(raw) == expected, 'Public source revision changed: ' + url
        return raw

    provider_raw = fetch(PROVIDER, {k: route['source'][k] for k in ('bytes', 'sha256')})
    anchors = Anchors(provider_raw).ids
    readings = []
    for unit, heading, size, digest, en, ind in PINS:
        anchor = unit + '--' + heading
        assert anchor in anchors, 'Missing live proof-section anchor'
        source_url = 'https://raw.githubusercontent.com/KokunoYumeto/methods-of-algebra-volume-2-en/main/source/en/' + unit + '.tex'
        source_raw = fetch(source_url, {'bytes': size, 'sha256': digest})
        local = WORKSPACE / '04_mirrors/en/methods-of-algebra-volume-2-en/source/en' / (unit + '.tex')
        assert local.read_bytes() == source_raw, 'Locally inspected proof differs from public source'
        readings.append({'id': unit, 'anchor': anchor, 'url': PROVIDER + '#' + anchor,
                         'title': {'en': en, 'id': ind}, 'content_language': 'en',
                         'editable_source': {'url': source_url, **identity(source_raw)},
                         'rights': 'CC-BY-4.0', 'author': 'Wen-Wei Li'})
    source_url = CONSUMER + 'src/complexes-cones-and-localization.md'
    consumer_raw = fetch(source_url, {'bytes': 31676, 'sha256': route['direct_consumer']['source_sha256']})
    local_consumer = WORKSPACE / 'kerodon_to_stacks_extension_20260906/reader/course_inputs/AFTER-R36-PUBLIC-20261002/6af59bcc/upstream/courses/derived-categories-and-sheaf-operations/src/complexes-cones-and-localization.md'
    assert local_consumer.read_bytes() == consumer_raw
    text = consumer_raw.decode('utf8')
    for phrase in ('Methods of Algebra, Volume 2', '**Lemma 1.2 (cohomology of a short exact sequence).**',
                   '**Lemma 2.4 (representable exactness and cone uniqueness).**', 'Five Lemma'):
        assert phrase in text, 'Consumer use locus changed'
    reader_url = CONSUMER + 'complexes-cones-and-localization.html'
    reader_raw = fetch(reader_url, {'bytes': 57574, 'sha256': 'd62cbe582b8510f9a4f9653813ff681a529c4f4986cce648355a5167f0341c7c'})
    result = {
        'schema': 'd80-source-bound-lesson-route/1', 'id': route['id'],
        'provider_course': 'D80', 'consumer_course': route['consumer_course'],
        'consumer_lesson': 'complexes-cones-and-localization',
        'relation': 'writer_reported_proof_prerequisite',
        'admission': 'verified_public_reading_route',
        'independent_mathematical_admission': False, 'whole_prerequisite_closure': False,
        'source_report_repetitions': 32, 'distinct_course_relationships': 1,
        'provider': {'url': PROVIDER, **identity(provider_raw), 'content_language': 'en',
                     'author': 'Wen-Wei Li', 'work': 'Methods of Algebra, Volume 2',
                     'edition': 'English translation', 'rights': 'CC-BY-4.0'},
        'readings': readings,
        'consumer': {'url': reader_url, **identity(reader_raw), 'content_language': 'en',
                     'title': {'en': 'Complexes, cones and localization', 'id': 'Kompleks, kerucut, dan lokalisasi'},
                     'editable_source': {'url': source_url, **identity(consumer_raw)},
                     'rights': 'GFDL-1.2-or-later; original independent passages retain CC0',
                     'course_complete': False},
        'use_loci': [
            {'provider_labels': ['prop:Abel-cat-pull-push', 'prop:Abel-cat-exact-aux', 'prop:snake-lemma', 'prop:long-exact-sequence-ses'],
             'consumer_locus': 'Lemma 1.2, entire proof',
             'label': {'id': 'Lema 1.2, seluruh pembuktian', 'en': 'Lemma 1.2, entire proof'},
             'conditions': {'id': 'Kategori abelian sebarang; barisan eksak pendek kompleks kokrantai pada setiap derajat; pengangkatan melalui epimorfisme, bukan melalui elemen.', 'en': 'Arbitrary abelian category; degreewise short exact sequence of cochain complexes; epimorphic rather than elementwise lifts.'},
             'comparison': {'id': 'Pelajaran lanjutan menggunakan konstruksi dari kokernel d^(n-2) ke kernel d^n dengan peta vertikal d^(n-1), sesuai indeks yang telah dikoreksi dalam sumber.', 'en': 'The consumer reproduces the cokernel d^(n-2) to kernel d^n construction with vertical d^(n-1), matching the corrected provider indices.'}},
            {'provider_labels': ['prop:5-lemma'], 'consumer_locus': 'Lemma 2.4, final paragraph',
             'label': {'id': 'Lema 2.4, paragraf terakhir', 'en': 'Lemma 2.4, final paragraph'},
             'conditions': {'id': 'Barisan eksak dengan lima suku berupa grup abelian setelah penerapan funktor representabel; keempat peta vertikal di sekitar peta tengah merupakan isomorfisme.', 'en': 'Exact five-term sequences of abelian groups after applying representable functors; four surrounding vertical maps are isomorphisms.'},
             'comparison': {'id': 'Hipotesis ini memenuhi syarat epimorfisme dan monomorfisme di ujung serta syarat isomorfisme di bagian dalam pada lema lima dalam sumber.', 'en': 'These hypotheses imply the provider Five Lemma endpoint epi/mono conditions and the inner isomorphism conditions.'}}],
        'scope': {'id': 'Bacaan ini menyediakan kategori abelian, pengangkatan epimorfik, lema ular dan lema lima, serta barisan kohomologi panjang. Pembuktian kerucut dan lokalisasi dikerjakan dalam pelajaran lanjutan; bukan konsekuensi dari tautan ini.',
                  'en': 'These readings supply abelian categories, epimorphic lifts, the Snake and Five Lemmas, and the long exact cohomology sequence. Cone and localization proofs belong to the advanced lesson; this link does not certify them.'},
        'verification': {'public_byte_identity': True, 'public_section_anchors': True,
                         'consumer_use_loci_present': True, 'producer_files_changed': False,
                         'mathematical_review': {'id': 'Perbandingan sumber terbatas oleh AI pengintegrasi; bukan klaim pemeriksaan lengkap semua prasyarat atau peninjauan independen seluruh mata kuliah.', 'en': 'Bounded source comparison by the integrating AI; no complete prerequisite-closure or independent-course-review claim.'}},
        'upstream_evidence': [{'kind': 'manager_r42', **identity(r42raw)}, {'kind': 'manager_r43', **identity(r43raw)}],
        'change_policy': {'id': 'Perubahan revisi sumber atau pelajaran pengguna harus diperiksa terhadap penggunaan yang tepat; mengganti URL tidak memvalidasi ulang suatu argumen.', 'en': 'Provider or consumer revision changes require use-specific reconciliation; replacing a URL does not revalidate an argument.'},
        'provenance': {'model': 'gpt-6-astra', 'effort': 'ultra', 'human_review_claimed': False,
                       'scope': {'id': 'Integrasi jalur bacaan yang terikat pada sumber dan perbandingan penggunaan terbatas; kredit penulis dan penerjemah sumber dipertahankan.', 'en': 'Source-bound reading-route integration and bounded use comparison; source authorship and translation credits retained.'}},
        'checked_at': datetime.now(timezone.utc).isoformat(),
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'state': 'admitted_reading_route', 'readings': 3, 'distinct_relationships': 1,
                      'whole_prerequisite_closure': False, **identity(OUT.read_bytes())}))


if __name__ == '__main__':
    main()
