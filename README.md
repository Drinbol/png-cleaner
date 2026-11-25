# png-cleaner

按大小规则批量清理 PNG 文件的命令行工具。

## 规则

1. 保留所有大于阈值（默认 50KB）的 PNG 文件
2. 同时保留这些文件的**下划线版本**（`a.png` > 50KB → 保留 `a.png` 和 `a_.png`）
3. 删除其余小于阈值、且没有对应大文件的 PNG

## 使用场景

一批 PNG 中混着：高质量大图（>50KB）、大图的缩略/预览版（同名多一个下划线的小文件）、
以及其它没用的小文件。本工具自动清理，只留重要文件。

## 安装

无第三方依赖，Python 3.8+ 直接运行。

## 使用

```bash
# 基本用法（删除前有确认提示）
python main.py /path/to/images

# 模拟运行：只列出将要删除的文件，不实际删除
python main.py /path/to/images --dry-run

# 自定义大小阈值（KB）
python main.py /path/to/images --threshold 100

# 显示每个文件的大小和保留/删除原因
python main.py /path/to/images --verbose
```

### 参数

| 参数 | 说明 |
|---|---|
| `folder` | 要处理的文件夹（递归处理子文件夹） |
| `-t, --threshold` | 大小阈值（KB），默认 50 |
| `--dry-run` | 模拟运行，不实际删除 |
| `--verbose` | 显示详细信息 |

## 示例

```
a.png    71KB  → 保留（大于阈值）
a_.png   12KB  → 保留（a.png 的下划线版本）
b.png    45KB  → 删除（小于阈值且无对应大文件）
c.png    60KB  → 保留
c_.png   15KB  → 保留
d.png    30KB  → 删除
e_.png   20KB  → 删除（没有对应的大文件）
```

## 注意事项

- 删除前会要求确认（`--dry-run` 除外），建议先 dry-run 确认清单
- 同时匹配 `.png` 和 `.PNG` 扩展名
- 下划线版本命名规则：`原名_.png`

## 许可证

MIT
