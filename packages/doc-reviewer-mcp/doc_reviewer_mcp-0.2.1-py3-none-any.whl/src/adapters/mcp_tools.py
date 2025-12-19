"""MCP tool registration for document diagnostics."""

from pathlib import Path
from fastmcp import FastMCP
from src.domain.models import DiagnosticReport
from src.usecases.toc_aligner import TocAligner
from src.usecases.latex_scanner import LatexScanner
from src.usecases.image_checker import ImageChecker
from src.adapters.git_provider import GitProvider


# Constants for output size limits
MAX_CONTENT_LENGTH = 80  # Max chars for formula/text content in output
MAX_ITEMS_DEFAULT = 50   # Max items to return in lists
MAX_ISSUES_DEFAULT = 100 # Max issues to return


def _truncate(text: str, max_length: int = MAX_CONTENT_LENGTH) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def _compact_formula(formula) -> dict:
    """Return compact representation of a formula."""
    return {
        "line": formula.line_number,
        "type": "block" if formula.is_block else "inline",
        "content": _truncate(formula.content),
    }


def _compact_formula_issue(issue) -> dict:
    """Return compact representation of a formula issue."""
    return {
        "line": issue.formula.line_number,
        "type": issue.issue_type.value,
        "description": issue.description,
        "suggestion": issue.suggestion,
        "content_preview": _truncate(issue.formula.content) if issue.formula.content else None,
    }


def _compact_header(header) -> dict:
    """Return compact representation of a header."""
    return {
        "line": header.line_number,
        "level": header.level,
        "text": _truncate(header.text),
    }


def _compact_toc_issue(issue) -> dict:
    """Return compact representation of a ToC issue."""
    return {
        "line": issue.line_number,
        "type": issue.issue_type.value,
        "toc_text": _truncate(issue.toc_text),
        "expected_level": issue.expected_level,
        "actual_level": issue.actual_level,
        "suggestion": issue.suggestion,
    }


def _compact_image(image) -> dict:
    """Return compact representation of an image."""
    return {
        "line": image.line_number,
        "path": _truncate(image.path),
        "alt": _truncate(image.alt_text, 40),
    }


def _compact_image_issue(issue) -> dict:
    """Return compact representation of an image issue."""
    return {
        "line": issue.image.line_number,
        "type": issue.issue_type.value,
        "path": _truncate(issue.image.path),
        "description": issue.description,
        "similar_paths": issue.similar_paths[:3],  # Limit suggestions
    }


