# D100 English capability adapter

This directory is a zero-copy `course-learning-capability/1` projection of the
frozen `en-v1.0.0` English release in the sibling
`algebraic-geometry-bridge-id` repository.

The adapter exposes 60 source-course unit aggregates, 32 separate companion
navigation units, 1,201 exercises, exact solution provenance, the 57-item
concentrated mastery route, native ledger references, and learner/educator
views. It does not copy mathematical bodies or rewrite the central Indonesian
(`id-ID`) course truth.

Important boundaries:

- 1,188 source exercises have 147 public source solutions and 1,041 explicit
  no-public-source-solution states.
- The companion has 13 integrative/capstone exercises with 13 solutions.
- Forty-four mastery solutions are new editorial material; thirteen mastery
  items reference existing public source solutions. They are not additional
  source exercises.
- Rights remain per native record/component. No umbrella licence is claimed.
- Native MathML, tagged PDF, WCAG conformance, assistive-technology user tests,
  human review, executable labs, strict source-profile reversibility, and
  Zenodo public-byte readback are not claimed.
- GitHub release and Pages availability are referenced from the frozen public
  readback receipt; this adapter changes no public state.

Build and validate from the program repository root:

```text
python -B scripts/build_d100_capability_v1.py
python -B scripts/validate_d100_capability_v1.py
```

`input/source-lock.json` pins the 19 native release, input-map, QA, and release
control files. Refresh it only for an intentional native release intake:

```text
python -B scripts/build_d100_capability_v1.py --refresh-source-lock
```

The validator independently streams the three large JSONL inputs, verifies the
strict common-contract shape, checks both views, rejects every negative fixture,
and compares two isolated builds byte-for-byte with the committed adapter.
