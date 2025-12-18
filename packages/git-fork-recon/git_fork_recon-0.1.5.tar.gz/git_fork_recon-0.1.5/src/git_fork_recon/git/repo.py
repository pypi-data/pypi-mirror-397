from dataclasses import dataclass
from typing import List, Optional
import logging
from pathlib import Path
import shutil

from git import Repo, Remote
from git.exc import GitCommandError

from ..github.api import RepoInfo, ForkInfo
from ..config import Config

logger = logging.getLogger(__name__)


@dataclass
class CommitInfo:
    """Information about a commit."""

    hash: str
    message: str
    author: str
    date: str
    files_changed: List[str]
    insertions: int
    deletions: int


class GitRepo:
    def __init__(self, repo_info: RepoInfo, config: Config, force_fetch: bool = False):
        self.repo_info = repo_info
        self.cache_dir = config.cache_repo
        self.repo_dir = self.cache_dir / repo_info.owner / repo_info.name
        self.force_fetch = force_fetch
        self._ensure_repo()

    def _ensure_repo(self) -> None:
        """Ensure the repository is cloned and up to date."""
        if not self.repo_dir.exists():
            logger.info(f"Cloning {self.repo_info.clone_url}")
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.repo = Repo.clone_from(self.repo_info.clone_url, self.repo_dir)
        else:
            logger.info(f"Using existing clone at {self.repo_dir}")
            self.repo = Repo(self.repo_dir)
            if self.force_fetch:
                try:
                    self.repo.remotes.origin.fetch()
                except GitCommandError as e:
                    logger.warning(f"Failed to fetch origin: {e}")
            else:
                logger.info("Cached repository found, skipping fetch")

    def add_fork(self, fork: ForkInfo) -> None:
        """Add a fork as a remote and fetch its contents."""
        remote_name = f"fork-{fork.repo_info.owner}"

        try:
            # Check if remote already exists
            remote = self.repo.remote(remote_name)
            logger.debug(
                f"Remote {remote_name} already exists, checking if URL matches"
            )
            logger.debug(f"Remote URL: {remote.url}, Fork URL: {fork.repo_info.clone_url}")

            # Normalize URLs for comparison (strip trailing .git and trailing slashes)
            def normalize_url(url: str) -> str:
                url = url.rstrip("/")
                if url.endswith(".git"):
                    url = url[:-4]
                return url

            remote_url_normalized = normalize_url(str(remote.url))
            fork_url_normalized = normalize_url(fork.repo_info.clone_url)

            # Check if the remote URL matches
            if remote_url_normalized == fork_url_normalized or remote.url == fork.repo_info.clone_url:
                logger.info(
                    f"Fork {fork.repo_info.owner}/{fork.repo_info.name} already cached as remote {remote_name}, skipping fetch"
                )
                if self.force_fetch:
                    logger.info(f"Force fetching remote {remote_name}")
                    try:
                        remote.fetch()
                        return
                    except GitCommandError as e:
                        logger.warning(
                            f"Failed to fetch existing remote {remote_name}: {e}"
                        )
                else:
                    return

            # If URL doesn't match or fetch failed, remove the remote
            logger.info(
                f"Remote {remote_name} exists but URL doesn't match (remote: {remote.url}, fork: {fork.repo_info.clone_url}), removing and re-adding"
            )
            remote.remove()

        except ValueError:
            # Remote doesn't exist, which is fine
            logger.debug(f"Remote {remote_name} doesn't exist, will create new remote")
            pass

        # Add new remote (always fetch new remotes)
        logger.info(f"Adding new remote {remote_name} for {fork.repo_info.clone_url}")
        remote = self.repo.create_remote(remote_name, fork.repo_info.clone_url)
        try:
            remote.fetch()
        except GitCommandError as e:
            logger.warning(f"Failed to fetch {remote_name}: {e}")
            remote.remove()
            raise

    def get_fork_commits(self, fork: ForkInfo) -> List[CommitInfo]:
        """Get commits that exist in the fork but not in the parent."""
        remote_name = f"fork-{fork.repo_info.owner}"
        try:
            remote = self.repo.remote(remote_name)
        except ValueError:
            self.add_fork(fork)
            remote = self.repo.remote(remote_name)

        # Get commits that are in the fork but not in parent
        parent_ref = f"origin/{self.repo_info.default_branch}"
        fork_ref = f"{remote_name}/{fork.repo_info.default_branch}"

        commits = []
        for commit in self.repo.iter_commits(f"{parent_ref}..{fork_ref}"):
            # Get stats for the commit
            stats = commit.stats.total

            commits.append(
                CommitInfo(
                    hash=commit.hexsha,
                    message=commit.message.strip(),
                    author=f"{commit.author.name} <{commit.author.email}>",
                    date=commit.committed_datetime.isoformat(),
                    files_changed=list(commit.stats.files.keys()),
                    insertions=stats["insertions"],
                    deletions=stats["deletions"],
                )
            )

        return commits

    def get_file_diff(self, fork: ForkInfo, file_path: str) -> str:
        """Get the diff for a specific file between parent and fork."""
        remote_name = f"fork-{fork.repo_info.owner}"
        parent_ref = f"origin/{self.repo_info.default_branch}"
        fork_ref = f"{remote_name}/{fork.repo_info.default_branch}"

        diff = self.repo.git.diff(parent_ref, fork_ref, "--", file_path)
        return diff

    def cleanup(self) -> None:
        """Remove the local repository."""
        if self.repo_dir.exists():
            shutil.rmtree(self.repo_dir)
