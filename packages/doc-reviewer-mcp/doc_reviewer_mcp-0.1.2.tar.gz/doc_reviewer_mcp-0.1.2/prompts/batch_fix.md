# 批量文档修复策略

## 准备工作

1. **创建工作目录快照**
```
git_checkpoint(working_dir="/path/to/docs", message="批量修复前快照")
```

2. **列出所有待修复文件**
```bash
find /path/to/docs -name "*.md" -type f
```

## 批量诊断

对每个文件运行诊断，收集所有问题：
```
analyze_document("/path/to/file1.md")
analyze_document("/path/to/file2.md")
...
```

## 修复策略

### 策略 A：按问题类型修复
1. 先修复所有文件的"未闭合公式"问题
2. 再修复所有文件的"标题层级"问题
3. 最后修复"OCR 噪点"问题

**优点**：可以使用统一的 sed 命令批量处理
**适用**：问题模式相似的文档集

### 策略 B：按文件逐个修复
1. 完整修复 file1.md
2. 完整修复 file2.md
3. ...

**优点**：每个文件修复完整，便于验证
**适用**：文档差异较大的情况

### 策略 C：优先级修复
1. 先修复问题最多的文件
2. 或先修复最重要的文件

## 常用批量命令

```bash
# 批量修复常见 OCR 错误
find /path/to/docs -name "*.md" -exec sed -i 's/\\alphal/\\alpha/g' {} \;

# 批量统一标题格式
find /path/to/docs -name "*.md" -exec sed -i 's/^###\s*第/## 第/g' {} \;
```

## 验证与提交

每完成一批修复：
1. `git_diff_summary()` 检查修改
2. `git_checkpoint(message="修复: 具体描述")` 提交
3. 如有问题 `git_rollback()` 回滚

## 注意事项

- 不要一次性修改太多文件
- 每种类型的修复单独提交
- 保留修复日志便于追溯
