# Universal reader navigation

The program treats navigation as a graph, not as a list of unrelated downloads.

For every course and every supported interface language, the central course card distinguishes three destinations:

1. a live program-hosted reader, when one exists;
2. an offline or preservation copy, when one exists; and
3. the authoritative author, publisher, or project source.

Every program-controlled HTML document links back to the same course in both current interfaces:

- [Bahasa Indonesia](https://kokunoyumeto.github.io/program-matematika-indonesia/id/)
- [English](https://kokunoyumeto.github.io/program-matematika-indonesia/en/)

It also links to every authoritative original bound to that course. A reader therefore never becomes a dead end, while a mirror never obscures where the material came from.

## Language namespaces

Current interface routes are `/id/` and `/en/`. Future interfaces use sibling `/{language_id}/` routes with stable BCP 47-compatible language identifiers. Course IDs and resource identities do not change when another language is added.

Interface language, content language, source language, edition, format, rights, and offline capability remain independent fields. An English interface may accurately point to Indonesian content, and a downloadable HTML file is not presented as a live site merely because its filename ends in `.html`.

## Current verified rollout

As of 2026-09-06:

- 42,255 live GitHub Pages HTML documents across 25 repositories carry the reciprocal navigation contract;
- 23 distinct course roles are represented in those repositories;
- all 28 currently selected off-origin learner entrypoints return HTTP 200 and satisfy the central and authoritative-original link contract;
- D90 and D100 preserve 21 additional navigable HTML documents on Zenodo as offline copies; and
- D90 and D100 use GitHub Pages, rather than Zenodo's `text/plain` delivery, as their live browser readers.

The large HTML count includes chapter pages, generated knowls, and other addressable learner documents; it is a document count, not a textbook page count.

The machine-verifiable rollout record is [`backend/authority/federated-navigation-publications/universal-reader-navigation-rollout-20260906.json`](backend/authority/federated-navigation-publications/universal-reader-navigation-rollout-20260906.json). The normative contract is [`backend/authority/universal-reader-navigation-contract-v1.json`](backend/authority/universal-reader-navigation-contract-v1.json).

## Validation rule

A live reader is admitted only when anonymous HTTP access works and each declared navigation placement contains exactly one accessible landmark. A top landmark is mandatory; a matching bottom landmark is allowed and encouraged for long documents. Every such landmark contains:

- the course anchor in every currently supported central interface language; and
- every authoritative-original URL registered for that course.

The course and original targets are absolute HTTPS links, so a copied or downloaded page still knows where to return when connectivity is available. Relative links are reserved for lineage-local contents and next/previous navigation whose portability depends on the surrounding folder.

Each repository retains its own deterministic and idempotent postprocessor because its HTML generator and source layout may differ. The global backend validates the common semantic relationship; the repository receipt binds the concrete marker, source revision, file inventory, deployment, and byte identities.

PDF and EPUB downloads remain discoverable from the central course. Newly generated editions should embed the same routes, but historical immutable releases are not silently rewritten merely to add navigation.
