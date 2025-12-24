# hwdocs-mcp 安装指南

本指南帮助您在电脑上安装 hwdocs-mcp 工具，让 Cursor 编辑器能够解析 PDF 文档并进行语义搜索。

## 系统要求

- **操作系统**：Windows 10/11、macOS 10.15+、Linux
- **Python**：3.10 或更高版本
- **Node.js**：18 或更高版本
- **Cursor**：已安装 Cursor 编辑器

---

## 方式一：一键安装（推荐）

### Windows 用户

1. 下载安装脚本 `install-hwdocs.ps1`
2. 右键点击脚本，选择 **"使用 PowerShell 运行"**
3. 按提示输入 API Token 和服务器地址
4. 等待安装完成

> 如果遇到 "禁止运行脚本" 错误，请以管理员身份运行 PowerShell 并执行：
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### macOS/Linux 用户

1. 打开终端
2. 进入脚本所在目录
3. 执行以下命令：
   ```bash
   chmod +x install-hwdocs.sh
   ./install-hwdocs.sh
   ```
4. 按提示输入 API Token 和服务器地址

---

## 方式二：手动安装

如果一键安装失败，可以按以下步骤手动安装。

### 步骤 1：安装 Python

**Windows：**
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.12
3. 安装时 **务必勾选 "Add Python to PATH"**

**macOS：**
```bash
brew install python@3.12
```

**Ubuntu/Debian：**
```bash
sudo apt update
sudo apt install python3.12 python3-pip
```

### 步骤 2：安装 Node.js

**Windows：**
1. 访问 https://nodejs.org/
2. 下载并安装 LTS 版本

**macOS：**
```bash
brew install node
```

**Ubuntu/Debian：**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
```

### 步骤 3：安装 hwdocs-mcp

```bash
pip install hwdocs-mcp
```

### 步骤 4：安装 semtools CLI

```bash
npm install -g @llamaindex/semtools
```

### 步骤 5：配置 API Token

创建配置文件：

**Windows：** `C:\Users\你的用户名\.hwdocs\config.json`

**macOS/Linux：** `~/.hwdocs/config.json`

内容如下（替换为实际值）：
```json
{
  "api_token": "你的API Token",
  "api_base": "https://你的服务器地址"
}
```

### 步骤 6：配置 Cursor

编辑 Cursor MCP 配置文件：

**Windows：** `C:\Users\你的用户名\.cursor\mcp.json`

**macOS/Linux：** `~/.cursor/mcp.json`

添加以下内容：
```json
{
  "mcpServers": {
    "hwdocs": {
      "command": "hwdocs-mcp"
    }
  }
}
```

---

## 验证安装

1. **重启 Cursor 编辑器**

2. 在 Cursor 中新建对话，输入以下测试命令：
   - "列出已解析的文档"
   - "查询我的配额"

3. 如果看到正常回复（即使显示"没有已解析的文档"），说明安装成功。

---

## 使用示例

### 解析 PDF 文档

```
用户：解析 D:\Documents\MCU_datasheet.pdf
```

AI 会调用 `parse_documents` 工具解析文档。

### 搜索内容

```
用户：搜索 PWM 定时器配置相关的内容
```

AI 会调用 `search_parsed` 工具搜索已解析的文档。

### 根据搜索结果生成代码

```
用户：根据搜索到的 PWM 配置信息，写一个定时器初始化函数
```

---

## 常见问题

### Q: 运行 hwdocs-mcp 提示 "找不到命令"

**原因**：Python Scripts 目录不在系统 PATH 中

**解决方法**：
- Windows：将 `C:\Users\你的用户名\AppData\Local\Programs\Python\Python312\Scripts` 添加到系统 PATH
- macOS/Linux：将 `~/.local/bin` 添加到 PATH

### Q: npm install 失败

**解决方法**：
1. 尝试使用管理员权限/sudo 运行
2. 检查网络连接，可能需要配置 npm 镜像：
   ```bash
   npm config set registry https://registry.npmmirror.com
   ```

### Q: Cursor 中看不到 hwdocs 工具

**解决方法**：
1. 确认 `~/.cursor/mcp.json` 配置正确
2. 完全退出 Cursor 后重新打开
3. 检查 Cursor 设置中 MCP 是否已启用

### Q: 解析文档时提示配额不足

**解决方法**：
联系管理员升级配额或等待下月配额重置。

---

## 获取帮助

如果遇到其他问题，请联系技术支持并提供：
1. 错误截图或错误信息
2. 操作系统版本
3. Python 和 Node.js 版本（运行 `python --version` 和 `node --version`）

