#!/usr/bin/env python3
"""Verify every public HTML edge in the central reader-navigation contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import (
    HTTPRedirectHandler,
    HTTPSHandler,
    ProxyHandler,
    Request,
    build_opener,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "backend" / "authority" / "central-reader-navigation-v1.json"
LOCAL_VALIDATOR = ROOT / "scripts" / "validate-central-reader-navigation-v1.py"
DEFAULT_RECEIPT = ROOT / "docs" / "data" / "CENTRAL_READER_NAVIGATION_PUBLIC_READBACK_V1.json"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


class NavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.navigation_markers = 0
        self.surface_navigation_markers = 0
        self.home_links: list[dict[str, str]] = []
        self.contents_links: list[dict[str, str]] = []
        self.surface_contents_links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "nav" and values.get("data-program-navigation") == "v1":
            self.navigation_markers += 1
        if tag.lower() == "nav" and values.get("data-central-surface-navigation") == "v1":
            self.surface_navigation_markers += 1
        if tag.lower() != "a":
            return
        row = {
            "href": values.get("href", ""),
            "course_id": values.get("data-course-id", ""),
        }
        if "data-program-home" in values:
            self.home_links.append(row)
        if "data-reader-contents" in values:
            self.contents_links.append(row)
        if "data-course-surface-contents" in values:
            self.surface_contents_links.append(row)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_fact(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
    }


def configured_html(root: Path, exclusions: list[str] | None = None) -> list[Path]:
    excluded = {
        (root / Path(*value.split("/"))).resolve() for value in (exclusions or [])
    }
    rows: list[Path] = []
    for path in sorted(root.rglob("*.html"), key=lambda item: item.as_posix()):
        resolved = path.resolve()
        if any(resolved == item or resolved.is_relative_to(item) for item in excluded):
            continue
        rows.append(path)
    return rows


def public_url_for_document(path: Path, site_origin: str) -> str:
    logical = path.relative_to(ROOT / "docs").as_posix()
    if logical == "index.html":
        logical = ""
    elif logical.endswith("/index.html"):
        logical = logical[: -len("index.html")]
    escaped = "/".join(quote(part, safe="") for part in logical.split("/"))
    return urljoin(site_origin, escaped)


def canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    path = parsed.path
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.fragment))


def cache_busted(url: str, commit: str, digest: str) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}navv1={quote(commit[:16] + '-' + digest[:16], safe='')}"


def fetch_once(url: str, timeout: int) -> tuple[int, str, str, bytes]:
    opener = build_opener(
        ProxyHandler({}),
        NoRedirect(),
        HTTPSHandler(context=ssl.create_default_context()),
    )
    request = Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "identity",
            "Connection": "close",
            "User-Agent": "program-matematika-central-navigation-readback-v1",
        },
        method="GET",
    )
    with opener.open(request, timeout=timeout) as response:
        return (
            int(response.status),
            response.geturl(),
            response.headers.get_content_type(),
            response.read(),
        )


def fetch_bounded(url: str, timeout: int) -> tuple[int, str, str, bytes, int]:
    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            status, final_url, content_type, payload = fetch_once(url, timeout)
            return status, final_url, content_type, payload, attempt
        except HTTPError as error:
            last_error = error
            if error.code != 429 and not 500 <= error.code <= 599:
                raise
        except (URLError, TimeoutError, ConnectionError, OSError) as error:
            last_error = error
        if attempt < 4:
            time.sleep(2 ** attempt)
    assert last_error is not None
    raise last_error


def parse_navigation(payload: bytes) -> NavigationParser:
    parser = NavigationParser()
    parser.feed(payload.decode("utf-8"))
    parser.close()
    return parser


def resolved_anchor(document_url: str, href: str) -> str:
    return canonical_url(urljoin(document_url, href))


def check_one(row: dict[str, object], commit: str, timeout: int) -> dict[str, object]:
    path = ROOT / str(row["document"])
    payload = path.read_bytes()
    digest = sha256_bytes(payload)
    public_url = str(row["public_url"])
    request_url = cache_busted(public_url, commit, digest)
    try:
        status, final_url, content_type, actual, attempts = fetch_bounded(request_url, timeout)
        exact = status == 200 and actual == payload
        result: dict[str, object] = {
            "role": row["role"],
            "course_id": row.get("course_id"),
            "locale": row.get("locale"),
            "document": row["document"],
            "public_url": public_url,
            "http_status": status,
            "content_type": content_type,
            "attempts": attempts,
            "unexpected_redirect": canonical_url(final_url) != canonical_url(request_url),
            "expected_bytes": len(payload),
            "actual_bytes": len(actual),
            "expected_sha256": digest,
            "actual_sha256": sha256_bytes(actual),
            "exact": exact,
        }
        if status == 200 and content_type != "text/html":
            exact = False
            result["exact"] = False
            result["content_type_error"] = "expected text/html"
        if result["unexpected_redirect"]:
            result["exact"] = False
        if status == 200:
            nav = parse_navigation(actual)
            if row["role"] == "reader":
                expected_home = canonical_url(str(row["home_url"]))
                home_matches = sum(
                    resolved_anchor(public_url, link["href"]) == expected_home
                    for link in nav.home_links
                )
                contents_required = bool(row["contents_required"])
                expected_contents = canonical_url(str(row["contents_url"]))
                contents_matches = sum(
                    resolved_anchor(public_url, link["href"]) == expected_contents
                    for link in nav.contents_links
                )
                result["navigation"] = {
                    "program_home_links": len(nav.home_links),
                    "program_home_exact_matches": home_matches,
                    "required_program_home_matches": 2,
                    "contents_links": len(nav.contents_links),
                    "contents_exact_matches": contents_matches,
                    "contents_required": contents_required,
                    "pass": home_matches >= 2 and (not contents_required or contents_matches >= 1),
                }
            elif row["role"] == "gateway":
                expected_home = canonical_url(str(row["home_url"]))
                home_matches = sum(
                    resolved_anchor(public_url, link["href"]) == expected_home
                    for link in nav.home_links
                )
                result["navigation"] = {
                    "program_home_links": len(nav.home_links),
                    "program_home_exact_matches": home_matches,
                    "required_program_home_matches": 1,
                    "pass": home_matches >= 1,
                }
            elif row["role"] == "course_surface":
                home_results = []
                for course_id, home_url in sorted(dict(row["home_urls"]).items()):
                    expected_home = canonical_url(str(home_url))
                    matches = sum(
                        link["course_id"] == course_id
                        and resolved_anchor(public_url, link["href"]) == expected_home
                        for link in nav.home_links
                    )
                    home_results.append({
                        "course_id": course_id,
                        "expected_url": str(home_url),
                        "exact_matches": matches,
                        "required_exact_matches": 2,
                    })
                contents_results = []
                for contents_url in list(row["contents_urls"]):
                    expected_contents = canonical_url(str(contents_url))
                    matches = sum(
                        resolved_anchor(public_url, link["href"]) == expected_contents
                        for link in nav.surface_contents_links
                    )
                    contents_results.append({
                        "expected_url": str(contents_url),
                        "exact_matches": matches,
                        "required_exact_matches": 2,
                    })
                result["navigation"] = {
                    "surface_navigation_markers": nav.surface_navigation_markers,
                    "course_returns": home_results,
                    "related_surface_links": contents_results,
                    "pass": (
                        nav.surface_navigation_markers == 2
                        and all(item["exact_matches"] == 2 for item in home_results)
                        and all(item["exact_matches"] == 2 for item in contents_results)
                    ),
                }
            elif row["role"] == "generic":
                navigation_required = bool(row["navigation_required"])
                expected_target = canonical_url(str(row.get("target_url", "")))
                matches = sum(
                    not link["course_id"]
                    and resolved_anchor(public_url, link["href"]) == expected_target
                    for link in nav.home_links
                ) if navigation_required else 0
                result["navigation"] = {
                    "navigation_required": navigation_required,
                    "surface_navigation_markers": nav.surface_navigation_markers,
                    "program_home_exact_matches": matches,
                    "required_program_home_matches": 2 if navigation_required else 0,
                    "pass": (
                        nav.surface_navigation_markers == 2 and matches == 2
                        if navigation_required
                        else nav.surface_navigation_markers == 0
                    ),
                }
            if isinstance(result.get("navigation"), dict) and not result["navigation"]["pass"]:
                result["exact"] = False
        return result
    except Exception as error:  # receipt records bounded transport/public failures
        return {
            "role": row["role"],
            "course_id": row.get("course_id"),
            "locale": row.get("locale"),
            "document": row["document"],
            "public_url": public_url,
            "http_status": getattr(error, "code", None),
            "expected_bytes": len(payload),
            "expected_sha256": digest,
            "exact": False,
            "error": f"{type(error).__name__}: {error}",
        }


def course_article(text: str, course_id: str) -> str:
    pattern = re.compile(
        rf'<article\b[^>]*\bid="course-{re.escape(course_id)}"[^>]*>.*?</article>',
        flags=re.IGNORECASE | re.DOTALL,
    )
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ValueError(f"expected exactly one public course-{course_id} card")
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    if args.receipt.resolve() != DEFAULT_RECEIPT.resolve():
        print("central navigation public readback: FAIL: receipt path is not canonical", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit) or not re.fullmatch(r"[0-9a-f]{40}", args.tree):
        print("central navigation public readback: FAIL: commit/tree must be full lowercase SHA-1", file=sys.stderr)
        return 1
    if not 1 <= args.workers <= 16 or not 10 <= args.timeout <= 120:
        print("central navigation public readback: FAIL: invalid worker/timeout bound", file=sys.stderr)
        return 1

    local_validation = subprocess.run(
        [sys.executable, "-B", str(LOCAL_VALIDATOR)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if local_validation.returncode != 0:
        print(local_validation.stderr or local_validation.stdout, file=sys.stderr)
        return 1

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    site_origin = str(contract["site_origin"])
    interfaces = contract["interfaces"]
    rows: list[dict[str, object]] = []
    local_path_rows: dict[str, dict[str, object]] = {}

    for locale, interface in sorted(interfaces.items()):
        document = str(interface["document"])
        row = {
            "role": "interface",
            "locale": locale,
            "document": document,
            "public_url": str(interface["public_url"]),
        }
        rows.append(row)
        local_path_rows[document] = row

    for reader in contract["readers"]:
        root = ROOT / str(reader["root"])
        root_url = str(reader["public_root"])
        home_url = str(interfaces[reader["locale"]]["public_url"]) + "#" + str(reader["course_fragment"])
        root_index = (root / "index.html").resolve()
        for path in configured_html(root):
            document = path.relative_to(ROOT).as_posix()
            row = {
                "role": "reader",
                "course_id": reader["course_id"],
                "locale": reader["locale"],
                "document": document,
                "public_url": public_url_for_document(path, site_origin),
                "home_url": home_url,
                "contents_url": root_url,
                "contents_required": path.resolve() != root_index,
            }
            rows.append(row)
            local_path_rows[document] = row

    for gateway in contract["gateways"]:
        root = ROOT / str(gateway["root"])
        home_url = str(interfaces[gateway["locale"]]["public_url"]) + "#course-" + str(gateway["course_id"])
        for path in configured_html(root, gateway.get("exclude_subtrees")):
            document = path.relative_to(ROOT).as_posix()
            row = {
                "role": "gateway",
                "course_id": gateway["course_id"],
                "locale": gateway["locale"],
                "document": document,
                "public_url": public_url_for_document(path, site_origin),
                "home_url": home_url,
            }
            rows.append(row)
            local_path_rows[document] = row

    for group in contract["course_surfaces"]:
        root = ROOT / str(group["root"])
        locale = str(group["locale"])
        for surface in group["documents"]:
            path = root / str(surface["path"])
            document = path.relative_to(ROOT).as_posix()
            home_urls = {
                str(course_id): str(interfaces[locale]["public_url"]) + "#course-" + str(course_id)
                for course_id in surface["course_ids"]
            }
            contents_urls = [
                public_url_for_document(root / str(relative), site_origin)
                for relative in surface.get("contents_paths", [])
            ]
            row = {
                "role": "course_surface",
                "course_id": ",".join(str(value) for value in surface["course_ids"]),
                "course_ids": list(surface["course_ids"]),
                "locale": locale,
                "document": document,
                "public_url": public_url_for_document(path, site_origin),
                "home_urls": home_urls,
                "contents_urls": contents_urls,
            }
            rows.append(row)
            local_path_rows[document] = row

    for surface in contract["generic_surfaces"]:
        path = ROOT / str(surface["document"])
        document = path.relative_to(ROOT).as_posix()
        navigation_required = bool(surface["navigation_required"])
        row = {
            "role": "generic",
            "locale": surface.get("locale"),
            "document": document,
            "public_url": public_url_for_document(path, site_origin),
            "navigation_required": navigation_required,
        }
        if navigation_required:
            row["target_url"] = public_url_for_document(
                ROOT / str(surface["target_document"]), site_origin
            )
        rows.append(row)
        local_path_rows[document] = row

    expected_local = int(contract["summary"]["classified_html_documents"])
    if len(rows) != expected_local or len(local_path_rows) != expected_local:
        print("central navigation public readback: FAIL: local endpoint closure changed", file=sys.stderr)
        return 1

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(check_one, row, args.commit, args.timeout): row["document"]
            for row in rows
        }
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: str(row["document"]))
    by_document = {str(row["document"]): row for row in results}

    interface_checks: list[dict[str, object]] = []
    interface_course_ids: dict[str, list[str]] = {}
    for locale, interface in sorted(interfaces.items()):
        document = str(interface["document"])
        result = by_document[document]
        path = ROOT / document
        public_text = b""
        if result["exact"]:
            public_text = path.read_bytes()
        text = public_text.decode("utf-8") if public_text else ""
        course_ids = re.findall(r'<article\b[^>]*\bid="course-([A-Z][0-9]+)"', text, flags=re.IGNORECASE)
        original_groups = 0
        hosted_groups = 0
        for course_id in course_ids:
            article = course_article(text, course_id)
            if 'data-access-group="authoritative-original"' in article and "data-original-source=" in article:
                original_groups += 1
            if 'data-access-group="hosted-reader"' in article:
                hosted_groups += 1
        hub_links = sum(str(hub["public_url"]) in text for hub in contract["reciprocal_hubs"] if locale in hub["linked_from_locales"])
        passed = (
            len(course_ids) == len(set(course_ids)) == 40
            and original_groups == 40
            and hosted_groups == 40
            and hub_links >= 1
        )
        interface_course_ids[locale] = course_ids
        interface_checks.append({
            "locale": locale,
            "document": document,
            "course_cards": len(course_ids),
            "hosted_reader_groups": hosted_groups,
            "authoritative_original_groups": original_groups,
            "reciprocal_hub_links": hub_links,
            "pass": passed,
        })

    inbound_checks: list[dict[str, object]] = []
    for reader in contract["readers"]:
        landing_document = str(reader["landing_document"])
        landing_result = by_document[landing_document]
        landing_text = (ROOT / landing_document).read_text(encoding="utf-8") if landing_result["exact"] else ""
        for suffix in reader["landing_required_paths"]:
            expected_url = str(reader["public_root"]) + str(suffix)
            inbound_checks.append({
                "course_id": reader["course_id"],
                "landing_document": landing_document,
                "reader_url": expected_url,
                "present": expected_url in landing_text,
            })

    external_results: list[dict[str, object]] = []
    for hub in contract["reciprocal_hubs"]:
        url = str(hub["public_url"])
        try:
            status, final_url, content_type, payload, attempts = fetch_bounded(
                cache_busted(url, args.commit, file_fact(CONTRACT_PATH)["sha256"]),
                args.timeout,
            )
            text = payload.decode("utf-8")
            backlink = site_origin in text
            external_results.append({
                "id": hub["id"],
                "public_url": url,
                "http_status": status,
                "content_type": content_type,
                "attempts": attempts,
                "unexpected_redirect": canonical_url(final_url) != canonical_url(cache_busted(url, args.commit, file_fact(CONTRACT_PATH)["sha256"])),
                "bytes": len(payload),
                "sha256": sha256_bytes(payload),
                "program_backlink": backlink,
                "pass": status == 200 and content_type == "text/html" and backlink,
            })
        except Exception as error:
            external_results.append({
                "id": hub["id"],
                "public_url": url,
                "pass": False,
                "error": f"{type(error).__name__}: {error}",
            })

    failures = [row for row in results if not row["exact"]]
    all_pass = (
        not failures
        and all(row["pass"] for row in interface_checks)
        and all(row["present"] for row in inbound_checks)
        and all(row["pass"] for row in external_results)
        and len(inbound_checks) == 10
        and len(interface_checks) == len(interfaces)
    )
    receipt = {
        "schema": "central-reader-navigation-public-readback-v1",
        "status": "pass" if all_pass else "fail",
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authentication": "anonymous",
        "transport": {
            "browser_used": False,
            "proxy_used": False,
            "cookies_used": False,
            "credentials_recorded": False,
            "accept_encoding": "identity",
            "redirect_policy": "fail_closed",
            "retry_policy": "four bounded attempts; retry only 429, 5xx, or transport failure",
        },
        "deployment": {
            "repository": "https://github.com/KokunoYumeto/program-matematika-indonesia",
            "commit": args.commit,
            "tree": args.tree,
            "pages_run_id": args.run_id,
            "pages_run_url": f"https://github.com/KokunoYumeto/program-matematika-indonesia/actions/runs/{args.run_id}",
            "site_origin": site_origin,
        },
        "authority": {
            "contract": file_fact(CONTRACT_PATH),
            "local_validator": file_fact(LOCAL_VALIDATOR),
            "verification_script": file_fact(Path(__file__).resolve()),
            "local_validation_stdout_sha256": sha256_bytes(local_validation.stdout.encode("utf-8")),
        },
        "scope": {
            "reader_roots": len(contract["readers"]),
            "reader_html_documents": int(contract["summary"]["reader_html_documents"]),
            "gateway_roots": len(contract["gateways"]),
            "gateway_html_documents": int(contract["summary"]["gateway_html_documents"]),
            "course_surface_roots": len(contract["course_surfaces"]),
            "course_surface_html_documents": int(contract["summary"]["course_surface_html_documents"]),
            "generic_html_documents": int(contract["summary"]["generic_html_documents"]),
            "classified_html_documents": int(contract["summary"]["classified_html_documents"]),
            "interface_documents": len(interfaces),
            "local_html_endpoints": len(results),
            "local_exact": len(results) - len(failures),
            "local_failures": len(failures),
            "landing_to_reader_links": len(inbound_checks),
            "localized_course_cards": sum(row["course_cards"] for row in interface_checks),
            "hosted_reader_groups": sum(row["hosted_reader_groups"] for row in interface_checks),
            "authoritative_original_groups": sum(row["authoritative_original_groups"] for row in interface_checks),
            "external_reciprocal_hubs": len(external_results),
        },
        "interface_checks": interface_checks,
        "landing_to_reader_checks": inbound_checks,
        "external_hubs": external_results,
        "local_endpoints": results,
        "first_failures": failures[:10],
    }
    DEFAULT_RECEIPT.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({
        "status": receipt["status"],
        "receipt": file_fact(DEFAULT_RECEIPT),
        "scope": receipt["scope"],
        "external_hubs": external_results,
        "first_failures": failures[:3],
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
