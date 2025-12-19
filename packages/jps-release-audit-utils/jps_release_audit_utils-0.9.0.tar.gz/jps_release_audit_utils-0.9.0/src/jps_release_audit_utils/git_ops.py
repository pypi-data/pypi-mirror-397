import logging
import typer

from typing import Dict, List
from datetime import datetime
from git import Repo
from .repo_helper import extract_pr_number


logger = logging.getLogger(__name__)


def get_branch_commits(repo: Repo, branch_name: str) -> Dict[str, dict]:
    """
    Return commit_hash -> metadata dict for a single branch:

        {
            "datetime": datetime,
            "date": "YYYY-MM-DD",
            "message": str,
            "author": "Name <email>",
            "pr": str,
        }
    
    Automatically checks out the branch and pulls from origin before reading commits.
    """
    logger.info("Loading commits for branch: %s", branch_name)

    # Check for uncommitted changes
    if repo.is_dirty(untracked_files=False):
        raise typer.Exit(
            f"ERROR: Repository has uncommitted changes. "
            f"Please commit or stash changes before running this tool."
        )

    # Checkout the branch
    try:
        logger.info("  Checking out branch: %s", branch_name)
        repo.git.checkout(branch_name)
    except Exception as e:
        raise typer.Exit(f"ERROR: Failed to checkout branch '{branch_name}': {e}")

    # Pull from origin
    try:
        logger.info("  Pulling latest changes from origin/%s", branch_name)
        repo.git.pull("origin", branch_name)
    except Exception as e:
        logger.warning("  Warning: Failed to pull from origin/%s: %s", branch_name, e)
        logger.warning("  Continuing with local branch state...")

    commit_map: Dict[str, dict] = {}

    for commit in repo.iter_commits(branch_name):
        dt = datetime.fromtimestamp(commit.authored_date)
        date_str = dt.strftime("%Y-%m-%d")
        msg = commit.message.strip().replace("\n", " ")
        author = f"{commit.author.name} <{commit.author.email}>"
        pr_num = extract_pr_number(msg)

        commit_map[commit.hexsha] = {
            "datetime": dt,
            "date": date_str,
            "message": msg,
            "author": author,
            "pr": pr_num,
        }

    logger.info("  Found %d commits in %s", len(commit_map), branch_name)
    return commit_map


def get_topo_sorted_commits(repo: Repo, branches: List[str]) -> List[str]:
    """
    Use git rev-list --topo-order <branches...> to get commit hashes
    in true Git ancestry order.
    """
    logger.info("Computing topological order across branches: %s", branches)
    rev_output = repo.git.rev_list("--topo-order", *branches)
    hexshas = [line.strip() for line in rev_output.splitlines() if line.strip()]
    logger.info("Topological commit count: %d", len(hexshas))
    return hexshas

