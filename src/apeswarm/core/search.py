from pathlib import Path
import re


def _extract_keywords(goal: str) -> list[str]:
	tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", goal.lower())
	filtered = [token for token in tokens if token not in {"the", "and", "for", "with", "this"}]
	return filtered[:8]


def collect_repo_context(goal: str, repo_root: Path, max_hits: int = 20) -> str:
	keywords = _extract_keywords(goal)
	if not keywords:
		return "No keywords extracted from goal."

	allowed_suffixes = {".py", ".md", ".toml", ".yml", ".yaml", ".txt"}
	hits: list[str] = []

	for file_path in repo_root.rglob("*"):
		if len(hits) >= max_hits:
			break
		if not file_path.is_file():
			continue
		if ".git" in file_path.parts or "__pycache__" in file_path.parts:
			continue
		if file_path.suffix and file_path.suffix.lower() not in allowed_suffixes:
			continue
		try:
			content = file_path.read_text(encoding="utf-8", errors="ignore")
		except OSError:
			continue
		lines = content.splitlines()
		for idx, line in enumerate(lines, start=1):
			line_lower = line.lower()
			if any(keyword in line_lower for keyword in keywords):
				rel = file_path.relative_to(repo_root)
				hits.append(f"{rel}:{idx}: {line.strip()}")
				if len(hits) >= max_hits:
					break

	if not hits:
		return "No repository matches found for extracted keywords."
	return "\n".join(hits)