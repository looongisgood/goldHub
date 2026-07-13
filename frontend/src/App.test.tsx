import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import App from "./App";


const dataset = {
  id: 7,
  idea: "self-hosted knowledge base",
  searched_at: "2026-07-10T12:00:00Z",
  github_query: "knowledge base",
  projects: [{
    repository_path: "octo/knowledge-base",
    repository_url: "https://github.com/octo/knowledge-base",
    image_url: "https://avatars.githubusercontent.com/u/1",
    name: "knowledge-base",
    owner: "octo",
    description: "A self-hosted knowledge base",
    stars: 250,
    language: "TypeScript",
    topics: ["knowledge-base"],
    license: "MIT",
    updated_at: "2026-07-01T00:00:00Z",
    archived: false,
  }],
};

const searchedDataset = {
  ...dataset,
  id: 8,
  idea: "local-first notes",
  projects: [{ ...dataset.projects[0], repository_path: "codex/local-notes", name: "local-notes" }],
};


beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/api/datasets")) {
      return new Response(JSON.stringify([dataset]), { status: 200 });
    }
    if (url.endsWith("/api/search")) {
      return new Response(JSON.stringify(searchedDataset), { status: 201 });
    }
    if (url.endsWith("/api/datasets/7/chat")) {
      return new Response(JSON.stringify({ dataset_id: 7, answer: "octo/knowledge-base has 250 stars." }), { status: 200 });
    }
    throw new Error(`Unexpected request: ${url}`);
  }));
});


test("shows a saved project's image and repository path", async () => {
  render(<App />);

  expect(await screen.findByText("octo/knowledge-base")).toBeInTheDocument();
  expect(screen.getByRole("img", { name: "knowledge-base project" })).toHaveAttribute(
    "src", "https://avatars.githubusercontent.com/u/1"
  );
  expect(screen.getByRole("link", { name: /open repository/i })).toHaveAttribute(
    "href", "https://github.com/octo/knowledge-base"
  );
});


test("sends chat questions against the selected dataset", async () => {
  render(<App />);
  await screen.findByText("octo/knowledge-base");

  fireEvent.change(screen.getByLabelText("Ask about this dataset"), {
    target: { value: "Which project has the most stars?" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() => expect(screen.getByText("octo/knowledge-base has 250 stars.")).toBeInTheDocument());
  expect(fetch).toHaveBeenCalledWith("/api/datasets/7/chat", expect.objectContaining({ method: "POST" }));
});


test("searches for an idea and selects the returned dataset", async () => {
  render(<App />);
  await screen.findByText("octo/knowledge-base");

  fireEvent.change(screen.getByLabelText("Idea"), { target: { value: "local-first notes" } });
  fireEvent.change(screen.getByLabelText("Language"), { target: { value: "TypeScript" } });
  fireEvent.change(screen.getByLabelText("Minimum stars"), { target: { value: "50" } });
  fireEvent.click(screen.getByRole("button", { name: "Search projects" }));

  expect(await screen.findByText("codex/local-notes")).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledWith("/api/search", expect.objectContaining({
    method: "POST",
    body: JSON.stringify({ idea: "local-first notes", language: "TypeScript", min_stars: 50 }),
  }));
});
