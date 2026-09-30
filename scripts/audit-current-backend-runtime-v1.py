"""Read-only static asset closure and privacy checks for an exact package plan."""
import argparse
from collections import defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TEXT = {'.py', '.js', '.mjs', '.css', '.html', '.json', '.jsonl', '.txt', '.md', '.csv', '.tsv'}


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets, self.links = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {'script', 'img', 'source'} and a.get('src'):
            self.assets.append(a['src'])
        if tag == 'link' and a.get('rel') in {'stylesheet', 'preload', 'modulepreload'} and a.get('href'):
            self.assets.append(a['href'])
        if tag == 'a' and a.get('href'):
            self.links.append(a['href'])


def destination(name, url):
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    path = unquote(parts.path)
    if path.startswith('/'):
        # GitHub project-root URLs may include this prefix.
        path = 'docs/' + path.removeprefix('/program-matematika-indonesia/').lstrip('/')
    else:
        path = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
    if parts.path.endswith('/'):
        path = path.rstrip('/') + '/index.html'
    return path


def audit(root, plan):
    members = {f['path'] for f in plan['files']}
    missing_assets, external_assets, outside_links = defaultdict(set), defaultdict(set), defaultdict(set)
    privacy = []
    patterns = {
        'absolute-user-path': re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+[\\/]+', re.I),
        'github-credential-shaped-value': re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
        'openai-credential-shaped-value': re.compile(rb'sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}'),
        'private-key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    }
    checked_html = 0
    for name in sorted(members):
        path = root / name
        if path.suffix not in TEXT:
            continue
        seen = set()
        tail = b''
        with path.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                value = tail + block
                for label, pattern in patterns.items():
                    if label not in seen and pattern.search(value):
                        privacy.append({'path': name, 'kind': label})
                        seen.add(label)
                tail = value[-256:]
        if not name.startswith('docs/') or path.suffix not in {'.html', '.css', '.js', '.mjs'}:
            continue
        text = path.read_text(encoding='utf-8-sig')
        links = []
        if path.suffix == '.html':
            page = Assets()
            page.feed(text)
            assets, links = page.assets, page.links
            checked_html += 1
        elif path.suffix == '.css':
            assets = re.findall(r'''url\(["']?([^\s"')]+)["']?\)''', text)
        else:
            assets = re.findall(r'''(?:from\s*|import\s*\(\s*|fetch\(\s*)["'](\.[^"']+)["']''', text)
        for url in assets:
            target = destination(name, url)
            if target and target not in members:
                missing_assets[target].add(name)
            elif urlsplit(url).scheme in {'http', 'https'}:
                external_assets[url].add(name)
        for url in links:
            target = destination(name, url)
            if target and target not in members:
                outside_links[target].add(name)
    return {'schema': 'current-backend-runtime-audit/1',
            'html_pages_checked': checked_html,
            'missing_static_assets': [{'path': p, 'referenced_by': sorted(v), 'exists_in_checkout': (root/p).is_file()} for p,v in sorted(missing_assets.items())],
            'external_runtime_assets': [{'url': p, 'referenced_by': sorted(v)} for p,v in sorted(external_assets.items())],
            'outside_package_navigation': [{'path': p, 'referenced_by': sorted(v)} for p,v in sorted(outside_links.items())],
            'privacy_findings': privacy,
            'scope': 'Literal HTML/CSS/JavaScript dependency checks and text-file privacy patterns; dynamic fetch branches and nested binary archives are not proved by this static scan.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(ROOT, json.loads(args.plan.read_bytes()))
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: len(report[key]) for key in ['missing_static_assets','external_runtime_assets','outside_package_navigation','privacy_findings']}))
