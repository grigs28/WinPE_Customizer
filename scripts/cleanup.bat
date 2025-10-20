@echo off
setlocal enabledelayedexpansion

for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "C_RED=%ESC%[91m"
set "C_GREEN=%ESC%[92m"
set "C_YELLOW=%ESC%[93m"
set "C_CYAN=%ESC%[96m"
set "C_WHITE=%ESC%[97m"
set "C_RESET=%ESC%[0m"

cls
echo.
echo %C_CYAN%========================================%C_RESET%
echo %C_CYAN%    WinPE 清理修复工具              %C_RESET%
echo %C_CYAN%========================================%C_RESET%
echo.
echo %C_WHITE%[说明] 此工具用于清理异常的 WIM 挂载%C_RESET%
echo %C_WHITE%[说明] 解决 "映像需要重新挂载" 等错误%C_RESET%
echo.

echo %C_YELLOW%[警告] 此操作将:%C_RESET%
echo %C_YELLOW%       1. 强制卸载所有挂载的 WIM 映像%C_RESET%
echo %C_YELLOW%       2. 清理 WIM 挂载点%C_RESET%
echo %C_YELLOW%       3. 放弃未保存的更改%C_RESET%
echo.
set /p "confirm=确认执行清理操作吗? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo %C_YELLOW%[取消] 操作已取消%C_RESET%
    pause
    exit /b 0
)

echo.
echo %C_CYAN%========================================%C_RESET%
echo %C_CYAN%    开始执行清理操作...              %C_RESET%
echo %C_CYAN%========================================%C_RESET%
echo.

echo %C_WHITE%[步骤1] 清理 WIM 挂载点...%C_RESET%
echo %C_CYAN%--------------------------------------------------------%C_RESET%
dism /cleanup-wim
echo %C_CYAN%--------------------------------------------------------%C_RESET%
if errorlevel 1 (
    echo %C_YELLOW%[警告] 清理命令返回警告，继续...%C_RESET%
) else (
    echo %C_GREEN%[完成] WIM 挂载点清理完成%C_RESET%
)
echo.

echo %C_WHITE%[步骤2] 获取当前挂载的映像信息...%C_RESET%
echo %C_CYAN%--------------------------------------------------------%C_RESET%
dism /get-mountedimageinfo
echo %C_CYAN%--------------------------------------------------------%C_RESET%
echo.

echo %C_WHITE%[步骤3] 尝试修复损坏的映像...%C_RESET%
echo %C_CYAN%--------------------------------------------------------%C_RESET%
dism /cleanup-mountpoints
echo %C_CYAN%--------------------------------------------------------%C_RESET%
if errorlevel 1 (
    echo %C_YELLOW%[警告] 修复命令返回警告%C_RESET%
) else (
    echo %C_GREEN%[完成] 挂载点修复完成%C_RESET%
)
echo.

echo %C_CYAN%========================================%C_RESET%
echo %C_CYAN%    清理操作已完成                   %C_RESET%
echo %C_CYAN%========================================%C_RESET%
echo.
echo %C_GREEN%[完成] 所有清理步骤已执行%C_RESET%
echo.
echo %C_WHITE%[后续] 您现在可以:%C_RESET%
echo %C_WHITE%       1. 重新运行 WinPE_Customizer.bat%C_RESET%
echo %C_WHITE%       2. 手动挂载 WIM 映像%C_RESET%
echo %C_WHITE%       3. 检查 DISM 日志了解问题原因%C_RESET%
echo.
echo %C_CYAN%[日志] DISM 日志位置:%C_RESET%
echo %C_WHITE%       C:\WINDOWS\Logs\DISM\dism.log%C_RESET%
echo.
pause
endlocal
exit /b 0

