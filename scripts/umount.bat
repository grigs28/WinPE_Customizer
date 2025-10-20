@echo off
setlocal enabledelayedexpansion

for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "C_RED=%ESC%[91m"
set "C_GREEN=%ESC%[92m"
set "C_YELLOW=%ESC%[93m"
set "C_CYAN=%ESC%[96m"
set "C_WHITE=%ESC%[97m"
set "C_RESET=%ESC%[0m"

if "%~1"=="" (
    set "WINPE_DIR=D:\WinPE_amd64"
) else (
    set "WINPE_DIR=%~1"
)
set "MOUNT_DIR=%WINPE_DIR%\mount"

cls
echo.
echo %C_CYAN%========================================%C_RESET%
echo %C_CYAN%    WinPE WIM 卸载工具               %C_RESET%
echo %C_CYAN%========================================%C_RESET%
echo.
echo %C_WHITE%[配置] WinPE 目录: %WINPE_DIR%%C_RESET%
echo %C_WHITE%[配置] 挂载目录: %MOUNT_DIR%%C_RESET%
echo.

if not exist "%MOUNT_DIR%\" (
    echo %C_YELLOW%[提示] 挂载目录不存在，可能未挂载%C_RESET%
    echo %C_YELLOW%[提示] 目录: %MOUNT_DIR%%C_RESET%
    echo.
    pause
    exit /b 0
)

if not exist "%MOUNT_DIR%\Windows\" (
    echo %C_YELLOW%[提示] WIM 映像未挂载%C_RESET%
    echo %C_YELLOW%[提示] 挂载目录中没有 Windows 文件夹%C_RESET%
    echo.
    pause
    exit /b 0
)

echo %C_CYAN%[检测] WIM 映像已挂载%C_RESET%
echo.
echo %C_WHITE%请选择卸载方式:%C_RESET%
echo %C_GREEN%  [1] 保存更改并卸载 (Commit)%C_RESET%
echo %C_RED%  [2] 放弃更改并卸载 (Discard)%C_RESET%
echo %C_YELLOW%  [3] 取消操作%C_RESET%
echo.
set /p "choice=请输入选项 (1/2/3): "

if "%choice%"=="1" goto :COMMIT
if "%choice%"=="2" goto :DISCARD
if "%choice%"=="3" goto :CANCEL
echo %C_RED%[错误] 无效选项%C_RESET%
pause
exit /b 1

:COMMIT
echo.
echo %C_CYAN%========================================%C_RESET%
echo %C_CYAN%    保存更改并卸载 WIM 映像          %C_RESET%
echo %C_CYAN%========================================%C_RESET%
echo.
echo %C_WHITE%[警告] 此操作将保存所有更改到 boot.wim%C_RESET%
echo %C_WHITE%[警告] 请确认已完成所有定制操作%C_RESET%
echo.
pause
echo.
echo %C_CYAN%[执行] 正在卸载并提交更改...%C_RESET%
echo %C_CYAN%--------------------------------------------------------%C_RESET%
dism /unmount-wim /mountdir:%MOUNT_DIR% /commit
set "result=%errorlevel%"
echo %C_CYAN%--------------------------------------------------------%C_RESET%
echo.
if %result% equ 0 (
    echo %C_GREEN%[成功] WIM 映像卸载成功，更改已保存%C_RESET%
    echo %C_GREEN%[成功] boot.wim 文件已更新%C_RESET%
) else (
    echo %C_RED%[失败] WIM 映像卸载失败 (错误代码: %result%)%C_RESET%
    echo %C_YELLOW%[建议] 尝试运行: dism /cleanup-wim%C_RESET%
)
echo.
pause
exit /b %result%

:DISCARD
echo.
echo %C_CYAN%========================================%C_RESET%
echo %C_CYAN%    放弃更改并卸载 WIM 映像          %C_RESET%
echo %C_CYAN%========================================%C_RESET%
echo.
echo %C_RED%[警告] 此操作将丢弃所有更改！%C_RESET%
echo %C_RED%[警告] boot.wim 将恢复到挂载前的状态%C_RESET%
echo.
set /p "confirm=确认放弃所有更改吗? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo %C_YELLOW%[取消] 操作已取消%C_RESET%
    pause
    exit /b 0
)
echo.
echo %C_CYAN%[执行] 正在卸载并放弃更改...%C_RESET%
echo %C_CYAN%--------------------------------------------------------%C_RESET%
dism /unmount-wim /mountdir:%MOUNT_DIR% /discard
set "result=%errorlevel%"
echo %C_CYAN%--------------------------------------------------------%C_RESET%
echo.
if %result% equ 0 (
    echo %C_GREEN%[成功] WIM 映像卸载成功，更改已放弃%C_RESET%
    echo %C_GREEN%[成功] boot.wim 文件保持原样%C_RESET%
) else (
    echo %C_RED%[失败] WIM 映像卸载失败 (错误代码: %result%)%C_RESET%
    echo %C_YELLOW%[建议] 尝试运行: dism /cleanup-wim%C_RESET%
)
echo.
pause
exit /b %result%

:CANCEL
echo.
echo %C_YELLOW%[取消] 操作已取消，WIM 映像保持挂载状态%C_RESET%
echo.
pause
exit /b 0

