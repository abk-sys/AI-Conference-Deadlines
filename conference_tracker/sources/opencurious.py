"""OpenCurious adapter: discover assets from the page, parse data literals."""
import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from ..literals import LiteralParser


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.assets, self.jsonld = [], []
        self.collect = False
        self.buffer = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            if attrs.get('src'):
                self.assets.append(attrs['src'])
            self.collect = attrs.get('type') == 'application/ld+json'
            self.buffer = ''

    def handle_data(self, data):
        if self.collect:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.collect:
            self.jsonld.append(json.loads(self.buffer))
            self.collect = False


def listed_slugs(page):
    slugs = set()
    for document in page.jsonld:
        for node in document.get('@graph', [document]):
            if node.get('@type') == 'ItemList' and 'deadlines' in node.get('@id', ''):
                for item in node['itemListElement']:
                    slugs.add(urlsplit(item['url']).path.rstrip('/').split('/')[-1])
                if len(slugs) != node.get('numberOfItems', len(slugs)):
                    raise ValueError('OpenCurious list count changed or contains duplicates')
    if not slugs:
        raise ValueError('OpenCurious conference index missing; refusing an empty update')
    return slugs


def extract_records(script):
    for match in re.finditer(r'\[\s*\{\s*(?:name|"name")\s*:', script):
        try:
            records = LiteralParser(script, match.start()).value()
        except (ValueError, IndexError):
            continue
        if records and all(isinstance(r, dict) and {'name', 'slug', 'deadline', 'website'} <= r.keys() for r in records):
            return records
    return None


def fetch(config, client):
    url = config['url']
    page = Page(client.get(url))
    expected = listed_slugs(page)
    for asset in dict.fromkeys(page.assets):
        asset_url = urljoin(url, asset)
        if urlsplit(asset_url).netloc != urlsplit(url).netloc or '/_next/static/' not in asset_url:
            continue
        records = extract_records(client.get(asset_url))
        if records is None:
            continue
        selected = [r for r in records if r['slug'] in expected]
        if len(selected) != len(expected) or {r['slug'] for r in selected} != expected:
            raise ValueError('OpenCurious index and asset disagree; retaining previous files')
        return [normalize(row, config, asset_url) for row in selected]
    raise ValueError('OpenCurious data array not found; the website format may have changed')


def normalize(row, config, asset_url):
    return {
        'id': row['slug'], 'name': row['name'], 'full_name': row['fullName'],
        'fields': row['fields'], 'deadline': row['deadline'],
        'abstract_deadline': row.get('abstractDeadline'),
        'deadline_precision': row.get('deadlinePrecision', 'day'),
        'deadline_status': 'confirmed' if row.get('deadlineConfirmed') is True else 'projected',
        'location': row['location'], 'website': row['website'],
        'dates_url': row.get('datesUrl'), 'conference_dates': row.get('conferenceDates'),
        'source_reviewed_on': row.get('verifiedOn'),
        'sources': [{'id': config['id'], 'url': config['url'], 'asset_url': asset_url}],
    }
