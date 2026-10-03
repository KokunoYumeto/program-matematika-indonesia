"""Preserve derived format pairs as versions of the exact native Zenodo concepts.

Old records and assets remain public and untouched. Only the four matching new
format files enter this revision; the descriptions link the complete native edition.
"""
import argparse
import copy
import hashlib
import html
import json
import re
from urllib.parse import quote, urlparse
import requests
from lxml import html as html_parser

from finalize import OUT, read, identity
from zenodo_inspect import client_for
from publish_github import public_identity

API = 'https://zenodo.org/api'
HEADERS = {'Accept': 'application/vnd.inveniordm.v1+json'}
RECORDS = {'id': (22053905, '22052052'), 'en': (22210474, '22210473')}


def request(client, method, url, expected=(200,), **kw):
    assert urlparse(url).netloc == 'zenodo.org'
    r = client.request(method, url, timeout=(20,90), **kw)
    if r.status_code not in expected:
        # Never expose request headers, response metadata, credentials or names.
        raise RuntimeError(f'Zenodo {method} {urlparse(url).path}: HTTP {r.status_code}')
    return r.json() if r.content else {}


def public(record):
    return request(requests.Session(), 'GET', f'{API}/records/{record}')


def verify_old(record, github):
    data = public(record)
    assert data['metadata']['access_right'] == 'open'
    facts = {r['file']: r for r in github['anonymous_readback']}
    verified = []
    for f in data['files']:
        item = public_identity(f['links']['self'])
        assert f['size'] == item['bytes'] == facts[f['key']]['bytes']
        assert item['sha256'] == facts[f['key']]['sha256']
        verified.append({'file': f['key'], 'url': f['links']['self'], **item})
    return verified


