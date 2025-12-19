# 1. 产品需求文档 (PRD)

## 1.1 项目背景
OCR（光学字符识别）生成的 Markdown 文件通常存在结构性缺陷：标题层级混乱、数学公式（LaTeX）识别错误、图片链接断裂。手动修复大型文档耗时且易出错。

## 1.2 核心目标
开发一个本地 MCP 服务器，作为 LLM（如 Claude、Cursor）的“高精度显微镜”，提供诊断信息，辅助模型利用 Code CLI 原生能力（Bash/Regex）安全地修复文档。

## 1.3 核心功能
1.  **目录三方对齐 (ToC Triangulation)**：对比“OCR 目录页”、“正文标题流”与“物理行号”，识别层级错位。
2.  **LaTeX 公式审计**：识别语法非法、未闭合或包含 OCR 噪点的公式。
3.  **Git 安全沙箱**：提供快照（Checkpoint）与语义化差异（Diff）功能，支持批量修改后的快速回滚。
4.  **静态资源校验**：检查本地图片路径是否存在，并提供相似路径建议。

---

# 2. 技术架构文档 (Architecture)

## 2.1 设计原则
*   **整洁架构 (Clean Architecture)**：业务逻辑与框架解耦。
*   **关注点分离**：MCP 负责“读与诊”，Code CLI 负责“写与改”。
*   **原子化反馈**：通过 Pydantic 模型返回结构化 JSON，降低模型幻觉。

## 2.2 逻辑分层
1.  **Domain (实体层)**：定义 `Header`, `Formula`, `DiagnosticReport` 等 Pydantic 模型。
2.  **Use Cases (领域逻辑层)**：
    *   `TocAligner`：执行 RapidFuzz 模糊匹配算法。
    *   `LatexScanner`：执行正则与语法校验。
3.  **Adapters (适配器层)**：
    *   `MCPController`：FastMCP 工具注册。
    *   `GitProvider`：封装 GitPython 操作。
4.  **Infrastructure (基础设施层)**：`uv` 环境管理、`Marko` 解析器。

## 2.3 数据流向
1.  模型调用 `analyze_document` (MCP)。
2.  MCP 读取文件 -> 提取标题 -> 模糊匹配目录页 -> 生成差异报告 (Pydantic)。
3.  模型阅读报告 -> 调用 `git_checkpoint` (MCP)。
4.  模型执行 `sed` 替换 (Code CLI Bash)。
5.  模型调用 `git_diff_summary` (MCP) 确认修改。

---

# 3. 技术规格说明书 (Technical Specs)

## 3.1 核心算法：目录模糊匹配
*   **输入**：全文文本。
*   **步骤**：
    1.  正则定位 `^#+ ` 的行作为 `ActualHeaders`。
    2.  识别文档前 N 页中包含“目录/Contents”的块作为 `ExpectedToC`。
    3.  对 `ExpectedToC` 的每一行，在 `ActualHeaders` 中搜索 `fuzz.WRatio` 得分最高的项。
    4.  对比 `ExpectedToC` 的缩进深度与 `ActualHeaders` 的 `#` 数量。
*   **输出**：`List[ToCAlignmentIssue]`。

## 3.2 Git 安全机制
*   **仓库初始化**：若目标目录无 `.git`，自动执行 `git init`。
*   **快照逻辑**：`git add . && git commit -m "MCP Checkpoint"`。
*   **差异摘要**：运行 `git diff HEAD^`，通过正则过滤掉琐碎修改，仅向模型报告结构性变化（如标题行、公式块的变化）。

## 3.3 技术栈选型
*   **包管理**：`uv` (pyproject.toml)
*   **通信协议**：MCP (Model Context Protocol)
*   **数据校验**：Pydantic v2
*   **文本处理**：RapidFuzz (C++ 加速的编辑距离库), Marko (CommonMark 解析)
*   **版本控制**：GitPython

---

# 4. 执行与部署文档 (Execution Plan)

## 4.1 环境初始化
```bash
# 1. 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建项目并添加依赖
mkdir mcp-ocr-fixer && cd mcp-ocr-fixer
uv init
uv add mcp[cli] fastmcp pydantic rapidfuzz marko gitpython
```

## 4.2 核心代码实现结构
创建 `src/domain/models.py`:
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ToCAlignmentIssue(BaseModel):
    toc_text: str
    matched_header: Optional[str]
    line_number: Optional[int]
    issue_type: str # 'level_mismatch', 'text_typo', 'missing'
    suggested_level: int
```

创建 `app.py`:
```python
from fastmcp import FastMCP
from src.adapters.mcp_tools import register_all_tools

mcp = FastMCP("OCR-Fixer")
register_all_tools(mcp)

if __name__ == "__main__":
    mcp.run()
```

## 4.3 部署至客户端 (Claude Desktop)
编辑 `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ocr-fixer": {
      "command": "uv",
      "args": ["--directory", "/绝对路径/mcp-ocr-fixer", "run", "app.py"]
    }
  }
}
```

---

# 5. 最终确认方案清单 (Final Checklist)

| 模块 | 确定方案 | 状态 |
| :--- | :--- | :--- |
| **项目管理** | 使用 `uv` 进行依赖锁定和环境隔离 | 确认 |
| **数据契约** | 所有工具输出必须经过 `Pydantic` 模型序列化 | 确认 |
| **目录对齐** | 采用 RapidFuzz 模糊匹配 + 三方对比逻辑 | 确认 |
| **安全保障** | 强制要求模型在批量修改前调用 Git Checkpoint | 确认 |
| **编辑职责** | MCP 严禁直接写文件，仅通过报告引导模型修改 | 确认 |
| **扩展性** | 采用整洁架构，支持未来增加表格、脚注等诊断模块 | 确认 |

---