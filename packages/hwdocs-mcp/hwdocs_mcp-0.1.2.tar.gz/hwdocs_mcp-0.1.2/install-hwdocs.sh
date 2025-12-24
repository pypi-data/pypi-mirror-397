#!/bin/bash
# hwdocs-mcp 一键安装脚本 (macOS/Linux)
# 运行方式: chmod +x install-hwdocs.sh && ./install-hwdocs.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

step() {
    echo -e "\n${CYAN}[*] $1${NC}"
}

success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# 欢迎信息
echo -e "${MAGENTA}"
echo "===================================="
echo "   hwdocs-mcp 安装程序"
echo "   为 Cursor 提供文档解析和语义搜索"
echo "===================================="
echo -e "${NC}"

# 1. 检查 Python
step "检查 Python 环境..."
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v $cmd &> /dev/null; then
        version=$($cmd --version 2>&1)
        if [[ $version =~ Python\ 3\.1[0-9] ]]; then
            PYTHON_CMD=$cmd
            success "找到 $version"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    error "未找到 Python 3.10+，请先安装 Python"
    echo "macOS: brew install python@3.12"
    echo "Ubuntu: sudo apt install python3.12"
    exit 1
fi

# 2. 检查 Node.js
step "检查 Node.js 环境..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    MAJOR_VERSION=$(echo $NODE_VERSION | sed 's/v\([0-9]*\).*/\1/')
    if [ "$MAJOR_VERSION" -ge 18 ]; then
        success "找到 Node.js $NODE_VERSION"
    else
        warning "Node.js 版本过低 ($NODE_VERSION)，建议升级到 v18+"
    fi
else
    error "未找到 Node.js，请先安装"
    echo "macOS: brew install node"
    echo "Ubuntu: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install nodejs"
    exit 1
fi

# 3. 安装 hwdocs-mcp
step "安装 hwdocs-mcp..."
if $PYTHON_CMD -m pip install --upgrade hwdocs-mcp; then
    success "hwdocs-mcp 安装完成"
else
    error "hwdocs-mcp 安装失败"
    exit 1
fi

# 4. 安装 semtools CLI
step "安装 semtools CLI..."
if npm install -g @llamaindex/semtools; then
    success "semtools CLI 安装完成"
else
    error "semtools CLI 安装失败"
    echo "请手动运行: npm install -g @llamaindex/semtools"
fi

# 5. 配置 API Token
step "配置 API Token..."
CONFIG_DIR="$HOME/.hwdocs"
CONFIG_FILE="$CONFIG_DIR/config.json"

mkdir -p "$CONFIG_DIR"

# 读取现有配置或创建新配置
if [ -f "$CONFIG_FILE" ]; then
    CONFIG=$(cat "$CONFIG_FILE")
else
    CONFIG='{}'
fi

# 获取 Token
echo ""
read -p "请输入您的 API Token (留空跳过): " TOKEN

if [ -n "$TOKEN" ]; then
    CONFIG=$(echo "$CONFIG" | $PYTHON_CMD -c "
import json, sys
config = json.loads(sys.stdin.read() or '{}')
config['api_token'] = '$TOKEN'
print(json.dumps(config, indent=2))
")
    success "Token 已配置"
fi

# 获取 API Base URL
echo ""
read -p "请输入 API 服务器地址 (留空使用默认值): " API_BASE

if [ -n "$API_BASE" ]; then
    CONFIG=$(echo "$CONFIG" | $PYTHON_CMD -c "
import json, sys
config = json.loads(sys.stdin.read() or '{}')
config['api_base'] = '$API_BASE'
print(json.dumps(config, indent=2))
")
    success "API 地址已配置: $API_BASE"
fi

# 保存配置
echo "$CONFIG" > "$CONFIG_FILE"
success "配置已保存到: $CONFIG_FILE"

# 6. 配置 Cursor MCP
step "配置 Cursor MCP..."
CURSOR_CONFIG_DIR="$HOME/.cursor"
MCP_CONFIG_FILE="$CURSOR_CONFIG_DIR/mcp.json"

mkdir -p "$CURSOR_CONFIG_DIR"

# 读取或创建 MCP 配置
if [ -f "$MCP_CONFIG_FILE" ]; then
    MCP_CONFIG=$(cat "$MCP_CONFIG_FILE")
else
    MCP_CONFIG='{"mcpServers":{}}'
fi

# 添加 hwdocs 服务器
MCP_CONFIG=$($PYTHON_CMD -c "
import json
config = json.loads('''$MCP_CONFIG''' or '{\"mcpServers\":{}}')
if 'mcpServers' not in config:
    config['mcpServers'] = {}
config['mcpServers']['hwdocs'] = {'command': 'hwdocs-mcp'}
print(json.dumps(config, indent=2))
")

# 保存配置
echo "$MCP_CONFIG" > "$MCP_CONFIG_FILE"
success "Cursor MCP 配置已更新: $MCP_CONFIG_FILE"

# 完成
echo -e "${GREEN}"
echo "===================================="
echo "   安装完成!"
echo "===================================="
echo ""
echo "下一步:"
echo "1. 重启 Cursor 编辑器"
echo "2. 在对话中使用以下命令测试:"
echo "   - \"列出已解析的文档\""
echo "   - \"解析 xxx.pdf 文件\""
echo "   - \"搜索 PWM 配置相关内容\""
echo ""
echo "配置文件位置:"
echo "- hwdocs 配置: $CONFIG_FILE"
echo "- Cursor MCP: $MCP_CONFIG_FILE"
echo ""
echo "如有问题，请查看安装指南或联系技术支持。"
echo -e "${NC}"

