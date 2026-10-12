# AI Conference Deadlines

An automated AI-conference tracker. A directory source discovers official conference websites; an AI extractor then reads only pages from each conference's own domain and produces the deadline table from that evidence.

OpenCurious is used only for official URL discovery. Its deadlines, locations, and descriptions are deliberately discarded.

<!-- CONFERENCES:START -->

_Run the GitHub Action to generate the official-site table with your Copilot allowance._

<!-- CONFERENCES:END -->

## How it works

1. A **directory adapter** (currently OpenCurious) discovers HTTPS official conference URLs only.
2. The updater fetches every discovered official website and up to two same-domain CFP/deadline pages linked from it.
3. The AI model returns structured JSON for that one conference: name, fields, paper/abstract deadline, location, dates URL, and short quoted evidence.
4. The updater verifies that each quoted deadline/location evidence string appears in the fetched official-page text. It never uses the directory's facts as a fallback.
5. Verified records update the README table and data exports. A site without a verified paper deadline is recorded in `data/scraper_todos.json` instead of appearing in the table.

## Data for a website

Every successful refresh writes these files together:

| File | Use |
| --- | --- |
| `data/conferences.json` | Website-ready structured data, including source pages and evidence |
| `data/conferences.csv` | Flat import/export format for spreadsheets and static-site data pipelines |
| `data/conference_websites.json` | Inventory of official URLs discovered from directory sources |
| `data/scraper_todos.json` | Official sites where the AI could not verify a paper deadline |

Use `data/conferences.json` as the primary website data source. Each record includes its official landing page, every official page read, and the exact evidence snippet used for deadline/location extraction.

## Run locally

Requires Python 3.10 or later plus an authenticated GitHub Copilot CLI. The included GitHub Action installs and authenticates it automatically with the built-in `GITHUB_TOKEN`.

```bash
python -m unittest discover -s tests -v
python -m conference_tracker.update
```

Use `python3` instead of `python` if required. To check the live sources without writing files:

```bash
python -m conference_tracker.update --dry-run
```

## Enable automatic updates on GitHub

1. Create an empty GitHub repository and push all project files, including `.github`.
2. Ensure your GitHub account has Copilot Free or a paid Copilot plan.
3. Open **Actions → Update conference deadlines → Run workflow → Run workflow**.
4. Optional: create an Actions variable named `COPILOT_MODEL` only when you want to select a model available to your Copilot plan.

The workflow runs each Sunday at 06:17 UTC and commits the README plus all generated data files. It uses GitHub's automatic, short-lived `GITHUB_TOKEN` for both Copilot CLI authentication and repository commits. No API key or repository secret is required; usage is charged against the repository owner's Copilot allowance. Use **Run workflow** for an additional refresh, or change the cron after reviewing your Copilot usage.

## Add sources

There are two source types:

- **Type A — directory website:** returns only `{id, website, directory_sources}`. Add a dedicated adapter and register it in `DIRECTORY_ADAPTERS`.
- **Type B — official conference website:** needs no shared HTML parser. The AI reads that conference's official pages individually, with same-domain-only link following and evidence verification.

To add another directory source, create `conference_tracker/sources/example_directory.py`, register it in `conference_tracker/sources/__init__.py`, and add it to `directory_sources` in `sources.json`. Add synthetic regression tests for the directory's URL structure before enabling it.

## Safety and accuracy

- The AI receives only fetched official-page text for the conference currently being processed. Page text is treated as evidence, not instructions.
- The AI must return strict JSON and quote exact evidence for non-empty deadlines and locations.
- A quote must be present in the downloaded official text before that fact is published.
- The tracker does not guess a missing deadline or use prior-directory data. Missing verification becomes a TODO record.
- Always confirm submission rules, time zones, abstract-registration requirements, and track-specific deadlines on the linked official CFP.

## Project files

| File | Purpose |
| --- | --- |
| `conference_tracker/sources/opencurious.py` | Type A official-URL discovery only |
| `conference_tracker/sources/official_copilot.py` | Official-site page collection, Copilot extraction, and evidence checks |
| `conference_tracker/update.py` | Discovery, AI collection, README/JSON/CSV/TODO outputs |
| `conference_tracker/render.py` | README table, escaping, and countdowns |
| `data/conferences.json` | Generated website data |
| `data/conferences.csv` | Generated flat data export |
| `.github/workflows/update-conferences.yml` | Scheduled/manual refresh and generated-file commit |

## Scraper TODOs

<!-- SCRAPER-TODOS:START -->

_The next successful refresh replaces this section with official sites that need review._

<!-- SCRAPER-TODOS:END -->

