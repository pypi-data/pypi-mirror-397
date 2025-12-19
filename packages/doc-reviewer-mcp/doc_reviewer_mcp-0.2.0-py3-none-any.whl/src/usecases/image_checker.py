"""Image link validation for markdown documents."""

import re
import os
from pathlib import Path
from rapidfuzz import fuzz
from src.domain.models import ImageLink, ImageIssue, ImageIssueType


class ImageChecker:
    """Checks image links in markdown documents for validity."""

    # Pattern to match markdown image syntax: ![alt](path)
    IMAGE_PATTERN = re.compile(
        r"!\[([^\]]*)\]\(([^)]+)\)"
    )

    # Pattern to match HTML img tags
    HTML_IMG_PATTERN = re.compile(
        r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
        re.IGNORECASE
    )

    def __init__(self, similarity_threshold: float = 70.0, max_suggestions: int = 3):
        """
        Initialize ImageChecker.

        Args:
            similarity_threshold: Minimum score for path suggestions (0-100)
            max_suggestions: Maximum number of similar paths to suggest
        """
        self.similarity_threshold = similarity_threshold
        self.max_suggestions = max_suggestions

    def extract_images(self, content: str) -> list[ImageLink]:
        """Extract all image links from document content."""
        images = []
        lines = content.split("\n")

        def get_line_number(match_start: int) -> int:
            return content[:match_start].count("\n") + 1

        # Extract markdown images
        for match in self.IMAGE_PATTERN.finditer(content):
            images.append(ImageLink(
                alt_text=match.group(1),
                path=match.group(2).strip(),
                line_number=get_line_number(match.start()),
                raw_text=match.group(0)
            ))

        # Extract HTML img tags
        for match in self.HTML_IMG_PATTERN.finditer(content):
            images.append(ImageLink(
                alt_text="",
                path=match.group(1).strip(),
                line_number=get_line_number(match.start()),
                raw_text=match.group(0)
            ))

        # Sort by line number
        images.sort(key=lambda img: img.line_number)
        return images

    def check(self, content: str, document_path: str) -> list[ImageIssue]:
        """
        Check all image links in document for issues.

        Args:
            content: Document content
            document_path: Path to the document (for resolving relative paths)

        Returns:
            List of image issues found
        """
        issues = []
        images = self.extract_images(content)
        doc_dir = Path(document_path).parent

        # Collect existing files for suggestions
        existing_files = self._collect_image_files(doc_dir)

        for image in images:
            issue = self._check_image(image, doc_dir, existing_files)
            if issue:
                issues.append(issue)

        return issues

    def _check_image(
        self,
        image: ImageLink,
        doc_dir: Path,
        existing_files: list[str]
    ) -> ImageIssue | None:
        """Check a single image link."""
        path = image.path

        # Skip URLs (http/https)
        if path.startswith(("http://", "https://", "data:")):
            return None

        # Check for broken syntax
        if self._has_broken_syntax(path):
            return ImageIssue(
                image=image,
                issue_type=ImageIssueType.BROKEN_SYNTAX,
                description=f"Invalid image path syntax: '{path}'",
                similar_paths=[]
            )

        # Check for invalid path characters
        if self._has_invalid_path(path):
            return ImageIssue(
                image=image,
                issue_type=ImageIssueType.INVALID_PATH,
                description=f"Path contains invalid characters: '{path}'",
                similar_paths=[]
            )

        # Resolve the path relative to document
        resolved_path = self._resolve_path(path, doc_dir)

        # Check if file exists
        if not resolved_path.exists():
            similar = self._find_similar_paths(path, existing_files)
            return ImageIssue(
                image=image,
                issue_type=ImageIssueType.FILE_NOT_FOUND,
                description=f"Image file not found: '{path}'",
                similar_paths=similar
            )

        return None

    def _has_broken_syntax(self, path: str) -> bool:
        """Check if path has broken syntax."""
        # Empty path
        if not path or path.isspace():
            return True

        # Unbalanced quotes
        if path.count('"') % 2 != 0 or path.count("'") % 2 != 0:
            return True

        # Contains newlines or tabs
        if "\n" in path or "\t" in path:
            return True

        return False

    def _has_invalid_path(self, path: str) -> bool:
        """Check if path contains invalid characters."""
        # Control characters
        if any(ord(c) < 32 for c in path):
            return True

        # Null bytes
        if "\x00" in path:
            return True

        return False

    def _resolve_path(self, path: str, doc_dir: Path) -> Path:
        """Resolve image path relative to document directory."""
        # Handle absolute paths
        if os.path.isabs(path):
            return Path(path)

        # Handle relative paths
        return doc_dir / path

    def _collect_image_files(self, base_dir: Path, max_depth: int = 3) -> list[str]:
        """Collect all image files in directory tree."""
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico"}
        files = []

        if not base_dir.exists():
            return files

        try:
            for root, dirs, filenames in os.walk(base_dir):
                # Calculate depth
                depth = len(Path(root).relative_to(base_dir).parts)
                if depth > max_depth:
                    dirs.clear()  # Don't descend further
                    continue

                for filename in filenames:
                    if Path(filename).suffix.lower() in image_extensions:
                        rel_path = os.path.relpath(os.path.join(root, filename), base_dir)
                        files.append(rel_path)
        except (PermissionError, OSError):
            pass

        return files

    def _find_similar_paths(self, target: str, existing_files: list[str]) -> list[str]:
        """Find similar existing paths using fuzzy matching."""
        target_name = Path(target).name.lower()
        scored_paths = []

        for file_path in existing_files:
            file_name = Path(file_path).name.lower()

            # Score based on filename similarity
            name_score = fuzz.ratio(target_name, file_name)

            # Bonus for matching extension
            if Path(target).suffix.lower() == Path(file_path).suffix.lower():
                name_score += 10

            # Bonus for partial path match
            if any(part in file_path.lower() for part in Path(target).parts[:-1]):
                name_score += 15

            if name_score >= self.similarity_threshold:
                scored_paths.append((file_path, name_score))

        # Sort by score descending
        scored_paths.sort(key=lambda x: x[1], reverse=True)

        return [path for path, _ in scored_paths[:self.max_suggestions]]
