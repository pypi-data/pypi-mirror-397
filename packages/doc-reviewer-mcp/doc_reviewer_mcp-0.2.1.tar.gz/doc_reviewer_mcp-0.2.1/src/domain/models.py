"""Domain models for document diagnostics."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class IssueType(str, Enum):
    """Types of ToC alignment issues."""
    LEVEL_MISMATCH = "level_mismatch"
    TEXT_TYPO = "text_typo"
    MISSING = "missing"
    EXTRA = "extra"


class FormulaIssueType(str, Enum):
    """Types of LaTeX formula issues."""
    UNCLOSED = "unclosed"
    SYNTAX_ERROR = "syntax_error"
    OCR_NOISE = "ocr_noise"
    UNBALANCED_BRACES = "unbalanced_braces"
    INVALID_COMMAND = "invalid_command"


class ImageIssueType(str, Enum):
    """Types of image link issues."""
    FILE_NOT_FOUND = "file_not_found"
    INVALID_PATH = "invalid_path"
    BROKEN_SYNTAX = "broken_syntax"


class Header(BaseModel):
    """Represents a markdown header extracted from document body."""
    text: str = Field(description="Header text without # prefix")
    level: int = Field(ge=1, le=6, description="Header level (1-6)")
    line_number: int = Field(ge=1, description="Line number in document")
    raw_line: str = Field(description="Original line content")


class ToCEntry(BaseModel):
    """Represents an entry from the Table of Contents page."""
    text: str = Field(description="ToC entry text")
    expected_level: int = Field(ge=1, le=6, description="Expected header level based on indentation")
    toc_line_number: int = Field(ge=1, description="Line number in ToC section")


class ToCAlignmentIssue(BaseModel):
    """Represents a mismatch between ToC and actual headers."""
    toc_text: str = Field(description="Text from ToC entry")
    matched_header: Optional[str] = Field(default=None, description="Best matching header text")
    line_number: Optional[int] = Field(default=None, description="Line number of matched header")
    issue_type: IssueType = Field(description="Type of alignment issue")
    expected_level: int = Field(ge=1, le=6, description="Expected level from ToC")
    actual_level: Optional[int] = Field(default=None, description="Actual level in document")
    match_score: float = Field(ge=0, le=100, description="Fuzzy match score (0-100)")
    suggestion: str = Field(description="Suggested fix action")


class Formula(BaseModel):
    """Represents a LaTeX formula in the document."""
    content: str = Field(description="Formula content without delimiters")
    line_number: int = Field(ge=1, description="Starting line number")
    is_block: bool = Field(description="True if block formula ($$), False if inline ($)")
    raw_text: str = Field(description="Original text including delimiters")


class FormulaIssue(BaseModel):
    """Represents an issue with a LaTeX formula."""
    formula: Formula = Field(description="The problematic formula")
    issue_type: FormulaIssueType = Field(description="Type of formula issue")
    description: str = Field(description="Human-readable description of the issue")
    suggestion: Optional[str] = Field(default=None, description="Suggested fix")


class ImageLink(BaseModel):
    """Represents an image link in the document."""
    alt_text: str = Field(description="Image alt text")
    path: str = Field(description="Image path/URL")
    line_number: int = Field(ge=1, description="Line number in document")
    raw_text: str = Field(description="Original markdown syntax")


class ImageIssue(BaseModel):
    """Represents an issue with an image link."""
    image: ImageLink = Field(description="The problematic image link")
    issue_type: ImageIssueType = Field(description="Type of image issue")
    description: str = Field(description="Human-readable description")
    similar_paths: list[str] = Field(default_factory=list, description="Similar existing paths")


class DiagnosticReport(BaseModel):
    """Complete diagnostic report for a document."""
    file_path: str = Field(description="Path to analyzed file")
    total_headers: int = Field(ge=0, description="Total headers found")
    total_formulas: int = Field(ge=0, description="Total formulas found")
    total_images: int = Field(ge=0, description="Total images found")
    toc_issues: list[ToCAlignmentIssue] = Field(default_factory=list)
    formula_issues: list[FormulaIssue] = Field(default_factory=list)
    image_issues: list[ImageIssue] = Field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.toc_issues or self.formula_issues or self.image_issues)

    @property
    def total_issues(self) -> int:
        return len(self.toc_issues) + len(self.formula_issues) + len(self.image_issues)


class GitCheckpointResult(BaseModel):
    """Result of creating a git checkpoint."""
    success: bool = Field(description="Whether checkpoint was created")
    commit_hash: Optional[str] = Field(default=None, description="Short commit hash")
    message: str = Field(description="Status message")
    files_staged: int = Field(ge=0, default=0, description="Number of files staged")


class DiffChange(BaseModel):
    """Represents a single change in git diff."""
    file_path: str = Field(description="Changed file path")
    change_type: str = Field(description="Type: added, deleted, modified")
    header_changes: list[str] = Field(default_factory=list, description="Changed header lines")
    formula_changes: list[str] = Field(default_factory=list, description="Changed formula lines")
    additions: int = Field(ge=0, default=0, description="Lines added")
    deletions: int = Field(ge=0, default=0, description="Lines deleted")


class GitDiffSummary(BaseModel):
    """Summary of git diff focusing on structural changes."""
    has_changes: bool = Field(description="Whether there are uncommitted changes")
    changes: list[DiffChange] = Field(default_factory=list)
    summary: str = Field(description="Human-readable summary")
