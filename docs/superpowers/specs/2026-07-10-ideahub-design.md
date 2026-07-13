# IdeaHub Design

## Decision

Build a full-stack, self-hostable project-discovery service and a reusable Codex skill in this repository. The app works without proprietary AI credentials: GitHub repository search and deterministic project comparison are available immediately; an optional OpenAI-compatible chat endpoint can be configured later.

## Alternatives considered

1. **Static browser-only tool** — quickest, but cannot securely use a GitHub token or retain shared datasets.
2. **Full-stack local-first service (selected)** — FastAPI owns GitHub access, SQLite owns search datasets, and a React dashboard provides the discovery workflow. Docker Compose makes the service portable.
3. **GitHub-only Codex skill** — reusable but has no persistent browser experience for search history or project comparison.

## User workflow

1. Enter an idea and optional language/star filters.
2. The backend converts the idea into a GitHub repository query, retrieves public repositories, normalizes their metadata, and persists the result as a dataset.
3. Browse visual project cards showing owner, repository, description, stars, language, topics, image/avatar, and repository path.
4. Open a dataset and ask chat-style questions. The backend answers from that dataset only, with deterministic comparisons when no model provider is configured.
5. Deploy the same service through Docker Compose; configure a GitHub token and optional chat provider through environment variables.

## Architecture

```text
React dashboard ──HTTP──> FastAPI
                              ├── GitHub REST search API
                              ├── SQLite datasets and chat messages
                              └── optional OpenAI-compatible chat API
```

The backend stores one immutable snapshot per search in `backend/data/ideahub.db`; a dataset contains its original query and normalized projects. Repository owner avatars are used as project thumbnails, avoiding screenshot scraping and copyright-sensitive image capture.

## Scope and constraints

- Search public GitHub repositories only; never clone, scan private repositories, or expose a GitHub token to the browser.
- Persist every successful search as a dataset; dataset project records include image URL and `owner/name` path.
- Use SQLite by default and Docker Compose for local/server deployment.
- Return useful search and dataset behavior with no GitHub token, subject to GitHub's anonymous rate limits.
- Remote deployment is not attempted until a host, domain, and access method are supplied.

## Acceptance checks

- Backend tests prove query normalization, dataset persistence, dataset retrieval, and dataset-grounded chat responses.
- Frontend build succeeds and renders search, dataset, project-card, and chat UI.
- Docker Compose starts the service and the health endpoint returns `200`.
- The reusable `search-github-projects` skill passes its structural validator and documents search, persistence, and deployment steps.
