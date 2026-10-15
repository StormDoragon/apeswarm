from pathlib import Path
import re
import sys
import tempfile

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo


def _confirm(preview: str) -> bool:
	print(preview)
	if not sys.stdin.isatty():
		return False
	try:
		return input("Create this branch and commit these changes? [y/N] ").strip().lower() == "y"
	except (EOFError, KeyboardInterrupt):
		return False


def create_branch_and_commit(
	diff: str, branch_name: str, commit_msg: str,
	repo_root: Path | None = None, *, allow_write: bool = False,
	auto_confirm: bool = False,
) -> str:
	"""Apply a reviewed unified diff to a clean repository; default to preview only."""
	preview = f"Branch Name: {branch_name}\nCommit Message: {commit_msg}\nDiff:\n{diff}"
	try:
		repo = Repo(repo_root or Path.cwd())
		if repo.bare or not repo.head.is_valid():
			return "Action: Failed. A non-bare repository with an initial commit is required."
		repo.git.check_ref_format("--branch", branch_name)
		if branch_name in repo.heads:
			return "Action: Failed. Branch already exists; it will not be reset."
		if not commit_msg.strip() or not diff.strip():
			return "Action: Failed. A nonempty diff and commit message are required."
		if repo.is_dirty(untracked_files=True):
			return "Action: Failed. Commit or stash existing changes before applying a diff."
		with tempfile.TemporaryDirectory(prefix="gitape-") as directory:
			patch = Path(directory) / "changes.patch"
			patch.write_text(diff, encoding="utf-8", newline="\n")
			repo.git.apply("--check", "--index", str(patch))
			if not allow_write:
				return preview + "\nAction: Dry-run only. Patch checked; no git changes were applied."
			if not auto_confirm and not _confirm(preview):
				return preview + "\nAction: Cancelled. No git changes were applied."
			# Never reset an existing branch or include unrelated worktree files.
			repo.git.checkout("-b", branch_name)
			repo.git.apply("--index", str(patch))
			commit = repo.index.commit(commit_msg)
			return f"Action: Commit created successfully: {commit.hexsha} on {branch_name}."
	except (GitCommandError, InvalidGitRepositoryError, NoSuchPathError, OSError, ValueError) as error:
		return f"Action: Failed: {error}. Inspect git status before retrying."


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

	try:
		repo = Repo(repo_root)
		if repo.bare:
			return preamble + "Action: Failed. Repository is bare."
		repo.git.check_ref_format("--branch", branch_name)
		if branch_name in repo.heads:
			return preamble + "Action: Failed. Branch already exists; it will not be reset."
		if not repo.is_dirty(untracked_files=True):
			return preamble + "Action: No changes to commit."
		preview = preamble + repo.git.status("--short") + "\n" + repo.git.diff("HEAD")
		if not allow_write:
			return preview + "\nAction: Dry-run only. No git changes were applied."
		if not auto_confirm and not _confirm(preview):
			return preamble + "Action: Cancelled. No git changes were applied."
		repo.git.checkout("-b", branch_name)
		repo.git.add(A=True)
		
		repo.index.commit(commit_message)
		
		# Build post-commit summary
		try:
			commit_hash = repo.head.commit.hexsha[:7]
			changed_files = []
			if repo.head.commit.parents:
				changed_files = list(repo.index.diff(repo.head.commit.parents[0]))
			
			# Get remote URL safely
			remote_url = ""
			if repo.remotes:
				try:
					remote_url = list(repo.remotes.origin.urls)[0] if hasattr(repo.remotes, 'origin') else ""
				except Exception:
					remote_url = ""
			
			summary = (
				f"Action: Branch created/updated and commit written successfully.\n"
				f"\n"
				f"═══════════════════════════════════════════════════════════\n"
				f"POST-COMMIT SUMMARY\n"
				f"═══════════════════════════════════════════════════════════\n"
				f"✅ Commit Created: {commit_hash}\n"
				f"📦 Branch: {branch_name}\n"
				f"📝 Message: {commit_message}\n"
				f"📄 Files Changed: {len(changed_files)}\n"
				f"\n"
				f"NEXT STEPS:\n"
				f"  → Review changes: git show {commit_hash}\n"
				f"  → Push branch: git push -u origin {branch_name}\n"
				f"  → Create PR: gh pr create\n"
				f"  → Merge when ready: gh pr merge --squash\n"
				f"\n"
				f"ℹ️  Current branch: {repo.active_branch.name}\n"
				f"🔗 Remote: {remote_url if remote_url else 'not configured'}\n"
				f"═══════════════════════════════════════════════════════════"
			)
		except Exception as e:
			summary = f"Action: Branch and commit created, but summary generation failed: {e}"
		
		return preamble + summary
	except (GitCommandError, InvalidGitRepositoryError, NoSuchPathError, OSError, ValueError) as error:
		return preamble + f"Action: Git command failed: {error}"
