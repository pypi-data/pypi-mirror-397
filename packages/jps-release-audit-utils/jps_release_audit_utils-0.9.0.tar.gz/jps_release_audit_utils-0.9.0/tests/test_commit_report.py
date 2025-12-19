import pytest
from typer.testing import CliRunner
from unittest.mock import Mock, MagicMock, patch, call
from git import Repo

from jps_release_audit_utils.config_loader import load_config
from jps_release_audit_utils.constants import DEFAULT_SHEET_NAMES, DEFAULT_COLORS
from jps_release_audit_utils.commit_report import app
from jps_release_audit_utils.git_ops import get_branch_commits

runner = CliRunner()


def test_cli_help_runs():
    """Ensure the CLI help command executes successfully."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout or "Usage" in result.stderr


def test_load_config_defaults():
    """Ensure load_config returns default values when config is missing."""
    sheet_names, colors = load_config(config_path=None, required=False)

    assert isinstance(sheet_names, dict)
    assert isinstance(colors, dict)

    assert sheet_names["timeline_by_date"] == DEFAULT_SHEET_NAMES["timeline_by_date"]
    assert colors["missing"] == DEFAULT_COLORS["missing"]


def test_load_config_with_custom_file(tmp_path):
    """Ensure YAML config overrides defaults correctly."""

    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
        sheets:
          timeline_by_date: "CustomDateSheet"
        colors:
          missing: "FF0000"
        """,
        encoding="utf-8",
    )

    sheet_names, colors = load_config(cfg, required=True)

    assert sheet_names["timeline_by_date"] == "CustomDateSheet"
    assert colors["missing"] == "FF0000"

    # Non-overridden values remain defaults
    assert sheet_names["timeline_by_topology"] == DEFAULT_SHEET_NAMES["timeline_by_topology"]
    assert colors["all_present"] == DEFAULT_COLORS["all_present"]


