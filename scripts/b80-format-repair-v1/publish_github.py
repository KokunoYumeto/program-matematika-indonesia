"""Append verified format pairs to exact native releases. Never replace an asset."""
import argparse
import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path

from finalize import ROOT, OUT, read, identity


def gh(*args):
    p = subprocess.run(['gh', *args], capture_output=True, text=True, encoding='utf-8', timeout=120)
    if p.returncode:
        raise RuntimeError('GitHub operation failed: ' + args[0])
    return json.loads(p.stdout) if args[0] == 'api' else p.stdout.strip()


def public_identity(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'B80-format-preservation'}), timeout=90) as r:
        digest = hashlib.sha256(); count = 0
        while data := r.read(1024 * 1024):
            digest.update(data); count += len(data)
    return {'bytes': count, 'sha256': digest.hexdigest()}


def run(lang, publish):
    final = read(OUT / 'FINAL_FORMAT_VALIDATION.json')
    assert final['status'] == 'validated_local_not_publication'
    edition = final['editions'][lang]
    repo = f'KokunoYumeto/mathematical-computing-reproducible-experiments-{lang}'
    tag = 'v2026.08.22.1' if lang == 'id' else 'v2026.08.31.en1'
    prefix = f'repos/{repo}/releases'
    release = gh('api', prefix + '/tags/' + tag)
    assert release['tag_name'] == tag and not release['draft']
    assert gh('api', 'repos/' + repo)['private'] is False
    assert gh('api', prefix + '/latest')['id'] == release['id'], 'Native latest changed; inspect before continuing'
    marker = '<!-- b80-format-pair-20261003 -->'
    state_path = OUT / lang / 'GITHUB_FORMAT_PUBLICATION.json'
    previous = read(state_path) if state_path.exists() else None
    assets = {a['name']: a for a in release['assets']}
    local = {f['file']: f for f in edition['files_in_reading_order']}
    original = previous['original_assets'] if previous else {
        n: {'id': a['id'], 'bytes': a['size'], 'digest': a.get('digest'), 'url': a['browser_download_url']}
        for n, a in assets.items() if n not in local}
    for n, a in original.items():
        assert n in assets and assets[n]['id'] == a['id'] and assets[n]['size'] == a['bytes']
    missing = []
    for n, f in local.items():
        assert identity(OUT / lang / n) == f
        if n in assets:
            assert assets[n]['size'] == f['bytes']
            assert public_identity(assets[n]['browser_download_url']) == {k: f[k] for k in ('bytes', 'sha256')}
        else:
            missing.append(n)
    assert len(assets) + len(missing) <= 100
    base = f'https://github.com/{repo}/releases/download/{tag}/'
    if lang == 'id':
        text = ('## PDF, LaTeX dan EPUB yang dapat direproduksi — 3 Oktober 2026\n\n'
                'Edisi format ini memuat 14 unit dan 75 latihan yang sama. PDF memiliki 135 halaman; '
                'perubahan tata letak bukan penambahan atau pengurangan cakupan. '
                'Quarto tetap sumber asli. Berkas rilis terdahulu di bawah tetap tersedia.\n\n')
        labels = ['Baca PDF edisi format', 'Unduh LaTeX kumulatif lengkap', 'Unduh sumber lengkap dan skrip reproduksi', 'Unduh EPUB yang diperbaiki']
        text += '\n'.join(f'{i}. [{label}]({base}{n})' for i, (n, label) in enumerate(zip(local, labels), 1))
        text += ('\n\nPerbaikan dan ekspor format: OpenAI Codex — GPT-6 Astra, upaya Ultra. '
                 'Teks, rumus, latihan, solusi dan kode dipertahankan; ini bukan penerjemahan atau peninjauan matematika baru. '
                 'PDF dan EPUB direproduksi byte-identik dari paket sumber; EPUBCheck 5.4.0 tidak menemukan kesalahan atau peringatan. '
                 '272 rumus dan 195 blok kode diperiksa terhadap sumber EPUB. Eksperimen Python/Sage tidak dijalankan ulang. '
                 'Teks tetap CC BY-SA 4.0, kode MIT; kredit dan lisensi komponen tetap berlaku. '
                 'LaTeX ini menghasilkan PDF baru di atas, bukan tata letak PDF historis.\n')
    else:
        text = ('## Reproducible PDF, LaTeX and EPUB — 3 October 2026\n\n'
                'This format edition contains the same 14 units and 75 exercises. Its PDF has 133 pages; '
                'repagination is not a change in course coverage. Quarto remains the native source. '
                'All earlier release files below remain available.\n\n')
        labels = ['Read the format-edition PDF', 'Download complete cumulative LaTeX', 'Download full source and rebuild scripts', 'Download repaired EPUB']
        text += '\n'.join(f'{i}. [{label}]({base}{n})' for i, (n, label) in enumerate(zip(local, labels), 1))
        text += ('\n\nFormat repair and export: OpenAI Codex — GPT-6 Astra, Ultra effort. '
                 'Lesson text, formulas, exercises, solutions and code are preserved; this is not a new translation or mathematical review. '
                 'PDF and EPUB reproduce byte-for-byte from the source package; EPUBCheck 5.4.0 reports no errors or warnings. '
                 '272 formulas and 195 code blocks were checked against the source EPUB. Python/Sage experiments were not rerun. '
                 'Text remains CC BY-SA 4.0 and code MIT; component credits and licences remain applicable. '
                 'This LaTeX reproduces the new PDF above, not the historical PDF layout.\n')
    oldbody = release['body'] or ''
    body = re.sub(r'atas arahan ' + re.escape(Path.home().name) + r'\b',
                  'atas instruksi pengguna', oldbody, flags=re.I)
    assert Path.home().name.casefold() not in body.casefold(), 'Unexpected personal attribution requires inspection'
    newbody = body if marker in body else marker + '\n\n' + text + '\n---\n\n' + body
    notes = OUT / lang / 'GITHUB_RELEASE_NOTES.txt'
    notes.write_text(newbody, encoding='utf-8')
    state = {'schema': 'b80-github-format-preservation/1', 'status': 'preflight_pass',
             'release': release['html_url'], 'original_assets': original, 'new_files': list(local.values()),
             'missing': missing, 'anonymous_readback': []}
    def save():
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    save()
    if publish:
        for n in missing:
            gh('release', 'upload', tag, '--repo', repo, str(OUT / lang / n))
        if newbody != oldbody:
            gh('release', 'edit', tag, '--repo', repo, '--notes-file', str(notes))
        current = gh('api', prefix + '/tags/' + tag)
        assets = {a['name']: a for a in current['assets']}
        assert marker in current['body'] and set(assets) == set(original) | set(local)
        state['status'] = 'published_pending_readback'; save()
        for n, a in assets.items():
            checked = public_identity(a['browser_download_url'])
            assert checked['bytes'] == a['size']
            if a.get('digest'):
                assert a['digest'] == 'sha256:' + checked['sha256']
            if n in local:
                assert checked == {k: local[n][k] for k in ('bytes', 'sha256')}
            else:
                assert a['id'] == original[n]['id'] and checked['bytes'] == original[n]['bytes']
                if original[n]['digest']:
                    assert original[n]['digest'] == 'sha256:' + checked['sha256']
            state['anonymous_readback'].append({'file': n, 'url': a['browser_download_url'], **checked}); save()
        state['status'] = 'published_and_anonymously_verified'; save()
    print(json.dumps({'language': lang, 'status': state['status'], 'release': state['release'],
                      'verified_files': len(state['anonymous_readback'])}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', choices=['id', 'en'], required=True)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    run(args.language, args.publish)
