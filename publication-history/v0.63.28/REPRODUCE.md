# Precalculus in English: online reader and offline program

Read the [complete English book](https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/A30/reader/) or return to the [mathematics program](https://kokunoyumeto.github.io/program-matematika-indonesia/en/#course-A30). The [original OpenStax website](https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions) remains the publisher's authoritative presentation.

The English text is the original work by Jay Abramson, OpenStax, and credited contributors, not a new translation. The mirror preserves all 87 selected modules, original MathML, 7,250 exercises, 4,183 source-provided solutions, figures and source IDs. Its rights and component-credit disclosures accompany the reader. No publisher endorsement or human accessibility certification is claimed.

## Read without an internet connection

Download the standalone book or expanded program from the [v0.63.28 release](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.63.28). Extract the complete ZIP and open `START-HERE.html`. Included text, mathematics, styles and images work locally. External websites remain external; some program tools require a local HTTP server. The expanded program includes the standalone original-source package under `original-sources/`.

## Reproduce the book

The standalone ZIP includes the exact original CNXML, source manifests, credited assets, rendering scripts, frozen rendering library, component-rights evidence, and validation receipts. Follow its `REPRODUCE.md` for the exact local layout and commands. The authority revision is `789b54099106b071d1d32bfcee454fed72eb4768` of `openstax/osbooks-college-algebra-bundle`.

The deterministic reader replay compares every generated payload byte. The independent final-byte review covers prose, MathML, IDs, exercise/solution ancestry, table/list structure and navigation. Static checks are not a claim of browser, screen-reader, or expert certification.

## Reproduce the expanded program ZIP

Use a checkout containing source commit `818dafebc973a6eff1330fcf6be86db8400192fd` and its history. Obtain the predecessor navigator from v0.63.27 and the standalone A30 package from v0.63.28. With Python 3.11 or later and Git available:

```sh
python -B publication-history/v0.63.28/prepare_navigator_v06328_20260908.py --repo . --predecessor /path/to/peta-belajar-multilingual-v0.63.27.zip --a30-package /path/to/A30-Precalculus-2e-original-English-reader-source-v1.zip --output /new/path/peta-belajar-multilingual-v0.63.28.zip --v27-helper publication-history/v0.63.27/prepare_navigator_v06327_20260908.py
```

The builder checks frozen input hashes, every inherited member, exact Git blobs, unique safe paths, per-file output hashes and CRC. It retains all 6,231 predecessor members. `PORTABLE_PROJECTION.json` identifies the single reversible navigation addition to each of 439 HTML documents; the mathematical bodies are unchanged. The older helper supplies only its portable resolver and start-page template; its standalone historical entry point is not run.

For additional final-byte and URL-resolver checks, place the generated ZIP and supplied `NAVIGATOR_V06328_LOCAL_RECEIPT.json` together and run:

```sh
python -B publication-history/v0.63.28/validate_navigator_v06328_20260908.py --artifacts /path/to/that/folder
```

This additional check uses Node.js, not a browser. Compression-library versions can affect ZIP byte identity; retain the recorded Python/zlib versions for compressed-byte comparison. Member identities and source bindings are the underlying reproducibility evidence. No second full navigator generation or new independent review of a user's rebuild is claimed.

The whole program remains unfinished: this publication does not claim complete original-language mirroring or full native-backend capability parity.
