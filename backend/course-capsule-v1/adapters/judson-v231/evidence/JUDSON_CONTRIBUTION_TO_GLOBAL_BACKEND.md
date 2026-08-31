# Judson: one native corpus, two navigable courses

Evidence snapshot: 31 August 2026. This is a validated integration candidate,
not an admitted central adapter or a claim that the public landing page already
consumes it. The published native Indonesian edition remains authoritative.

## What this adds to the distributed-backend workflow

The program's working method lets corpus tasks develop native solutions, compares
the resulting implementations, and carries useful patterns into a common layer.
Judson supplies a concrete example of why that layer should preserve native
structure rather than replace it. Its existing graph already separates one book
into two coherent courses. The common adapter retains that distinction and joins
it to actual chapter pages.

This is engineering evidence from one implementation, not a controlled comparison
proving one universal optimum. It adds to the existing comparative findings and
does not replace the native backends or the published methodology.

| Native pattern | Common representation | Learner consequence |
| --- | --- | --- |
| One graph with two course selectors | 3,323 unit rows once; 23 chapter memberships; separate C30/C40 views | Choose the course and see its own ordered chapters without two copies of the book |
| Stable IDs and birth/current source selectors | Exact native IDs plus deterministic projection IDs and 3,323 identity mappings | A language or source-layout revision need not break the identity of a learning unit |
| Typed mathematical relationships | All 6,505 edges, including hints, responses, references, assets and prerequisites | Future interfaces can navigate the relationships actually present; no missing solutions are invented |
| Explicit segment disposition | 4,150 translated and 316 intentionally source-frozen pairs | Names, bibliography entries, code labels and authoritative license text are not mistaken for untranslated omissions |
| Native publication and HTML witnesses | 23 actual chapter routes, frozen WEB archive hashes, dated live observations | Students can open a chapter online or use the preserved downloadable HTML edition |
| Exact evidence and reusable serialization | Unchanged common 2.3.1 contracts, 19 JSONL/CSV table pairs | Other tools can select units without depending on this conversation or parsing a PDF |

C30 has 15 selected chapters and 2,014 units in their descendant closure. C40 has
8 chapters and 1,279 units. Another 30 corpus-support units remain outside both
course selectors. They are preserved, not silently forced into a course. Course
selection does not duplicate any canonical unit.

## Student-facing implementation contract

The central learner interface should consume `course-views.json`, join each
chapter's `route_id` to `tables/routes.jsonl`, and present its Indonesian title
and native course sequence. The student-facing action is a chapter link, not a
JSON download. Keep technical exports available separately for reuse.

For each course, the resulting interaction is:

1. Select Aljabar Abstrak I (C30) or Aljabar Abstrak II (C40).
2. Choose one of that course's 15 or 8 ordered chapters.
3. Open the chapter online, or download the frozen WEB ZIP and open its exact
   relative HTML filename after extracting the full archive with its assets.

The routes are real entries from the preserved WEB package and its actual table
of contents, with matching chapter IDs and Indonesian headings. No descendant
fragment anchor was guessed. Chapter routing does not yet imply exercise-level
navigation, mastery tracking, an executable exercise engine, or curriculum-wide
learner-runtime integration.

All 23 live URLs responded HTTP 200 during the recorded checks. None had the
same bytes as the frozen 2026.08.22.2 HTML. Preserve the distinction: the online
site is accessible, but this audit has not established equivalence to the frozen
edition. Do not label the differing bytes an access failure or silently present
them as the frozen version. Suggested student labels are already in the route
handoff: an online chapter action with a version caveat, and a preserved offline
edition download. There were no browser windows or tabs involved in these checks.

## Evidence and limits

The native source/backend archive is public at [Zenodo record 22062449](https://zenodo.org/records/22062449).
Its SOURCE_BACKEND ZIP is 69,370,499 bytes, SHA-256
`0aa85116679703b632333f4003b3373f42bb7b282c3719bea3731257c0fe55e0`.
Its separate WEB ZIP is 27,339,920 bytes, SHA-256
`cb27ec5671b7e2378da0754a607125b43367ba6eca473d3dc11afd307313a7c1`.

The native replay ran the published topology verifier, backend builder, builder
check and strict backend verifier in an isolated copy. All four passed and all
416 original archive files remained byte-identical. This is backend replay, not
a new reader render, new mathematical or language review, or Sage execution.

The common candidate contains 17,745 records. Its two independently generated
65-file trees are byte-identical. The unchanged generic validator checks all
40 declared authority facts, all 19 JSONL/CSV pairs and six schemas. Root-owned
tests additionally check native semantic mappings and reject 16 deliberate
identity, course, relation, translation-state, rights, capability and route
mutations. Two separate fail-closed input tests cover a synthetic wrong-digest
archive and an absent required central contract without copying another archive.

Reference-assisted inverse tests recover seven selected native metadata streams
byte-for-byte using the exact archive and projected row witnesses. This is not
standalone reconstruction after deleting the native archive. Full prose, formula
XML, executable Sage cells and richer native capability shards remain native.

Only structure/localization metadata is declared materialized. Eight other
capabilities are explicitly native-shard references; accessibility is not
projected by this candidate. These limits are not assertions that native courses
lack those features. GFDL-1.2-or-later upstream rights, GFDL-1.3-or-later modified
edition rights and operative English license text remain distinct.

## Integration and preservation boundary

Use `build-a-routes2` as the final candidate payload and `build-b-routes2` as its
byte-identical replay witness. Older preliminary builds are not admission inputs.
Bind the independent semantic, route, replay-boundary, native replay and generic
validation receipts before admission. Add the student chapter selector to the
existing central interface, test that actual interface, then preserve the package,
these findings and the integration receipts in the existing central release/DOI
lineage. Do not create a replacement corpus owner or a second publication lane.

The manager's final handoff identifies every accepted input by bytes and SHA-256.
The central integrator alone edits the shared hub and publishes. Until its
integration and public readback are proved, this remains a validated candidate,
not a sixth globally admitted adapter or an implemented learner feature.

Prepared by Codex on instructions of the user; original author, translator and
native contributor credits remain in the preserved native edition.
