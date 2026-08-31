# Post-completion native-Indonesian terminology QA

Date: 2026-08-31  
Witness: *Teori Bilangan* (UPP FKIP Universitas Bengkulu, 2021), ISBN 978-623-7074-62-5  
Record: https://repository.unib.ac.id/id/eprint/12240/  
PDF: https://repository.unib.ac.id/12240/1/Buku%20Teori%20Bilangan%20B5%20%28versi%20Cetak%29.pdf

## Outcome

The witness supports the present choices `pertidaksamaan`, `nilai mutlak`,
`linear`, `bilangan real/riil`, `relatif prima`/`saling prima`, `koefisien`,
`derajat`, and the standard modulo vocabulary. It is not a reliable
prescriptive authority: it repeatedly varies between competing forms and
contains several mathematical and editorial errors. Decisions therefore use it
as a usage witness, not as a replacement corpus or a source of prose.

No source paragraph was copied. Only short terminology strings and page-level
citations were recorded.

Two D100 changes are supported strongly enough for canonical consideration:

1. `domain integral` -> `daerah integral`.
2. `kelas sisa` -> `kelas residu` in the quotient-ring context.

The first is independently attested in university abstract-algebra texts; the
second is used by the UNIB witness for residue terminology and explicitly in a
Universitas Hasanuddin quotient-ring definition. The delivered D100 helper
packet was not silently changed because its terminology hash, QA seal, and
manager-delivery receipt are terminal. The exact occurrences and evidence are
in `terminology_concordance.json` for deterministic owner-side integration.

The following D100 wording should be reconsidered together with the canonical
glossary, not by isolated substitution: `perluasan gelanggang integral`,
`homomorfisme gelanggang integral`, and the coined phrase `persamaan
keintegralan`. The lecture already uses the cleaner `perluasan integral`, but
the available witness does not cover all three abstract-algebra concepts well
enough to justify an uncoordinated post-seal rewrite.

The collision-stopped A10 packet was read only. Its core vocabulary is sound,
but the manager should normalize the following before canonical integration:

- reserve `grafik garis` for a statistical line chart; use `grafik persamaan
  linear` or `grafik suatu garis` for an algebraic line;
- use `ruas`, not `sisi`, for the two sides of an equation;
- distinguish a point of intersection (`titik potong`) from its scalar
  coordinate/value;
- define the m82488 concept as `pertidaksamaan linear dua variabel`;
- normalize `sumbu-y` to the glossary form `sumbu y`;
- remove or recast the English-only wordplay in m82480 line 275.

## Page convention

The PDF has 255 physical pages. Numbered body page 1 is physical PDF page 9,
so for the numbered body `physical page = printed page + 8` through printed
page 247. Both numbers are recorded.

## Rights boundary

The repository page labels the file "Creative Commons GNU GPL (Software)", but
PDF physical page 3 says Copyright 2021, "All right reserved", and prohibits
translation, photocopying, or reproduction without written permission. Because
those notices conflict, this packet treats the PDF only as a terminology
witness and copies no substantive prose.

## Source integrity

- PDF bytes: 3,105,284
- PDF SHA-256: `f3cd2697e4fabecb6f37ccfe00ada6e5a5a0b89f857daec88d1b483040ec3cf1`
- Retrieved: 2026-08-31T15:27:56Z
- HTTP ETag: `490f907e22a9ebb4256f2f2c8ef4b74e`
- HTTP Last-Modified: 2023-06-19T04:09:36Z

## Known witness defects affecting authority weight

- physical 9 / printed 1: `BILANGANAN REAL` and `IRRASIONAL`;
- physical 14 / printed 6: rational numbers are mislabeled with symbol `Z`;
- physical 75 / printed 67: a false claim says a nonzero integer has
  infinitely many divisors;
- physical 148 / printed 140: the modular-inverse computation and displayed
  verification disagree;
- physical 149 / printed 141: `PBB(9,11)=2` and the resulting inverse are
  false;
- terminology varies among `ketaksamaan`, `pertidaksamaan`, and misspellings;
  among `linear`, `linier`, and `lanjar`; and among several GCD, coprime, and
  modular-inverse labels.

The machine-readable record contains the complete cited decision set and the
non-applied manager patch queue.
