"""Run with python -m conference_tracker.update from the repository root."""
import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from .http import HttpClient
from .render import render, replace_section, validate
from .sources import ADAPTERS

ROOT = Path(__file__).resolve().parent.parent


def collect(config, client):
    merged, source_ids = {}, set()
    for source in config['sources']:
        if not source.get('enabled', True):
            continue
        if source['id'] in source_ids:
            raise ValueError('Duplicate source ID')
        source_ids.add(source['id'])
        rows = ADAPTERS[source['adapter']](source, client)
        if not rows:
            raise ValueError(f'No records returned by {source["id"]}')
        seen = set()
        for row in rows:
            validate(row)
            if row['id'] in seen:
                raise ValueError(f'Duplicate conference ID in {source["id"]}: {row["id"]}')
            seen.add(row['id'])
            if row['id'] in merged:
                winner = merged[row['id']]
                if any(row[k] != winner[k] for k in row if k != 'sources'):
                    logging.warning('Conflicting record %s; keeping first configured source', row['id'])
                winner['sources'].extend(row['sources'])
            else:
                merged[row['id']] = row
        logging.info('%s: %d conferences', source['id'], len(rows))
    if not merged:
        raise ValueError('No enabled sources or no conferences')
    return sorted(merged.values(), key=lambda r: (r['deadline'], r['id']))


def update(root=ROOT, config_path=None, now=None, client=None, dry_run=False):
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(second=0, microsecond=0)
    config = json.loads((config_path or root / 'sources.json').read_text(encoding='utf-8'))
    # Complete all fetching, validation, and rendering before touching output files.
    rows = collect(config, client or HttpClient())
    readme_path = root / 'README.md'
    readme = replace_section(readme_path.read_text(encoding='utf-8'), render(rows, now))
    payload = {'schema_version': 1, 'updated_at': now.isoformat(), 'conferences': rows}
    outputs = {
        root / 'data/conferences.json': json.dumps(payload, ensure_ascii=False, indent=2) + '\n',
        readme_path: readme,
    }
    if dry_run:
        logging.info('Dry run: validated %d records; no files written', len(rows))
        return rows
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
    logging.info('Updated README.md and data/conferences.json (%d records)', len(rows))
    return rows


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
