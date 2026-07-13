---
name: search-github-projects
description: Use when finding public GitHub repositories for a product idea, saving search results as a UI-ready dataset, or deploying the IdeaHub discovery service.
---

# Search GitHub Projects

Turn a product idea into a reproducible public-repository dataset. Keep discovery data separate from credentials and deploy IdeaHub itself—not a discovered repository—unless the user explicitly asks to deploy that repository.

## Workflow

1. Clarify the idea, desired technology, license constraints, and minimum maintenance signal. Treat the user's natural-language request as the dataset `idea`.
2. Build a traceable GitHub repository-search query. Use the GitHub REST API and an optional server-side `GITHUB_TOKEN`; never put a token in browser code, a dataset, or command output.
3. Normalize results to the schema in [references/dataset-schema.md](references/dataset-schema.md). Use the GitHub owner avatar for `image_url` and `owner/name` for `repository_path`.
4. Save one immutable JSON file per successful search under `datasets/`. Set `SKILL_DIR` to this skill's real folder and use a timestamp plus UUID so an existing dataset cannot be replaced:

   ```bash
   export SKILL_DIR=/absolute/path/to/search-github-projects
   dataset_id="$(date -u +%Y%m%dT%H%M%SZ)-$(uuidgen | tr '[:upper:]' '[:lower:]')"
   python3 "$SKILL_DIR/scripts/save_dataset.py" \
     --file normalized-results.json \
     --out "datasets/${dataset_id}.json"
   python3 "$SKILL_DIR/scripts/validate_dataset.py" --file "datasets/${dataset_id}.json"
   ```

5. Rank results transparently by relevance, stars, update date, license, and archived state. Preserve the GitHub query and retrieval time.
6. For IdeaHub deployment, configure `GITHUB_TOKEN`, optional `OPENAI_BASE_URL`/`OPENAI_API_KEY`, and `APP_PORT` in `.env`, then run:

   ```bash
   docker compose up --build -d
   curl -fsS http://localhost:${APP_PORT:-8080}/api/health
   ```

## GitHub search

Use repository search only; do not clone code or inspect private repositories. IdeaHub requests one sorted result set of up to 20 repositories for each saved dataset; request further pages only when the user asks for broader coverage, deduplicate by repository ID, and handle rate-limit responses before retrying.

```bash
auth=()
if [ -n "${GITHUB_TOKEN:-}" ]; then
  auth=(-H "Authorization: Bearer $GITHUB_TOKEN")
fi

curl --fail-with-body -G \
  -H 'Accept: application/vnd.github+json' \
  "${auth[@]}" \
  --data-urlencode 'q=knowledge base language:TypeScript stars:>30' \
  --data-urlencode 'sort=updated' \
  --data-urlencode 'order=desc' \
  https://api.github.com/search/repositories
```

If `GITHUB_TOKEN` is absent, omit the Authorization header and tell the user that anonymous rate limits apply.

## Dataset rules

- Store only normalized public metadata in the dataset. Keep raw API snapshots separately and redact authorization headers or secret-like keys.
- Require `id`, `idea`, `searched_at`, `github_query`, and a non-empty `projects` list.
- Require every project to contain `repository_path`, `repository_url`, and `image_url`; the web UI relies on them.
- Record license and archived state. Label unknown or incompatible licensing for review; never infer legal compatibility.
- Do not add user tokens, copied source code, or private data to datasets.

## Deployment boundary

Docker deployment here means the IdeaHub service that searches and presents the dataset. Do not combine untrusted discovered projects into the IdeaHub Compose file. Only deploy a discovered repository after a separate explicit request, source review, and dedicated deployment plan.

For remote deployment, first obtain the target host, access method, domain/port, and rollback expectation. Build locally, run the health endpoint, then deploy through the user-authorized environment.
