# hwdocs-mcp 开发文档

## 项目概述

hwdocs-mcp 是一个 MCP (Model Context Protocol) 服务器，将 semtools 的文档解析和语义搜索能力封装为 MCP 工具，让 Cursor、Claude Desktop 等 AI 编辑器能够方便地使用这些功能。

### 核心价值

- **面向 Cursor 用户**：原 semtools CLI 主要面向 Claude Code 等可执行 bash 的 Agent，本项目让 Cursor 用户也能使用
- **配额管理**：集成 LlamaIndex Cloud API，支持配额追踪和管理
- **简化工作流**：工程师可以解析 PDF 手册后，让 AI 根据手册内容生成代码

### 目标用户场景

```
电机控制软件工程师:
1. 解析芯片数据手册 PDF
2. 搜索寄存器配置、时序说明等信息
3. AI 根据搜索结果生成符合规范的代码
```

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cursor / Claude Desktop                  │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   │ MCP Protocol (stdio)
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                         hwdocs-mcp Server                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Tools     │  │   Config    │  │     Cloud Client        │  │
│  │ - parse     │  │ - api_token │  │ - get_quota()           │  │
│  │ - search    │  │ - api_base  │  │ - deduct_quota()        │  │
│  │ - workspace │  └─────────────┘  └─────────────────────────┘  │
│  └─────────────┘                                                 │
└─────────────────────────────────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              ┌──────────┐  ┌──────────┐  ┌──────────────┐
              │  parse   │  │  search  │  │  workspace   │
              │  binary  │  │  binary  │  │    binary    │
              └──────────┘  └──────────┘  └──────────────┘
                    │              │
                    ▼              ▼
              ┌──────────┐  ┌──────────────────┐
              │ ~/.parse │  │ ~/.semtools/     │
              │ (cache)  │  │ workspaces/      │
              └──────────┘  └──────────────────┘
```

### 数据流

```
PDF 文件 ──parse──> ~/.parse/*.md ──search──> 搜索结果 ──> AI 生成代码
                        │
                        └── workspace 缓存 embeddings 加速搜索
```

---

## 代码结构

```
mcp-server/
├── pyproject.toml          # 项目配置、依赖、入口点
├── README.md               # 用户文档
├── DEVELOPMENT.md          # 开发文档（本文件）
├── src/
│   └── hwdocs_mcp/
│       ├── __init__.py     # 版本信息
│       ├── server.py       # MCP 服务器主逻辑 ⭐
│       ├── config.py       # 配置管理
│       ├── client.py       # Cloud API 客户端
│       ├── bridge.py       # CLI 桥接层（未使用）
│       └── storage.py      # 手册存储（未使用，遗留代码）
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_config.py
    ├── test_storage.py
    └── test_bridge.py
```

### 核心文件说明

| 文件 | 职责 | 状态 |
|------|------|------|
| `server.py` | MCP 服务器、工具定义、命令执行 | ✅ 核心文件 |
| `config.py` | 配置加载/保存、环境变量 | ✅ 使用中 |
| `client.py` | Cloud API 通信、配额管理 | ✅ 使用中 |


---

## MCP 工具详解

### 工具列表

| 工具名 | 功能 | 消耗配额 |
|--------|------|----------|
| `parse_documents` | 解析 PDF/DOCX 等文档 | ✅ 是 |
| `search_documents` | 语义搜索指定文件 | ❌ 否 |
| `search_parsed` | 搜索所有已解析文件 | ❌ 否 |
| `list_parsed` | 列出已解析文件 | ❌ 否 |
| `manage_workspace` | 管理 workspace | ❌ 否 |
| `get_quota` | 查询配额 | ❌ 否 |

### 工具参数详解

#### parse_documents

```python
{
    "files": ["./docs", "*.pdf", "report.pdf"],  # 必需，支持目录/通配符
    "pattern": "*.pdf"                            # 可选，过滤模式
}
```

**处理流程**：
1. `_expand_paths()` 展开目录和通配符
2. 过滤可解析的文件类型
3. 检查配额（如果配置了 API token）
4. 调用 `parse` 二进制执行解析
5. 扣除配额
6. 返回解析后的文件路径

#### search_documents

```python
{
    "query": "PWM configuration",  # 必需
    "files": ["~/.parse"],         # 必需，支持目录/通配符
    "pattern": "*.md",             # 可选
    "top_k": 5,                    # 返回结果数
    "n_lines": 30,                 # 上下文行数
    "max_distance": 0.5,           # 相似度阈值
    "ignore_case": true            # 大小写不敏感
}
```

#### search_parsed

```python
{
    "query": "timer interrupt",    # 必需
    "filter": "MCU",               # 可选，按文件名过滤
    "top_k": 5,
    "n_lines": 30,
    "max_distance": 0.5,
    "ignore_case": true
}
```

自动搜索 `~/.parse` 目录下所有 `.md` 文件。

#### list_parsed

```python
{
    "filter": "datasheet"          # 可选，按文件名过滤
}
```

#### manage_workspace

```python
{
    "action": "use" | "status" | "prune",
    "name": "my_workspace"         # use 时必需
}
```

**重要**：调用 `use` 后，workspace 会保存在全局变量 `_current_workspace`，后续所有搜索自动使用。

---

## 关键实现细节

### 1. Windows 兼容性

`_find_binary()` 函数处理 Windows 上的 `.cmd` 包装脚本问题：

```python
def _find_binary(name: str) -> str | None:
    if sys.platform == "win32":
        # .cmd 脚本无法被 asyncio.create_subprocess_exec 正确执行
        # 需要找到实际的 .exe 文件
        exe_path = shutil.which(f"{name}.exe")
        if exe_path:
            return exe_path
        # 尝试 npm global modules 路径...
    return shutil.which(name)
```

### 2. 路径展开

`_expand_paths()` 支持：
- 绝对路径和相对路径
- `~` 展开为用户目录
- 通配符 `*.pdf`, `**/*.md`
- 目录（配合 pattern 参数过滤）

### 3. Workspace 自动应用

```python
# 全局状态
_current_workspace: str | None = None

