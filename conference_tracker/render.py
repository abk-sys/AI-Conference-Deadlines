import calendar
import html
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import quote, urlsplit

AOE = timezone(timedelta(hours=-12))
START = '<!-- CONFERENCES:START -->'
END = '<!-- CONFERENCES:END -->'
TODO_START = '<!-- SCRAPER-TODOS:START -->'
TODO_END = '<!-- SCRAPER-TODOS:END -->'


def validate(row):
    for key in ('id', 'name', 'full_name', 'deadline', 'location', 'website'):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f'Missing/invalid {key}: {row.get("id")}')
    date.fromisoformat(row['deadline'])
    if row.get('abstract_deadline'):
        date.fromisoformat(row['abstract_deadline'])
        if row['abstract_deadline'] > row['deadline']:
            raise ValueError('Abstract deadline is after paper deadline')
    for key in ('website', 'dates_url'):
        if row.get(key) and (urlsplit(row[key]).scheme not in ('https', 'http') or not urlsplit(row[key]).netloc):
            raise ValueError(f'Invalid {key}')
    if row['deadline_precision'] not in ('day', 'month'):
        raise ValueError('Unsupported deadline precision')
    if row['deadline_status'] not in ('confirmed', 'projected', 'unknown'):
        raise ValueError('Unsupported deadline status')
    if not isinstance(row.get('fields'), list) or not all(isinstance(f, str) for f in row['fields']):
        raise ValueError('Invalid fields')
    if not row.get('sources'):
        raise ValueError('Source provenance required')


def boundary(row):
    day = date.fromisoformat(row['deadline'])
    if row['deadline_precision'] == 'month':
        day = day.replace(day=calendar.monthrange(day.year, day.month)[1])
    # AoE end of day, expressed as the exclusive next-midnight boundary.
    return datetime.combine(day + timedelta(days=1), time.min, AOE)


def cell(value):
    text = html.escape(str(value), quote=True).replace('|', '&#124;')
    for char in ('[', ']', '*', '_', '`', '\\'):
        text = text.replace(char, f'&#{ord(char)};')
    return ' '.join(text.split())


def link(label, url):
    return f'[{cell(label)}](<{quote(url, safe=":/?=&%#@+~-._")}>)'


def time_left(row, now):
    seconds = (boundary(row) - now).total_seconds()
    if seconds <= 0:
        return 'Passed'
    if row['deadline_precision'] == 'month':
        return 'Exact date TBA'
    days, remainder = divmod(int(seconds), 86400)
    hours = remainder // 3600
    prefix = '≈ ' if row['deadline_status'] != 'confirmed' else ''
    color = '🔴' if seconds <= 14 * 86400 else '🟡' if seconds <= 45 * 86400 else '🟢'
    duration = f'{days}d {hours}h' if days < 60 else f'{days}d'
    return f'{color} {prefix}{duration}'


def table(rows, now):
    lines = ['| Conference | Deadline | Location | Time left |', '| --- | --- | --- | --- |']
    for row in rows:
        conference = link(row['name'], row['website']) + '<br>' + cell(row['full_name'])
        conference += '<br>' + cell(' · '.join(row['fields']))
        day = date.fromisoformat(row['deadline'])
        deadline = day.strftime('%b %Y') if row['deadline_precision'] == 'month' else day.isoformat()
        if row.get('abstract_deadline'):
            deadline = 'Abstract: ' + cell(row['abstract_deadline']) + '<br>Paper: ' + deadline
        status = row['deadline_status'].capitalize()
        if row['deadline_precision'] == 'month':
            status += '; month only'
        deadline += '<br>' + cell(status)
        if row.get('dates_url'):
            deadline += ' · ' + link('Dates / CFP', row['dates_url'])
        lines.append(f'| {conference} | {deadline} | {cell(row["location"])} | {time_left(row, now)} |')
    return '\n'.join(lines) if rows else '_No conferences in this section._'


def render(rows, now):
    ordered = sorted(rows, key=lambda r: (r['deadline'], r['name']))
    upcoming = [r for r in ordered if boundary(r) > now]
    passed = [r for r in reversed(ordered) if boundary(r) <= now]
    sources = {s['id']: s['url'] for row in rows for s in row['sources']}
    source_links = ', '.join(link(k, v) for k, v in sorted(sources.items()))
    return '\n\n'.join([
        f'Last successful refresh: **{now:%Y-%m-%d %H:%M UTC}** · **{len(upcoming)} upcoming** · **{len(passed)} passed**',
        f'Official sources: {source_links}. Each published deadline/location has AI-returned evidence checked against fetched official-page text.',
        'Countdowns are snapshots at refresh time, using end-of-day Anywhere-on-Earth (UTC−12). '
        '≈ indicates a projected date; month-only deadlines have no precise countdown. '
        'Always check the linked official dates / CFP, including required abstract registration.',
        table(upcoming, now),
        '<details>\n<summary>Show passed deadlines</summary>\n\n' + table(passed, now) + '\n\n</details>',
    ])


def replace_section(readme, content, start=START, end=END):
    if readme.count(start) != 1 or readme.count(end) != 1 or readme.index(start) >= readme.index(end):
        raise ValueError('README must contain exactly one correctly ordered marker pair')
    before, rest = readme.split(start)
    _, after = rest.split(end)
    return before + start + '\n\n' + content + '\n\n' + end + after


def render_todos(todos):
    if not todos:
        return '_No outstanding official-site extraction TODOs._'
    lines = []
    for todo in sorted(todos, key=lambda item: item['id']):
        lines.append(f'- {link(todo["id"], todo["website"])} — {cell(todo["description"])}')
    return '\n'.join(lines)
