# Mathematics Library integration

This additive directory connects the existing study programs and independently
identified editions. It does not replace course readers, select a new course
canon, or certify the mathematical completeness of linked works.

Only four sealed R2 assets are deployed under `docs/library/`. Their exact byte
identities, the intake receipt identity and the source/QA inventory are recorded
in `backend/authority/library-handoff-v1.json`. The source/QA ZIP beside this
file preserves the registry, template, generator, stylesheet, browser script
and producer QA. Unzip it into a separate directory and run
`node scripts/validate.mjs` to replay the original generation check. To edit
that source, change its registry/template and run `node scripts/build.mjs`.
Do not edit generated deployed files without issuing a new verified handoff.

Run `python -B scripts/library-handoff-v1.py --self-test` from the program
repository to check the exact deployed assets, source/QA archive, static
catalogue, bilingual return landmarks and negative navigation fixtures.
The whole-site navigation validator invokes this check. The Library supplies
its own top/bottom English and Indonesian program returns, so an additional
central navigation overlay is neither required nor injected.

## Integration browser checks, 2026-09-21

Checked the actual staged `/library/index.html` in a hidden browser. Thirteen
entries render; the Indonesian filter returns the program interface alone and
points to the existing `/id/` route. The development filter returns four draft
courses. An unmatched search displays zero results and the recovery button;
recovery restores all thirteen entries. The Library-home link returns to the
actual index, not a directory. Desktop visual inspection found legible text,
controls and navigation without clipping. The sealed producer QA separately
records mobile widths, keyboard skip link and no-JavaScript checks; those are
producer evidence, not newly repeated integration checks.

No book text is copied, no unpublished reader URL is invented, and interface
language is not misrepresented as the content language of every linked work.
Publication/readback is tracked separately from these local checks.

## Reciprocal program navigation

The program generator places a localized Library link in the header and footer
of both language interfaces and their standalone/paired offline maps. The root
language chooser also links the Library. These are online navigation links;
offline maps do not pretend to contain the Library or linked books.

`node scripts/test-library-navigation-v1.mjs` verifies all six localized
documents and the root chooser, including twelve rejected broken-link fixtures.
The regular multilingual-interface test suite runs it automatically.

The integration check also found and fixed an existing narrow-screen grid
minimum-width defect. With the final stylesheet, Indonesian online cards and
the English offline map have no horizontal overflow at 320/390-pixel viewport
settings. Versioned stylesheet URLs prevent an older cached stylesheet from
concealing the fix. This is a bounded navigation/layout check, not blanket
accessibility certification.
