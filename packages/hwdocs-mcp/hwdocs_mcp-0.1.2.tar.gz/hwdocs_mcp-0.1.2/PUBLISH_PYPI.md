# 发布 hwdocs-mcp 到 PyPI

本文档介绍如何将 hwdocs-mcp 发布到 Python Package Index (PyPI)。

## 前置要求

1. **PyPI 账号**：在 https://pypi.org/account/register/ 注册
2. **API Token**：在 https://pypi.org/manage/account/token/ 创建

## 发布步骤

### 1. 安装构建工具

**推荐：使用虚拟环境（避免污染全局环境）**

**macOS/Linux：**
```bash
cd mcp-server
uv venv
source .venv/bin/activate
uv pip install build twine
```

**Windows (PowerShell)：**
```powershell
cd mcp-server
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install build twine
```

**或使用 pip：**

**macOS/Linux：**
```bash
cd mcp-server
python -m venv .venv
source .venv/bin/activate
pip install build twine
```

**Windows (PowerShell)：**
```powershell
cd mcp-server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install build twine
```

**直接安装（不推荐）**：
```bash
# 会安装到用户目录，不是全局
uv pip install build twine
# 或
pip install build twine
```

### 2. 更新版本号（如需要）

编辑 `src/hwdocs_mcp/__init__.py`：

```python
__version__ = "0.1.0"  # 修改为新版本号
```

### 3. 构建包

```bash
cd mcp-server
python -m build
```

成功后会在 `dist/` 目录生成：
- `hwdocs_mcp-0.1.0-py3-none-any.whl`
- `hwdocs_mcp-0.1.0.tar.gz`

### 4. 测试发布（可选）

先发布到 TestPyPI 测试：

```bash
python -m twine upload --repository testpypi dist/*
```

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ hwdocs-mcp
```

### 5. 正式发布

```bash
python -m twine upload dist/*
```

系统会提示输入：
- Username: `__token__`
- Password: 粘贴您的 PyPI API Token

### 6. 验证发布

```bash
pip install hwdocs-mcp
hwdocs --help
```

## 使用 .pypirc 简化认证

创建 `~/.pypirc` 文件（Windows: `C:\Users\你的用户名\.pypirc`）：

```ini
[pypi]
username = __token__
password = pypi-您的API-Token

[testpypi]
username = __token__
password = pypi-您的TestPyPI-Token
```

之后发布时不再需要输入认证信息。

## 自动化发布（GitHub Actions）

可以配置 GitHub Actions 自动发布。创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install build twine
      
      - name: Build package
        working-directory: ./semtools/mcp-server
        run: python -m build
      
      - name: Publish to PyPI
        working-directory: ./semtools/mcp-server
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
```

然后在 GitHub 仓库设置中添加 Secret `PYPI_API_TOKEN`。

## 版本号规范

建议使用语义化版本号：
- `0.1.0` - 初始版本
- `0.1.1` - Bug 修复
- `0.2.0` - 新功能（向后兼容）
- `1.0.0` - 稳定版本/重大更改

## 常见问题

### Q: 上传失败 "File already exists"

已发布的版本无法覆盖，请更新版本号后重新构建。

### Q: 包名被占用

如果 `hwdocs-mcp` 被占用，需要修改 `pyproject.toml` 中的包名。

### Q: 安装后找不到命令

检查 `pyproject.toml` 中的 `[project.scripts]` 配置是否正确。

