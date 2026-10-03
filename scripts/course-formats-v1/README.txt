OFFLINE COURSE FORMAT TOOLS - VERSION 1

This tool connects existing, source-bound PDF/LaTeX/ZIP/EPUB editions to a
readable offline directory. It does not translate a course, create an EPUB,
compile LaTeX, execute code from source archives, contact a server, or publish.
It preserves the producer's native structure and exact released-format bytes.

OpenAI Codex - GPT-6 Astra, Ultra effort: intake validation, offline navigation,
tests and documentation. Original course authorship, component licences and
AI provenance remain with each course. Software licence: included MIT LICENSE.

REQUIREMENTS
Python 3.11 or later with pypdf and lxml. Tested with pypdf 6.12.2 and lxml 6.1.1.
The optional headless browser check needs Node.js, Playwright and Chromium.
No content is downloaded by the tool. Install dependencies separately if needed.

USE FROM THE EXTRACTED TOOL ARCHIVE
python -B scripts/course-formats-v1/course_formats.py LOCAL_INTAKE --reader NEW_READER_DIRECTORY --report NEW_PRIVATE_RECEIPT.json

LOCAL_INTAKE must contain a programme-course-format-handoff/1 or /2 HANDOFF.json,
its exact referenced receipt, source manifest, locator sidecar, evidence files,
native source payloads and four format files. Sources use course-format-source/2.
Source ZIP inventory uses course-editable-source-closure/1. Locator schemas are
native-course-format-entry-locators/1 or course-format-locator-index/1. Other
native contracts need an explicit adapter; do not relabel incompatible files.
The public core-course download catalogue is not itself an intake manifest.

Without --reader and --report the command validates without writing. New output
paths must not exist. The reader output must be separate from the producer
directory. A failure never deletes or changes producer files. An incomplete new
output after an I/O failure is not a validated edition; inspect it before retry.

Open NEW_READER_DIRECTORY/index.html in a browser. English and Bahasa Indonesia
interfaces contain direct downloads in this order: PDF, cumulative editable
LaTeX, complete source ZIP, EPUB. Each lesson links to its PDF page. Supplied
native locations also have named-destination PDF links and page fallbacks.
Open the EPUB in a compatible reading app; internal member/fragment locations
are recorded honestly rather than presented as browser EPUB deep links.

Language switching changes navigation, not the course text. Original lesson
titles, credits and legal notices stay in their declared content language.
Editorial supplements remain distinct from lessons. Source drafting/admission
states and private/public status are not upgraded by successful formatting.

CHECKS AND LIMITS
The tool independently checks file sizes and SHA-256 hashes, the exact ZIP
inventory, all declared source payloads, direct-TeX/archive identity, actual
PDF pages and named destinations, EPUB language/spine/navigation/fragments,
local links, and native locations where supplied. It rejects archive path
escapes, duplicate/case-colliding files, non-regular entries, duplicate JSON
keys, XML entities, scripts, and unsafe links. It does not extract or run ZIP
source scripts. These checks are not a sandbox for arbitrary executable content.

If output/FORMULA_INDEX.json exists, the ordered EPUB formula annotations are
compared with that supplied ledger, ignoring whitespace only. Navigation
headings repeated in the EPUB table of contents are counted separately. This
is not a fresh source-text-to-formula parse or an independent mathematical
proof. Source ZIP completeness here means verified declared payload closure;
successful rebuild, mathematical correctness and visual accessibility require
their own evidence. The report explicitly records those checks as not run.

Untagged PDFs and empty PDF title metadata are reported. Passing EPUB structure
checks does not certify screen-reader performance. Run EPUBCheck independently
and inspect actual PDF/EPUB rendering before declaring a new edition ready.

TEST
python -B scripts/course-formats-v1/test_course_formats.py -v
python -B scripts/course-formats-v1/test_course_formats.py --intake LOCAL_INTAKE -v

Optional browser checks:
node scripts/course-formats-v1/check_reader.mjs NEW_READER_DIRECTORY QA_DIRECTORY
Set COURSE_PLAYWRIGHT_MODULE and COURSE_CHROMIUM if those dependencies are not
on the usual lookup paths. This uses a separate headless browser, blocks remote
requests, checks both interfaces at 1280/390/320 pixels, and writes screenshots
and a bounded QA receipt. For the first locator schema, optional third/fourth
arguments are an already safely extracted EPUB and FORMAT_ENTRY_LOCATORS.json.
For the second schema, use the generated receipt's entry_routes as a locators
array when preparing that optional geometry input; do not discard native IDs.

PRIVACY AND REUSE
Generated readers and reports inherit their input's access boundary. A private
course stays local: putting its files into a new directory is not publication
permission. The distributed toolkit contains no courses or private intake data.
The same reader directory is portable to static hosting only when publication
of its exact edition is already authorized. Local validation is not public
download verification and does not change the programme's completion census.
