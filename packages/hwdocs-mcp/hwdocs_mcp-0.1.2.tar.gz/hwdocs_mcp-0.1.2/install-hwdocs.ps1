# hwdocs-mcp 一键安装脚本 (Windows PowerShell)
# 运行方式: 右键点击脚本 -> 使用 PowerShell 运行
# 或在 PowerShell 中执行: .\install-hwdocs.ps1

param(
    [string]$Token = "",
    [string]$ApiBase = ""
)

# 设置 UTF-8 编码，解决中文显示乱码问题
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n[*] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# 欢迎信息
Write-Host @"

====================================
   hwdocs-mcp 安装程序
   为 Cursor 提供文档解析和语义搜索
====================================

"@ -ForegroundColor Magenta

# 1. 检查 Python
Write-Step "检查 Python 环境..."
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3\.1[0-9]") {
            $pythonCmd = $cmd
            Write-Success "找到 $version"
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Error "未找到 Python 3.10+，请先安装 Python"
    Write-Host "下载地址: https://www.python.org/downloads/"
    Write-Host "安装时请勾选 'Add Python to PATH'"
    pause
    exit 1
}

# 2. 检查 Node.js
Write-Step "检查 Node.js 环境..."
try {
    $nodeVersion = & node --version 2>&1
    if ($nodeVersion -match "v(\d+)") {
        $major = [int]$Matches[1]
        if ($major -ge 18) {
            Write-Success "找到 Node.js $nodeVersion"
        } else {
            Write-Warning "Node.js 版本过低 ($nodeVersion)，建议升级到 v18+"
        }
    }
} catch {
    Write-Error "未找到 Node.js，请先安装"
    Write-Host "下载地址: https://nodejs.org/"
    pause
    exit 1
}

# 3. 安装 hwdocs-mcp
Write-Step "安装 hwdocs-mcp..."
try {
    & $pythonCmd -m pip install --upgrade hwdocs-mcp
    Write-Success "hwdocs-mcp 安装完成"
} catch {
    Write-Error "hwdocs-mcp 安装失败: $_"
    pause
    exit 1
}

# 4. 安装 semtools CLI
Write-Step "安装 semtools CLI..."
try {
    & npm install -g @llamaindex/semtools
    Write-Success "semtools CLI 安装完成"
} catch {
    Write-Error "semtools CLI 安装失败: $_"
    Write-Host "请手动运行: npm install -g @llamaindex/semtools"
}

# 5. 配置 API Token
Write-Step "配置 API Token..."
$configDir = Join-Path $env:USERPROFILE ".hwdocs"
$configFile = Join-Path $configDir "config.json"

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

# 读取现有配置或创建新配置
$config = @{}
if (Test-Path $configFile) {
    try {
        $config = Get-Content $configFile | ConvertFrom-Json -AsHashtable
    } catch {}
}

# 获取 Token
if (-not $Token) {
    Write-Host "`n请输入您的 API Token (留空跳过):"
    $Token = Read-Host
}

if ($Token) {
    $config["api_token"] = $Token
    Write-Success "Token 已配置"
}

# 获取 API Base URL
if (-not $ApiBase) {
    Write-Host "`n请输入 API 服务器地址 (留空使用默认值):"
    $ApiBase = Read-Host
}

if ($ApiBase) {
    $config["api_base"] = $ApiBase
    Write-Success "API 地址已配置: $ApiBase"
}

# 保存配置
$config | ConvertTo-Json | Set-Content $configFile -Encoding UTF8
Write-Success "配置已保存到: $configFile"

# 6. 配置 Cursor MCP
Write-Step "配置 Cursor MCP..."
$cursorConfigDir = Join-Path $env:USERPROFILE ".cursor"
$mcpConfigFile = Join-Path $cursorConfigDir "mcp.json"

if (-not (Test-Path $cursorConfigDir)) {
    New-Item -ItemType Directory -Path $cursorConfigDir -Force | Out-Null
}

# 读取或创建 MCP 配置
$mcpConfig = @{ "mcpServers" = @{} }
if (Test-Path $mcpConfigFile) {
    try {
        $mcpConfig = Get-Content $mcpConfigFile | ConvertFrom-Json -AsHashtable
        if (-not $mcpConfig.ContainsKey("mcpServers")) {
            $mcpConfig["mcpServers"] = @{}
        }
    } catch {}
}

# 添加 hwdocs 服务器
$mcpConfig["mcpServers"]["hwdocs"] = @{
    "command" = "hwdocs-mcp"
}

# 保存配置
$mcpConfig | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigFile -Encoding UTF8
Write-Success "Cursor MCP 配置已更新: $mcpConfigFile"

# 完成
Write-Host @"

====================================
   安装完成!
====================================

下一步:
1. 重启 Cursor 编辑器
2. 在对话中使用以下命令测试:
   - "列出已解析的文档"
   - "解析 xxx.pdf 文件"
   - "搜索 PWM 配置相关内容"

配置文件位置:
- hwdocs 配置: $configFile
- Cursor MCP: $mcpConfigFile

如有问题，请查看安装指南或联系技术支持。

"@ -ForegroundColor Green

pause

