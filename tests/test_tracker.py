import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from conference_tracker.render import render, validate
from conference_tracker.sources.official_copilot import CopilotExtractor, ExtractionError, fetch as fetch_official, verify
from conference_tracker.sources.opencurious import fetch as discover_opencurious
from conference_tracker.update import collect, csv_export, update

DIRECTORY = 'https://directory.example/conferences'
ASSET = 'https://directory.example/_next/static/app.js'
OFFICIAL = 'https://conf.example/'
CFP = 'https://conf.example/cfp'
CONFIG = {'directory_sources': [{'id': 'directory', 'adapter': 'opencurious_directory', 'url': DIRECTORY}]}


def directory_html():
    index = {'@graph': [{'@type': 'ItemList', '@id': DIRECTORY + '/#deadlines', 'numberOfItems': 1, 'itemListElement': [{'url': DIRECTORY + '/test-2027'}]}]}
    return '<script type="application/ld+json">' + json.dumps(index) + '</script><script src="/_next/static/app.js"></script>'


def directory_asset():
    return 'let records=[{name:"ignored",slug:"test-2027",website:"https://conf.example/",deadline:"2099-01-01",location:"must not leak"}];'


class FakeClient:
    def __init__(self):
        self.requests = []

    def get(self, url):
        self.requests.append(url)
        pages = {
            DIRECTORY: directory_html(), ASSET: directory_asset(),
            OFFICIAL: '<h1>Test Conference 2027</h1><a href="/cfp">Call for Papers</a>',
            CFP: 'Test Conference 2027. Abstract deadline: 2026-10-01. Paper deadline: 2026-10-08. The conference will be held in Test City, Testland.',
        }
        return pages[url]


class FakeExtractor:
    def extract(self, conference_id, website, pages):
        self.called_with = (conference_id, website, [page.source for page in pages])
        return {
            'name': 'TEST 2027', 'full_name': 'Test Conference', 'fields': ['ML'],
            'deadline': '2026-10-08', 'abstract_deadline': '2026-10-01',
            'location': 'Test City, Testland', 'conference_dates': None, 'dates_url': CFP,
            'name_evidence': 'Test Conference 2027', 'deadline_evidence': 'Paper deadline: 2026-10-08',
            'location_evidence': 'held in Test City, Testland',
        }


class TrackerTests(unittest.TestCase):
    def test_directory_discovers_only_official_urls(self):
        entries = discover_opencurious(CONFIG['directory_sources'][0], FakeClient())
        self.assertEqual(entries[0]['id'], 'test-2027')
        self.assertEqual(entries[0]['website'], OFFICIAL)
        self.assertNotIn('deadline', entries[0])
        self.assertNotIn('location', entries[0])

    def test_ai_extracts_from_official_pages_only(self):
        entry = discover_opencurious(CONFIG['directory_sources'][0], FakeClient())[0]
        extractor, client = FakeExtractor(), FakeClient()
        row = fetch_official(entry, client, extractor)
        self.assertEqual(row['deadline'], '2026-10-08')
        self.assertEqual(row['location'], 'Test City, Testland')
        self.assertEqual(extractor.called_with[2], [OFFICIAL, CFP])
        self.assertIn('official_pages', row['sources'][0])
        validate(row)

    def test_ai_evidence_must_exist_in_fetched_official_text(self):
        pages = [type('Page', (), {'text': 'Paper deadline: 2026-10-08', 'source': OFFICIAL})()]
        facts = FakeExtractor().extract('test-2027', OFFICIAL, pages)
        facts['deadline_evidence'] = 'invented deadline'
        with self.assertRaises(ExtractionError):
            verify(facts, pages)

    def test_copilot_cli_is_used_without_an_external_api_key(self):
        pages = [type('Page', (), {'text': 'Test Conference 2027. Paper deadline: 2026-10-08. held in Test City, Testland.', 'source': OFFICIAL})()]
        facts = {
            'name': 'TEST 2027', 'full_name': 'Test Conference', 'fields': ['ML'],
            'deadline': '2026-10-08', 'abstract_deadline': None, 'location': 'Test City, Testland',
            'conference_dates': None, 'dates_url': OFFICIAL, 'name_evidence': 'Test Conference 2027',
            'deadline_evidence': 'Paper deadline: 2026-10-08', 'location_evidence': 'held in Test City, Testland',
        }
        completed = type('Result', (), {'returncode': 0, 'stdout': json.dumps(facts), 'stderr': ''})()
        with patch('conference_tracker.sources.official_copilot.subprocess.run', return_value=completed) as run:
            result = CopilotExtractor(model='test-model').extract('test-2027', OFFICIAL, pages)
        self.assertEqual(result['deadline'], '2026-10-08')
        command = run.call_args.args[0]
        self.assertEqual(command[0], 'copilot')
        self.assertIn('--no-ask-user', command)
        self.assertIn('--model', command)

    def test_failed_ai_record_becomes_todo_not_table_data(self):
        bad = FakeExtractor()
        bad.extract = lambda *args: (_ for _ in ()).throw(ExtractionError('no verified deadline'))
        rows, websites, todos = collect(CONFIG, FakeClient(), bad)
        self.assertEqual(rows, [])
        self.assertEqual(websites[0]['website'], OFFICIAL)
        self.assertEqual(todos[0]['description'], 'no verified deadline')

    def test_csv_is_website_usable_flat_export(self):
        row = fetch_official(discover_opencurious(CONFIG['directory_sources'][0], FakeClient())[0], FakeClient(), FakeExtractor())
        export = csv_export([row])
        self.assertIn('evidence_deadline', export)
        self.assertIn('TEST 2027', export)

    def test_end_to_end_outputs_readme_json_csv_inventory_and_todos(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'data').mkdir()
            (root / 'sources.json').write_text(json.dumps(CONFIG))
            (root / 'README.md').write_text('# Test\n<!-- CONFERENCES:START -->old<!-- CONFERENCES:END -->\n<!-- SCRAPER-TODOS:START -->old<!-- SCRAPER-TODOS:END -->')
            rows, todos = update(root=root, client=FakeClient(), extractor=FakeExtractor(), now=datetime(2026, 10, 10, tzinfo=timezone.utc))
            self.assertEqual(len(rows), 1)
            self.assertEqual(todos, [])
            self.assertEqual(json.loads((root / 'data/conferences.json').read_text())['collection_method'], 'official-site-copilot')
            self.assertTrue((root / 'data/conferences.csv').read_text().startswith('id,name'))
            self.assertEqual(json.loads((root / 'data/conference_websites.json').read_text())['websites'][0]['website'], OFFICIAL)
            self.assertEqual(json.loads((root / 'data/scraper_todos.json').read_text())['todos'], [])
            self.assertIn('TEST 2027', (root / 'README.md').read_text())

    def test_readme_does_not_claim_directory_fields_are_sources(self):
        row = fetch_official(discover_opencurious(CONFIG['directory_sources'][0], FakeClient())[0], FakeClient(), FakeExtractor())
        output = render([row], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertIn('official-site-copilot', output)
        self.assertNotIn('directory', output)


if __name__ == '__main__':
    unittest.main()
