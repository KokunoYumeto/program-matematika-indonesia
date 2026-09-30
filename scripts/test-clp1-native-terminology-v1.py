"""Bounded positive and negative checks for the CLP-1 metadata projection."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('clp1_terms',Path(__file__).with_name('clp1-native-terminology-v1.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
BASE=p.ROOT/'backend/course-capsule-v1/adapters/clp1-native-terminology-v1'

class ProjectionTests(unittest.TestCase):
    def setUp(self):
        self.terms=[json.loads(l) for l in (BASE/'input/terms.jsonl').read_text(encoding='utf-8').splitlines()]
        self.concepts=[json.loads(l) for l in (BASE/'input/concepts.jsonl').read_text(encoding='utf-8').splitlines()]
        self.decisions=(BASE/'input/TRANSLATION_DECISIONS.id-ID.md').read_text(encoding='utf-8')
    def test_three_exact_repairs_and_stable_ids(self):
        before=copy.deepcopy((self.terms,self.concepts))
        result=p.project(self.terms,self.concepts,self.decisions)
        self.assertEqual((self.terms,self.concepts),before)
        self.assertEqual([r['id'] for r in result['terms']],[r['id'] for r in self.terms])
        by_id={r['id']:r for r in result['terms']}
        self.assertEqual(by_id['clp1.term.absolute_maximum']['target_term'],'maksimum absolut')
        self.assertEqual(by_id['clp1.term.local']['source_term'],'local maximum')
        self.assertEqual(by_id['clp1.term.down']['source_term'],'concave down')
        self.assertEqual(by_id['clp1.term.down']['target_term'],'cekung ke bawah')
        self.assertEqual(sum(a!=b for a,b in zip(result['terms'],self.terms)),3)
        self.assertEqual(sum(a!=b for a,b in zip(result['concepts'],self.concepts)),3)
        self.assertEqual(result['semantic_canon_review'],'not_established')
        self.assertEqual(p.canonical(result),(BASE/'projection.json').read_bytes())
    def test_changed_table_rejected(self):
        with self.assertRaisesRegex(AssertionError,'locator drift'):
            p.project(self.terms,self.concepts,self.decisions.replace('maksimum lokal/absolut','other'))
    def test_changed_native_term_rejected(self):
        self.terms[0]['target_term']='other'
        with self.assertRaisesRegex(AssertionError,'term drift'):
            p.project(self.terms,self.concepts,self.decisions)
    def test_changed_native_concept_rejected(self):
        self.concepts[0]['label']='other'
        with self.assertRaisesRegex(AssertionError,'concept drift'):
            p.project(self.terms,self.concepts,self.decisions)
    def test_missing_record_rejected(self):
        with self.assertRaises(AssertionError):
            p.project(self.terms[:-1],self.concepts,self.decisions)
    def test_raw_inputs_bound(self):
        for key,(native,expected) in p.INPUTS.items():
            name={'decisions':'TRANSLATION_DECISIONS.id-ID.md','terms':'terms.jsonl','concepts':'concepts.jsonl'}[key]
            self.assertEqual(p.fact((BASE/'input'/name).read_bytes())['sha256'],expected)

if __name__=='__main__':
    unittest.main()
