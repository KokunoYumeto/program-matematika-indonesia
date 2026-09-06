# D30 zero-copy learning-capability adapter

This additive adapter projects the pinned O009/D30 modular backend into
`course-learning-capability/1`. It preserves native IDs, states, relations,
component rights, hashes, and public reader/original-source routes. It never
copies native prose, formulas, solutions, code, HTML, PDF, or archive payloads.

The native repository and checkpoint-38 Zenodo record remain authoritative.
The 42 rights records remain component-specific; no blanket license is claimed.
The O006/C140 prerequisite remains an external reference without copied bytes.

Build, validate, and package from the central checkout:

```text
python -B scripts/build_d30_capability_v1.py
python -B scripts/validate_d30_capability_v1.py
python -B scripts/package_d30_capability_v1.py
```

The learner and educator views link visibly back to `/en/` and `/id/`, and each
course surface links to both the public native reader and pinned original source.
No shared integration, Git, or publication state is changed by these scripts.
