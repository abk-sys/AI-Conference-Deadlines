import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from conference_tracker.literals import LiteralParser
from conference_tracker.render import boundary, render, replace_section, time_left, validate
from conference_tracker.sources.opencurious import Page, extract_records, fetch, listed_slugs
from conference_tracker.update import collect, update

URL = 'https://www.opencurious.com/ai-conference-deadlines'
CONFIG = {'sources': [{'id': 'opencurious', 'adapter': 'opencurious', 'url': URL}]}
# Synthetic fixtures preserve the observed HTML/JS structure, not source prose.
RECORD = {
    'name': 'TEST 2027', 'slug': 'test-2027', 'fullName': 'Test Conference',
    'deadline': '2027-01-10', 'abstractDeadline': '2027-01-03',
    'location': 'Test City', 'fields': ['ML'], 'website': 'https://example.org/',
    'deadlineConfirmed': True,
}


def page(slugs=('test-2027',)):
    index = {'@graph': [{'@type': 'ItemList', '@id': URL + '/#deadlines',
                        'numberOfItems': len(slugs),
                        'itemListElement': [{'url': URL + '/' + s} for s in slugs]}]}
    return '<script type="application/ld+json">' + json.dumps(index) + '</script><script src="/_next/static/hash.js"></script>'


def script(records=None):
    text = json.dumps(records or [RECORD], ensure_ascii=False)
    return 'let data=' + text.replace('"name":', 'name:').replace('true', '!0') + ';'


class FakeClient:
    def __init__(self, html=None, js=None):
        self.html = html if html is not None else page()
        self.js = js if js is not None else script()

    def get(self, url):
        return self.html if url == URL else self.js


def rows():
    return fetch(CONFIG['sources'][0], FakeClient())


class TrackerTests(unittest.TestCase):
    def test_js_literals_do_not_alter_strings(self):
        value = LiteralParser('[{name:"Unicode Montréal | [x]",text:"literal !0 and deadline:",flag:!0,empty:null}]').value()
        self.assertTrue(value[0]['flag'])
        self.assertEqual(value[0]['text'], 'literal !0 and deadline:')

    def test_js_expressions_are_rejected(self):
        for text in ['[{name:fetch("https://example.org")}]', '[{name:"x",name:"y"}]', '[{name:(()=>1)()}]']:
            with self.assertRaises(ValueError):
                LiteralParser(text).value()

    def test_asset_discovery_and_index_filter(self):
        extra = dict(RECORD, slug='test-2026', name='TEST 2026')
        found = fetch(CONFIG['sources'][0], FakeClient(js=script([RECORD, extra])))
        self.assertEqual([r['id'] for r in found], ['test-2027'])
        self.assertEqual(found[0]['deadline_status'], 'confirmed')

    def test_missing_index_and_changed_asset_fail(self):
        for client in [FakeClient(html='<h1>Unavailable</h1>'), FakeClient(js='let data=[];'), FakeClient(html=page(('missing-2027',)))]:
            with self.assertRaises(ValueError):
                fetch(CONFIG['sources'][0], client)

    def test_aoe_boundary(self):
        row = rows()[0]
        before = datetime(2027, 1, 11, 11, 59, tzinfo=timezone.utc)
        end = datetime(2027, 1, 11, 12, 0, tzinfo=timezone.utc)
        self.assertNotEqual(time_left(row, before), 'Passed')
        self.assertEqual(time_left(row, end), 'Passed')

    def test_month_precision_has_no_invented_exact_date(self):
        row = rows()[0]
        row.update(deadline='2027-02-28', abstract_deadline=None, deadline_precision='month', deadline_status='projected')
        now = datetime(2027, 2, 1, tzinfo=timezone.utc)
        output = render([row], now)
        self.assertIn('Feb 2027', output)
        self.assertNotIn('2027-02-28', output)
        self.assertIn('Exact date TBA', output)
        self.assertEqual(boundary(row), datetime(2027, 3, 1, 12, tzinfo=timezone.utc))

    def test_markdown_escaping_and_marker_validation(self):
        row = rows()[0]
        row['location'] = 'A|B\n<script>alert(1)</script>'
        output = render([row], datetime(2026, 10, 10, tzinfo=timezone.utc))
        self.assertIn('A&#124;B', output)
        self.assertNotIn('<script>', output)
        original = 'intro\n<!-- CONFERENCES:START -->old<!-- CONFERENCES:END -->\nend'
        result = replace_section(original, output)
        self.assertTrue(result.startswith('intro\n'))
        self.assertTrue(result.endswith('\nend'))
        for invalid in ['no markers', original + original, '<!-- CONFERENCES:END --><!-- CONFERENCES:START -->']:
            with self.assertRaises(ValueError):
                replace_section(invalid, output)

    def test_record_validation(self):
        for change in [{'deadline': '2027-02-30'}, {'website': 'javascript:alert(1)'}, {'abstract_deadline': '2027-02-01'}, {'deadline_precision': 'unknown'}]:
            with self.assertRaises(ValueError):
                validate(dict(rows()[0], **change))

    def test_duplicate_precedence_and_provenance(self):
        first = rows()
        second = copy.deepcopy(first)
        second[0]['location'] = 'Other city'
        second[0]['sources'] = [{'id': 'other', 'url': 'https://example.org/'}]
        config = {'sources': [{'id': 'first', 'adapter': 'a'}, {'id': 'other', 'adapter': 'b'}]}
        with patch('conference_tracker.update.ADAPTERS', {'a': lambda *args: first, 'b': lambda *args: second}):
            with self.assertLogs(level='WARNING'):
                result = collect(config, None)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['location'], 'Test City')
        self.assertEqual(len(result[0]['sources']), 2)

    def test_failed_source_and_invalid_markers_preserve_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            (root / 'sources.json').write_text(json.dumps(CONFIG))
            readme = '<!-- CONFERENCES:START -->old<!-- CONFERENCES:END -->'
            (root / 'README.md').write_text(readme)
            (root / 'data/conferences.json').write_text('old data')
            with self.assertRaises(ValueError):
                update(root=root, client=FakeClient(js='broken'))
            self.assertEqual((root / 'README.md').read_text(), readme)
            self.assertEqual((root / 'data/conferences.json').read_text(), 'old data')
            (root / 'README.md').write_text('missing markers')
            with self.assertRaises(ValueError):
                update(root=root, client=FakeClient())
            self.assertEqual((root / 'data/conferences.json').read_text(), 'old data')

    def test_end_to_end_determinism_and_dry_run(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'sources.json').write_text(json.dumps(CONFIG))
            (root / 'README.md').write_text('intro\n<!-- CONFERENCES:START -->old<!-- CONFERENCES:END -->\nend')
            now = datetime(2026, 10, 10, tzinfo=timezone.utc)
            update(root=root, client=FakeClient(), now=now, dry_run=True)
            self.assertFalse((root / 'data/conferences.json').exists())
            update(root=root, client=FakeClient(), now=now)
            original = (root / 'README.md').read_bytes()
            update(root=root, client=FakeClient(), now=now)
            self.assertEqual((root / 'README.md').read_bytes(), original)
            self.assertEqual(len(json.loads((root / 'data/conferences.json').read_text())['conferences']), 1)


if __name__ == '__main__':
    unittest.main()
