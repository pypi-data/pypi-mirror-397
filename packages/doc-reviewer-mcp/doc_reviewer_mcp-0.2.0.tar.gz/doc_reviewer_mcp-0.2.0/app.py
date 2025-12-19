"""
Doc Reviewer MCP Server

A local MCP server that provides diagnostic tools for OCR-generated Markdown documents.
Acts as a "high-precision microscope" for LLMs to identify and fix document issues.

Features:
- ToC Triangulation: Compare ToC entries with actual headers
- LaTeX Audit: Validate formula syntax and detect OCR noise
- Git Safety: Checkpoint and rollback support for batch modifications
- Image Validation: Check local image paths and suggest fixes
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastmcp import FastMCP
from src.adapters.mcp_tools import register_all_tools
from src.adapters.prompts import register_all_prompts

# Create MCP server instance
mcp = FastMCP(
    "Doc-Reviewer",
    instructions="MCP server for OCR-generated Markdown document diagnostics. "
                 "Use analyze_document for comprehensive diagnostics, or individual tools "
                 "(analyze_toc, analyze_formulas, analyze_images) for specific checks. "
                 "Always call git_checkpoint before batch modifications. "
                 "Use prompts (fix_document_workflow, fix_toc_issues, fix_formula_issues, "
                 "fix_image_issues, batch_fix_strategy) for repair guidance."
)

# Register all diagnostic tools and prompts
register_all_tools(mcp)
register_all_prompts(mcp)

if __name__ == "__main__":
    mcp.run()
