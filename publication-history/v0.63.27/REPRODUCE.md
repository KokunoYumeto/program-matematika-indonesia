# Reproducing the portable program bundle

This directory preserves the executed builder, navigation tests, and readback evidence. It does not contain credentials or replace corpus-owner sources.

Recreate this small directory layout in a new working directory:

```text
d100-capability-v1-worktree/     checkout of source commit below
curriculum_logbook/
  prepare_navigator_v06327_20260908.py
  test_portable_navigation_v06327_20260908.py
  central-v0.63.26-candidate/
    peta-belajar-multilingual-v0.63.26.zip
  central-a10-reader-20260908/   empty output directory
```

Use the public central repository at commit `a593c3b32eea860c3f1a7d7009093cc4ca2c17d4`, including history through `4cfcc7e106ce1e99bbd0a7260a297d878a793c5a`. Download the predecessor navigator from [Zenodo version 0.63.26](https://zenodo.org/records/22649718); the builder verifies its SHA-256 before reading any members. Copy the two scripts from this directory into the indicated layout.

Run the builder with Python, then the navigation test with Python and Node.js. The builder creates two archives, compares their byte identities, verifies every checksum and predecessor member name, and removes only its temporary second replay. Runtime versions are recorded in the current publication receipt. No network access, corpus-owner edits, or publication occurs during reconstruction.

`PORTABLE_PROJECTION.json` inside the resulting ZIP distinguishes exact committed source HTML from its offline projection. Removing the one appended navigation script restores the committed HTML byte-for-byte. Author text, mathematics, figures and source links are preserved. The additional script maps only exact packaged program paths; publishers and unavailable resources stay online. The three documented claim-boundary aliases copy exact source bytes.

The public A10 reader has a separately documented reversible navigation layer. Its online and offline identities are intentionally different, not interchangeable source hashes. Neither this bundle nor the 40-role common adapter layer establishes complete native-backend capability parity; the current verified count is 14 of 40 roles.