def register_all_tools(mcp: FastMCP) -> None:
    """Register all MCP tools for document diagnostics."""

    @mcp.tool()
    def analyze_document(
        file_path: str,
        check_toc: bool = True,
        check_formulas: bool = True,
        check_images: bool = True
    ) -> dict:
        """
        Analyze a markdown document for structural issues.

        This tool performs comprehensive diagnostics on OCR-generated markdown files:
        - ToC alignment: Compares table of contents with actual headers
        - LaTeX formulas: Validates syntax and detects OCR noise
        - Image links: Checks if referenced images exist

        Args:
            file_path: Absolute path to the markdown file
            check_toc: Whether to check ToC alignment (default: True)
            check_formulas: Whether to check LaTeX formulas (default: True)
            check_images: Whether to check image links (default: True)

        Returns:
            Diagnostic report with all issues found
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        if not path.is_file():
            return {"error": f"Not a file: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="gbk")
            except Exception as e:
                return {"error": f"Failed to read file: {str(e)}"}

        # Initialize analyzers
        toc_aligner = TocAligner()
        latex_scanner = LatexScanner()
        image_checker = ImageChecker()

        # Collect statistics
        headers = toc_aligner.extract_headers(content)
        formulas = latex_scanner.extract_formulas(content)
        images = image_checker.extract_images(content)

        # Run diagnostics
        toc_issues = toc_aligner.align(content) if check_toc else []
        formula_issues = latex_scanner.scan(content) if check_formulas else []
        image_issues = image_checker.check(content, file_path) if check_images else []

        # Return compact format to reduce context size
        return {
            "file_path": file_path,
            "summary": {
                "total_headers": len(headers),
                "total_formulas": len(formulas),
                "total_images": len(images),
                "total_issues": len(toc_issues) + len(formula_issues) + len(image_issues),
            },
            "toc_issues": [_compact_toc_issue(i) for i in toc_issues[:MAX_ISSUES_DEFAULT]],
            "formula_issues": [_compact_formula_issue(i) for i in formula_issues[:MAX_ISSUES_DEFAULT]],
            "image_issues": [_compact_image_issue(i) for i in image_issues[:MAX_ISSUES_DEFAULT]],
            "truncated": {
                "toc": len(toc_issues) > MAX_ISSUES_DEFAULT,
                "formula": len(formula_issues) > MAX_ISSUES_DEFAULT,
                "image": len(image_issues) > MAX_ISSUES_DEFAULT,
            }
        }

    @mcp.tool()
    def analyze_toc(file_path: str) -> dict:
        """
        Analyze table of contents alignment in a markdown document.

        Performs three-way comparison between:
        1. ToC entries (from document's table of contents section)
        2. Actual headers (lines starting with #)
        3. Physical line numbers

        Uses fuzzy matching to detect typos and level mismatches.

        Args:
            file_path: Absolute path to the markdown file

        Returns:
            List of ToC alignment issues with suggestions
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="gbk")

        aligner = TocAligner()
        headers = aligner.extract_headers(content)
        toc_entries = aligner.extract_toc(content)
        issues = aligner.align(content)

        return {
            "file_path": file_path,
            "total_headers": len(headers),
            "toc_entries_found": len(toc_entries),
            "issues": [_compact_toc_issue(issue) for issue in issues[:MAX_ISSUES_DEFAULT]],
            "headers": [_compact_header(h) for h in headers[:20]],  # First 20 headers
            "truncated": len(issues) > MAX_ISSUES_DEFAULT,
        }

    @mcp.tool()
    def analyze_formulas(file_path: str) -> dict:
        """
        Analyze LaTeX formulas in a markdown document.

        Checks for:
        - Unclosed formula delimiters ($ or $$)
        - Unbalanced braces and brackets
        - Invalid LaTeX commands
        - OCR noise patterns
        - Common syntax errors

        Args:
            file_path: Absolute path to the markdown file

        Returns:
            List of formula issues with suggestions
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="gbk")

        scanner = LatexScanner()
        formulas = scanner.extract_formulas(content)
        issues = scanner.scan(content)

        return {
            "file_path": file_path,
            "total_formulas": len(formulas),
            "block_formulas": len([f for f in formulas if f.is_block]),
            "inline_formulas": len([f for f in formulas if not f.is_block]),
            "issues": [_compact_formula_issue(issue) for issue in issues[:MAX_ISSUES_DEFAULT]],
            "truncated": len(issues) > MAX_ISSUES_DEFAULT,
        }

    @mcp.tool()
    def analyze_images(file_path: str) -> dict:
        """
        Analyze image links in a markdown document.

        Checks for:
        - Missing image files
        - Invalid path syntax
        - Broken markdown image syntax

        Provides similar path suggestions for missing files.

        Args:
            file_path: Absolute path to the markdown file

        Returns:
            List of image issues with similar path suggestions
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="gbk")

        checker = ImageChecker()
        images = checker.extract_images(content)
        issues = checker.check(content, file_path)

        return {
            "file_path": file_path,
            "total_images": len(images),
            "issues": [_compact_image_issue(issue) for issue in issues[:MAX_ISSUES_DEFAULT]],
            "images": [_compact_image(img) for img in images[:MAX_ITEMS_DEFAULT]],
            "truncated": len(issues) > MAX_ISSUES_DEFAULT or len(images) > MAX_ITEMS_DEFAULT,
        }

    @mcp.tool()
    def git_checkpoint(
        working_dir: str,
        message: str = "MCP Checkpoint"
    ) -> dict:
        """
        Create a git checkpoint before making changes.

        IMPORTANT: Always call this before batch modifications to enable rollback.

        If the directory is not a git repository, one will be initialized.

        Args:
            working_dir: Directory containing the files to checkpoint
            message: Commit message for the checkpoint

        Returns:
            Checkpoint result with commit hash
        """
        provider = GitProvider(working_dir)
        result = provider.checkpoint(message)
        return result.model_dump()

    @mcp.tool()
    def git_diff_summary(
        working_dir: str,
        structural_only: bool = True
    ) -> dict:
        """
        Get summary of changes since last checkpoint.

        Use this after making modifications to verify changes are correct.

        Args:
            working_dir: Directory to check for changes
            structural_only: If True, focus on header and formula changes

        Returns:
            Summary of changes with structural highlights
        """
        provider = GitProvider(working_dir)
        result = provider.diff_summary(structural_only)
        return result.model_dump()

    @mcp.tool()
    def git_rollback(
        working_dir: str,
        commit_hash: str | None = None
    ) -> dict:
        """
        Rollback to a previous checkpoint.

        WARNING: This discards all uncommitted changes.

        Args:
            working_dir: Directory to rollback
            commit_hash: Specific commit to rollback to (default: previous commit)

        Returns:
            Rollback result
        """
        provider = GitProvider(working_dir)
        result = provider.rollback(commit_hash)
        return result.model_dump()

    @mcp.tool()
    def git_history(
        working_dir: str,
        max_commits: int = 10
    ) -> dict:
        """
        Get recent commit history for a directory.

        Args:
            working_dir: Directory to get history for
            max_commits: Maximum number of commits to return

        Returns:
            List of recent commits
        """
        provider = GitProvider(working_dir)
        commits = provider.get_history(max_commits)
        return {
            "working_dir": working_dir,
            "commits": commits
        }

    @mcp.tool()
    def extract_headers(file_path: str) -> dict:
        """
        Extract all markdown headers from a document.

        Useful for understanding document structure before making changes.

        Args:
            file_path: Absolute path to the markdown file

        Returns:
            List of headers with levels and line numbers
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="gbk")

        aligner = TocAligner()
        headers = aligner.extract_headers(content)

        return {
            "file_path": file_path,
            "total_headers": len(headers),
            "headers": [_compact_header(h) for h in headers[:MAX_ITEMS_DEFAULT]],
            "truncated": len(headers) > MAX_ITEMS_DEFAULT,
        }

    @mcp.tool()
    def extract_toc(file_path: str) -> dict:
        """
        Extract table of contents entries from a document.

        Looks for ToC section in the first 100 lines of the document.

        Args:
            file_path: Absolute path to the markdown file

        Returns:
            List of ToC entries with expected levels
        """
        path = Path(file_path)

        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="gbk")

        aligner = TocAligner()
        toc_entries = aligner.extract_toc(content)

        compact_entries = [
            {"line": e.toc_line_number, "level": e.expected_level, "text": _truncate(e.text)}
            for e in toc_entries[:MAX_ITEMS_DEFAULT]
        ]
        return {
            "file_path": file_path,
            "total_entries": len(toc_entries),
            "toc_entries": compact_entries,
            "truncated": len(toc_entries) > MAX_ITEMS_DEFAULT,
        }
