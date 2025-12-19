# 修复 LaTeX 公式问题

文件: `{file_path}`

## 诊断
首先调用 `analyze_formulas("{file_path}")` 查看具体问题。

## 问题类型与修复方法

### 1. unclosed（未闭合）
**问题**：`$` 或 `$$` 没有配对

**修复方法**：
```bash
# 找到未闭合的位置，添加缺失的定界符
# 行内公式用 $...$
# 块级公式用 $$...$$
```

**常见情况**：
- OCR 把 `$` 识别成了其他字符
- 公式跨行时 `$$` 被拆开

### 2. unbalanced_braces（括号不平衡）
**问题**：`{` 和 `}` 数量不匹配

**修复方法**：
```bash
# 检查公式中的花括号配对
# 常见错误：\frac{a}{b 缺少闭合的 }
sed -i 's/\\frac{a}{b$/\\frac{a}{b}/' "{file_path}"
```

**技巧**：
- 从内向外检查嵌套的括号
- `\left(` 必须配对 `\right)`

### 3. ocr_noise（OCR 噪点）
**问题**：公式中包含明显的 OCR 错误

**常见噪点**：
- `l` 和 `1` 混淆：`\alpha` 变成 `\alphal`
- `O` 和 `0` 混淆：`\beta` 变成 `\betaO`
- 多余的数字或字符

**修复方法**：
```bash
# 清理 OCR 噪点
sed -i 's/\\alphal23/\\alpha/g' "{file_path}"
sed -i 's/\\betaOOO/\\beta/g' "{file_path}"
```

### 4. invalid_command（无效命令）
**问题**：LaTeX 命令拼写错误

**修复方法**：
```bash
# 根据建议修正命令
# 例如：\apha -> \alpha
sed -i 's/\\apha/\\alpha/g' "{file_path}"
```

### 5. syntax_error（语法错误）
**问题**：LaTeX 语法不正确

**常见错误**：
- `\frac` 缺少参数：`\frac{a}` -> `\frac{a}{b}`
- 空的上下标：`x^` -> `x^{2}`
- `\sqrt` 缺少参数

## 公式修复原则

1. **保持数学含义**：修复时确保公式的数学意义不变
2. **检查上下文**：参考公式前后的文字理解其含义
3. **常见 OCR 错误对照表**：
   - `α` -> `a` 或 `\alpha`
   - `β` -> `B` 或 `\beta`
   - `∫` -> `f` 或 `\int`
   - `∑` -> `E` 或 `\sum`
   - `×` -> `x` 或 `\times`

## 验证
修复后调用 `analyze_formulas("{file_path}")` 确认问题已解决。
