"""Keep original-language mirrors distinct from authoritative author links."""
from pathlib import Path
import runpy
import unittest

api = runpy.run_path(str(Path(__file__).with_name('validate-central-reader-navigation-v1.py')))
urls = api['article_original_urls']
AUTHOR = '<a href="https://hefferon.net/linearalgebra/" data-original-source="upstream-original" data-access-role="authoritative-original">Original author</a>'
MIRROR = '<a href="https://example.org/programme/reader/" data-original-source="program-mirror" data-access-role="hosted-reader">Original English</a>'


class OriginalLinkTests(unittest.TestCase):
    def test_author_is_retained_beside_original_language_mirror(self):
        self.assertEqual(urls(AUTHOR + MIRROR), {'https://hefferon.net/linearalgebra/'})

    def test_mirror_alone_cannot_supply_author_link(self):
        self.assertEqual(urls(MIRROR), set())

    def test_mirror_mislabelled_as_author_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'program mirror'):
            urls(MIRROR.replace('hosted-reader', 'authoritative-original'))

    def test_http_author_rejected(self):
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            urls(AUTHOR.replace('https:', 'http:'))

    def test_missing_author_href_rejected(self):
        with self.assertRaisesRegex(ValueError, 'lacks href'):
            urls(AUTHOR.replace('href="https://hefferon.net/linearalgebra/"', ''))

    def test_unmarked_author_role_is_not_silently_admitted(self):
        self.assertEqual(urls(AUTHOR.replace('data-original-source="upstream-original"', '')), set())


if __name__ == '__main__':
    unittest.main()
