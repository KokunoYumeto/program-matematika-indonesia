"""Narrow supplement exercise candidates using hash-bound file/page evidence.

This diagnostic is not an admitted exercise map. Page-range containment and
literal prose witnesses cannot alone resolve short formula/reference problems.
"""
import argparse
from collections import Counter
import csv
import difflib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import fitz

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ol_mapping', ROOT/'scripts/map-openlogic-problems-v1.py')
mapping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapping)
intake = mapping.intake


def candidates(problem, unit, coverage, destinations, target_bytes):
    """Return evidence without selecting an identity based on similarity."""
    assert coverage['source_path'] == unit['source_path']
    assert coverage['source_sha256'] == unit['source']['sha256']
    assert coverage['target_sha256'] == unit['target']['sha256']
    assert problem['source_path'] == unit['source_path']
    block = target_bytes[problem['target']['byte_start']:problem['target']['byte_end_exclusive']]
    assert intake.identity(block) == problem['target']['block']
    words = mapping.tokens(intake.clean_tex(block.decode('utf-8-sig')))
    lo, hi = int(coverage['pdf_start_page']), int(coverage['pdf_end_page'])
    assert 1 <= lo <= hi <= 139
    rows = []
    for item in destinations:
        # A destination can lie immediately before a page break. Match the
        # actual visible heading page against the file's physical page span.
        page = item['heading_combined_page']
        if page is None or not lo <= page - 1116 <= hi:
            continue
        rendered = mapping.tokens(item['_text'])
        match = difflib.SequenceMatcher(None, words, rendered, autojunk=False).find_longest_match()
        rows.append({
            **{k:v for k,v in item.items() if not k.startswith('_')},
            'longest_literal_word_run': match.size,
            'literal_witness': ' '.join(words[match.a:match.a+match.size]),
            'pdf_preview': item['_text'][:320],
        })
    return {
        'source_problem_id': problem['id'],
        'source_path': unit['source_path'],
        'native_unit_id': unit['native_unit_id'],
        'producer_closure_id': coverage['closure_id'],
        'join_key': 'source_path + source_sha256 + target_sha256; not closure_id',
        'target_block': problem['target'],
        'target_preview': block.decode('utf-8-sig')[:400],
        'file_component_page_span': [lo, hi],
        'file_combined_page_span': [lo+1116, hi+1116],
        'candidates': sorted(rows, key=lambda x:(-x['longest_literal_word_run'],x['component_page'],x['destination'])),
        'state': 'diagnostic_not_admitted',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    inventory_path = ROOT/'backend/course-capsule-v1/adapters/openlogic-teacher-v1/source-problems.json'
    inventory_bytes = intake.checked_file(inventory_path, {
        'bytes':1312777, 'sha256':'655d56f4ea8535e4424902b693fcc393e7e0bdcb4a245835f63bd5ae761e4199'})
    inventory = json.loads(inventory_bytes)
    authority = json.loads((intake.NATIVE/'INPUT_AUTHORITIES.json').read_bytes())
    target_ref = next(a for a in authority['authorities'] if a['role']=='frozen_localized_zip')
    target_bytes = intake.checked_file(args.workspace/target_ref['path'], target_ref)
    qa_bytes = intake.checked_file(args.cache/'06_OPENLOGIC_id_SUPPLEMENT_COVERAGE_AND_QA_20260904.zip', {
        'bytes':272337, 'sha256':'a74ddffccac99b434abcc4ea2e2a73819a01a286400e9a63b6fb15d55cf9c082'})
    pdf_bytes = intake.checked_file(args.cache/'04_OPENLOGIC_id_READER_SUPPLEMENT_80_20260904.pdf', {
        'bytes':857775, 'sha256':'bad0b8a0e22652cccab782e6e159868e00e137796d41578b3dd649b8a1831bae'})
    units = {u['source_path']:u for u in inventory['units']}
    with zipfile.ZipFile(io.BytesIO(qa_bytes)) as qa:
        coverage_bytes = qa.read('audit/rendered-coverage-80.csv')
    coverage = list(csv.DictReader(io.StringIO(coverage_bytes.decode('utf-8-sig'))))
    assert len(coverage)==80 and len({r['source_path'] for r in coverage})==80
    by_path = {r['source_path']:r for r in coverage}
    with fitz.open(stream=pdf_bytes, filetype='pdf') as pdf:
        assert len(pdf)==139
        names = pdf.resolve_names()
        anchored = 0
        cursor_only = []
        for row in coverage:
            unit = units[row['source_path']]
            assert not unit['in_frozen_main_reader']
            assert row['source_sha256']==unit['source']['sha256']
            assert row['target_sha256']==unit['target']['sha256']
            assert row['supplement_pdf_sha256']==intake.identity(pdf_bytes)['sha256']
            if row['page_anchor']:
                assert names[row['page_anchor']]['page']+1==int(row['pdf_start_page'])
                anchored += 1
            else:
                assert row['supplement_page_mapping']=='inclusive_input_cursor_span'
                cursor_only.append(row['source_path'])
        assert anchored==78 and sorted(cursor_only)==[
            'content/model-theory/basics/nonstandard-arithmetic.tex',
            'content/proof-theory/cut-elimination/intuitionistic.tex']
        destinations = mapping.destinations(pdf, 'prob*.', 1116)
        assert len(destinations)==31 and all(d['printed_number'] for d in destinations)
        with zipfile.ZipFile(io.BytesIO(target_bytes)) as target:
            comparisons = []
            for problem in inventory['problems']:
                if problem['in_frozen_main_reader']:
                    continue
                unit = units[problem['source_path']]
                raw = target.read('source/'+unit['target_path'])
                assert intake.identity(raw)==unit['target']
                comparisons.append(candidates(problem, unit, by_path[unit['source_path']], destinations, raw))
    assert len(comparisons)==31
    result = {
        'schema':'openlogic-supplement-candidates/1', 'state':'diagnostic_not_admitted',
        'source_inventory':intake.identity(inventory_bytes),
        'coverage_csv':intake.identity(coverage_bytes),
        'coverage_archive':intake.identity(qa_bytes), 'supplement_pdf':intake.identity(pdf_bytes),
        'verified_unit_hash_joins':80, 'verified_section_destinations':anchored,
        'producer_cursor_only_spans_not_independent_anchors':cursor_only,
        'source_problems':31, 'rendered_destinations':31,
        'page_range_candidate_counts':dict(Counter(len(r['candidates']) for r in comparisons)),
        'comparisons':comparisons,
        'limits':'No identity selection from equal counts, containment, or similarity. No canonical-ID substitution. Combined links must use physical pages, not supplement-only named destinations.',
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'}))


if __name__=='__main__':
    main()
