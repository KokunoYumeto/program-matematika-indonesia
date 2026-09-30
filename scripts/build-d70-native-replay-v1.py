"""Package the exact missing D70 metadata inputs, not native book bodies."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

spec = importlib.util.spec_from_file_location('d70_audit', Path(__file__).with_name('audit-d70-native-source-closure-v1.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'D70_METADATA_REPLAY_MANIFEST.json'
STAMP = (1980, 1, 1, 0, 0, 0)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def prepare(report, isolated, scripts):
    audit.require(report['extended_metadata_replay_pass'] is True and report['whole_native_parity_proven'] is False,
                  'Exact scoped replay evidence is required')
    rows, contents = [], {}
    audit.require(len(report['explicit_external_dependencies']) == 26, 'Dependency scope differs')
    for row in report['explicit_external_dependencies']:
        audit.safe_name(row['path'])
        data = (isolated / row['path']).read_bytes()
        audit.require({'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} ==
                      {key: row[key] for key in ['bytes', 'sha256']}, 'Frozen dependency changed')
        name = 'dependencies/' + row['path']
        contents[name] = data
        rows.append({'path': name, **{key: row[key] for key in ['bytes', 'sha256']},
                     'origin': {key: value for key, value in row.items() if key not in ['bytes', 'sha256']}})
    audit.require(sum(row['bytes'] for row in rows) == 4322608, 'Dependency byte count differs')
    for name in ['audit-d70-native-source-closure-v1.py', 'replay-d70-native-metadata-v1.py',
                 'build-d70-native-replay-v1.py', 'test-d70-native-replay-v1.py', 'test-d70-native-replay-package-v1.py']:
        contents['scripts/' + name] = (scripts / name).read_bytes()
        rows.append({'path': 'scripts/' + name, **audit.identity(scripts / name), 'origin': {'method': 'central_replay_source'}})
    command = ('python -B scripts/replay-d70-native-metadata-v1.py --bundle D70_NATIVE_METADATA_REPLAY_V1.zip '
               '--source-archive 05_o013-sumber-backend-1.0.0.zip --work-dir replay-work --output replay-result.json')
    instructions = {
        'PETUNJUK.id.txt': ('D70: pembangunan ulang metadata native\n\n'
            'Ekstrak ZIP ini. Simpan ZIP asli di samping hasil ekstraksi dan unduh arsip sumber native terpisah: '
            'https://zenodo.org/api/records/22160944/files/05_o013-sumber-backend-1.0.0.zip/content\n'
            'Identitas arsip native: 1.295.518 byte; SHA-256 ' + audit.EXPECTED_ARCHIVE['sha256'] + '\n'
            'Dengan Python 3.10 atau lebih baru, jalankan dari direktori hasil ekstraksi:\n' + command + '\n\n'
            'Hasil yang diharapkan: dua validator lulus dan 13 berkas metadata sama persis dengan rilis native. '
            'Tidak diperlukan direktori pembuat buku, jaringan saat replay, model penerjemahan atau TeX. '
            'Dua skrip penerjemahan lama disertakan hanya sebagai input bukti; keduanya tidak dijalankan. '
            'Ini bukan pembangunan PDF, replay seluruh Li, audit kanon baru atau klaim backend seluruh program selesai. '
            'Hak komponen dan atribusi penerjemahan asli tidak berubah.\n'
            'Integrasi dependensi dan verifikasi: OpenAI Codex — gpt-6.1-sol, Ultra effort.\n'),
        'INSTRUCTIONS.en.txt': ('D70: native metadata replay\n\n'
            'Extract this ZIP. Keep the original ZIP beside the extracted files and download the separate unchanged native source archive: '
            'https://zenodo.org/api/records/22160944/files/05_o013-sumber-backend-1.0.0.zip/content\n'
            'Native source identity: 1,295,518 bytes; SHA-256 ' + audit.EXPECTED_ARCHIVE['sha256'] + '\n'
            'With Python 3.10 or later, run from the extracted directory:\n' + command + '\n\n'
            'Expected: two passing validators and 13 metadata artifacts byte-identical to the native release. '
            'No producer tree, network during replay, translation model or TeX is needed. '
            'Two historical translation scripts are included only as evidence inputs; neither is executed. '
            'This is not a PDF build, whole-Li replay, new canon review or whole-program completion claim. '
            'Native component rights and translation attribution are unchanged.\n'
            'Dependency integration and verification: OpenAI Codex — gpt-6.1-sol, Ultra effort.\n')}
    for name, text in instructions.items():
        contents[name] = text.encode('utf-8')
        rows.append({'path': name, 'bytes': len(contents[name]), 'sha256': hashlib.sha256(contents[name]).hexdigest(),
                     'origin': {'method': 'localized_replay_instructions'}})
    report_source = {'name': audit.ARCHIVE, **audit.EXPECTED_ARCHIVE}
    manifest = {'schema': 'd70-native-metadata-replay-bundle/1', 'course_id': 'D70',
                'source_archive': report_source,
                'source_url': 'https://zenodo.org/api/records/22160944/files/' + audit.ARCHIVE + '/content',
                'files': sorted(rows, key=lambda row: row['path']),
                'native_book_bodies_included': False, 'whole_native_parity_proven': False,
                'scope_id': 'Input tambahan untuk membangun ulang metadata Duncan dan CRing; bukan kompilasi PDF atau audit kanon baru.',
                'scope_en': 'Additional inputs to reproduce Duncan and CRing metadata; not a PDF build or new canon review.',
                'attribution': 'OpenAI Codex — gpt-6.1-sol, Ultra effort: dependency integration and verification. Native translation attribution unchanged.'}
    contents[MANIFEST] = canonical(manifest)
    return manifest, contents


def write_bundle(path, contents):
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(contents):
            audit.safe_name(name)
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, contents[name], compresslevel=9)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, default=ROOT / 'work/d70-native-source-closure-v1/audit.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'backend/course-capsule-v1/adapters/d70-native-replay-v1/build/D70_NATIVE_METADATA_REPLAY_V1.zip')
    args = parser.parse_args()
    report = json.loads(args.audit.read_bytes())
    isolated = (ROOT / report['isolated_directory']).resolve(strict=True)
    audit.require(isolated.is_relative_to((ROOT / 'work/d70-native-source-closure-v1').resolve()), 'Audit cursor escapes owned replay directory')
    manifest, contents = prepare(report, isolated, Path(__file__).parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_bundle(args.output, contents)
    with zipfile.ZipFile(args.output) as archive:
        audit.require(archive.testzip() is None, 'Bundle CRC failure')
        audit.require(set(archive.namelist()) == set(contents), 'Bundle inventory differs')
        audit.require(all(archive.read(name) == data for name, data in contents.items()), 'Bundle bytes differ')
    receipt = {'schema': 'd70-native-metadata-replay-build/1', 'state': 'pass',
               'bundle': {'path': args.output.relative_to(ROOT).as_posix(), **audit.identity(args.output)},
               'manifest': {'bytes': len(contents[MANIFEST]), 'sha256': hashlib.sha256(contents[MANIFEST]).hexdigest()},
               'member_count': len(contents), 'dependency_files': 26, 'dependency_bytes': 4322608,
               'native_book_bodies_included': False, 'native_source_zip_supplied_separately': manifest['source_archive'],
               'whole_native_parity_proven': False}
    (args.output.parent / 'BUILD_RECEIPT.json').write_bytes(canonical(receipt))
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
