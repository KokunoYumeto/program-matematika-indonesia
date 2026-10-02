"""Verify one reported reader conversion defect without changing the producer."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import time
import requests

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/KokunoYumeto/methods-of-algebra-volume-2-en/'
HTML_COMMIT = '8524fbc9dee45c737a5a02bb87cc8773470c5bf6'
SOURCE_COMMIT = '674ef26c04dba544e80a95a3f320a9961649407c'
PINS = {
    'html': (BASE + HTML_COMMIT + '/index.html', 4494800,
             'fbc3f62e83215690adb4f4909f7df05e6cc1472e5c9d7558b04611a427543a16'),
    'tex': (BASE + SOURCE_COMMIT + '/source/en/chapter2-unit-023.tex', 24152,
            '65ce863946f2f3f4fa33f4aa088f59e6aa82ed8403e93f8939e1c269e6863a5d'),
    'pdf': (BASE + SOURCE_COMMIT + '/output/pdf/methods-of-algebra-volume-2-independent-english-edition.pdf', 3894743,
            '8193d44ef52c9c39807e769ad04507130f163481f82aa9cfaa0a1a3022ef7aa5'),
}

def main():
    session = requests.Session()
    session.trust_env = False
    session.auth = None
    session.headers.clear()
    data, records, last = {}, {}, 0
    for name, (url, size, digest) in PINS.items():
        time.sleep(max(0, 2.1 - (time.monotonic() - last)))
        last = time.monotonic()
        with session.get(url, timeout=(20, 60), allow_redirects=False) as response:
            assert response.status_code == 200, (name, response.status_code)
            assert 'Authorization' not in response.request.headers
            raw = response.content
        assert len(raw) == size and sha256(raw).hexdigest() == digest, name
        data[name] = raw
        records[name] = {'url': url, 'bytes': size, 'sha256': digest}
    figure = re.search(rb'<figure\b[^>]*data-diagram-id="chapter2-unit-023-d015"[^>]*>.*?</figure>', data['html'], re.S)
    assert figure, 'Reported figure is absent'
    assert b'S_0' in figure[0] and b'ker' in figure[0] and b'X_1' not in figure[0]
    fragment = data['tex'][19679:20164]
    assert sha256(fragment).hexdigest() == 'e4030119cdfd2798eba5967c65a2451c59975a514c0fb74d26aafddf138614d9'
    assert b'prop:5-lemma' in fragment
    for n in range(1, 6):
        for prefix in ('X_', 'Y_', 'f_'):
            assert (prefix + str(n)).encode() in fragment
    report = {
        'schema': 'd80-reader-diagram-notice-evidence/1', 'state': 'pass',
        'checked_at': datetime.now(timezone.utc).isoformat(), 'anonymous': True,
        'public_sources': records,
        'html_figure_id': 'chapter2-unit-023-d015',
        'html_figure': figure[0].decode(),
        'tex_fragment_bytes': [19679, 20164],
        'tex_fragment_sha256': sha256(fragment).hexdigest(),
        'tex_fragment': fragment.decode(),
        'pdf_physical_page': 119, 'pdf_printed_page': 109,
        'visual_check': 'Integrator inspected the supplied rendering of PDF physical page119: Proposition2.3.4 shows X1..X5 over Y1..Y5 with f1..f5; preceding Snake Lemma diagrams appear above it.',
        'finding': 'The linked HTML figure describes a preceding Snake Lemma diagram rather than the Five Lemma diagram in the pinned TeX/PDF.',
        'scope': 'One conversion correspondence defect; no whole-book or full-proof certification.',
        'producer_files_changed': False, 'producer_fix_complete': False,
        'provenance': {'model': 'gpt-6-astra', 'effort': 'ultra', 'human_review_claimed': False},
    }
    target = ROOT / 'backend/cross-programme-v1/d80-diagram-notice-evidence-v1.json'
    assert not target.exists(), 'Existing evidence must be inspected, not overwritten'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'state': 'pass', 'public_sources_verified': 3, 'producer_files_changed': False}))

if __name__ == '__main__':
    main()
