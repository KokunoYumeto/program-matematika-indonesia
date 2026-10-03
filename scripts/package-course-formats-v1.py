"""Deterministic software-only archive; never include course intake or QA output."""
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ['LICENSE', 'scripts/package-course-formats-v1.py', *[
    'scripts/course-formats-v1/' + name for name in
    ['course_formats.py', 'test_course_formats.py', 'check_reader.mjs', 'README.txt', 'README.id.txt']]]


def package():
    payloads = {name: (ROOT / name).read_bytes() for name in FILES}
    manifest = {'schema': 'course-format-tools-package/1', 'model': 'gpt-6-astra', 'effort': 'ultra',
                'private_course_data': False, 'course_conversion_performed': False,
                'files': [{'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
                          for name, raw in payloads.items()]}
    payloads['MANIFEST.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, raw in payloads.items():
            info = zipfile.ZipInfo(name, (2026, 10, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, raw)
    raw = stream.getvalue()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert set(archive.namelist()) == set(payloads)
        for name, expected in payloads.items():
            assert archive.read(name) == expected
    target = ROOT / 'docs/downloads/course-format-tools-v1.zip'
    if '--check' in sys.argv:
        assert target.read_bytes() == raw, 'Tool archive differs from exact source'
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    print(json.dumps({'state': 'pass', 'path': target.relative_to(ROOT).as_posix(),
                      'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'members': len(payloads)}))


if __name__ == '__main__':
    package()
