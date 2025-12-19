"""LaTeX formula scanning and validation."""

import re
from src.domain.models import Formula, FormulaIssue, FormulaIssueType


class LineIndex:
    """Pre-computed line number index for O(log n) position-to-line lookup."""

    def __init__(self, content: str):
        """Build line start positions index."""
        self.line_starts = [0]
        for i, char in enumerate(content):
            if char == '\n':
                self.line_starts.append(i + 1)

    def get_line(self, pos: int) -> int:
        """Get 1-indexed line number for a position using binary search."""
        lo, hi = 0, len(self.line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.line_starts[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1


class LatexScanner:
    """Scans and validates LaTeX formulas in markdown documents."""

    # Pattern to match block formulas ($$...$$ or \[...\])
    BLOCK_FORMULA_PATTERN = re.compile(
        r"\$\$([^$]+?)\$\$",
        re.DOTALL
    )
    BLOCK_FORMULA_BRACKET_PATTERN = re.compile(
        r"\\\[(.+?)\\\]",
        re.DOTALL
    )

    # Pattern to match inline formulas ($...$ or \(...\))
    # Avoid matching $$
    INLINE_FORMULA_PATTERN = re.compile(
        r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)"
    )
    INLINE_FORMULA_PAREN_PATTERN = re.compile(
        r"\\\((.+?)\\\)"
    )

    # Common OCR noise patterns
    OCR_NOISE_PATTERNS = [
        re.compile(r"[|l1]{3,}"),  # Multiple l/1/| confusion
        re.compile(r"[oO0]{3,}"),  # Multiple o/O/0 confusion
        re.compile(r"\\[a-z]+[0-9]{2,}"),  # Commands with numbers like \alpha123
        re.compile(r"[^\x00-\x7F]{2,}"),  # Multiple non-ASCII chars (potential garbage)
        re.compile(r"\\\\{3,}"),  # Too many backslashes
        re.compile(r"\s{5,}"),  # Excessive whitespace
    ]

    # Valid LaTeX commands (common subset)
    VALID_COMMANDS = {
        # Greek letters
        "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
        "iota", "kappa", "lambda", "mu", "nu", "xi", "pi", "rho", "sigma",
        "tau", "upsilon", "phi", "chi", "psi", "omega",
        "Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Upsilon",
        "Phi", "Psi", "Omega",
        # Operators
        "sum", "prod", "int", "oint", "iint", "iiint", "lim", "sup", "inf",
        "max", "min", "log", "ln", "exp", "sin", "cos", "tan", "cot", "sec",
        "csc", "arcsin", "arccos", "arctan", "sinh", "cosh", "tanh",
        # Relations
        "leq", "geq", "neq", "approx", "equiv", "sim", "simeq", "cong",
        "propto", "subset", "supset", "subseteq", "supseteq", "in", "notin",
        "ni", "forall", "exists", "nexists",
        # Arrows
        "leftarrow", "rightarrow", "leftrightarrow", "Leftarrow", "Rightarrow",
        "Leftrightarrow", "uparrow", "downarrow", "mapsto", "to",
        # Formatting
        "frac", "sqrt", "root", "overline", "underline", "hat", "bar", "vec",
        "dot", "ddot", "tilde", "widetilde", "widehat", "overbrace", "underbrace",
        # Delimiters
        "left", "right", "big", "Big", "bigg", "Bigg", "langle", "rangle",
        "lfloor", "rfloor", "lceil", "rceil", "lvert", "rvert",
        # Environments
        "begin", "end", "text", "mathrm", "mathbf", "mathit", "mathsf",
        "mathtt", "mathcal", "mathbb", "mathfrak",
        # Spacing
        "quad", "qquad", "hspace", "vspace", "phantom", "hphantom", "vphantom",
        # Misc
        "cdot", "cdots", "ldots", "vdots", "ddots", "times", "div", "pm", "mp",
        "ast", "star", "circ", "bullet", "oplus", "otimes", "odot",
        "partial", "nabla", "infty", "prime", "backslash", "setminus",
        "cup", "cap", "emptyset", "varnothing",
        # Accents
        "acute", "grave", "breve", "check",
        # Arrays/matrices
        "array", "matrix", "pmatrix", "bmatrix", "vmatrix", "Vmatrix",
        "cases", "aligned", "align", "equation", "gather",
        # Additional
        "not", "neg", "land", "lor", "implies", "iff", "therefore", "because",
    }

    # Paired delimiters that must be balanced
    PAIRED_DELIMITERS = [
        ("{", "}"),
        ("[", "]"),
        ("(", ")"),
        ("\\{", "\\}"),
        ("\\[", "\\]"),
        ("\\(", "\\)"),
        ("\\left", "\\right"),
        ("\\begin", "\\end"),
    ]

    def __init__(self):
        """Initialize LatexScanner."""
        pass

    def extract_formulas(self, content: str, line_index: LineIndex | None = None) -> list[Formula]:
        """Extract all LaTeX formulas from document content."""
        formulas = []

        # Use provided line index or create new one
        idx = line_index or LineIndex(content)

        # Extract block formulas ($$...$$)
        for match in self.BLOCK_FORMULA_PATTERN.finditer(content):
            formulas.append(Formula(
                content=match.group(1).strip(),
                line_number=idx.get_line(match.start()),
                is_block=True,
                raw_text=match.group(0)
            ))

        # Extract block formulas (\[...\])
        for match in self.BLOCK_FORMULA_BRACKET_PATTERN.finditer(content):
            formulas.append(Formula(
                content=match.group(1).strip(),
                line_number=idx.get_line(match.start()),
                is_block=True,
                raw_text=match.group(0)
            ))

        # Extract inline formulas ($...$)
        for match in self.INLINE_FORMULA_PATTERN.finditer(content):
            formulas.append(Formula(
                content=match.group(1).strip(),
                line_number=idx.get_line(match.start()),
                is_block=False,
                raw_text=match.group(0)
            ))

        # Extract inline formulas (\(...\))
        for match in self.INLINE_FORMULA_PAREN_PATTERN.finditer(content):
            formulas.append(Formula(
                content=match.group(1).strip(),
                line_number=idx.get_line(match.start()),
                is_block=False,
                raw_text=match.group(0)
            ))

        # Sort by line number
        formulas.sort(key=lambda f: f.line_number)
        return formulas

    def scan(self, content: str) -> list[FormulaIssue]:
        """
        Scan document for LaTeX formula issues.

        Returns list of formula issues found.
        """
        issues = []

        # Build line index once for all operations
        line_index = LineIndex(content)

        # Check for unclosed formulas first
        unclosed_issues = self._check_unclosed_formulas(content, line_index)
        issues.extend(unclosed_issues)

        # Check for nested delimiters in raw content
        nested_issues = self._check_nested_delimiters(content, line_index)
        issues.extend(nested_issues)

        # Check for double pipe errors in raw content
        pipe_issues = self._check_double_pipe_errors(content, line_index)
        issues.extend(pipe_issues)

        # Extract and validate individual formulas
        formulas = self.extract_formulas(content, line_index)

        for formula in formulas:
            # Check for unbalanced braces
            brace_issue = self._check_balanced_braces(formula)
            if brace_issue:
                issues.append(brace_issue)
                continue

            # Check for OCR noise
            noise_issue = self._check_ocr_noise(formula)
            if noise_issue:
                issues.append(noise_issue)
                continue

            # Check for invalid commands
            cmd_issue = self._check_invalid_commands(formula)
            if cmd_issue:
                issues.append(cmd_issue)

            # Check for syntax errors
            syntax_issue = self._check_syntax_errors(formula)
            if syntax_issue:
                issues.append(syntax_issue)

        return issues

    def _check_unclosed_formulas(self, content: str, line_index: LineIndex) -> list[FormulaIssue]:
        """Check for unclosed formula delimiters."""
        issues = []

        # Check for unmatched $$ (block)
        block_count = content.count("$$")
        if block_count % 2 != 0:
            # Find the problematic location
            positions = [m.start() for m in re.finditer(r"\$\$", content)]
            if positions:
                last_pos = positions[-1]
                line_num = line_index.get_line(last_pos)
                issues.append(FormulaIssue(
                    formula=Formula(
                        content="",
                        line_number=line_num,
                        is_block=True,
                        raw_text="$$"
                    ),
                    issue_type=FormulaIssueType.UNCLOSED,
                    description=f"Unclosed block formula delimiter $$ at line {line_num}",
                    suggestion="Add matching $$ to close the formula"
                ))

        # Check for unmatched \[ \] (block)
        open_bracket_count = len(re.findall(r"\\\[", content))
        close_bracket_count = len(re.findall(r"\\\]", content))
        if open_bracket_count != close_bracket_count:
            # Find the problematic location
            if open_bracket_count > close_bracket_count:
                positions = [m.start() for m in re.finditer(r"\\\[", content)]
                if positions:
                    last_pos = positions[-1]
                    line_num = line_index.get_line(last_pos)
                    issues.append(FormulaIssue(
                        formula=Formula(
                            content="",
                            line_number=line_num,
                            is_block=True,
                            raw_text="\\["
                        ),
                        issue_type=FormulaIssueType.UNCLOSED,
                        description=f"Unclosed block formula delimiter \\[ at line {line_num}",
                        suggestion="Add matching \\] to close the formula"
                    ))
            else:
                positions = [m.start() for m in re.finditer(r"\\\]", content)]
                if positions:
                    last_pos = positions[-1]
                    line_num = line_index.get_line(last_pos)
                    issues.append(FormulaIssue(
                        formula=Formula(
                            content="",
                            line_number=line_num,
                            is_block=True,
                            raw_text="\\]"
                        ),
                        issue_type=FormulaIssueType.UNCLOSED,
                        description=f"Unmatched \\] at line {line_num}",
                        suggestion="Add matching \\[ or remove stray \\]"
                    ))

        # Check for unmatched $ (inline) - more complex due to $$ interference
        # Remove $$ first, then count $
        content_no_block = re.sub(r"\$\$", "", content)
        inline_count = content_no_block.count("$")
        if inline_count % 2 != 0:
            # Find potential unclosed inline formula
            # Build a separate line index for modified content
            modified_index = LineIndex(content_no_block)
            in_formula = False
            formula_start = -1
            for i, char in enumerate(content_no_block):
                if char == "$":
                    if not in_formula:
                        in_formula = True
                        formula_start = i
                    else:
                        in_formula = False

            if in_formula and formula_start >= 0:
                line_num = modified_index.get_line(formula_start)
                issues.append(FormulaIssue(
                    formula=Formula(
                        content="",
                        line_number=line_num,
                        is_block=False,
                        raw_text="$"
                    ),
                    issue_type=FormulaIssueType.UNCLOSED,
                    description=f"Unclosed inline formula delimiter $ near line {line_num}",
                    suggestion="Add matching $ to close the formula or remove stray $"
                ))

        # Check for unmatched \( \) (inline)
        open_paren_count = len(re.findall(r"\\\(", content))
        close_paren_count = len(re.findall(r"\\\)", content))
        if open_paren_count != close_paren_count:
            if open_paren_count > close_paren_count:
                positions = [m.start() for m in re.finditer(r"\\\(", content)]
                if positions:
                    last_pos = positions[-1]
                    line_num = line_index.get_line(last_pos)
                    issues.append(FormulaIssue(
                        formula=Formula(
                            content="",
                            line_number=line_num,
                            is_block=False,
                            raw_text="\\("
                        ),
                        issue_type=FormulaIssueType.UNCLOSED,
                        description=f"Unclosed inline formula delimiter \\( at line {line_num}",
                        suggestion="Add matching \\) to close the formula"
                    ))
            else:
                positions = [m.start() for m in re.finditer(r"\\\)", content)]
                if positions:
                    last_pos = positions[-1]
                    line_num = line_index.get_line(last_pos)
                    issues.append(FormulaIssue(
                        formula=Formula(
                            content="",
                            line_number=line_num,
                            is_block=False,
                            raw_text="\\)"
                        ),
                        issue_type=FormulaIssueType.UNCLOSED,
                        description=f"Unmatched \\) at line {line_num}",
                        suggestion="Add matching \\( or remove stray \\)"
                    ))

        return issues

    def _check_balanced_braces(self, formula: Formula) -> FormulaIssue | None:
        """Check if braces are balanced in formula."""
        content = formula.content

        for open_delim, close_delim in self.PAIRED_DELIMITERS:
            # Simple counting for single-char delimiters
            if len(open_delim) == 1 and len(close_delim) == 1:
                # Skip if it's an escaped brace - build pattern without f-string
                open_pattern = r"(?<!\\)" + re.escape(open_delim)
                close_pattern = r"(?<!\\)" + re.escape(close_delim)
                open_count = len(re.findall(open_pattern, content))
                close_count = len(re.findall(close_pattern, content))

                if open_count != close_count:
                    return FormulaIssue(
                        formula=formula,
                        issue_type=FormulaIssueType.UNBALANCED_BRACES,
                        description=f"Unbalanced '{open_delim}' and '{close_delim}': "
                                    f"{open_count} open, {close_count} close",
                        suggestion=f"Check braces at line {formula.line_number}"
                    )
            else:
                # For multi-char delimiters like \left \right
                open_count = content.count(open_delim)
                close_count = content.count(close_delim)

                if open_count != close_count:
                    return FormulaIssue(
                        formula=formula,
                        issue_type=FormulaIssueType.UNBALANCED_BRACES,
                        description=f"Unbalanced '{open_delim}' and '{close_delim}': "
                                    f"{open_count} open, {close_count} close",
                        suggestion=f"Check {open_delim}/{close_delim} pairs at line {formula.line_number}"
                    )

        return None

    def _check_ocr_noise(self, formula: Formula) -> FormulaIssue | None:
        """Check for OCR noise patterns in formula."""
        content = formula.content

        for pattern in self.OCR_NOISE_PATTERNS:
            match = pattern.search(content)
            if match:
                return FormulaIssue(
                    formula=formula,
                    issue_type=FormulaIssueType.OCR_NOISE,
                    description=f"Potential OCR noise detected: '{match.group()}'",
                    suggestion=f"Review formula at line {formula.line_number} for OCR artifacts"
                )

        return None

    def _check_invalid_commands(self, formula: Formula) -> FormulaIssue | None:
        """Check for invalid LaTeX commands."""
        content = formula.content

        # Find all commands (backslash followed by letters)
        commands = re.findall(r"\\([a-zA-Z]+)", content)

        for cmd in commands:
            if cmd not in self.VALID_COMMANDS:
                # Check if it might be a typo of a valid command
                suggestion = self._suggest_command(cmd)
                return FormulaIssue(
                    formula=formula,
                    issue_type=FormulaIssueType.INVALID_COMMAND,
                    description=f"Unknown LaTeX command: \\{cmd}",
                    suggestion=suggestion or f"Check if \\{cmd} is correct at line {formula.line_number}"
                )

        return None

    def _suggest_command(self, cmd: str) -> str | None:
        """Suggest a valid command for a potentially misspelled one."""
        from rapidfuzz import fuzz

        best_match = None
        best_score = 0

        for valid_cmd in self.VALID_COMMANDS:
            score = fuzz.ratio(cmd.lower(), valid_cmd.lower())
            if score > best_score and score > 70:
                best_score = score
                best_match = valid_cmd

        if best_match:
            return f"Did you mean \\{best_match}?"
        return None

    def _check_syntax_errors(self, formula: Formula) -> FormulaIssue | None:
        """Check for common LaTeX syntax errors."""
        content = formula.content

        # Check for empty subscript/superscript
        if re.search(r"[_^]\s*(?=[_^$]|$)", content):
            return FormulaIssue(
                formula=formula,
                issue_type=FormulaIssueType.SYNTAX_ERROR,
                description="Empty subscript or superscript",
                suggestion=f"Add content after _ or ^ at line {formula.line_number}"
            )

        # Check for \frac without two arguments
        frac_matches = list(re.finditer(r"\\frac\s*", content))
        for match in frac_matches:
            after = content[match.end():]
            # Check if followed by two brace groups (handles nested braces)
            if after.startswith("{"):
                # Find matching closing brace for first argument
                first_arg_end = self._find_matching_brace(after, 0)
                if first_arg_end == -1:
                    return FormulaIssue(
                        formula=formula,
                        issue_type=FormulaIssueType.SYNTAX_ERROR,
                        description="\\frac first argument has unmatched braces",
                        suggestion=f"Check \\frac braces at line {formula.line_number}"
                    )
                # Check for second argument
                remaining = after[first_arg_end + 1:].lstrip()
                if not remaining.startswith("{"):
                    # Could be single char second arg like \frac{a}b
                    if not remaining or not remaining[0].isalnum():
                        return FormulaIssue(
                            formula=formula,
                            issue_type=FormulaIssueType.SYNTAX_ERROR,
                            description="\\frac requires two arguments",
                            suggestion=f"Use \\frac{{num}}{{denom}} at line {formula.line_number}"
                        )
            else:
                # Could be \frac12 style (single chars)
                if not re.match(r"[a-zA-Z0-9]\s*[a-zA-Z0-9]", after):
                    return FormulaIssue(
                        formula=formula,
                        issue_type=FormulaIssueType.SYNTAX_ERROR,
                        description="\\frac requires two arguments",
                        suggestion=f"Use \\frac{{num}}{{denom}} at line {formula.line_number}"
                    )

        # Check for \sqrt without argument
        sqrt_matches = list(re.finditer(r"\\sqrt\s*(?!\[)(?!\{)", content))
        for match in sqrt_matches:
            after = content[match.end():]
            if not after or after[0] not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ{[":
                return FormulaIssue(
                    formula=formula,
                    issue_type=FormulaIssueType.SYNTAX_ERROR,
                    description="\\sqrt requires an argument",
                    suggestion=f"Use \\sqrt{{x}} at line {formula.line_number}"
                )

        return None

    def _find_matching_brace(self, text: str, start: int) -> int:
        """
        Find the index of the closing brace matching the opening brace at start.

        Args:
            text: The text to search in
            start: Index of the opening brace '{'

        Returns:
            Index of matching '}', or -1 if not found
        """
        if start >= len(text) or text[start] != "{":
            return -1

        depth = 0
        i = start
        while i < len(text):
            if text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
                depth += 1
            elif text[i] == "}" and (i == 0 or text[i - 1] != "\\"):
                depth -= 1
                if depth == 0:
                    return i
            i += 1

        return -1

    def _check_nested_delimiters(self, content: str, line_index: LineIndex) -> list[FormulaIssue]:
        """Check for nested formula delimiters like \\(\\(...\\)\\) or \\[\\[...\\]\\]."""
        issues = []

        # Pattern for nested inline delimiters: \(\(...\)\)
        nested_inline_pattern = re.compile(r"\\\(\s*\\\(")
        for match in nested_inline_pattern.finditer(content):
            line_num = line_index.get_line(match.start())
            issues.append(FormulaIssue(
                formula=Formula(
                    content="",
                    line_number=line_num,
                    is_block=False,
                    raw_text=match.group(0)
                ),
                issue_type=FormulaIssueType.SYNTAX_ERROR,
                description=f"Nested inline formula delimiters \\(\\( at line {line_num}",
                suggestion="Remove the extra \\( - use \\(...\\) not \\(\\(...\\)\\)"
            ))

        # Pattern for nested block delimiters: \[\[...\]\]
        nested_block_pattern = re.compile(r"\\\[\s*\\\[")
        for match in nested_block_pattern.finditer(content):
            line_num = line_index.get_line(match.start())
            issues.append(FormulaIssue(
                formula=Formula(
                    content="",
                    line_number=line_num,
                    is_block=True,
                    raw_text=match.group(0)
                ),
                issue_type=FormulaIssueType.SYNTAX_ERROR,
                description=f"Nested block formula delimiters \\[\\[ at line {line_num}",
                suggestion="Remove the extra \\[ - use \\[...\\] not \\[\\[...\\]\\]"
            ))

        # Also check closing nested delimiters
        nested_close_inline = re.compile(r"\\\)\s*\\\)")
        for match in nested_close_inline.finditer(content):
            line_num = line_index.get_line(match.start())
            issues.append(FormulaIssue(
                formula=Formula(
                    content="",
                    line_number=line_num,
                    is_block=False,
                    raw_text=match.group(0)
                ),
                issue_type=FormulaIssueType.SYNTAX_ERROR,
                description=f"Nested closing delimiters \\)\\) at line {line_num}",
                suggestion="Remove the extra \\) - use \\(...\\) not \\(\\(...\\)\\)"
            ))

        nested_close_block = re.compile(r"\\\]\s*\\\]")
        for match in nested_close_block.finditer(content):
            line_num = line_index.get_line(match.start())
            issues.append(FormulaIssue(
                formula=Formula(
                    content="",
                    line_number=line_num,
                    is_block=True,
                    raw_text=match.group(0)
                ),
                issue_type=FormulaIssueType.SYNTAX_ERROR,
                description=f"Nested closing delimiters \\]\\] at line {line_num}",
                suggestion="Remove the extra \\] - use \\[...\\] not \\[\\[...\\]\\]"
            ))

        return issues

    def _check_double_pipe_errors(self, content: str, line_index: LineIndex) -> list[FormulaIssue]:
        """Check for double pipe errors like ||x|| which should be \\|x\\|."""
        issues = []

        # Pattern for double pipes used as norm notation (not escaped)
        # Match ||...|| but not \|...\|
        double_pipe_pattern = re.compile(r"(?<!\\)\|\|([^|]+?)\|\|(?!\|)")
        for match in double_pipe_pattern.finditer(content):
            line_num = line_index.get_line(match.start())
            inner_content = match.group(1)
            issues.append(FormulaIssue(
                formula=Formula(
                    content=inner_content,
                    line_number=line_num,
                    is_block=False,
                    raw_text=match.group(0)
                ),
                issue_type=FormulaIssueType.SYNTAX_ERROR,
                description=f"Double pipe ||...|| at line {line_num} should use \\|...\\| for norm notation",
                suggestion=f"Replace ||{inner_content}|| with \\|{inner_content}\\|"
            ))

        # Pattern for single pipe used as norm (common in OCR errors)
        # Match |x|_p pattern which likely should be \|x\|_p
        single_pipe_norm_pattern = re.compile(r"(?<!\\)\|([a-zA-Z0-9_{}\\]+)\|_([a-zA-Z0-9])")
        for match in single_pipe_norm_pattern.finditer(content):
            line_num = line_index.get_line(match.start())
            inner = match.group(1)
            subscript = match.group(2)
            issues.append(FormulaIssue(
                formula=Formula(
                    content=f"|{inner}|_{subscript}",
                    line_number=line_num,
                    is_block=False,
                    raw_text=match.group(0)
                ),
                issue_type=FormulaIssueType.SYNTAX_ERROR,
                description=f"Norm notation |...|_{{subscript}} at line {line_num} should use \\|...\\|",
                suggestion=f"Replace |{inner}|_{subscript} with \\|{inner}\\|_{subscript}"
            ))

        return issues
