# IdeaHub dataset schema

```json
{
  "id": "dataset-20260710-001",
  "idea": "self-hosted idea discovery",
  "searched_at": "2026-07-10T12:00:00Z",
  "github_query": "idea discovery language:TypeScript",
  "projects": [{
    "repository_path": "owner/repository",
    "repository_url": "https://github.com/owner/repository",
    "image_url": "https://avatars.githubusercontent.com/u/123",
    "name": "repository",
    "owner": "owner",
    "description": "Public repository description",
    "stars": 42,
    "language": "TypeScript",
    "topics": ["ideas"],
    "license": "MIT",
    "updated_at": "2026-07-01T00:00:00Z",
    "archived": false
  }]
}
```

`repository_path`, `repository_url`, and `image_url` are required because they are displayed in every IdeaHub project card. `archived` keeps inactive repositories out of recommendations by default; the remaining fields provide sorting and context.
