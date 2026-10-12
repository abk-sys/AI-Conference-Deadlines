"""OpenCurious directory adapter: discover official conference URLs only."""
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
        if records and all(isinstance(record, dict) and {'slug', 'website'} <= record.keys() for record in records):
            return records
    return None


def fetch(config, client):
    """Return canonical IDs and HTTPS official URLs; discard all directory facts."""
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
        selected = [record for record in records if record['slug'] in expected]
        if len(selected) != len(expected) or {record['slug'] for record in selected} != expected:
            raise ValueError('OpenCurious index and asset disagree; retaining previous files')
        result, seen_urls = [], set()
        for record in selected:
            website = record['website']
            parsed = urlsplit(website)
            if parsed.scheme != 'https' or not parsed.netloc or website in seen_urls:
                raise ValueError(f'Invalid or duplicate official URL for {record["slug"]}')
            seen_urls.add(website)
            result.append({
                'id': record['slug'], 'website': website,
                'directory_sources': [{'id': config['id'], 'url': url, 'asset_url': asset_url}],
            })
        return result
    raise ValueError('OpenCurious data array not found; the website format may have changed')
