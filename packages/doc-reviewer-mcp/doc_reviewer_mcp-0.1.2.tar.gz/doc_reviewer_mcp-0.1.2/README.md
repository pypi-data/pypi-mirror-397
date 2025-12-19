# doc-reviewer-mcp

MCP server for OCR-generated Markdown document review and diagnostics.

## Features

- **ToC Alignment**: Compares table of contents with actual headers using fuzzy matching
- **LaTeX Formula Validation**: Detects syntax errors and OCR noise in formulas
- **Image Link Checking**: Verifies referenced images exist with similar path suggestions
- **Git Integration**: Checkpoint, diff, and rollback support for safe batch modifications

## Installation

```bash
# Using uvx (recommended)
uvx doc-reviewer-mcp

# Using pip
pip install doc-reviewer-mcp
```

## Usage

### As MCP Server

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "doc-reviewer": {
      "command": "uvx",
      "args": ["doc-reviewer-mcp"]
    }
  }
}
```

### Available Tools

- `analyze_document` - Comprehensive document analysis
- `analyze_toc` - Table of contents alignment check
- `analyze_formulas` - LaTeX formula validation
- `analyze_images` - Image link verification
- `extract_headers` - Extract all markdown headers
- `extract_toc` - Extract ToC entries
- `git_checkpoint` - Create a checkpoint before changes
- `git_diff_summary` - View changes since checkpoint
- `git_rollback` - Rollback to previous checkpoint
- `git_history` - View commit history

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/doc-reviewer-mcp.git
cd doc-reviewer-mcp

# Install dependencies
uv sync

# Run locally
uv run doc-reviewer-mcp
```

## License

MIT
