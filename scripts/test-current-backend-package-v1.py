"""Small positive and adversarial fixtures for preservation package safety."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('pack', Path(__file__).with_name('package-current-backend-v1.py'))
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)
runtime_spec = importlib.util.spec_from_file_location('runtime', Path(__file__).with_name('audit-current-backend-runtime-v1.py'))
runtime = importlib.util.module_from_spec(runtime_spec)
runtime_spec.loader.exec_module(runtime)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='backend-package-fixture-')
        self.root = Path(self.temp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'docs/example.json').write_bytes(b'{"example":true}\n')
        self.manifest = {'files': [{'path': 'docs/example.json', **pack.identity(self.root / 'docs/example.json')}],
                         'roles': [], 'file_count': 1}

    def tearDown(self):
        self.temp.cleanup()

    def test_exact_and_deterministic_zip(self):
        a, b = self.root / 'a.zip', self.root / 'b.zip'
        pack.write_archive(self.root, a, self.manifest)
        pack.write_archive(self.root, b, self.manifest)
        self.assertEqual(pack.verify_archive(a), self.manifest)
        self.assertEqual(pack.identity(a), pack.identity(b))

    def test_existing_archive_is_not_overwritten(self):
        path = self.root / 'a.zip'
        pack.write_archive(self.root, path, self.manifest)
        with self.assertRaises(FileExistsError):
            pack.write_archive(self.root, path, self.manifest)

    def test_source_change_during_preparation_rejects(self):
        (self.root / 'docs/example.json').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Source changed'):
            pack.write_archive(self.root, self.root / 'a.zip', self.manifest)

    def test_corrupted_payload_rejects(self):
        with zipfile.ZipFile(self.root / 'a.zip', 'w') as z:
            z.writestr('docs/example.json', b'changed')
            z.writestr(pack.MANIFEST, pack.canonical(self.manifest))
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            pack.verify_archive(self.root / 'a.zip')

    def test_extra_member_rejects(self):
        with zipfile.ZipFile(self.root / 'a.zip', 'w') as z:
            z.writestr('docs/example.json', b'{"example":true}\n')
            z.writestr('extra.txt', b'unexpected')
            z.writestr(pack.MANIFEST, pack.canonical(self.manifest))
        with self.assertRaisesRegex(ValueError, 'extra'):
            pack.verify_archive(self.root / 'a.zip')

    def test_noncanonical_paths_reject(self):
        for path in ['../escape', '/absolute', 'C:/absolute', 'docs/../escape', 'docs\\bad', 'docs//bad', '.git/config']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                pack.safe_name(path)

    def test_missing_local_fact_rejects(self):
        with self.assertRaises(FileNotFoundError):
            pack.local_path(self.root, 'docs/missing.json')

    def native_fixture(self):
        path = self.root/'docs/native-audit.json'
        path.write_text(json.dumps({'state':'pass','all_source_checksums_verified':True,
            'source_archive':{'anonymous':True,'url':'https://example.org/native-source.zip','bytes':123,'sha256':'a'*64},
            'fresh_html_backend_replay':{'commands':[{'command':['python','fixtures/native.py'],'exit_code':0}]}}), encoding='utf-8')
        return [{'referrer':'fixtures/auditor.py','archive_script_paths':['fixtures/native.py'],
                 'evidence':{'path':'docs/native-audit.json',**pack.identity(path)}}]

    def test_declared_native_archive_command_has_explicit_boundary(self):
        row = pack.native_script_dependency(self.root,'fixtures/auditor.py','fixtures/native.py',self.native_fixture())
        self.assertEqual(row['archive_script_path'],'fixtures/native.py')
        self.assertIn('not a shared-capsule build dependency',row['scope'])

    def test_wrong_referrer_does_not_hide_missing_local_script(self):
        with self.assertRaises(FileNotFoundError):
            pack.native_script_dependency(self.root,'fixtures/other.py','fixtures/native.py',self.native_fixture())

    def test_undeclared_native_script_rejects(self):
        with self.assertRaises(FileNotFoundError):
            pack.native_script_dependency(self.root,'fixtures/auditor.py','fixtures/missing.py',self.native_fixture())

    def test_changed_native_evidence_rejects(self):
        declarations = self.native_fixture()
        (self.root/'docs/native-audit.json').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'evidence identity'):
            pack.native_script_dependency(self.root,'fixtures/auditor.py','fixtures/native.py',declarations)

    def test_unevidenced_archive_command_rejects(self):
        declarations = self.native_fixture()
        declarations[0]['archive_script_paths'].append('fixtures/unevidenced.py')
        with self.assertRaisesRegex(AssertionError,'not evidenced'):
            pack.native_script_dependency(self.root,'fixtures/auditor.py','fixtures/unevidenced.py',declarations)

    def preserved_source_fixture(self):
        code = self.root / 'docs/native-code.py.txt'
        code.write_bytes(b'def nonempty_blocks(text):\n    return text.split("\\n\\n")\n')
        lock = self.root / 'docs/source-lock.json'
        lock.write_text(json.dumps({'schema': 'c130-native-ledger-lock/1',
            'native_alignment_authority': {'exporter': {'member': 'fixtures/native.py', **pack.identity(code)}},
            'archives': {'backend': {'url': 'https://example.org/native.zip', 'bytes': 123, 'sha256': 'a' * 64}}}), encoding='utf-8')
        return [{'referrers': ['fixtures/auditor.py'], 'archive_script_path': 'fixtures/native.py',
            'source_lock': {'path': 'docs/source-lock.json', **pack.identity(lock)},
            'preserved_source': {'path': 'docs/native-code.py.txt', **pack.identity(code)}}]

    def test_preserved_native_source_has_exact_code_and_no_execution_claim(self):
        row = pack.preserved_native_source(self.root, 'fixtures/auditor.py', 'fixtures/native.py', self.preserved_source_fixture())
        self.assertEqual(row['preserved_source']['path'], 'docs/native-code.py.txt')
        self.assertIn('not a full native execution', row['scope'])

    def test_preserved_source_referrer_and_member_are_exact(self):
        rules = self.preserved_source_fixture()
        for referrer, member in [('fixtures/other.py', 'fixtures/native.py'), ('fixtures/auditor.py', 'fixtures/other.py')]:
            with self.assertRaises(FileNotFoundError):
                pack.preserved_native_source(self.root, referrer, member, rules)

    def test_changed_preserved_native_code_rejects(self):
        rules = self.preserved_source_fixture()
        (self.root / 'docs/native-code.py.txt').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'code identity'):
            pack.preserved_native_source(self.root, 'fixtures/auditor.py', 'fixtures/native.py', rules)

    def test_changed_preserved_native_lock_rejects(self):
        rules = self.preserved_source_fixture()
        (self.root / 'docs/source-lock.json').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'lock identity'):
            pack.preserved_native_source(self.root, 'fixtures/auditor.py', 'fixtures/native.py', rules)

    def test_duplicate_preserved_native_source_refusals(self):
        rules = self.preserved_source_fixture()
        with self.assertRaises(FileNotFoundError):
            pack.preserved_native_source(self.root, 'fixtures/auditor.py', 'fixtures/native.py', rules + rules)

    def test_wrong_preserved_member_authority_rejects(self):
        rules = self.preserved_source_fixture()
        lock = self.root / 'docs/source-lock.json'
        data = json.loads(lock.read_bytes())
        data['native_alignment_authority']['exporter']['member'] = 'fixtures/other.py'
        lock.write_text(json.dumps(data), encoding='utf-8')
        rules[0]['source_lock'].update(pack.identity(lock))
        with self.assertRaisesRegex(AssertionError, 'Wrong native member'):
            pack.preserved_native_source(self.root, 'fixtures/auditor.py', 'fixtures/native.py', rules)

    def test_static_assets_and_extensionless_licence(self):
        (self.root/'docs/index.html').write_text('<link rel="stylesheet" href="style.css"><a href="COPYING">Licence</a>',encoding='utf-8')
        plan = {'files':[{'path':'docs/index.html'},{'path':'docs/example.json'}]}
        report = runtime.audit(self.root,plan)
        self.assertEqual(report['missing_static_assets'][0]['path'],'docs/style.css')
        self.assertEqual(report['outside_package_navigation'][0]['path'],'docs/COPYING')
        self.assertEqual(runtime.destination('docs/backend/index.html','../id/'),'docs/id/index.html')

    def test_privacy_guard_not_mistaken_for_private_path(self):
        (self.root/'docs/check.txt').write_text('C:/'+'Users/',encoding='utf-8')
        plan = {'files':[{'path':'docs/check.txt'}]}
        self.assertEqual(runtime.audit(self.root,plan)['privacy_findings'],[])
        (self.root/'docs/check.txt').write_text('C:/'+'Users/'+'Example/'+'file.txt',encoding='utf-8')
        self.assertEqual(runtime.audit(self.root,plan)['privacy_findings'],[{'path':'docs/check.txt','kind':'absolute-user-path'}])

    def test_commonjs_browser_harness_privacy_is_checked(self):
        path = self.root / 'scripts/check.cjs'
        path.parent.mkdir()
        plan = {'files': [{'path': 'scripts/check.cjs'}]}
        path.write_text("require(process.env.PLAYWRIGHT_MODULE_PATH || 'playwright');", encoding='utf-8')
        self.assertEqual(runtime.audit(self.root, plan)['privacy_findings'], [])
        path.write_text("require('" + 'C:/' + 'Users/' + "Example/dependency');", encoding='utf-8')
        self.assertEqual(runtime.audit(self.root, plan)['privacy_findings'],
                         [{'path': 'scripts/check.cjs', 'kind': 'absolute-user-path'}])


if __name__ == '__main__':
    unittest.main()
