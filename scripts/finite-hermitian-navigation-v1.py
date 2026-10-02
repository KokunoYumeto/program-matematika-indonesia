"""Validate the sealed Hermitian reader's native, reciprocal navigation.

This checks delivery and byte identities, not independent mathematical review.
The existing reader is left unchanged: its manifest and proof locators bind it.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "docs/en/readers/finite-hermitian-spaces/"
DOCUMENT = PREFIX + "index.html"
ORIGIN = "https://kokunoyumeto.github.io/program-matematika-indonesia/"
PUBLIC = ORIGIN + PREFIX.removeprefix("docs/")
ANCHORS = (
    "gramschmidt-with-the-coefficients-in-the-correct-order",
    "orthogonal-projection-and-decomposition",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.locale = None
        self.ids = []
        self.hrefs = []
        self.programme_navs = []
        self.active_nav = None
        self.math_count = 0
        self.overlays = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.locale = values.get("lang")
        if "id" in values:
            self.ids.append(values["id"])
        if tag == "math":
            self.math_count += 1
        if tag == "nav":
            if "data-central-surface-navigation" in values:
                self.overlays += 1
            if values.get("aria-label") == "Programme navigation":
                self.active_nav = []
                self.programme_navs.append(self.active_nav)
        if tag == "a" and "href" in values:
            self.hrefs.append(values["href"])
            if self.active_nav is not None:
                self.active_nav.append(values["href"])

    def handle_endtag(self, tag):
        if tag == "nav":
            self.active_nav = None


def parse(raw):
    page = Page()
    page.feed(raw.decode("utf-8"))
    page.close()
    return page


def validate(root=ROOT):
    directory = root / PREFIX
    manifest = json.loads((directory / "READER_MANIFEST.json").read_bytes())
    require(manifest["schema"] == "finite-hermitian-reader/1", "Wrong reader manifest")
    require(manifest["language"] == "en", "Wrong manifest language")
    require(manifest["independent_review"] is False and manifest["whole_course_verified"] is False,
            "Navigation validation cannot grant mathematical completion")
    require(manifest["formula_count"] == 144, "Unexpected formula scope")
    required = {"index.html", "finite-hermitian-spaces.md", "SOURCE_REVIEW.json",
                "00-finite-hermitian.tex", "01-editable-source.zip", "README.md", "BUILD_INPUTS.json"}
    rows = manifest["files"]
    require(len(rows) == len(required) and {row["path"] for row in rows} == required,
            "Reader/source file inventory changed")
    files = {}
    for row in rows:
        # The fixed inventory excludes path escapes and unrelated documents.
        raw = (directory / row["path"]).read_bytes()
        require(len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"],
                "Sealed Hermitian file changed: " + row["path"])
        files[row["path"]] = raw
    require(hashlib.sha256(files["finite-hermitian-spaces.md"]).hexdigest() == manifest["source_sha256"],
            "Reader source identity disagrees with manifest")
    reader = parse(files["index.html"])
    require(reader.locale == "en" and reader.overlays == 0, "Native reader locale/overlay changed")
    require(reader.math_count == 144, "Rendered formula count changed")
    for anchor in ANCHORS:
        require(reader.ids.count(anchor) == 1, "Missing or duplicate native proof anchor: " + anchor)
    returns = {
        ORIGIN + "en/programme/#core-B40",
        ORIGIN + "en/programme/#advanced-RT-FIN",
        ORIGIN + "id/programme/#core-B40",
    }
    require(len(reader.programme_navs) == 2, "Reader requires native top and bottom navigation")
    for nav in reader.programme_navs:
        require({urljoin(PUBLIC, href) for href in nav} == returns and len(nav) == 3,
                "Native programme returns changed")
    for source in ("00-finite-hermitian.tex", "01-editable-source.zip"):
        require(PUBLIC + source in {urljoin(PUBLIC, href) for href in reader.hrefs},
                "Missing editable source download: " + source)
    for locale in ("en", "id"):
        hub = parse((root / "docs" / locale / "programme/index.html").read_bytes())
        require(hub.ids.count("core-B40") == 1 and hub.ids.count("advanced-RT-FIN") == 1,
                "Programme return destination missing or duplicated: " + locale)
        links = {urljoin(ORIGIN + locale + "/programme/", href) for href in hub.hrefs}
        require(all(PUBLIC + "#" + anchor in links for anchor in ANCHORS),
                "Programme no longer links back to Hermitian proofs: " + locale)
    return {"schema": "finite-hermitian-native-navigation/1", "state": "pass",
            "files": [{"document": DOCUMENT, "bytes": len(files["index.html"]),
                       "sha256": hashlib.sha256(files["index.html"]).hexdigest()}],
            "html_documents": 1, "source_files_verified": len(rows),
            "reciprocal_programme_locales": ["en", "id"],
            "proof_anchors": list(ANCHORS), "native_reader_changed": False,
            "independent_mathematical_review": False}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