def test_cli_runs_with_minimal_args(tmp_path, monkeypatch):
    """
    Sanity check: Patch Repo() so no real git repo is required.
    Validate that CLI executes and fails cleanly with missing branches.
    """

    class DummyRepo:
        bare = False
        branches = {}
        def __init__(self, *args, **kwargs):
            self.git = Mock()
            # Make git.rev_list return empty string to avoid iteration issues
            self.git.rev_list.return_value = ""
            # Make git.checkout raise exception to simulate branch doesn't exist
            self.git.checkout.side_effect = Exception("Branch does not exist")
            
        def is_dirty(self, untracked_files=False):
            return False
            
        def iter_commits(self, branch_name):
            return []

    monkeypatch.setattr("jps_release_audit_utils.commit_report.Repo", DummyRepo)

    output_file = tmp_path / "report.xlsx"

    result = runner.invoke(
        app,
        [
            "--repo-path",
            str(tmp_path),
            "--branches",
            "main",
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code != 0
    # Error message changed due to new checkout logic
    assert ("Failed to checkout branch" in result.stdout or 
            "Failed to checkout branch" in result.stderr)


def test_get_branch_commits_checks_out_and_pulls():
    """Test that get_branch_commits performs checkout and pull operations."""
    mock_repo = Mock(spec=Repo)
    mock_repo.is_dirty.return_value = False
    mock_repo.git = Mock()
    
    # Mock the iter_commits to return empty list
    mock_repo.iter_commits.return_value = []
    
    branch_name = "test-branch"
    
    # Call the function
    result = get_branch_commits(mock_repo, branch_name)
    
    # Verify checkout was called
    mock_repo.git.checkout.assert_called_once_with(branch_name)
    
    # Verify pull was called
    mock_repo.git.pull.assert_called_once_with("origin", branch_name)
    
    # Should return empty dict since no commits
    assert result == {}


def test_get_branch_commits_exits_on_dirty_repo():
    """Test that get_branch_commits exits if repository has uncommitted changes."""
    from typer import Exit
    
    mock_repo = Mock(spec=Repo)
    mock_repo.is_dirty.return_value = True
    
    branch_name = "test-branch"
    
    # Should raise typer.Exit
    with pytest.raises(Exit):
        get_branch_commits(mock_repo, branch_name)
    
    # Should not attempt checkout or pull
    assert not mock_repo.git.checkout.called
    assert not mock_repo.git.pull.called


def test_get_branch_commits_handles_checkout_failure():
    """Test that get_branch_commits exits gracefully on checkout failure."""
    from typer import Exit
    
    mock_repo = Mock(spec=Repo)
    mock_repo.is_dirty.return_value = False
    mock_repo.git = Mock()
    mock_repo.git.checkout.side_effect = Exception("Branch does not exist")
    
    branch_name = "nonexistent-branch"
    
    # Should raise typer.Exit on checkout failure
    with pytest.raises(Exit):
        get_branch_commits(mock_repo, branch_name)


def test_get_branch_commits_continues_on_pull_failure():
    """Test that get_branch_commits continues if pull fails (e.g., network issue)."""
    mock_repo = Mock(spec=Repo)
    mock_repo.is_dirty.return_value = False
    mock_repo.git = Mock()
    mock_repo.git.pull.side_effect = Exception("Network error")
    
    # Mock the iter_commits to return a single commit
    mock_commit = Mock()
    mock_commit.hexsha = "abc123"
    mock_commit.authored_date = 1234567890
    mock_commit.message = "Test commit"
    mock_commit.author.name = "Test Author"
    mock_commit.author.email = "test@example.com"
    mock_repo.iter_commits.return_value = [mock_commit]
    
    branch_name = "test-branch"
    
    # Should not raise, but continue processing
    result = get_branch_commits(mock_repo, branch_name)
    
    # Verify checkout was called
    mock_repo.git.checkout.assert_called_once_with(branch_name)
    
    # Verify pull was attempted
    mock_repo.git.pull.assert_called_once_with("origin", branch_name)
    
    # Should still return commit data
    assert len(result) == 1
    assert "abc123" in result


def test_cli_restores_original_branch(tmp_path, monkeypatch):
    """Test that CLI restores the original branch after processing all branches."""
    
    class MockBranch:
        def __init__(self, name):
            self.name = name
    
    class DummyRepo:
        bare = False
        def __init__(self, *args, **kwargs):
            self.active_branch = MockBranch("original-branch")
            self._checkout_calls = []
            self.git = Mock()
            
        def is_dirty(self, untracked_files=False):
            return False
    
    # Track all instantiated repos
    repos = []
    original_repo_init = None
    
    def create_dummy_repo(*args, **kwargs):
        repo = DummyRepo(*args, **kwargs)
        repos.append(repo)
        return repo
    
    monkeypatch.setattr("jps_release_audit_utils.commit_report.Repo", create_dummy_repo)
    monkeypatch.setattr("jps_release_audit_utils.git_ops.Repo", Repo)  # Keep original for git_ops
    
    # Mock get_branch_commits to avoid actual git operations
    def mock_get_branch_commits(repo, branch_name):
        return {}
    
    monkeypatch.setattr(
        "jps_release_audit_utils.commit_report.get_branch_commits",
        mock_get_branch_commits
    )
    
    output_file = tmp_path / "report.xlsx"
    
    result = runner.invoke(
        app,
        [
            "--repo-path",
            str(tmp_path),
            "--branches",
            "branch1,branch2",
            "--output",
            str(output_file),
        ],
    )
    
    # Verify the repo instance was created
    assert len(repos) == 1
    repo = repos[0]
    
    # Verify checkout was called to restore original branch
    # The last checkout call should restore the original branch
    assert repo.git.checkout.called
    calls = repo.git.checkout.call_args_list
    # Last call should restore original branch
    assert calls[-1] == call("original-branch")


def test_get_branch_commits_processes_commits_correctly():
    """Test that get_branch_commits correctly processes commit metadata."""
    from datetime import datetime
    
    mock_repo = Mock(spec=Repo)
    mock_repo.is_dirty.return_value = False
    mock_repo.git = Mock()
    
    # Create mock commits with timezone-aware dates
    mock_commit1 = Mock()
    mock_commit1.hexsha = "abc123"
    # Use timestamp that converts cleanly: Jan 1, 2021 12:00 UTC
    mock_commit1.authored_date = 1609502400  # 2021-01-01 12:00:00 UTC
    mock_commit1.message = "First commit (#123)"
    mock_commit1.author.name = "Alice"
    mock_commit1.author.email = "alice@example.com"
    
    mock_commit2 = Mock()
    mock_commit2.hexsha = "def456"
    # Jan 2, 2021 12:00 UTC
    mock_commit2.authored_date = 1609588800  # 2021-01-02 12:00:00 UTC
    mock_commit2.message = "Second commit\nMultiline message"
    mock_commit2.author.name = "Bob"
    mock_commit2.author.email = "bob@example.com"
    
    mock_repo.iter_commits.return_value = [mock_commit1, mock_commit2]
    
    branch_name = "main"
    result = get_branch_commits(mock_repo, branch_name)
    
    # Verify both commits are in result
    assert len(result) == 2
    assert "abc123" in result
    assert "def456" in result
    
    # Verify commit1 metadata - date may vary by timezone
    commit1_data = result["abc123"]
    # Check date is in expected range (could be 2020-12-31 or 2021-01-01 depending on TZ)
    assert commit1_data["date"] in ["2020-12-31", "2021-01-01", "2021-01-02"]
    assert commit1_data["message"] == "First commit (#123)"
    assert commit1_data["author"] == "Alice <alice@example.com>"
    assert commit1_data["pr"] == "123"
    
    # Verify commit2 metadata (multiline message should be flattened)
    commit2_data = result["def456"]
    assert commit2_data["date"] in ["2021-01-01", "2021-01-02", "2021-01-03"]
    assert commit2_data["message"] == "Second commit Multiline message"
    assert commit2_data["author"] == "Bob <bob@example.com>"
    assert commit2_data["pr"] == ""
