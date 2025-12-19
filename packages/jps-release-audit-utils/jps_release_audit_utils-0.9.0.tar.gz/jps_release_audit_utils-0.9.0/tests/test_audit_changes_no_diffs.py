import subprocess
import os
from typer.testing import CliRunner

from jps_release_audit_utils.git_true_changes_report import app

runner = CliRunner()


def test_no_changes_produces_clean_output(temp_git_repo):
    repo = temp_git_repo

    f = repo / "clean.txt"
    f.write_text("hello\n")
    subprocess.run(["git", "add", "clean.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True)

    # Change to repo directory and run test there
    original_cwd = os.getcwd()
    try:
        os.chdir(repo)
        result = runner.invoke(
            app,
            ["audit-changes", "--fail-if-changed"],
        )
    finally:
        os.chdir(original_cwd)

    assert result.exit_code == 0
    assert "No true content modifications" in result.stdout
