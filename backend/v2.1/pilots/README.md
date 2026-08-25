# Global backend v2.1 unit/search pilots

These three packages are additive, read-only projections of already admitted
owner-native backends. They do not replace the owner backend or the v1/v2
federation. Their narrow purpose is to prove a compact learner-navigation and
search layer with stable native unit identities.

The shared pilot contract is self-describing in each `manifest.json`:

- `units.jsonl` preserves native unit IDs and document order, localized titles,
  native locators, source/target hashes, and a learner route or an explicit
  course-level fallback.
- `relations.jsonl` contains only relations supported by a named native or
  central authority. It does not infer prerequisites from prose.
- `search.jsonl` contains titles and short structural metadata only. It never
  copies textbook prose.
- `rights_accessibility.json` summarizes the admitted rights and accessibility
  evidence without weakening component-level terms.
- `manifest.json` binds the input authorities and every materialized data file.
- `validation_report.json` is a deterministic, independently rerunnable report
  and is deliberately outside the manifest's non-circular file inventory.

Rebuild and validate from the program repository root:

```powershell
python -B backend/v2.1/pilots/build_all_pilots.py
python -B backend/v2.1/pilots/validate_pilots.py
```

The A00 pilot exposes its 75 owner-native CNXML module pages because that
edition has a verified per-module HTML reader. The B10 pilot preserves all 161
book/chapter/section/subsection identities, but deliberately uses the published
course root as the learner fallback: the central authority says clean per-unit
routes are planned, not published.

The D20 pilot preserves 19 owner-native roots (preface, 17 chapters, and the
queued bridge unit), 686 relations, and 19 compact search records. It binds the
public `/output/html/bab-NN/index.html` routes proven by the owner deployment,
records absent/short-route failures explicitly, and never emits a nonexistent
`/bab-NN/` learner URL or copies textbook prose.
