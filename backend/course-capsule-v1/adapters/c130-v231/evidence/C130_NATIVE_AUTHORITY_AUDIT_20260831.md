# C130 owner-native authority audit — 2026-08-31

## Owner and publication identity

- Owner root: `04_mirrors/id/open-optimization-or-book-id`.
- Frozen upstream commit: `1745df89b608899f66983834fa4ec8c8910d18ff`.
- Frozen upstream tree: `209d5de696ebac4e5921b73d6b6b2f539fc23d1c`.
- Frozen upstream archive SHA-256:
  `4bee88ed3af700b16d5643a3c18b9846244d3467eec7f4fb1f009a782b9143fc`.
- Public GitHub commit:
  `a639b69cf84c4d4f60f7dcdb62dbeb5cfb153adc`.
- Public GitHub tree:
  `1ab559b3540d9362bc0333caf017acd9fe540a9c`.
- Repository: `https://github.com/KokunoYumeto/open-optimization-or-book-id`.
- Learner landing page:
  `https://kokunoyumeto.github.io/open-optimization-or-book-id/`.
- Zenodo version DOI: `10.5281/zenodo.22070653`.
- Zenodo concept DOI: `10.5281/zenodo.22059794`.

The edition is complete. Its 666-page PDF is 26,425,739 bytes with SHA-256
`daa9b79df3684729cc204b563669f400866d8fbd12c0977d32ff9897276a7a49`.
The Pages index is a learner-facing landing page, 8,184 bytes, SHA-256
`69f434663726dfcda90043e92ac6df5eb495c4226d71abf860389f6bd5535651`.
It embeds or links the reader but is not native chapter HTML and supplies no
unit or page anchors.

## Frozen backend

- `backend/dist/backend-v0.json`: 26,022,240 bytes, SHA-256
  `7c2ec930a7472021b37101f860b2b1846503fd52f4b495f863508cd91d741804`.
- `backend/dist/manifest.json`: 4,853 bytes, SHA-256
  `f800590f07fafa47c7eb900dddc8cf99bbf5cb892218fa4ab1722677b7b2efa4`.
- `backend/dist/SHA256SUMS.txt`: 2,623 bytes, SHA-256
  `1dabfdb58c910fc5c1e659356361c51056c6084a214f7b20583a42e9750e6515`.

The monolith contains 17,987 records across the owner projections:

| Projection | Count |
|---|---:|
| programs | 1 |
| courses | 1 |
| resources | 4 |
| editions | 5 |
| units | 1,993 |
| segments | 5,525 |
| concepts | 128 |
| terms | 140 |
| assets | 346 |
| rights | 21 |
| corrections | 94 |
| qa_events | 101 |
| artifacts | 83 |
| relations | 9,545 |

The JSONL tables and monolith agree, the owner-native identifiers are unique,
and the owner manifest/checksum inventory closes. All 1,993 units are part of
the edition topology, including the paired `mul` source/target units; therefore
filtering units by target locale would destroy the owner topology.

Segment states are 2,293 `translation`, 2,884
`translation_target_projection`, 9 `target_native_correction`, and 339
`locally_authored_adaptation`. Relations are typed owner evidence and all 9,545
must be retained, not reduced to prerequisite edges. The 21 rights records bind
different components; primary content is CC BY-SA 4.0 while code and third-party
components have their own licenses.

## Publication evidence

The public release has 13 files totaling 53,594,467 bytes. The GitHub receipt
binds a 528-file tree and the release assets/Pages downloads. The Zenodo receipt
records anonymous byte-and-hash readback for the 13-file inventory. The current
source, backend, and labs ZIP SHA-256 values are respectively
`55d62c...`, `7cd763...`, and `99628d...`; exact full values must be taken from
the live release manifest and receipts during the adapter build rather than
expanded from abbreviated notes.

## Known metadata lag

`00_control/CURRENT_CURSOR.json` is 5,676 bytes, SHA-256
`a79969903d29a26872c78d1dd573aabdeefff9c08720e7a99dc5b7d8f0499f1c`.
It retains an older `qa/release-package-report.json` digest, while the current
live report is 5,130 bytes, SHA-256
`ae2e905782c099db7d1c177255fbbc6f07146caa2c3cacf2293498cdac3b308f`
and is corroborated by the later GitHub plan and receipt. The cursor also says
there is no upstream issue although a later receipt records issue #3. These are
disclosed control-metadata lags; this adapter does not rewrite owner controls.

## Adapter consequences

The common projection is zero-copy. It binds paths, bytes, SHA-256 identities,
line spans, locales, states, rights, topology, artifacts, and learner routes. It
does not embed textbook prose, remint owner IDs, claim aggregate-program
conformance, substitute JSON for a learner reader, claim native chapter HTML,
or claim PDF/UA conformance.
