@echo off
REM ============================================================================
REM WinPE Customizer 命令行版本启动脚本
REM 必须在"部署和映像工具环境"中以管理员身份运行
REM ============================================================================

echo ============================================================
echo    WinPE Customizer v3.0 - Windows PE 定制工具
echo ============================================================
echo.
echo [提示] 请确保在"部署和映像工具环境"中运行此脚本
echo.

REM 检查是否提供了参数
if "%~1"=="" (
    echo 使用方法:
    echo   WinPE_Customizer.bat [WinPE工作目录]
    echo.
    echo 示例:
    echo   WinPE_Customizer.bat D:\WinPE_amd64
    echo.
    pause
    exit /b 1
)

REM 运行Python脚本
python -m core.WinPE_Customizer %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 执行失败，退出代码: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [完成] 执行成功
pause