def main(lang, publish):
    record, concept = RECORDS[lang]
    final = read(OUT / 'FINAL_FORMAT_VALIDATION.json')
    edition = final['editions'][lang]
    files = edition['files_in_reading_order']
    github = read(OUT / lang / 'GITHUB_FORMAT_PUBLICATION.json')
    assert github['status'] == 'published_and_anonymously_verified'
    for f in files:
        assert identity(OUT / lang / f['file']) == f
    session, predecessor = client_for(record)
    assert str(predecessor['conceptrecid']) == concept
    state_path = OUT / lang / 'ZENODO_FORMAT_PUBLICATION.json'
    state = read(state_path) if state_path.exists() else {
        'schema': 'b80-zenodo-format-preservation/1', 'status': 'preflight',
        'predecessor': record, 'concept': concept, 'new_files': files,
        'original_records_unchanged': True,
        'revision_scope': 'Only paired derived formats; native editions stay in linked original records.',
        'credentials_recorded': False}
    def save():
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if 'original_readback_before' not in state:
        state['original_readback_before'] = verify_old(record, github); save()
    latest = request(requests.Session(), 'GET', f'{API}/records/{concept}/versions/latest')
    assert int(latest['id']) in (record, state.get('draft_id')), 'Another latest version exists'
    if not publish:
        print(json.dumps({'language': lang, 'status': 'preflight_pass', 'original_files_verified': len(state['original_readback_before'])})); return
    if 'draft_id' not in state:
        draft_link = predecessor['links']['latest_draft']
        assert int(draft_link.rstrip('/').split('/')[-1]) == record, 'Unowned draft exists; do not overwrite'
        assert not state.get('reservation_attempted'), 'Recover unknown reservation before retrying'
        state['reservation_attempted'] = True; save()
        draft = request(session, 'POST', f'{API}/records/{record}/versions', expected=(201,), json={}, headers=HEADERS)
        assert draft['is_draft'] and str(draft['parent']['id']) == concept
        state['draft_id'] = int(draft['id']); state['status'] = 'reserved'; save()
    draft_id = state['draft_id']
    if int(latest['id']) != draft_id:
        draft_url = f'{API}/records/{draft_id}/draft'
        draft = request(session, 'GET', draft_url, headers=HEADERS)
        assert str(draft['parent']['id']) == concept
        native = copy.deepcopy(predecessor['metadata'])
        keep = ('title','publication_date','description','access_right','creators','contributors','keywords',
                'version','language','license','imprint_publisher','upload_type','publication_type','related_identifiers')
        metadata = {k: v for k, v in native.items() if k in keep}
        private_name = __import__('pathlib').Path.home().name
        generic = 'Kontributor proyek O002' if lang == 'id' else 'O002 project contributors'
        for role in ('creators', 'contributors'):
            for person in metadata.get(role, []):
                if private_name.casefold() in person.get('name', '').casefold():
                    person['name'] = generic
        original_description = re.sub(r'atas arahan '+re.escape(private_name)+r'\b', 'atas instruksi pengguna',
                                      metadata.get('description', ''), flags=re.I)
        base = f'https://zenodo.org/records/{draft_id}/files/'
        label = (['Baca PDF', 'LaTeX kumulatif lengkap', 'Sumber lengkap dan skrip reproduksi', 'EPUB yang diperbaiki']
                 if lang == 'id' else ['Read PDF', 'Complete cumulative LaTeX', 'Full source and rebuild scripts', 'Repaired EPUB'])
        links = '<ol>'+''.join('<li><a href="'+base+quote(f['file'])+'?download=1">'+label[i]+'</a></li>' for i,f in enumerate(files))+'</ol>'
        if lang == 'id':
            note = ('<p>Edisi format 3 Oktober 2026: 14 unit, 75 latihan, PDF 135 halaman. '
                    'LaTeX kumulatif mereproduksi PDF turunan ini, bukan tata letak PDF historis. '
                    'EPUB yang diperbaiki dan sumber lengkap disertakan. PDF dan EPUB direproduksi byte-identik '
                    'dari paket sumber; EPUBCheck 5.4.0 tidak menemukan kesalahan atau peringatan. '
                    '272 rumus dan 195 blok kode diperiksa terhadap EPUB sumber. '
                    'Perbaikan dan ekspor format: OpenAI Codex - GPT-6 Astra, upaya Ultra. '
                    'Ini bukan penerjemahan atau peninjauan matematika baru. Eksperimen Python/Sage tidak dijalankan ulang. '
                    'Teks CC BY-SA 4.0; kode MIT; lisensi komponen tetap berlaku.</p>'
                    f'<p><a href="https://zenodo.org/records/{record}">Edisi asli, sumber Quarto dan paket luring</a> '
                    'tetap tersedia tanpa perubahan. Sumber utama tetap Quarto. Versi ini menyimpan empat berkas '
                    'format yang saling cocok; semua unduhan historis tetap terbuka pada rekaman asli.</p>')
            metadata['title'] = 'Komputasi Matematis dan Eksperimen yang Dapat Direproduksi — Bahasa Indonesia — edisi format 2026.10.03'
            metadata['keywords'] = ['Bahasa Indonesia','komputasi matematis','eksperimen yang dapat direproduksi','Python','SageMath','SciPy','sumber pendidikan terbuka']
        else:
            note = ('<p>Format edition 3 October 2026: 14 units, 75 exercises, 133-page PDF. '
                    'Cumulative LaTeX reproduces this derived PDF, not the historical PDF layout. '
                    'Repaired EPUB and complete editable source are included. PDF and EPUB rebuild byte-identically '
                    'from the source package; EPUBCheck 5.4.0 reports no errors or warnings. '
                    '272 formulas and 195 code blocks were checked against the source EPUB. '
                    'Format repair and export: OpenAI Codex - GPT-6 Astra, Ultra effort. '
                    'This is not a new translation or mathematical review. Python/Sage experiments were not rerun. '
                    'Text remains CC BY-SA 4.0; code MIT; component licences remain applicable.</p>'
                    f'<p><a href="https://zenodo.org/records/{record}">The native edition, Quarto source and offline package</a> '
                    'remain unchanged and publicly available. Quarto remains the native master. This revision '
                    'contains four matching format files; all historical downloads remain open on the original record.</p>')
            metadata['title'] = 'Mathematical Computing and Reproducible Experiments — English — format edition 2026.10.03'
        metadata.update(description=links+note+'<hr>'+original_description, version='2026.10.03-formats',
                        publication_date='2026-10-03', access_right='open')
        assert private_name.casefold() not in json.dumps(metadata).casefold()
        request(session, 'PUT', f'{API}/deposit/depositions/{draft_id}', json={'metadata':metadata})
        legacy = request(session, 'GET', f'{API}/deposit/depositions/{draft_id}')
        remote = {f['filename']: f for f in legacy['files']}
        assert set(remote) <= {f['file'] for f in files}, 'Unexpected draft file; do not remove or overwrite'
        for f in files:
            path = OUT/lang/f['file']
            md5 = hashlib.md5(path.read_bytes()).hexdigest()
            if f['file'] not in remote:
                state['status'] = 'uploading'; state['next_file'] = f['file']; save()
                with path.open('rb') as data:
                    request(session, 'PUT', legacy['links']['bucket']+'/'+quote(f['file']), expected=(200,201), data=data)
            legacy = request(session, 'GET', f'{API}/deposit/depositions/{draft_id}')
            remote = {f['filename']: f for f in legacy['files']}
            actual = remote[f['file']]
            assert actual['filesize'] == f['bytes'] and actual['checksum'].removeprefix('md5:') == md5
        assert set(remote) == {f['file'] for f in files}
        rdm = request(session, 'GET', draft_url, headers=HEADERS)
        payload = {k:rdm[k] for k in ('metadata','access','custom_fields') if k in rdm}
        payload['files'] = {'enabled':True, 'default_preview':files[0]['file'], 'order':[f['file'] for f in files]}
        updated = request(session, 'PUT', draft_url, json=payload, headers=HEADERS)
        assert updated['files']['default_preview'] == files[0]['file']
        assert updated['access']['record'] == updated['access']['files'] == 'public'
        state['status'] = 'publish_attempted'; save()
        request(session, 'POST', f'{API}/deposit/depositions/{draft_id}/actions/publish', expected=(200,201,202))
    released = public(draft_id)
    assert str(released['conceptrecid']) == concept and released['metadata']['access_right'] == 'open'
    remote = {f['key']: f for f in released['files']}
    assert set(remote) == {f['file'] for f in files}
    state['status'] = 'published_pending_anonymous_readback'; state['doi'] = released['doi']; save()
    state['public_readback'] = []
    for f in files:
        actual = public_identity(remote[f['file']]['links']['self'])
        assert actual == {k:f[k] for k in ('bytes','sha256')}
        state['public_readback'].append({'file':f['file'], 'url':remote[f['file']]['links']['self'], **actual}); save()
    rdm_public = request(requests.Session(), 'GET', f'{API}/records/{draft_id}', headers=HEADERS)
    assert rdm_public['files']['default_preview'] == files[0]['file']
    # Zenodo normalizes alphabetical order to []; verify the actual reader-facing table.
    page = requests.get(f'https://zenodo.org/records/{draft_id}', timeout=(20,45))
    assert page.status_code == 200
    document = html_parser.fromstring(page.content)
    rendered_order = [a.text_content().strip() for a in document.xpath('//table//a[not(@role)]')
                      if a.text_content().strip() in remote]
    assert rendered_order == [f['file'] for f in files]
    assert document.xpath('string(//*[@id="preview-file-title"])').strip() == files[0]['file']
    state['api_file_order'] = rdm_public['files']['order']
    state['rendered_file_order_verified'] = rendered_order
    state['preview'] = files[0]['file']; state['file_order'] = [f['file'] for f in files]
    state['original_readback_after'] = verify_old(record, github)
    assert state['original_readback_after'] == state['original_readback_before']
    state['status'] = 'published_and_anonymously_verified'; save()
    print(json.dumps({'language':lang,'status':state['status'],'doi':state['doi'],'files':4,
                      'original_files_preserved':len(state['original_readback_after'])}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--language',choices=['id','en'],required=True)
    parser.add_argument('--publish',action='store_true'); args=parser.parse_args()
    main(args.language,args.publish)
