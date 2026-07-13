import { FormEvent, useEffect, useState } from "react";

import { askDataset, Dataset, listDatasets, Project, searchProjects } from "./api";

function ProjectCard({ project }: { project: Project }) {
  return (
    <article className="project-card">
      <img className="project-image" src={project.image_url} alt={`${project.name} project`} />
      <div className="project-body">
        <div className="project-heading">
          <h3>{project.repository_path}</h3>
          <span aria-label={`${project.stars} stars`}>★ {project.stars.toLocaleString()}</span>
        </div>
        <p>{project.description || "No description provided."}</p>
        <div className="project-meta">
          {project.language && <span>{project.language}</span>}
          {project.license && <span>{project.license}</span>}
          {project.archived && <span>Archived</span>}
        </div>
        <a href={project.repository_url} target="_blank" rel="noreferrer">Open repository</a>
      </div>
    </article>
  );
}

export default function App() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [idea, setIdea] = useState("");
  const [language, setLanguage] = useState("");
  const [minStars, setMinStars] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  const [searching, setSearching] = useState(false);
  const [asking, setAsking] = useState(false);

  const selectedDataset = datasets.find((dataset) => dataset.id === selectedId) ?? null;

  useEffect(() => {
    listDatasets()
      .then((loaded) => {
        setDatasets(loaded);
        setSelectedId((current) => current ?? loaded[0]?.id ?? null);
      })
      .catch(() => setError("Could not load saved datasets."));
  }, []);

  async function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!idea.trim()) return;

    setSearching(true);
    setError("");
    try {
      const dataset = await searchProjects({
        idea: idea.trim(),
        ...(language.trim() ? { language: language.trim() } : {}),
        ...(minStars ? { min_stars: Number(minStars) } : {}),
      });
      setDatasets((current) => [dataset, ...current.filter((item) => item.id !== dataset.id)]);
      setSelectedId(dataset.id);
      setAnswer("");
    } catch {
      setError("Search failed. Please try again.");
    } finally {
      setSearching(false);
    }
  }

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedDataset || !question.trim()) return;

    setAsking(true);
    setError("");
    try {
      const response = await askDataset(selectedDataset.id, question.trim());
      setAnswer(response.answer);
      setQuestion("");
    } catch {
      setError("Could not answer that question.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">IdeaHub</p>
        <h1>Find the building blocks for your next idea.</h1>
        <p>Search public GitHub projects, save a focused dataset, and ask it the questions that matter.</p>
      </header>

      <section className="search-panel" aria-label="Search GitHub projects">
        <form onSubmit={submitSearch}>
          <label>
            Idea
            <input value={idea} onChange={(event) => setIdea(event.target.value)} placeholder="e.g. self-hosted knowledge base" required />
          </label>
          <label>
            Language
            <input value={language} onChange={(event) => setLanguage(event.target.value)} placeholder="Optional" />
          </label>
          <label>
            Minimum stars
            <input type="number" min="0" value={minStars} onChange={(event) => setMinStars(event.target.value)} placeholder="Optional" />
          </label>
          <button type="submit" disabled={searching}>{searching ? "Searching…" : "Search projects"}</button>
        </form>
      </section>

      {error && <p className="error" role="alert">{error}</p>}

      <section className="workspace">
        <aside className="datasets" aria-label="Saved datasets">
          <h2>Saved datasets</h2>
          {datasets.length === 0 ? <p>No datasets saved yet.</p> : (
            <div className="dataset-list">
              {datasets.map((dataset) => (
                <button
                  className={dataset.id === selectedId ? "dataset active" : "dataset"}
                  key={dataset.id}
                  onClick={() => { setSelectedId(dataset.id); setAnswer(""); }}
                  type="button"
                >
                  <strong>{dataset.idea}</strong>
                  <span>{dataset.projects.length} projects</span>
                </button>
              ))}
            </div>
          )}
        </aside>

        <section className="results" aria-live="polite">
          {selectedDataset ? <>
            <div className="dataset-title">
              <div>
                <p className="eyebrow">Dataset #{selectedDataset.id}</p>
                <h2>{selectedDataset.idea}</h2>
              </div>
              <span>{selectedDataset.projects.length} projects</span>
            </div>
            <div className="project-grid">
              {selectedDataset.projects.map((project) => <ProjectCard key={project.repository_url} project={project} />)}
            </div>
          </> : <div className="empty-state"><h2>Start with an idea</h2><p>Your saved project datasets will appear here.</p></div>}
        </section>
      </section>

      {selectedDataset && <section className="chat-panel">
        <h2>Ask this dataset</h2>
        <form onSubmit={submitQuestion}>
          <label htmlFor="dataset-question">Ask about this dataset</label>
          <div className="chat-input">
            <input id="dataset-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Which project has the most stars?" required />
            <button type="submit" disabled={asking}>{asking ? "Thinking…" : "Send"}</button>
          </div>
        </form>
        {answer && <p className="answer">{answer}</p>}
      </section>}
    </main>
  );
}
