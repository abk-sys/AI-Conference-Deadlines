# Adding a source

The first adapter is OpenCurious. Extend the collection stage without changing README rendering or the scheduled workflow.

1. Create `conference_tracker/sources/example.py` with `fetch(config, client)` returning a nonempty list of normalized dictionaries. Use `client.get(url)` for robots-aware requests, validate the site's structure, and fail loudly on incomplete results.
2. Register it in `conference_tracker/sources/__init__.py`:

   ```python
   from . import example, opencurious
   ADAPTERS = {
       "opencurious": opencurious.fetch,
       "example": example.fetch,
   }
   ```

3. Append the new source configuration (with its real URL) to `sources.json`:

   ```json
   {"id": "example", "adapter": "example", "url": "https://example.org/conferences", "enabled": true}
   ```

4. Add tests with small, synthetic fixtures matching that site's data structure. Test missing fields, empty pages, and changed markup as well as a valid record.
5. Run `python -m unittest discover -s tests -v`, then `python -m conference_tracker.update --dry-run`. Review a normal run's README/JSON diff before pushing.

## Adapter record contract

| Field | Type and meaning |
| --- | --- |
| `id` | Stable canonical slug, e.g. `icml-2027`; normalize aliases across sources |
| `name` | Conference name and edition |
| `full_name` | Expanded conference name |
| `fields` | List of field labels, e.g. `["ML", "CV"]` |
| `deadline` | ISO `YYYY-MM-DD`; source placeholder allowed only with month precision |
| `abstract_deadline` | ISO date or `null` |
| `deadline_precision` | `day` or `month` |
| `deadline_status` | `confirmed`, `projected`, or `unknown` |
| `location` | Source location, or explicit `TBA` |
| `website` | Official conference HTTP(S) URL |
| `dates_url` | Official dates / CFP HTTP(S) URL or `null` |
| `conference_dates` | Display string or `null` |
| `source_reviewed_on` | Source's own review date or `null`; never invent it |
| `sources` | List of objects with `id`, `url`, and optionally `asset_url` |

The current schema models one tracked deadline per conference edition, matching OpenCurious. If a future source tracks multiple submission rounds, assign canonical round-specific IDs consistently in all adapters, e.g. `kdd-2027-cycle-2`, and include the round in `name`. More complex track/time-zone support needs a schema/rendering change; do not flatten different deadlines into one record accidentally.

## Merge and failure policy

Sources are ordered by precedence in `sources.json`: the first source wins the **whole record** for a duplicate canonical ID. Additional source references are appended, and conflicting values produce a warning. Values from conflicting sources are not silently combined into a synthetic record. Put an official source first if it should take priority.

An enabled source failing prevents the entire refresh. This intentionally preserves the previous successful published snapshot instead of publishing a partial table. Temporarily set a source's `enabled` to `false` if you intentionally want to exclude it; its records disappear unless another enabled source provides them.

Each run represents the currently collected source index. It does not accumulate conferences removed from a source; old snapshots remain in Git history. Within the current snapshot, passed entries appear in the README's collapsible section.
