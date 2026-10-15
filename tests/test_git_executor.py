from pathlib import Path
import sys

import pytest
from git import Repo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from apeswarm.core import git_executor as executor

PATCH = "--- a/example.txt\n+++ b/example.txt\n@@ -1 +1 @@\n-before\n+after\n"


@pytest.fixture
def repo(tmp_path):
    repository = Repo.init(tmp_path)
    with repository.config_writer() as config:
        config.set_value("core", "autocrlf", "false")
        config.set_value("user", "name", "Test")
        config.set_value("user", "email", "test@example.invalid")
    (tmp_path / "example.txt").write_text("before\n", newline="\n")
    repository.index.add(["example.txt"])
    repository.index.commit("initial")
    yield repository
    repository.close()


def apply(repo, **kwargs):
    return executor.create_branch_and_commit(
        PATCH, "feat/test", "Apply test", Path(repo.working_tree_dir), **kwargs
    )


def test_dry_run_does_not_mutate(repo):
    before = repo.head.commit.hexsha
    assert "Dry-run" in apply(repo)
    assert repo.head.commit.hexsha == before
    assert "feat/test" not in repo.heads
    assert not repo.is_dirty(untracked_files=True)


def test_declined_confirmation_does_not_mutate(repo, monkeypatch):
    monkeypatch.setattr(executor, "_confirm", lambda preview: False)
    assert "Cancelled" in apply(repo, allow_write=True)
    assert "feat/test" not in repo.heads
    assert not repo.is_dirty(untracked_files=True)


def test_confirmed_patch_commits_only_patch(repo, monkeypatch):
    monkeypatch.setattr(executor, "_confirm", lambda preview: PATCH in preview)
    assert "successfully" in apply(repo, allow_write=True)
    assert repo.active_branch.name == "feat/test"
    assert repo.head.commit.message == "Apply test"
    assert (Path(repo.working_tree_dir) / "example.txt").read_text() == "after\n"
    assert not repo.is_dirty(untracked_files=True)


def test_existing_branch_not_reset(repo):
    branch = repo.create_head("feat/test")
    before = branch.commit.hexsha
    assert "already exists" in apply(repo, allow_write=True, auto_confirm=True)
    assert branch.commit.hexsha == before
    assert repo.active_branch.name != "feat/test"


def test_unrelated_changes_rejected(repo):
    (Path(repo.working_tree_dir) / "private.txt").write_text("unrelated")
    assert "existing changes" in apply(repo, allow_write=True, auto_confirm=True)
    assert "feat/test" not in repo.heads


def test_invalid_patch_fails_before_branch_creation(repo):
    result = executor.create_branch_and_commit(
        "not a patch", "feat/test", "test", Path(repo.working_tree_dir),
        allow_write=True, auto_confirm=True,
    )
    assert "Failed" in result
    assert "feat/test" not in repo.heads


def test_non_repository_returns_failure(tmp_path):
    assert "Failed" in executor.create_branch_and_commit(PATCH, "feat/test", "test", tmp_path)


def test_existing_plan_interactive_confirmation(repo, monkeypatch):
    (Path(repo.working_tree_dir) / "example.txt").write_text("updated\n")
    monkeypatch.setattr(executor, "_confirm", lambda preview: "updated" in preview)
    result = executor.execute_git_plan(
        "Branch Name: feat/plan\nCommit Message: planned", Path(repo.working_tree_dir), True, False
    )
    assert "successfully" in result
    assert repo.active_branch.name == "feat/plan"


def test_noninteractive_confirmation_fails_closed(monkeypatch):
    class Noninteractive:
        def isatty(self):
            return False
    monkeypatch.setattr(executor.sys, "stdin", Noninteractive())
    assert executor._confirm("preview") is False
