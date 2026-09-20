# D60 browser checks — 2026-09-21

Tested the generated English teaching view in a hidden in-app browser against
the task-local preview. Search `capstone-ex` returned six exercises; selecting
the visible page showed six selected units and enabled export. Expanding the
first exercise's support disclosure exposed its exact hint and solution links.
The screenshot was visually inspected: controls, counts and links were legible.

The actual JSON download was read from disk and compared structurally with the
plan built independently from those six IDs. It contained six selected units
and twelve supporting units. Size: 44,356 bytes; SHA-256:
`aabdaefe39df16072cd74749bae48d66f8bd58aa8729dc050fd7ec45a32f6224`.
The browser download-event observer timed out, but the file itself was present
and verified; no second download was submitted.

Clearing selection showed zero units. Clearing the search through keyboard
selection and Backspace restored 278 practice units. Next page showed 41–80 / 278.
The language switch opened the Indonesian teaching page, with the expected
heading and initial 1–40 / 278 range. Captured browser warning/error list: empty.

This is a functional desktop-browser check, not a blanket accessibility or
mobile certification. Mathematical content was not translated or revised.
The common navigation shell is applied separately and preserves source bodies.
