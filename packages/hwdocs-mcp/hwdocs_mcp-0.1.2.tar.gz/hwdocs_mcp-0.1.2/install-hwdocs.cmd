@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ====================================
echo    hwdocs-mcp 安装程序
echo    为 Cursor 提供文档解析和语义搜索
echo ====================================
echo.

:: 1. 检查 Python
echo [*] 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 'Add Python to PATH'
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] 找到 Python %PYTHON_VERSION%

:: 2. 检查 Node.js
echo.
echo [*] 检查 Node.js 环境...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Node.js，请先安装
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo [OK] 找到 Node.js %NODE_VERSION%

:: 3. 安装 hwdocs-mcp
echo.
echo [*] 安装 hwdocs-mcp...
python -m pip install --upgrade hwdocs-mcp
if %errorlevel% neq 0 (
    echo [ERROR] hwdocs-mcp 安装失败
    pause
    exit /b 1
)
echo [OK] hwdocs-mcp 安装完成

:: 4. 安装 semtools CLI
echo.
echo [*] 安装 semtools CLI...
call npm install -g @llamaindex/semtools
if %errorlevel% neq 0 (
    echo [WARNING] semtools CLI 安装失败
    echo 请手动运行: npm install -g @llamaindex/semtools
) else (
    echo [OK] semtools CLI 安装完成
)

:: 5. 配置 API Token
echo.
echo [*] 配置 API Token...
set "CONFIG_DIR=%USERPROFILE%\.hwdocs"
set "CONFIG_FILE=%CONFIG_DIR%\config.json"

if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

echo.
set /p "TOKEN=请输入您的 API Token (留空跳过): "
echo.
set /p "API_BASE=请输入 API 服务器地址 (留空使用默认值): "

:: 创建配置文件
echo { > "%CONFIG_FILE%"
if not "%TOKEN%"=="" (
    echo   "api_token": "%TOKEN%", >> "%CONFIG_FILE%"
    echo [OK] Token 已配置
)
if not "%API_BASE%"=="" (
    echo   "api_base": "%API_BASE%" >> "%CONFIG_FILE%"
    echo [OK] API 地址已配置: %API_BASE%
) else (
    echo   "api_base": "" >> "%CONFIG_FILE%"
)
echo } >> "%CONFIG_FILE%"
echo [OK] 配置已保存到: %CONFIG_FILE%

:: 6. 配置 Cursor MCP
echo.
echo [*] 配置 Cursor MCP...
set "CURSOR_DIR=%USERPROFILE%\.cursor"
set "MCP_FILE=%CURSOR_DIR%\mcp.json"

if not exist "%CURSOR_DIR%" mkdir "%CURSOR_DIR%"

:: 创建 MCP 配置文件
echo { > "%MCP_FILE%"
echo   "mcpServers": { >> "%MCP_FILE%"
echo     "hwdocs": { >> "%MCP_FILE%"
echo       "command": "hwdocs-mcp" >> "%MCP_FILE%"
echo     } >> "%MCP_FILE%"
echo   } >> "%MCP_FILE%"
echo } >> "%MCP_FILE%"
echo [OK] Cursor MCP 配置已更新: %MCP_FILE%

:: 完成
echo.
echo ====================================
echo    安装完成!
echo ====================================
echo.
echo 下一步:
echo 1. 重启 Cursor 编辑器
echo 2. 在对话中使用以下命令测试:
echo    - "列出已解析的文档"
echo    - "解析 xxx.pdf 文件"
echo    - "搜索 PWM 配置相关内容"
echo.
echo 配置文件位置:
echo - hwdocs 配置: %CONFIG_FILE%
echo - Cursor MCP: %MCP_FILE%
echo.
echo 如有问题，请查看安装指南或联系技术支持。
echo.

pause
