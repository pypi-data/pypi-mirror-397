"""Git operations provider for safe document editing."""

import re
from pathlib import Path
from git import Repo, InvalidGitRepositoryError, GitCommandError
from src.domain.models import GitCheckpointResult, GitDiffSummary, DiffChange


class GitProvider:
    """Provides Git operations for document safety (checkpoint/rollback)."""

    def __init__(self, working_dir: str):
        """
        Initialize GitProvider.

        Args:
            working_dir: Working directory path
        """
        self.working_dir = Path(working_dir)
        self._repo: Repo | None = None

    @property
    def repo(self) -> Repo:
        """Get or initialize git repository."""
        if self._repo is None:
            self._repo = self._get_or_init_repo()
        return self._repo

    def _get_or_init_repo(self) -> Repo:
        """Get existing repo or initialize a new one."""
        try:
            repo = Repo(self.working_dir)
        except InvalidGitRepositoryError:
            # Initialize new repository
            repo = Repo.init(self.working_dir)

        # Create initial commit if repo is empty (no HEAD)
        if not repo.head.is_valid():
            # Stage all files
            repo.git.add(A=True)
            # Check if there are files to commit
            if repo.untracked_files or repo.git.diff("--cached", "--name-only"):
                repo.index.commit("Initial commit (MCP auto-init)")

        return repo

    def checkpoint(self, message: str = "MCP Checkpoint") -> GitCheckpointResult:
        """
        Create a git checkpoint (commit) of current state.

        Args:
            message: Commit message

        Returns:
            GitCheckpointResult with status
        """
        try:
            repo = self.repo

            # Check for changes
            has_changes = repo.is_dirty(untracked_files=True)

            if not has_changes:
                return GitCheckpointResult(
                    success=True,
                    commit_hash=None,
                    message="No changes to checkpoint",
                    files_staged=0
                )

            # Stage all changes
            repo.git.add(A=True)

            # Count staged files
            staged_files = len(repo.index.diff("HEAD"))
            untracked = len(repo.untracked_files)
            total_staged = staged_files + untracked

            # Create commit
            commit = repo.index.commit(message)

            return GitCheckpointResult(
                success=True,
                commit_hash=commit.hexsha[:7],
                message=f"Checkpoint created: {message}",
                files_staged=total_staged
            )

        except GitCommandError as e:
            return GitCheckpointResult(
                success=False,
                commit_hash=None,
                message=f"Git error: {str(e)}",
                files_staged=0
            )
        except Exception as e:
            return GitCheckpointResult(
                success=False,
                commit_hash=None,
                message=f"Error creating checkpoint: {str(e)}",
                files_staged=0
            )

    def diff_summary(self, structural_only: bool = True) -> GitDiffSummary:
        """
        Get summary of changes since last commit.

        Args:
            structural_only: If True, filter to show only structural changes
                           (headers, formulas) rather than all changes

        Returns:
            GitDiffSummary with change details
        """
        try:
            repo = self.repo

            # Check if there are any commits
            if not repo.head.is_valid():
                return GitDiffSummary(
                    has_changes=False,
                    changes=[],
                    summary="No commits in repository"
                )

            # Get diff against HEAD
            has_staged = bool(repo.index.diff("HEAD"))
            has_unstaged = repo.is_dirty()
            has_untracked = bool(repo.untracked_files)

            if not (has_staged or has_unstaged or has_untracked):
                return GitDiffSummary(
                    has_changes=False,
                    changes=[],
                    summary="No uncommitted changes"
                )

            changes = []

            # Process staged changes
            for diff_item in repo.index.diff("HEAD"):
                change = self._process_diff_item(diff_item, structural_only)
                if change:
                    changes.append(change)

            # Process unstaged changes
            for diff_item in repo.index.diff(None):
                change = self._process_diff_item(diff_item, structural_only)
                if change:
                    # Avoid duplicates
                    if not any(c.file_path == change.file_path for c in changes):
                        changes.append(change)

            # Process untracked files
            for file_path in repo.untracked_files:
                changes.append(DiffChange(
                    file_path=file_path,
                    change_type="added",
                    header_changes=[],
                    formula_changes=[],
                    additions=0,
                    deletions=0
                ))

            # Generate summary
            summary = self._generate_summary(changes)

            return GitDiffSummary(
                has_changes=True,
                changes=changes,
                summary=summary
            )

        except Exception as e:
            return GitDiffSummary(
                has_changes=False,
                changes=[],
                summary=f"Error getting diff: {str(e)}"
            )

    def _process_diff_item(self, diff_item, structural_only: bool) -> DiffChange | None:
        """Process a single diff item."""
        try:
            # Determine change type
            if diff_item.new_file:
                change_type = "added"
            elif diff_item.deleted_file:
                change_type = "deleted"
            else:
                change_type = "modified"

            # Get file path
            file_path = diff_item.a_path or diff_item.b_path

            # Skip non-markdown files if structural_only
            if structural_only and not file_path.endswith((".md", ".markdown")):
                return None

            # Get diff content
            try:
                diff_text = diff_item.diff.decode("utf-8", errors="replace")
            except (AttributeError, TypeError):
                diff_text = ""

            # Extract structural changes
            header_changes = []
            formula_changes = []
            additions = 0
            deletions = 0

            for line in diff_text.split("\n"):
                if line.startswith("+") and not line.startswith("+++"):
                    additions += 1
                    content = line[1:]
                    if re.match(r"^#{1,6}\s+", content):
                        header_changes.append(f"+ {content.strip()}")
                    elif "$" in content:
                        formula_changes.append(f"+ {content.strip()[:50]}...")
                elif line.startswith("-") and not line.startswith("---"):
                    deletions += 1
                    content = line[1:]
                    if re.match(r"^#{1,6}\s+", content):
                        header_changes.append(f"- {content.strip()}")
                    elif "$" in content:
                        formula_changes.append(f"- {content.strip()[:50]}...")

            # If structural_only and no structural changes, skip
            if structural_only and not (header_changes or formula_changes):
                # Still report if there are significant changes
                if additions + deletions < 5:
                    return None

            return DiffChange(
                file_path=file_path,
                change_type=change_type,
                header_changes=header_changes,
                formula_changes=formula_changes,
                additions=additions,
                deletions=deletions
            )

        except Exception:
            return None

    def _generate_summary(self, changes: list[DiffChange]) -> str:
        """Generate human-readable summary of changes."""
        if not changes:
            return "No structural changes detected"

        parts = []
        total_additions = sum(c.additions for c in changes)
        total_deletions = sum(c.deletions for c in changes)
        total_header_changes = sum(len(c.header_changes) for c in changes)
        total_formula_changes = sum(len(c.formula_changes) for c in changes)

        parts.append(f"{len(changes)} file(s) changed")

        if total_additions or total_deletions:
            parts.append(f"+{total_additions}/-{total_deletions} lines")

        if total_header_changes:
            parts.append(f"{total_header_changes} header change(s)")

        if total_formula_changes:
            parts.append(f"{total_formula_changes} formula change(s)")

        return ", ".join(parts)

    def rollback(self, commit_hash: str | None = None) -> GitCheckpointResult:
        """
        Rollback to a previous commit.

        Args:
            commit_hash: Specific commit to rollback to, or None for HEAD^

        Returns:
            GitCheckpointResult with status
        """
        try:
            repo = self.repo

            if commit_hash:
                target = commit_hash
            else:
                # Rollback to previous commit
                target = "HEAD^"

            # Perform hard reset
            repo.git.reset("--hard", target)

            return GitCheckpointResult(
                success=True,
                commit_hash=repo.head.commit.hexsha[:7],
                message=f"Rolled back to {target}",
                files_staged=0
            )

        except GitCommandError as e:
            return GitCheckpointResult(
                success=False,
                commit_hash=None,
                message=f"Rollback failed: {str(e)}",
                files_staged=0
            )

    def get_history(self, max_commits: int = 10) -> list[dict]:
        """
        Get recent commit history.

        Args:
            max_commits: Maximum number of commits to return

        Returns:
            List of commit info dicts
        """
        try:
            repo = self.repo

            if not repo.head.is_valid():
                return []

            commits = []
            for commit in repo.iter_commits(max_count=max_commits):
                commits.append({
                    "hash": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": str(commit.author),
                    "date": commit.committed_datetime.isoformat()
                })

            return commits

        except Exception:
            return []
