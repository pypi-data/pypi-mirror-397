# 修复图片链接问题

文件: `{file_path}`

## 诊断
首先调用 `analyze_images("{file_path}")` 查看具体问题。

## 问题类型与修复方法

### 1. file_not_found（文件不存在）
**问题**：图片路径指向的文件不存在

**修复方法**：

方法 A - 使用建议的相似路径：
```bash
# 如果诊断报告提供了 similar_paths
sed -i 's|images/old_name.png|images/correct_name.png|g' "{file_path}"
```

方法 B - 搜索正确的文件：
```bash
# 在文档目录下搜索可能的图片
find "$(dirname "{file_path}")" -name "*.png" -o -name "*.jpg"
```

方法 C - 如果图片确实丢失：
```bash
# 添加占位符注释
sed -i 's|!\[alt\](missing.png)|<!-- 图片丢失: missing.png -->|g' "{file_path}"
```

### 2. invalid_path（无效路径）
**问题**：路径包含非法字符

**修复方法**：
```bash
# 移除或替换非法字符
# 常见问题：空格、中文、特殊符号
sed -i 's|images/图片 1.png|images/image_1.png|g' "{file_path}"
```

### 3. broken_syntax（语法错误）
**问题**：Markdown 图片语法不正确

**正确语法**：
```markdown
![替代文本](图片路径)
![](图片路径)  # 无替代文本也可以
```

**常见错误**：
- `![]()` 中括号不完整
- 路径中有换行符
- 引号不匹配

## 批量修复路径

```bash
# 统一修复路径格式
# 将 Windows 路径转换为 Unix 路径
sed -i 's|\\|/|g' "{file_path}"

# 移除路径中的空格
sed -i 's| |_|g' "{file_path}"
```

## 验证
修复后调用 `analyze_images("{file_path}")` 确认问题已解决。