# manage_workspace 中设置
if action == "use":
    _current_workspace = name

# search 中自动应用
env = os.environ.copy()
if _current_workspace:
    env["SEMTOOLS_WORKSPACE"] = _current_workspace
```

### 4. 配额管理

```python
# 解析前检查
quota = await client.get_quota()
if quota.remaining_pages < 1:
    return error

# 解析后扣除（估算）
estimated_pages = len(parsed_files) * 5
await client.deduct_quota(estimated_pages)
```

---

## 配置说明

### 用户配置文件

位置：`~/.hwdocs/config.json`

```json
{
    "api_token": "your_token_here",
    "api_base": "https://api.hwdocs.dev"
}
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HWDOCS_DEBUG` | 调试模式 | false |
| `HWDOCS_LOG_LEVEL` | 日志级别 | INFO |
| `SEMTOOLS_WORKSPACE` | 当前 workspace | - |

### MCP 客户端配置

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

或使用虚拟环境：
```json
{
    "mcpServers": {
        "hwdocs": {
            "command": "path/to/.venv/Scripts/python.exe",
            "args": ["-m", "hwdocs_mcp.server"]
        }
    }
}
```

---

## 开发指南

### 环境搭建

```bash
cd mcp-server

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# 安装开发依赖
pip install -e ".[dev]"

# 安装 semtools CLI
npm install -g @llamaindex/semtools
```

### 运行测试

```bash
pytest tests/ -v
```

### 代码格式化

```bash
ruff format src/
ruff check --fix src/
```

### 本地调试

```bash
# 直接运行服务器（stdio 模式）
python -m hwdocs_mcp.server

# 使用 MCP Inspector 调试
npx @modelcontextprotocol/inspector python -m hwdocs_mcp.server
```

### 添加新工具

1. 在 `list_tools()` 中添加 Tool 定义
2. 在 `call_tool()` 中添加路由
3. 实现 `_handle_xxx()` 处理函数
4. 添加测试

示例：
```python
# 1. 工具定义
Tool(
    name="new_tool",
    description="...",
    inputSchema={...}
)

# 2. 路由
elif name == "new_tool":
    return await _handle_new_tool(arguments)

# 3. 处理函数
async def _handle_new_tool(arguments: dict[str, Any]) -> list[TextContent]:
    # 实现逻辑
    return [TextContent(type="text", text="result")]
```

---

## 未来改进方向

### 优先级高（用户反馈后考虑）

| 功能 | 说明 | 复杂度 |
|------|------|--------|
| `filter_regex` | 搜索结果正则过滤 | 低 |
| 更精确的配额计算 | 根据实际页数扣除 | 中 |

### 优先级中

| 功能 | 说明 | 复杂度 |
|------|------|--------|
| `parse_and_search` | 组合工具 | 中 |
| 解析进度反馈 | 大文件解析时显示进度 | 中 |
| 多语言支持 | 工具描述国际化 | 低 |

### 优先级低（暂不建议）

| 功能 | 说明 | 原因 |
|------|------|------|
| stdin 输入 | 搜索文本内容 | 场景不匹配 |
| 实时流式输出 | 边执行边返回 | MCP 协议限制 |
| 管道组合 | 工具间管道 | 过度工程化 |

---



---

## 版本历史

### v0.1.0 (当前)

- 基础 MCP 服务器实现
- 6 个核心工具
- Windows 兼容性修复
- 目录和通配符支持
- Workspace 自动应用
- Cloud API 配额集成

---

## 联系与支持

- 项目仓库：https://github.com/run-llama/semtools
- 问题反馈：通过 GitHub Issues

