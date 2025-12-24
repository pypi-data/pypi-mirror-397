# 面试鸭题目搜索 MCP 服务器

基于 MCP 协议的面试鸭题目搜索服务器，使用 Python 实现。

## 工具

### question_search

根据搜索词搜索面试鸭面试题目。

- **输入**: `search_text` - 搜索关键词
- **输出**: 面试鸭搜索结果的题目链接列表（最多5条）

## 安装

```bash
uv sync
```

## 在 Cursor 中使用

在 Cursor 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "mianshiya-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mianshiya-search-mcp",
        "run",
        "mianshiya-search-mcp"
      ]
    }
  }
}
```

请将 `/path/to/mianshiya-search-mcp` 替换为实际的项目路径。

