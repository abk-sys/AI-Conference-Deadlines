# AI Conference Deadlines

A daily-updated conference table collected from [OpenCurious](https://www.opencurious.com/ai-conference-deadlines), with official conference links and an extensible source adapter system.

The four columns match the source: **Conference · Deadline · Location · Time left**. Field tags, abstract deadlines, and date confidence appear within the cells. The JSON export includes all listed conferences, including passed deadlines.

<!-- CONFERENCES:START -->

Last successful refresh: **2026-10-12 06:06 UTC** · **11 upcoming** · **7 passed**

Sources: [opencurious](<https://www.opencurious.com/ai-conference-deadlines>). Confirmation labels are reported by the source, not independently verified.

Countdowns are snapshots at refresh time, using end-of-day Anywhere-on-Earth (UTC−12). ≈ indicates a projected date; month-only deadlines have no precise countdown. Always check the linked official dates / CFP, including required abstract registration.

| Conference | Deadline | Location | Time left |
| --- | --- | --- | --- |
| [FAccT 2027](<https://facctconference.org/>)<br>ACM Conference on Fairness, Accountability, and Transparency<br>AI · ML | Abstract: 2026-10-27<br>Paper: 2026-11-03<br>Confirmed · [Dates / CFP](<https://facctconference.org/2027/cfp.html>) | Porto, Portugal | 🟡 23d 5h |
| [CVPR 2027](<https://cvpr.thecvf.com/>)<br>IEEE/CVF Conference on Computer Vision and Pattern Recognition<br>CV · ML | Abstract: 2026-11-10<br>Paper: 2026-11-16<br>Confirmed · [Dates / CFP](<https://cvpr.thecvf.com/Conferences/2027/Dates>) | Seattle, Washington, USA | 🟡 36d 5h |
| [IJCAI 2027](<https://2027.ijcai.org/>)<br>International Joint Conference on Artificial Intelligence<br>AI | Abstract: 2027-01-04<br>Paper: 2027-01-11<br>Confirmed | Kyoto, Japan | 🟢 92d |
| [ICML 2027](<https://icml.cc/>)<br>International Conference on Machine Learning<br>ML | Abstract: 2027-01-16<br>Paper: 2027-01-22<br>Projected · [Dates / CFP](<https://icml.cc/Conferences/FutureMeetings>) | South America (city TBA) | 🟢 ≈ 103d |
| [ACL 2027](<https://2027.aclweb.org/>)<br>Annual Meeting of the Association for Computational Linguistics<br>NLP | Jan 2027<br>Projected; month only | Kyoto, Japan | Exact date TBA |
| [COLT 2027](<https://learningtheory.org/colt2027/>)<br>Annual Conference on Learning Theory<br>ML | 2027-02-05<br>Projected | Tokyo, Japan | 🟢 ≈ 117d |
| [UAI 2027](<https://www.auai.org/>)<br>Conference on Uncertainty in Artificial Intelligence<br>ML · AI | 2027-02-12<br>Projected | TBA | 🟢 ≈ 124d |
| [KDD 2027](<https://kdd2027.kdd.org/>)<br>ACM SIGKDD Conference on Knowledge Discovery and Data Mining<br>Data Mining · ML | Feb 2027<br>Projected; month only · [Dates / CFP](<https://kdd2027.kdd.org/research-track-call-for-papers/>) | San Jose, California, USA | Exact date TBA |
| [ICCV 2027](<https://iccv.thecvf.com/>)<br>IEEE/CVF International Conference on Computer Vision<br>CV | Abstract: 2027-03-01<br>Paper: 2027-03-08<br>Projected | Hong Kong | 🟢 ≈ 148d |
| [ECAI 2027](<https://ecai2027.org/>)<br>European Conference on Artificial Intelligence<br>AI | 2027-04-14<br>Confirmed | Athens, Greece | 🟢 185d |
| [NeurIPS 2027](<https://neurips.cc/>)<br>Conference on Neural Information Processing Systems<br>ML | Abstract: 2027-05-14<br>Paper: 2027-05-21<br>Projected · [Dates / CFP](<https://neurips.cc/Conferences/FutureMeetings>) | Europe (city TBA) | 🟢 ≈ 222d |

<details>
<summary>Show passed deadlines</summary>

| Conference | Deadline | Location | Time left |
| --- | --- | --- | --- |
| [AISTATS 2027](<https://aistats.org/aistats2027/>)<br>International Conference on Artificial Intelligence and Statistics<br>ML | Abstract: 2026-09-29<br>Paper: 2026-10-06<br>Confirmed · [Dates / CFP](<https://virtual.aistats.org/Conferences/2027/Dates>) | Montréal, Canada | Passed |
| [ICLR 2027](<https://iclr.cc/>)<br>International Conference on Learning Representations<br>ML | Abstract: 2026-09-18<br>Paper: 2026-09-25<br>Confirmed · [Dates / CFP](<https://iclr.cc/Conferences/2027/Dates>) | California, USA | Passed |
| [ICASSP 2027](<https://2027.ieeeicassp.org/>)<br>IEEE International Conference on Acoustics, Speech and Signal Processing<br>Speech · ML | 2026-09-16<br>Confirmed · [Dates / CFP](<https://2027.ieeeicassp.org/important-dates/>) | Toronto, Canada | Passed |
| [WACV 2027](<https://wacv.thecvf.com/>)<br>IEEE/CVF Winter Conference on Applications of Computer Vision<br>CV | 2026-08-28<br>Confirmed · [Dates / CFP](<https://wacv.thecvf.com/Conferences/2027/Dates>) | Orlando, Florida, USA | Passed |
| [EMNLP 2026](<https://2026.emnlp.org/>)<br>Conference on Empirical Methods in Natural Language Processing<br>NLP | 2026-08-02<br>Confirmed · [Dates / CFP](<https://2026.emnlp.org/calls/main_conference_papers/>) | Budapest, Hungary | Passed |
| [AAAI 2027](<https://aaai.org/conference/aaai/aaai-27/>)<br>AAAI Conference on Artificial Intelligence<br>AI · ML | Abstract: 2026-07-21<br>Paper: 2026-07-28<br>Confirmed | Montréal, Canada | Passed |
| [ECCV 2026](<https://eccv.ecva.net/>)<br>European Conference on Computer Vision<br>CV | 2026-03-05<br>Confirmed · [Dates / CFP](<https://eccv.ecva.net/Conferences/2026/Dates>) | Malmö, Sweden | Passed |

</details>

<!-- CONFERENCES:END -->

## Run locally

Requires Python 3.10 or later (GitHub Actions uses 3.12). No pip packages, API keys, database, browser, or paid services are needed.

From the extracted project directory:

```bash
python -m unittest discover -s tests -v
python -m conference_tracker.update
```

Use `python3` instead of `python` if required on your machine. To validate the live source without modifying files:

```bash
python -m conference_tracker.update --dry-run
```

The script writes `data/conferences.json` and replaces only the section between the two `CONFERENCES` markers in this README. Keep those markers exactly once. Introductory text and instructions outside them are preserved.

## Enable automatic updates on GitHub

1. Create a new, empty GitHub repository, such as `ai-conference-deadlines`.
2. Push **all contents of this project**, including the `.github` directory. Do not upload only the ZIP or README. From this directory, replacing the URL with your repository:

   ```bash
   git init
   git add .
   git commit -m "Add automated AI conference tracker"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-conference-deadlines.git
   git push -u origin main
   ```

3. Open **Settings → Actions → General** and enable GitHub Actions. Under **Workflow permissions**, allow **Read and write permissions** if repository/organization policy requires it. The workflow itself requests only `contents: write`.
4. Open **Actions → Update conference deadlines → Run workflow**. Verify a successful run and a bot commit updating the README.
5. The included schedule runs every day at **06:17 UTC** (11:17 p.m. PDT or 10:17 p.m. PST on the previous local date). Change `cron` in `.github/workflows/update-conferences.yml` to adjust it. For every six hours use `17 */6 * * *`.

The automatic `GITHUB_TOKEN` is supplied by GitHub; no personal token or repository secrets are required. The workflow always updates the repository's default branch. Branch rules must permit the bot's direct push; if your repository requires all updates via PR, replace the final commit/push step with your approved PR workflow. Do not disable organization protections just to run this project.

GitHub schedules run from the default branch and may be delayed. Public-repository schedules can be disabled after 60 days without repository activity; re-enable the workflow if this happens. A fork may require Actions to be explicitly enabled. A rejected push is reported as a failed run; it never force-pushes. Rerun after resolving branch changes or permissions.

Reference: [GitHub scheduled workflow documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## How collection works

1. Fetch `robots.txt` and the configured OpenCurious page.
2. Read its structured conference index and discover JavaScript assets linked by that page. No asset hash is hard-coded.
3. Extract the conference data array using a restricted literal parser; downloaded JavaScript is never executed.
4. Select the conferences present in the page's index, validate required fields and dates, and normalize them into a shared schema.
5. Merge sources by conference ID, sort by deadline, generate upcoming and passed tables, and write JSON and Markdown.
6. GitHub Actions commits the generated files together, creating a version history of changes.

The linked asset can contain historical entries absent from the page's index. Those are deliberately excluded to match the selected source page. An empty response, missing data array, invalid record, index mismatch, or failed enabled source aborts before output changes. Existing data stays available with its previous successful-refresh timestamp. Inspect the failed Actions run to diagnose it.

Requests use a named user agent, HTTPS, timeouts, bounded response sizes, robots checks, and retries for transient failures. Asset parsing depends on the site's current format; if the site changes, update its adapter and tests. No scraper can guarantee compatibility with future redesigns.

## Date interpretation

- `Confirmed` means OpenCurious marks it confirmed. This project does not independently verify official CFPs.
- `Projected` is retained when the source does not mark a date confirmed. Approximate countdowns use `≈`.
- Month-only dates (for example, Jan 2027) stay month-only in the table. The raw source's placeholder day remains in JSON with `deadline_precision: "month"`; never treat it as an exact due date. These rows move to passed after the month ends.
- Dates use end-of-day AoE (UTC−12). The last instant of a given AoE day is immediately before 12:00 UTC the following day. Check official CFPs for exceptions and track-specific rules.
- README countdowns refresh when the workflow runs; GitHub Markdown cannot run a live countdown or interactive field filters. Passed deadlines are in a collapsible section.
- The refresh timestamp records collection time. `source_reviewed_on` records the source's review date; these are different.

## Add more websites

See [docs/ADDING_SOURCES.md](docs/ADDING_SOURCES.md). Every new website gets an adapter that returns the same normalized records, plus an entry in `sources.json`. Different sites usually require different parsers; adding a URL alone does not implement one.

## Project files

| File | Purpose |
| --- | --- |
| `conference_tracker/sources/opencurious.py` | OpenCurious parsing and normalization |
| `conference_tracker/sources/__init__.py` | Source adapter registry |
| `conference_tracker/update.py` | Collection, validation, merging, output writes |
| `conference_tracker/render.py` | Four-column table, escaping, AoE countdowns |
| `conference_tracker/literals.py` | Data-only JavaScript literal parser |
| `conference_tracker/http.py` | HTTP and robots checks |
| `sources.json` | Enabled sources and precedence |
| `data/conferences.json` | Generated data with source provenance |
| `.github/workflows/update-conferences.yml` | Daily/manual refresh and bot commit |
| `tests/test_tracker.py` | Parser, dates, merging, and failure regression checks |
| `docs/ORIGINAL_REPO.md` | Explanation and run instructions for the jobs repository |

This project is independently implemented. Source attribution belongs to OpenCurious; official conference links are preserved. Only factual fields needed for the tracker are exported, not the site's editorial descriptions or notes.
