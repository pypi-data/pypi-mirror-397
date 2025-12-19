"""MCP prompts registration for document repair guidance."""

from pathlib import Path
from fastmcp import FastMCP

# Prompts directory relative to project root
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Load prompt template from file."""
    prompt_file = PROMPTS_DIR / f"{name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    return prompt_file.read_text(encoding="utf-8")


def register_all_prompts(mcp: FastMCP) -> None:
    """Register all MCP prompts for document repair guidance."""

    @mcp.prompt()
    def fix_document_workflow(file_path: str) -> str:
        """
        Complete workflow guide for fixing OCR-generated markdown documents.
        Provides step-by-step instructions for safe document repair.

        Args:
            file_path: Path to the markdown file to fix
        """
        template = load_prompt("fix_workflow")
        return template.format(file_path=file_path)

    @mcp.prompt()
    def fix_toc_issues(file_path: str) -> str:
        """
        Guide for fixing Table of Contents alignment issues.
        Covers level mismatches, typos, missing and extra headers.

        Args:
            file_path: Path to the markdown file
        """
        template = load_prompt("fix_toc")
        return template.format(file_path=file_path)

    @mcp.prompt()
    def fix_formula_issues(file_path: str) -> str:
        """
        Guide for fixing LaTeX formula issues in markdown.
        Covers unclosed delimiters, unbalanced braces, OCR noise, and syntax errors.

        Args:
            file_path: Path to the markdown file
        """
        template = load_prompt("fix_formulas")
        return template.format(file_path=file_path)

    @mcp.prompt()
    def fix_image_issues(file_path: str) -> str:
        """
        Guide for fixing image link issues in markdown.
        Covers missing files, invalid paths, and broken syntax.

        Args:
            file_path: Path to the markdown file
        """
        template = load_prompt("fix_images")
        return template.format(file_path=file_path)

    @mcp.prompt()
    def batch_fix_strategy() -> str:
        """
        Strategy guide for batch fixing multiple documents.
        Provides workflow for efficiently repairing many files.
        """
        return load_prompt("batch_fix")
