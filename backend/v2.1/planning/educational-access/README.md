# Educational-access planning projection

This zero-prose package makes the educational-access research workflow usable by
the modular curriculum backend. It is an exact-hash-bound projection of the
research dossier, not a replacement for that dossier and not a claim about
observed learning outcomes or account usage.

`authority_snapshot.json` is the minimal replay closure kept with this package:
the six planning tables used by the adapter, exact identities of all nine
upstream dossier files, and only the ten asset/evidence-register rows actually
referenced by those tables. A checkout beside the research dossier regenerates
and compares that snapshot; a standalone source release rebuilds from the same
repo-local frozen rows without requiring unrelated workspace state.

It adds four planning dimensions that course-only records cannot express:

- 29 source curriculum units and 13 cumulative curriculum portfolios;
- five adaptation depths from terminology infrastructure (D0) through local
  pedagogical adaptation (D4);
- eight independently selectable accessibility derivatives, including semantic
  HTML/MathML, tagged PDF, offline delivery, figure remediation, narration, and
  plain-language companions; and
- 12 compute assumptions plus three source-versioned low/base/high scenarios.

The portfolio graph has 10 explicit prerequisite edges. The fixed comparator
for the current access model is FR-2/D3: 210 formal-reasoning units and 120,083
measured source alpha tokens. Population/ranking evidence stays in the research
dossier; the central mathematics release publishes only the curriculum-planning
contract and its source bindings.

Rebuild and validate:

```powershell
python -B scripts/build-educational-access-planning-v21.py
python -B scripts/validate-educational-access-planning-v21.py
```
