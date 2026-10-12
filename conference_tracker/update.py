"""Refresh official conference facts with GitHub Copilot extraction.

Run with: python -m conference_tracker.update
Requires: GitHub Copilot CLI authenticated by GitHub Actions' GITHUB_TOKEN.
"""
import argparse
import csv
import io
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from .http import HttpClient
from .render import TODO_END, TODO_START, render, render_todos, replace_section, validate
from .sources import DIRECTORY_ADAPTERS
from .sources.official_copilot import CopilotExtractor, ExtractionError, fetch as fetch_official

ROOT = Path(__file__).resolve().parent.parent


def discover(config, client):
    websites, source_ids = {}, set()
    for source in config['directory_sources']:
        if not source.get('enabled', True):
            continue
        if source['id'] in source_ids:
            raise ValueError(f'Duplicate directory source ID: {source["id"]}')
        source_ids.add(source['id'])
        adapter = DIRECTORY_ADAPTERS.get(source.get('adapter'))
        if not adapter:
            raise ValueError(f'Unknown directory adapter: {source.get("adapter")}')
        entries = adapter(source, client)
        for entry in entries:
            existing = websites.get(entry['id'])
            if existing and existing['website'] != entry['website']:
                logging.warning('Conflicting official URL for %s; keeping first configured directory source', entry['id'])
                continue
            websites.setdefault(entry['id'], entry)
        logging.info('%s: %d official URLs', source['id'], len(entries))
    if not websites:
        raise ValueError('No official conference URLs were discovered')
    return dict(sorted(websites.items()))


def collect(config, client, extractor):
    discovered = discover(config, client)
    rows, todos = [], []
    for conference_id, entry in discovered.items():
        try:
            row = fetch_official(entry, client, extractor)
            validate(row)
            rows.append(row)
        except (ExtractionError, ValueError) as error:
            logging.warning('%s: %s', conference_id, error)
            todos.append({'id': conference_id, 'website': entry['website'], 'description': str(error), 'directory_sources': entry['directory_sources']})
    return sorted(rows, key=lambda row: (row['deadline'], row['id'])), list(discovered.values()), todos


def csv_export(rows):
    columns = ['id', 'name', 'full_name', 'fields', 'deadline', 'abstract_deadline', 'deadline_precision', 'deadline_status', 'location', 'website', 'dates_url', 'conference_dates', 'evidence_deadline', 'evidence_location', 'official_pages']
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({
            'id': row['id'], 'name': row['name'], 'full_name': row['full_name'], 'fields': '; '.join(row['fields']),
            'deadline': row['deadline'], 'abstract_deadline': row.get('abstract_deadline') or '',
            'deadline_precision': row['deadline_precision'], 'deadline_status': row['deadline_status'],
            'location': row['location'], 'website': row['website'], 'dates_url': row.get('dates_url') or '',
            'conference_dates': row.get('conference_dates') or '',
            'evidence_deadline': row['evidence'].get('deadline') or '', 'evidence_location': row['evidence'].get('location') or '',
            'official_pages': '; '.join(row['sources'][0]['official_pages']),
        })
    return output.getvalue()


def update(root=ROOT, config_path=None, now=None, client=None, extractor=None, dry_run=False):
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(second=0, microsecond=0)
    config = json.loads((config_path or root / 'sources.json').read_text(encoding='utf-8'))
    rows, websites, todos = collect(config, client or HttpClient(), extractor or CopilotExtractor())
    readme_path = root / 'README.md'
    readme = replace_section(readme_path.read_text(encoding='utf-8'), render(rows, now))
    readme = replace_section(readme, render_todos(todos), TODO_START, TODO_END)
    payload = {'schema_version': 2, 'updated_at': now.isoformat(), 'collection_method': 'official-site-copilot', 'conferences': rows}
    outputs = {
        root / 'data/conferences.json': json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
        root / 'data/conferences.csv': csv_export(rows),
        root / 'data/conference_websites.json': json.dumps({'schema_version': 1, 'updated_at': now.isoformat(), 'directory_sources': config['directory_sources'], 'websites': websites}, ensure_ascii=False, indent=2) + '\n',
        root / 'data/scraper_todos.json': json.dumps({'schema_version': 1, 'updated_at': now.isoformat(), 'todos': todos}, ensure_ascii=False, indent=2) + '\n',
        readme_path: readme,
    }
    if dry_run:
        logging.info('Dry run: verified %d official records; %d need review; no files written', len(rows), len(todos))
        return rows, todos
    staged = []
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + '.tmp')
            temporary.write_text(content, encoding='utf-8')
            staged.append((temporary, path))
        for temporary, path in staged:
            os.replace(temporary, path)
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    logging.info('Updated README plus JSON, CSV, website inventory, and TODO data (%d verified; %d TODOs)', len(rows), len(todos))
    return rows, todos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, help='Source configuration; defaults to sources.json')
    parser.add_argument('--dry-run', action='store_true', help='Fetch and validate without writing')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    try:
        update(config_path=args.config, dry_run=args.dry_run)
    except Exception as error:
        logging.error('Refresh failed: %s', error)
        raise SystemExit(1) from error


if __name__ == '__main__':
    main()
