@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: EconoNews 一键启动脚本 (Windows)
:: 用法: start.bat [--backend-only | --frontend-only | --setup-only | --stop | --status]

:: 项目根目录
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

:: 打印 Banner
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║       EconoNews Intelligence Hub - 一键启动脚本         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: 解析参数
set "MODE=%1"
if "%MODE%"=="" set "MODE=full"

:: 帮助信息
if "%MODE%"=="--help" goto :show_help
if "%MODE%"=="-h" goto :show_help

:: 停止服务
if "%MODE%"=="--stop" goto :stop_services

:: 查看状态
if "%MODE%"=="--status" goto :show_status

:: 检测 Python
echo [INFO] 检查系统依赖...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.8+
    echo         下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python 版本: %PYTHON_VERSION%

:: 检测 pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 pip，请先安装 pip
    pause
    exit /b 1
)
echo [SUCCESS] pip 已就绪

:: 仅后端模式跳过 Node.js 检查
if "%MODE%"=="--backend-only" goto :setup_backend
if "%MODE%"=="--setup-only" goto :setup_backend

:: 检测 Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 16+
    echo         下载地址: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1 delims= " %%i in ('node --version') do set NODE_VERSION=%%i
echo [SUCCESS] Node.js 版本: %NODE_VERSION%

:: 检测 npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 npm，请先安装 npm
    pause
    exit /b 1
)

for /f "tokens=1 delims= " %%i in ('npm --version') do set NPM_VERSION=%%i
echo [SUCCESS] npm 版本: %NPM_VERSION%

:: 设置后端环境
:setup_backend
echo.
echo [INFO] 配置后端环境...
cd /d "%BACKEND_DIR%"

:: 创建虚拟环境
if not exist ".venv" (
    echo [INFO] 创建 Python 虚拟环境...
    python -m venv .venv
    echo [SUCCESS] 虚拟环境创建完成
) else (
    echo [INFO] 虚拟环境已存在，跳过创建
)

:: 激活虚拟环境
echo [INFO] 激活虚拟环境...
call .venv\Scripts\activate.bat

:: 升级 pip
echo [INFO] 升级 pip...
python -m pip install --upgrade pip -q

:: 安装依赖
echo [INFO] 安装 Python 依赖...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [ERROR] Python 依赖安装失败
    pause
    exit /b 1
)
echo [SUCCESS] Python 依赖安装完成

:: 配置 .env 文件
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] 创建 .env 配置文件...
        copy .env.example .env >nul
        echo [SUCCESS] .env 文件已创建
        echo [WARNING] 请编辑 backend\.env 文件配置必要的参数 (如 TUSHARE_TOKEN)
    ) else (
        echo [WARNING] 未找到 .env.example 文件
    )
) else (
    echo [INFO] .env 文件已存在，跳过创建
)

:: 仅安装模式
if "%MODE%"=="--setup-only" goto :setup_frontend_only

:: 仅前端模式跳过后端启动
if "%MODE%"=="--frontend-only" goto :setup_frontend

:: 启动后端服务
echo.
echo [INFO] 启动后端服务...
start "EconoNews Backend" cmd /c ".venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo [SUCCESS] 后端服务已在新窗口启动 (http://127.0.0.1:8000)
echo [INFO] API 文档地址 (http://127.0.0.1:8000/docs)

:: 仅后端模式
if "%MODE%"=="--backend-only" (
    echo.
    echo [SUCCESS] 后端服务已启动！
    echo.
    echo 访问地址:
    echo   - 后端 API: http://127.0.0.1:8000
    echo   - API 文档: http://127.0.0.1:8000/docs
    pause
    exit /b 0
)

:: 设置前端环境
:setup_frontend
echo.
echo [INFO] 配置前端环境...
cd /d "%FRONTEND_DIR%"

:: 安装依赖
if not exist "node_modules" (
    echo [INFO] 安装前端依赖...
    call npm install
    echo [SUCCESS] 前端依赖安装完成
) else (
    echo [INFO] node_modules 已存在，检查更新...
    call npm install
)

:: 配置 .env 文件
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] 创建前端 .env 配置文件...
        copy .env.example .env >nul
        echo [SUCCESS] 前端 .env 文件已创建
    ) else (
        echo [WARNING] 未找到前端 .env.example 文件
    )
) else (
    echo [INFO] 前端 .env 文件已存在，跳过创建
)

:: 仅安装模式
if "%MODE%"=="--setup-only" (
    echo.
    echo [SUCCESS] 环境配置完成！
    echo.
    echo 下一步:
    echo   1. 编辑 backend\.env 配置必要参数
    echo   2. 运行 start.bat 启动服务
    pause
    exit /b 0
)

:: 启动前端服务
echo.
echo [INFO] 启动前端服务...
start "EconoNews Frontend" cmd /c "npm run dev"
echo [SUCCESS] 前端服务已在新窗口启动 (http://localhost:5173)

:: 完成
echo.
echo ══════════════════════════════════════════════════════════
echo [SUCCESS] 所有服务启动完成！
echo ══════════════════════════════════════════════════════════
echo.
echo 访问地址:
echo   - 前端应用: http://localhost:5173
echo   - 后端 API: http://127.0.0.1:8000
echo   - API 文档: http://127.0.0.1:8000/docs
echo.
echo 停止服务:
echo   - 关闭弹出的命令行窗口，或
echo   - 运行 start.bat --stop
echo.
pause
exit /b 0

:: 仅设置前端（用于 --setup-only）
:setup_frontend_only
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo [INFO] 安装前端依赖...
    call npm install
    echo [SUCCESS] 前端依赖安装完成
)
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [SUCCESS] 前端 .env 文件已创建
    )
)
echo.
echo [SUCCESS] 环境配置完成！
echo.
echo 下一步:
echo   1. 编辑 backend\.env 配置必要参数
echo   2. 运行 start.bat 启动服务
pause
exit /b 0

:: 停止服务
:stop_services
echo [INFO] 停止服务...
taskkill /f /im "python.exe" /fi "WINDOWTITLE eq EconoNews*" >nul 2>&1
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq EconoNews*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq EconoNews Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq EconoNews Frontend*" >nul 2>&1
echo [SUCCESS] 服务已停止
pause
exit /b 0

:: 查看状态
:show_status
echo [INFO] 服务状态:
echo.

:: 检查后端
curl -s http://127.0.0.1:8000/api/v1/system/heartbeats >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] 后端服务: 运行中 (http://127.0.0.1:8000^)
) else (
    echo [WARNING] 后端服务: 未运行
)

:: 检查前端
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] 前端服务: 运行中 (http://localhost:5173^)
) else (
    echo [WARNING] 前端服务: 未运行
)

echo.
pause
exit /b 0

:: 显示帮助
:show_help
echo 用法: start.bat [选项]
echo.
echo 选项:
echo   无参数          完整安装并启动所有服务
echo   --setup-only    仅安装依赖，不启动服务
echo   --backend-only  仅启动后端服务
echo   --frontend-only 仅启动前端服务
echo   --stop          停止所有服务
echo   --status        查看服务状态
echo   --help          显示此帮助信息
echo.
echo 首次运行建议:
echo   1. 编辑 backend\.env 配置 TUSHARE_TOKEN 等参数
echo   2. 运行 start.bat 启动服务
echo   3. 访问 http://localhost:5173 使用应用
echo.
pause
exit /b 0