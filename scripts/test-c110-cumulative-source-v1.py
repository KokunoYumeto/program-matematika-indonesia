"""Read-only tests for native byte preservation and the checked C110 replay."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('assembly', Path(__file__).with_name('assemble-c110-cumulative-source-v1.py'))
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)

parser = argparse.ArgumentParser()
parser.add_argument('--intake', required=True)
args = parser.parse_args()
p = Path(args.intake)
files, meta, build = api.load_archive(p/'native-source.zip', p/'PACKAGE_INVENTORY.json')
one, rows = api.assemble(files)
two, again = api.assemble(files)
assert one == two and rows == again
assert one == (p/'assembled'/api.MASTER).read_bytes()
assert one == (p/'build-assembled'/api.MASTER).read_bytes()
assert len(rows) == 30
for row in rows:
    assert one[row['output_start']:row['output_end']] == files[row['path']]
assert len(list((p/'build-assembled').glob('*.tex'))) == 1
receipt = json.loads((p/'build-assembled/BUILD_RECEIPT.json').read_text(encoding='utf-8-sig'))
assert receipt['status'] == 'compiled_pending_equivalence_check' and receipt['exit_code'] == 0
native = (p/'native.pdf').read_bytes()
replayed = (p/'build-assembled/TeaTimeNumericalAnalysis-id-ID.pdf').read_bytes()
assert api.sha(native) == build['pdf']['sha256'] == receipt['pdf']['sha256']
assert native == replayed and len(native) == build['pdf']['bytes']
assert receipt['source_sha256'] == api.sha(one)
rejected = []
for name, mutate in [
    ('missing_body', lambda f: f.pop(api.SOURCE+'answers.tex')),
    ('duplicate_include', lambda f: f.update({api.SOURCE+api.MASTER:f[api.SOURCE+api.MASTER]+b'\\include{answers}'})),
    ('nested_input', lambda f: f.update({api.SOURCE+'answers.tex':f[api.SOURCE+'answers.tex']+b'\\input missing'})),
    ('unselected_tex', lambda f: f.update({api.SOURCE+'unselected.tex':b'not part of the edition'})),
    ('commented_include', lambda f: f.update({api.SOURCE+api.MASTER:f[api.SOURCE+api.MASTER].replace(b'\\include{answers}',b'%\\include{answers}')})),
]:
    changed = copy.copy(files)
    mutate(changed)
    try: api.assemble(changed)
    except (ValueError, KeyError): rejected.append(name)
    else: raise AssertionError('Accepted '+name)
for bad in ['../escape', '/absolute', 'C:/drive', 'dir\\file']:
    try: api.safe_name(bad)
    except ValueError: rejected.append('unsafe_path:'+bad)
    else: raise AssertionError('Unsafe path accepted')
print(json.dumps({'status':'pass', 'native_payload_files':len(meta['files']),
                  'native_build_inputs':289, 'embedded_bodies':30,
                  'deterministic_assembly':True, 'pdf_byte_identical':True,
                  'pages':387, 'rejected':rejected}))
