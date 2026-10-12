# What the jobs repository actually runs

Inspected repository: [speedyapply/2027-AI-College-Jobs](https://github.com/speedyapply/2027-AI-College-Jobs), `main` commit `9acb7ac68a52de199848ff5193acba925c470cc9`, inspected October 10, 2026 UTC.

## Update pipeline

1. [`.github/workflows/get-jobs.yml`](https://github.com/speedyapply/2027-AI-College-Jobs/blob/main/.github/workflows/get-jobs.yml) runs at `0 12 * * *` (daily 12:00 UTC) or on manual `workflow_dispatch`.
2. It checks out the repo, installs Bun, runs `bun install` inside `.github/scripts`, and invokes `bun run get-jobs`.
3. [`src/queries.ts`](https://github.com/speedyapply/2027-AI-College-Jobs/blob/main/.github/scripts/src/queries.ts) calls Supabase RPCs `jobs.get_jobs` and `jobs.get_ai_job_counts`.
4. [`src/get-jobs.ts`](https://github.com/speedyapply/2027-AI-College-Jobs/blob/main/.github/scripts/src/get-jobs.ts) builds Markdown tables, replaces marked sections, and updates counts. [`src/config.ts`](https://github.com/speedyapply/2027-AI-College-Jobs/blob/main/.github/scripts/src/config.ts) selects files, categories, and salary formatting.
5. The workflow commits and pushes `README.md`, `INTERN_INTL.md`, `NEW_GRAD_USA.md`, and `NEW_GRAD_INTL.md`.

There is also an approved-issue workflow that calls database mutation RPCs, regenerates the tables, and closes the contribution issue.

**This public repository is a database-to-Markdown publisher.** Its checked-in code does not include the upstream job-board scraping pipeline, database DDL, or Supabase RPC definitions. Forking it does not give you the authors' database or recreate its data collection system. Its exact upstream scraping and hosting arrangements cannot be established from these files.

## Run the original publisher locally

Install Bun, then:

```bash
git clone https://github.com/speedyapply/2027-AI-College-Jobs.git
cd 2027-AI-College-Jobs/.github/scripts
bun install
```

Create a local `.env` in `.github/scripts` with your **authorized** database connection and an apply-button image URL:

```dotenv
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=YOUR_AUTHORIZED_KEY
APPLY_IMG_URL=https://YOUR_HOST/apply-button.png
```

Do not commit secrets. Ensure `.env` is ignored. Your database must expose the `jobs` schema and compatible `get_jobs` and `get_ai_job_counts` RPCs; the public repository does not supply their implementation. A new, empty Supabase project plus credentials is insufficient. Query inputs and response types are documented by `queries.ts` and `src/types/*.schema.ts`.

Then:

```bash
bun run get-jobs
```

## Run the original publisher automatically

Fork it, enable Actions, and configure these repository Actions secrets:

| Secret | Purpose |
| --- | --- |
| `SUPABASE_URL` | Authorized database endpoint |
| `SUPABASE_KEY` | Credential allowed to call the required RPCs |
| `APPLY_IMG_URL` | Image rendered for the Apply button |
| `GIT_USER_NAME` | Commit author name |
| `GIT_USER_EMAIL` | Commit author email |

GitHub supplies `GITHUB_TOKEN` automatically. Give the workflow `contents: write` permission and ensure branch rules allow its push. Use **Actions → Get Jobs and Update Tables → Run workflow** to test. With compatible backend access, the existing daily schedule will refresh the tables.

## Conference project comparison

| Layer | Jobs repository | This conference project |
| --- | --- | --- |
| Collection | Upstream collection not included | Directory URL discovery plus official-site AI extraction |
| Data storage | External Supabase | Versioned JSON and CSV in repository |
| Runtime | Bun / TypeScript | Python standard library |
| Credentials | Supabase credentials and commit settings | Built-in GitHub token and the repository owner's Copilot allowance |
| Rendering | Marked Markdown tables | Marked four-column Markdown table |
| Scheduling | GitHub Actions, daily 12:00 UTC | GitHub Actions, daily 06:17 UTC |
| Extensibility | Database queries and table configuration | Source adapters and shared record schema |

The delivered workflow is ready to upload, but is not activated until it is pushed to your repository and GitHub Actions is enabled.
