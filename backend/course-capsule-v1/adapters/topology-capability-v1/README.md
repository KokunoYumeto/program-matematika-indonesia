# C90 topology learning capability

This adapter connects the completed Indonesian topology edition to the shared
curriculum without copying or rewriting the book. It preserves the native
chapter, companion, staged-practice, terminology, correction, rights, and
release identities and exposes them through learner and educator views.

The adapter covers 20 chapters, 20 self-study companions, eight completion
modules, and 1,227 canonical support or mastery records. Each record retains
separate statement, hint, answer, and solution destinations with byte and
SHA-256 identities. The source book's 252 exercise containers and 1,142 tasks
remain separate source-level counts; they are not re-labelled as staged
records.

HTML is the primary accessible reading surface. The PDF is not tagged. Two
source corrections remain unresolved and one terminology decision remains
provisional. These states are deliberately preserved rather than silently
promoted. The adapter does not claim a general round trip into the native
authoring format or human certification of learning outcomes.

Build and validate from the repository root:

```text
python -B scripts/build-topology-capability-v1.py
python -B scripts/validate-topology-capability-v1.py
```

Open `docs/backend/topology/C90.html` for the learner route and
`docs/backend/topology/pengajar.html` for the educator selector.
