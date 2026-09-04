# D40 thin learning-capability adapter

This directory is an additive `course-learning-capability/1` projection of the
native O010/D40 repository. The native repository remains authoritative. The
adapter contains identity, relationship, rights, evidence, and access metadata;
it contains no book prose, exercise or solution bodies, TeX, notebook/code
bodies, runtime artifacts, PDF, or release ZIP.

The projection retains:

- 68 native mastery roots: 48 practice problems, 16 assessment items, and 4 labs;
- all 108 native prerequisite relations;
- all 14 stable Dionne chapter IDs/titles and all 130 many-to-many `supports`
  relations (no forced one-chapter-per-item mapping);
- a hash-bound, zero-copy Dionne import of 3,920 objects;
- 4 executed-notebook identities, 8 execution surfaces, and 116 required cell
  identities (54 code and 62 Markdown), without executing them;
- the native `executed_as` multiplicity across labs (1, 2, 1, 0), rather than
  fabricating one notebook for every lab;
- all 5 native rights records, including the unasserted runtime-record boundary
  and the no-blanket-relicensing rules;
- the exact public PDF and ZIP byte identities and their verified Zenodo URLs.

The offline semantic HTML reader is accurately described as
`reader/html/index.html` inside the public ZIP. Native evidence reports 24,118
static MathML elements and zero runtime network dependencies. The adapter does
not claim a live whole-course HTML URL or MathJax runtime. It also makes no WCAG,
assistive-technology testing, complete-ToUnicode, or tagged-PDF claim; PDF
tagging remains unknown because the evidence does not establish it.

`data/learning-map.json` is the strict shared-contract projection. Learner and
educator views are generated from the same 68 native object IDs. Paths shown for
archive members are labels, never fabricated direct URLs.

Build and validate from the central checkout:

```text
python -B scripts/build_d40_capability_v1.py
python -B scripts/validate_d40_capability_v1.py
python -B scripts/package_d40_capability_v1.py
```

The validator verifies every locked native input, compares two isolated builds
byte-for-byte with the committed projection, parses both views, checks the
shared contract and native evidence independently, and requires every negative
fixture to be rejected with its named stable code.

The packager creates a deterministic offline validation packet containing only
the adapter, the four D40 scripts, and the exact metadata/evidence inputs needed
for rebuild and validation. Apart from those adapter scripts, it excludes the
public PDF/ZIP, reader payload, source/book prose, TeX, notebooks, native course
code bodies, and runtime artifacts. It proves sorted fixed-metadata ZIP replay,
CRC and full-entry readback, extraction, rebuild, and validation.

All generated adapter paths are portable and relative. One exact locked native
input, `D40_MASTERY_VALIDATION.json`, retains its historical `scope_absolute`
receipt field byte-for-byte; the packet inventories that field explicitly and
never uses it for routing. Any additional absolute-path-bearing packet member
is rejected.

No admission, shared integration, Git, or publication state is changed here.
`contract_2_3_1_conformance` and `full_native_roundtrip_claimed` both remain
false/not claimed.
