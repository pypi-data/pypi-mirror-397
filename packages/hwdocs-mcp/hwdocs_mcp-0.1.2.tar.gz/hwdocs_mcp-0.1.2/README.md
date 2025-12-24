# hwdocs-mcp

MCP (Model Context Protocol) 服务器，为 Cursor、Claude Desktop 等 AI 编辑器提供文档解析和语义搜索能力。

## 特性

- **PDF 解析**：将 PDF、DOCX 等文档解析为可搜索的 Markdown（通过 LlamaIndex Cloud）
- **语义搜索**：使用本地 embeddings 进行语义关键词搜索（免费）
- **Workspace 缓存**：缓存 embeddings 加速重复搜索
- **配额管理**：追踪和管理文档解析配额
- **AI 编辑器集成**：支持 Cursor、Claude Desktop 等 MCP 兼容编辑器

## 安装

```bash
pip install hwdocs-mcp
```

同时需要安装 semtools CLI：

```bash
npm install -g @llamaindex/semtools
```

## 快速开始

### 1. 配置编辑器

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "hwdocs": {
      "command": "hwdocs-mcp"
    }
  }
}
```

**Claude Desktop** (`~/.claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "hwdocs": {
      "command": "hwdocs-mcp"
    }
  }
}
```

### 2. 登录（可选，用于配额管理）

```bash
hwdocs login --token YOUR_TOKEN
```

### 3. 在 AI 编辑器中使用

```
用户: "解析 docs 文件夹里的 PDF 文件"
AI: → parse_documents(files=["./docs"], pattern="*.pdf")

用户: "搜索 PWM 配置相关的内容"
AI: → search_parsed(query="PWM configuration")

用户: "根据搜索结果写一个定时器初始化函数"
AI: → 生成代码...
```

## 可用工具

| 工具 | 说明 | 配额消耗 |
|------|------|----------|
| `parse_documents` | 解析文档为 Markdown，支持目录和通配符 | ✅ 是 |
| `search_documents` | 搜索指定文件，支持目录和通配符 | ❌ 否（本地） |
| `search_parsed` | 搜索所有已解析的文件 | ❌ 否（本地） |
| `list_parsed` | 列出所有已解析的文件 | ❌ 否 |
| `manage_workspace` | 管理 workspace 缓存 | ❌ 否 |
| `get_quota` | 查询剩余配额 | ❌ 否 |

### 工具参数示例

**parse_documents**
```python
parse_documents(
    files=["./docs", "*.pdf", "report.docx"],  # 支持目录、通配符、具体文件
    pattern="*.pdf"  # 可选，过滤文件类型
)
```

**search_parsed**
```python
search_parsed(
    query="timer interrupt, PWM",  # 关键词搜索效果最好
    filter="MCU",                   # 可选，按文件名过滤
    top_k=5,                        # 返回结果数
    n_lines=30,                     # 上下文行数（建议 30-50）
    ignore_case=True                # 大小写不敏感（推荐）
)
```

**manage_workspace**
```python
# 创建/选择 workspace（后续搜索自动使用）
manage_workspace(action="use", name="my_project")

# 查看状态
manage_workspace(action="status")

# 清理过期文件
manage_workspace(action="prune")
```

## 使用场景

### 电机控制软件开发

```
1. 解析芯片数据手册
   → parse_documents(files=["FU6816_datasheet.pdf"])

2. 搜索寄存器配置
   → search_parsed(query="PWM timer register")

3. AI 根据手册生成代码
   → 生成符合规范的 C 代码
```

### API 文档查询

```
1. 解析 API 文档
   → parse_documents(files=["./api_docs"], pattern="*.pdf")

2. 搜索接口说明
   → search_parsed(query="authentication, API key")

3. AI 生成调用代码
```

## 配置

配置文件位置：`~/.hwdocs/config.json`

```json
{
  "api_token": "your_token_here",
  "api_base": "https://api.hwdocs.dev"
}
```

## 依赖

- Python 3.10+
- semtools CLI (`npm install -g @llamaindex/semtools`)
- MCP 兼容的 AI 编辑器（Cursor、Claude Desktop 等）

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
ruff format
ruff check --fix
```

详细开发文档见 [DEVELOPMENT.md](DEVELOPMENT.md)

## License

MIT
