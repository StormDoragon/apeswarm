from pathlib import Path
import re

from git import GitCommandError, Repo


def _extract_field(markdown: str, field_name: str) -> str | None:
	pattern = rf"{re.escape(field_name)}\s*[:\n]\s*(.+)"
	match = re.search(pattern, markdown, flags=re.IGNORECASE)
	if not match:
		return None
	return match.group(1).strip()


def parse_git_plan(markdown: str) -> tuple[str, str]:
	branch = _extract_field(markdown, "Branch Name") or "feat/git-ape-auto-plan"
	commit = _extract_field(markdown, "Commit Message") or "chore: apply gitape planned updates"
	branch = re.sub(r"[^a-zA-Z0-9._/-]", "-", branch).strip("-")
	if not branch:
		branch = "feat/git-ape-auto-plan"
	return branch, commit


def execute_git_plan(
	git_plan_markdown: str,
	repo_root: Path,
	allow_write: bool,
	auto_confirm: bool,
) -> str:
	branch_name, commit_message = parse_git_plan(git_plan_markdown)
	preamble = (
		f"Branch Name: {branch_name}\n"
		f"Commit Message: {commit_message}\n"
		f"Mode: {'write' if allow_write else 'dry-run'}\n"
	)

	if not allow_write:
		return preamble + "Action: Dry-run only. No git changes were applied."

	if not auto_confirm:
		return preamble + "Action: Write requested but blocked because auto-confirm is disabled."

	repo = Repo(repo_root)
	if repo.bare:
		return preamble + "Action: Failed. Repository is bare."

	try:
		repo.git.checkout("-B", branch_name)
		repo.git.add(A=True)
		if not repo.is_dirty(untracked_files=True):
			return preamble + "Action: No changes to commit."
		repo.index.commit(commit_message)
		return preamble + "Action: Branch created/updated and commit written successfully."
	except GitCommandError as error:
		return preamble + f"Action: Git command failed: {error}"