"""Bounded path, dependency and producer-write guards for the D70 audit."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name('audit-d70-native-source-closure-v1.py')
spec = importlib.util.spec_from_file_location('d70_native_audit', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AuditGuards(unittest.TestCase):
    def test_unsafe_and_aliased_source_names_rejected(self):
        for name in ['', '.', '..', '../file', 'path/../file', '/file', 'C:/file',
                     'path\\file', 'path:stream', './file', 'path//file', 'path/./file']:
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                m.safe_name(name)

    def test_exact_normal_source_names_accepted(self):
        for name in ['SOURCE_ARCHIVE_MANIFEST.json', 'components/duncan/backend/duncan-component.json',
                     'authority/cring-project-official-20260828/CRing.pdf']:
            m.safe_name(name)

    def test_streamed_byte_identity(self):
        with tempfile.TemporaryDirectory(prefix='d70-audit-unit-') as directory:
            source = Path(directory) / 'identity.bin'
            value = bytes(range(256)) * 5000
            source.write_bytes(value)
            self.assertEqual(m.identity(source), {'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest()})

    def test_changed_authority_archive_rejected_before_copy(self):
        with tempfile.TemporaryDirectory(prefix='d70-audit-unit-') as directory:
            native, isolated = Path(directory) / 'native', Path(directory) / 'isolated'
            rel = 'authority/duncan-representation-theory-notes-c62d36f41189da4bd3da4671668f68720df54ff7/representation-theory-notes-c62d36f41189da4bd3da4671668f68720df54ff7.zip'
            source = native / rel
            source.parent.mkdir(parents=True)
            source.write_bytes(b'changed archive')
            with self.assertRaisesRegex(RuntimeError, 'External frozen dependency differs'):
                m.provision_native_dependencies(native, isolated)
            self.assertFalse(isolated.exists())

    def test_validator_execution_never_targets_native(self):
        # A synthetic result checks exact captured command and cwd boundaries
        # without launching a worker or writing a producer receipt.
        class Result:
            returncode = 1
            stdout = ''
            stderr = '{"result":"FAIL","error":"<isolated-root>/authority/missing"}'
        with tempfile.TemporaryDirectory(prefix='d70-audit-unit-') as directory:
            isolated = Path(directory).resolve()
            with patch.object(m.subprocess, 'run', return_value=Result()) as run:
                rows = m.replay_validators(isolated)
                self.assertEqual(len(rows), 2)
                for call in run.call_args_list:
                    command = call.args[0]
                    self.assertTrue(Path(command[2]).is_relative_to(isolated))
                    self.assertEqual(call.kwargs['cwd'], isolated)
                    self.assertEqual(call.kwargs['timeout'], 90)
                    self.assertNotIn('shell', call.kwargs)

    def test_no_tex_cloud_git_or_producer_mutation_execution(self):
        tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
        # No hidden platform clients or alternate process-launch paths.
        imports = {node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)}
        self.assertFalse(imports & {'requests', 'urllib', 'os', 'socket'})
        launches = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == 'subprocess']
        self.assertEqual(len(launches), 1)
        self.assertEqual(launches[0].func.attr, 'run')

if __name__ == '__main__':
    unittest.main()
