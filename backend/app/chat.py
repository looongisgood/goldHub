from .models import Dataset


def answer_from_dataset(dataset: Dataset, message: str) -> str:
    """Return a deterministic response based only on the persisted snapshot."""
    if not dataset.projects:
        return "This dataset has no projects."
    question = message.lower()
    for project in dataset.projects:
        if project.repository_path.lower() in question or project.name.lower() in question:
            return f"{project.repository_path}: {project.description}"
    most_starred = max(dataset.projects, key=lambda project: project.stars)
    if "star" in question or "popular" in question:
        return f"{most_starred.repository_path} has {most_starred.stars} stars."
    projects = ", ".join(project.repository_path for project in dataset.projects[:5])
    return f"This dataset contains {projects}. Ask about a project name or which project has the most stars."
