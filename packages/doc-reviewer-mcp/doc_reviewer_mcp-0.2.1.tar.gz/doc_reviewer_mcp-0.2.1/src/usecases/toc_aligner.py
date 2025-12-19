"""ToC alignment analysis using fuzzy matching."""

import re
from rapidfuzz import fuzz
from src.domain.models import (
    Header,
    ToCEntry,
    ToCAlignmentIssue,
    IssueType,
)


class TocAligner:
    """Aligns Table of Contents entries with actual document headers."""

    # Patterns for ToC detection
    TOC_MARKERS = re.compile(
        r"^(目录|contents|table\s+of\s+contents|toc)$",
        re.IGNORECASE
    )
    HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
    # ToC entry pattern: captures indentation and text
    TOC_ENTRY_PATTERN = re.compile(r"^(\s*)[-*]?\s*\[?([^\]]+)\]?\s*(?:\(#[^)]*\))?$")

    def __init__(self, match_threshold: float = 70.0, toc_search_lines: int = 100):
        """
        Initialize TocAligner.

        Args:
            match_threshold: Minimum fuzzy match score to consider a match (0-100)
            toc_search_lines: Number of lines from start to search for ToC
        """
        self.match_threshold = match_threshold
        self.toc_search_lines = toc_search_lines

    def extract_headers(self, content: str) -> list[Header]:
        """Extract all markdown headers from document content."""
        headers = []
        lines = content.split("\n")

        for i, line in enumerate(lines, start=1):
            match = self.HEADER_PATTERN.match(line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headers.append(Header(
                    text=text,
                    level=level,
                    line_number=i,
                    raw_line=line
                ))

        return headers

    def extract_toc(self, content: str) -> list[ToCEntry]:
        """
        Extract Table of Contents entries from document.

        Looks for a ToC section in the first N lines and extracts entries.
        """
        lines = content.split("\n")
        toc_entries = []
        in_toc = False
        toc_start = -1
        base_indent = 0

        # Search for ToC marker in first N lines
        search_range = min(len(lines), self.toc_search_lines)

        for i, line in enumerate(lines[:search_range]):
            stripped = line.strip()

            # Check for ToC marker
            if self.TOC_MARKERS.match(stripped):
                in_toc = True
                toc_start = i
                continue

            # Also check if line is a header containing ToC marker
            header_match = self.HEADER_PATTERN.match(stripped)
            if header_match and self.TOC_MARKERS.match(header_match.group(2).strip()):
                in_toc = True
                toc_start = i
                continue

            if in_toc:
                # Empty line might end ToC section
                if not stripped:
                    # Allow some empty lines within ToC
                    if toc_entries and i - toc_start > 3:
                        # Check if next non-empty line looks like ToC entry
                        next_content = self._peek_next_content(lines, i, search_range)
                        if not next_content or not self._looks_like_toc_entry(next_content):
                            break
                    continue

                # Check if this looks like a ToC entry
                if self._looks_like_toc_entry(stripped):
                    # Calculate level from indentation
                    leading_spaces = len(line) - len(line.lstrip())
                    if not toc_entries:
                        base_indent = leading_spaces

                    # Estimate level: every 2-4 spaces = 1 level deeper
                    indent_diff = leading_spaces - base_indent
                    level = 1 + max(0, indent_diff // 2)
                    level = min(level, 6)  # Cap at h6

                    # Extract text
                    text = self._extract_toc_text(stripped)
                    if text:
                        toc_entries.append(ToCEntry(
                            text=text,
                            expected_level=level,
                            toc_line_number=i + 1
                        ))

                # A header line (##) likely ends ToC
                elif header_match and toc_entries:
                    break

        return toc_entries

    def _peek_next_content(self, lines: list[str], start: int, end: int) -> str | None:
        """Look ahead for next non-empty line."""
        for i in range(start + 1, min(len(lines), end)):
            if lines[i].strip():
                return lines[i].strip()
        return None

    def _looks_like_toc_entry(self, text: str) -> bool:
        """Check if text looks like a ToC entry."""
        # ToC entries typically:
        # - Start with bullet or number
        # - Contain link syntax [text](#anchor)
        # - Are short-ish text lines
        # - Don't start with # (that's a header)
        # - Chinese chapter/section markers

        if text.startswith("#"):
            return False

        # Link syntax
        if re.match(r"^[-*\d.]+\s*\[.+\]", text):
            return True

        # Numbered entry
        if re.match(r"^\d+[.)]\s+\S", text):
            return True

        # Bullet entry
        if re.match(r"^[-*+]\s+\S", text):
            return True

        # Chinese chapter/section patterns (第X章, 第X节, X.X.X 等)
        if re.match(r"^第[一二三四五六七八九十百千\d]+[章节篇部]", text):
            return True

        # Section number patterns (1.1, 1.1.1, §1.1, etc.)
        if re.match(r"^[§]?\d+(\.\d+)+", text):
            return True

        # Plain text that looks like a title (capitalized for English, reasonable length)
        if len(text) < 100 and text[0].isupper():
            return True

        # Chinese text that looks like a title (reasonable length, starts with Chinese char)
        if len(text) < 100 and re.match(r"^[\u4e00-\u9fff]", text):
            return True

        return False

    def _extract_toc_text(self, text: str) -> str:
        """Extract clean text from ToC entry."""
        # Remove bullet/number prefix
        text = re.sub(r"^[-*+\d.)\s]+", "", text)

        # Extract text from link syntax [text](#anchor)
        link_match = re.match(r"\[([^\]]+)\]", text)
        if link_match:
            text = link_match.group(1)

        # Remove page numbers at end
        text = re.sub(r"\s*\.{2,}\s*\d+\s*$", "", text)
        text = re.sub(r"\s+\d+\s*$", "", text)

        return text.strip()

    def align(self, content: str) -> list[ToCAlignmentIssue]:
        """
        Perform three-way alignment between ToC, headers, and line numbers.

        Returns list of alignment issues found.
        """
        headers = self.extract_headers(content)
        toc_entries = self.extract_toc(content)

        if not toc_entries:
            return []

        issues = []
        matched_headers: set[int] = set()

        for toc_entry in toc_entries:
            best_match = None
            best_score = 0.0
            best_header_idx = -1

            # Find best matching header using fuzzy matching
            for idx, header in enumerate(headers):
                if idx in matched_headers:
                    continue

                score = fuzz.WRatio(toc_entry.text, header.text)
                if score > best_score:
                    best_score = score
                    best_match = header
                    best_header_idx = idx

            if best_score >= self.match_threshold and best_match:
                matched_headers.add(best_header_idx)

                # Check for level mismatch
                if best_match.level != toc_entry.expected_level:
                    issues.append(ToCAlignmentIssue(
                        toc_text=toc_entry.text,
                        matched_header=best_match.text,
                        line_number=best_match.line_number,
                        issue_type=IssueType.LEVEL_MISMATCH,
                        expected_level=toc_entry.expected_level,
                        actual_level=best_match.level,
                        match_score=best_score,
                        suggestion=f"Change line {best_match.line_number}: "
                                   f"{'#' * toc_entry.expected_level} {best_match.text}"
                    ))

                # Check for text typo (high but not perfect match)
                elif best_score < 95:
                    issues.append(ToCAlignmentIssue(
                        toc_text=toc_entry.text,
                        matched_header=best_match.text,
                        line_number=best_match.line_number,
                        issue_type=IssueType.TEXT_TYPO,
                        expected_level=toc_entry.expected_level,
                        actual_level=best_match.level,
                        match_score=best_score,
                        suggestion=f"Verify text at line {best_match.line_number}: "
                                   f"ToC says '{toc_entry.text}', found '{best_match.text}'"
                    ))
            else:
                # No good match found - missing header
                issues.append(ToCAlignmentIssue(
                    toc_text=toc_entry.text,
                    matched_header=best_match.text if best_match else None,
                    line_number=best_match.line_number if best_match else None,
                    issue_type=IssueType.MISSING,
                    expected_level=toc_entry.expected_level,
                    actual_level=best_match.level if best_match else None,
                    match_score=best_score,
                    suggestion=f"Missing header for ToC entry: '{toc_entry.text}' "
                               f"(best match score: {best_score:.1f})"
                ))

        # Check for extra headers not in ToC
        for idx, header in enumerate(headers):
            if idx not in matched_headers:
                # Find if any ToC entry is close
                best_score = 0.0
                for toc_entry in toc_entries:
                    score = fuzz.WRatio(toc_entry.text, header.text)
                    best_score = max(best_score, score)

                if best_score < self.match_threshold:
                    issues.append(ToCAlignmentIssue(
                        toc_text="",
                        matched_header=header.text,
                        line_number=header.line_number,
                        issue_type=IssueType.EXTRA,
                        expected_level=header.level,
                        actual_level=header.level,
                        match_score=best_score,
                        suggestion=f"Header at line {header.line_number} not in ToC: "
                                   f"'{header.text}'"
                    ))

        return issues
