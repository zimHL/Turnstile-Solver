@echo off
rem =================================================================
rem  Turnstile Solver 初始化脚本 (for Windows)
rem =================================================================
rem
rem  该脚本用于执行以下操作:
rem  1. 确保 'camoufox_cache' 目录存在，用于存放浏览器文件。
rem  2. 运行一次性的 fetch 命令，下载 Camoufox 浏览器和相关依赖。
rem
rem  在首次启动服务前，或在清除了缓存后，请运行此脚本。
rem =================================================================

echo --- [1/2] 正在检查并创建 'camoufox_cache' 目录...
if not exist "camoufox_cache" (
    mkdir "camoufox_cache"
    echo 目录 'camoufox_cache' 已成功创建。
) else (
    echo 目录 'camoufox_cache' 已存在，无需创建。
)
echo.

echo --- [2/2] 准备执行 Camoufox 浏览器下载程序...
echo.
echo     ******************************************************
echo     *  注意: 此过程将下载数百MB的文件，耗时较长，       *
echo     *  具体时间取决于您的网络速度，请耐心等待...        *
echo     ******************************************************
echo.

rem 执行核心下载命令
docker compose run --rm turnstile_solver python -m camoufox fetch

echo.
echo ============================================================
echo.
echo     初始化成功！
echo.
echo     所有必要的浏览器文件都已下载到 'camoufox_cache' 目录。
echo     现在您可以使用 'docker compose up -d' 来启动主服务了。
echo.
echo ============================================================
echo.
pause
