# Adding sources

There are two source types. Keep their roles separate.

## Type A: directory website

A directory site may discover official links but must never supply facts for the table.

1. Add `conference_tracker/sources/example_directory.py` with `fetch(config, client)`.
2. Return only records shaped as `{"id": "example-2028", "website": "https://2028.example.org/", "directory_sources": [...]}`.
3. Reject non-HTTPS URLs, duplicates, an empty index, and markup changes rather than guessing.
4. Register the adapter in `DIRECTORY_ADAPTERS` and add it to `directory_sources` in `sources.json`.
5. Add synthetic tests for the site's URL list.

## Type B: official conference website

No common HTML parser is used. The updater fetches each discovered official website separately, follows at most two relevant links within the same domain, and sends only that conference's fetched text to the configured AI model.

The model must return strict JSON plus exact supporting quotes. A deadline or location is published only when the quote occurs in the fetched official text. If no verified paper deadline is available, the conference is written to `data/scraper_todos.json`, not the README table.

If an official site uses a separate verified organizer domain for its CFP, add a dedicated official-site collector for that conference/domain rather than weakening the same-domain rule for every conference.
