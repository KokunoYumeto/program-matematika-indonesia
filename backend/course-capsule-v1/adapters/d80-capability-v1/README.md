# D80 native capability adapter

This is a bounded, zero-copy projection of the O014/D80 *Methods of Algebra,
Volume 2* Indonesian lane. It exposes 146 native translated-source units, two
separately typed independent mastery bridges, 148 routes into the corrected
GitHub Pages reader, and 32 exact mastery exercise/solution fragments.

The learner and educator views are generated from the same stable unit and
fragment identities. They route to the corrected Pages reader, not the stale
reader retained on GitHub `main`. Segment text, terminology rows, diagram
descriptions, reader overrides, and correction bodies remain in their native
ledgers; this adapter binds those ledgers by path, byte count, hash, count, and
the few distinctions central consumers must not erase.

## Build and validate

From the central checkout:

```text
python -B scripts/build_d80_capability_v1.py
python -B scripts/validate_d80_capability_v1.py
```

The validator checks every frozen input, all 146 translation targets, every
projected route and mastery anchor against the corrected local reader, output
hashes, shared learner/educator identities, two isolated byte-identical builds,
and eleven retained negative fixtures. It also preserves the frozen 51-unit
checkpoint's identity boundary: Unit 001 lacks native target fields and Units
002--051 retain 50 superseded target-hash strings (Unit 026's historical value
is explicitly retained as malformed 67-character hex), while the final 146-row manifest
and matching target bytes govern current routing. It uses only the Python standard library.
Neither command invokes TeX, publishes, modifies the native producer, or
changes shared admission, coverage, interface, packaging, or release files.

## Scope and limitations

Contract: `course-learning-capability/1`. Contract 2.3.1 conformance is not
claimed. The source has 194 exercises and 117 hints but no answers or
solutions. The 16 exercises and 16 solutions surfaced here belong only to the
two independent mastery bridges and are not attributed to Wen-Wei Li.

The source backend has no native MathML; the corrected reader retains 27,308
MathJax source nodes and can obtain assistive MathML only at runtime. No WCAG
level, tagged-PDF, complete-ToUnicode, or user assistive-technology test claim
is made. The adapter is metadata/navigation, not a copy of the reader or the
native semantic ledgers.
