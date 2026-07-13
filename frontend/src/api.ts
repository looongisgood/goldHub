export type Project = {
  repository_path: string;
  repository_url: string;
  image_url: string;
  name: string;
  owner: string;
  description: string | null;
  stars: number;
  language: string | null;
  topics: string[];
  license: string | null;
  updated_at: string | null;
  archived: boolean;
};

export type Dataset = {
  id: number;
  idea: string;
  searched_at: string;
  github_query: string;
  projects: Project[];
};

type SearchInput = {
  idea: string;
  language?: string;
  min_stars?: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    throw new Error(`Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function listDatasets(): Promise<Dataset[]> {
  return request<Dataset[]>("/api/datasets");
}

export function searchProjects(input: SearchInput): Promise<Dataset> {
  return request<Dataset>("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
}

export function askDataset(datasetId: number, message: string): Promise<{ answer: string }> {
  return request<{ answer: string }>(`/api/datasets/${datasetId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
}
