#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WinPE Customizer v3.0 - Python 版本
用途: 自动化创建、定制和打包 Windows PE 启动映像
作者: Auto Customizer
日期: 2025-10-20
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path
from colorama import init, Fore, Style

# 导入配置
from . import config

# 初始化 colorama（Windows 彩色输出支持）
init(autoreset=True)


class WinPECustomizer:
    """WinPE 定制工具类"""
    
    def __init__(self, winpe_dir=None, silent_mode=False):
        """初始化配置"""
        # work_dir 是项目根目录（core的父目录）
        self.work_dir = Path(__file__).parent.parent.absolute()
        self.silent_mode = silent_mode  # 静默模式（不输出到控制台）
        self.last_progress = -1  # 上次显示的进度（用于去重）
        
        # 从 config.py 加载路径配置
        if winpe_dir:
            winpe_dir = str(winpe_dir).replace('\\', '/')
            self.winpe_dir = Path(winpe_dir)
        else:
            self.winpe_dir = Path(config.WINPE_DIR)
        
        self.mount_dir = self.winpe_dir / "mount"
        self.cab_path = Path(config.CAB_PATH)
        self.external_apps = self.work_dir / config.EXTERNAL_APPS_DIR
        self.driver_path = self.work_dir / config.DRIVER_DIR
        self.final_iso = self.work_dir / config.OUTPUT_ISO_NAME
        
        # 从 config.py 加载模块开关
        self.enable_copype_setup = config.ENABLE_COPYPE_SETUP
        self.enable_auto_mount = config.ENABLE_AUTO_MOUNT
        self.enable_feature_packs = config.ENABLE_FEATURE_PACKS
        self.enable_language_packs = config.ENABLE_LANGUAGE_PACKS
        self.enable_fonts_lp = config.ENABLE_FONTS_LP
        self.enable_regional_settings = config.ENABLE_REGIONAL_SETTINGS
        self.enable_drivers = config.ENABLE_DRIVERS
        self.enable_external_apps = config.ENABLE_EXTERNAL_APPS
        self.enable_create_dirs = config.ENABLE_CREATE_DIRS
        self.enable_make_iso = config.ENABLE_MAKE_ISO
        
        # 从 config.py 加载包列表
        self.feature_packages = config.FEATURE_PACKAGES
        self.language_packages = config.LANGUAGE_PACKAGES
    
    def print_header(self, text):
        """打印标题"""
        if not self.silent_mode:
            print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{text:^50}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    
    def print_info(self, text):
        """打印普通信息（白色）"""
        if not self.silent_mode:
            print(f"{Fore.WHITE}{text}{Style.RESET_ALL}")
    
    def print_success(self, text):
        """打印成功信息（绿色）"""
        if not self.silent_mode:
            print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")
    
    def print_error(self, text):
        """打印错误信息（红色）"""
        if not self.silent_mode:
            print(f"{Fore.RED}{text}{Style.RESET_ALL}")
    
    def print_warning(self, text):
        """打印警告信息（黄色）"""
        if not self.silent_mode:
            print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")
    
    def print_cyan(self, text):
        """打印青色信息"""
        if not self.silent_mode:
            print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
    
    def run_command(self, cmd):
        """执行命令并显示输出"""
        if not self.silent_mode:
            print()
            self.print_cyan("[命令执行] 准备执行命令:")
            self.print_info(f"   {cmd}")
            self.print_cyan("=" * 56)
            print()
            
            result = subprocess.run(cmd, shell=True)
            
            print()
            self.print_cyan("=" * 56)
            if result.returncode == 0:
                self.print_success("[命令结果] 命令执行成功 (Exit Code: 0)")
            else:
                self.print_error(f"[命令结果] 命令执行失败 (Exit Code: {result.returncode})")
            print()
        else:
            # 静默模式：捕获输出，不显示在控制台
            self.print_cyan("[命令执行] 准备执行命令:")
            self.print_info(f"   {cmd}")
            
            # Windows: 隐藏窗口
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                cmd, 
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=startupinfo
            )
            
            # 处理输出（发送到日志队列）
            if result.stdout:
                self._process_command_output(result.stdout)
            
            if result.returncode == 0:
                self.print_success("[命令结果] 命令执行成功")
            else:
                self.print_error(f"[命令结果] 命令执行失败 (Exit Code: {result.returncode})")
                if result.stderr:
                    self.print_error(result.stderr)
        
        return result.returncode
    
    def _process_command_output(self, output):
        """处理命令输出"""
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # 检测进度条
            if '[' in line and '%' in line and '=' in line:
                # 提取百分比
                import re
                match = re.search(r'(\d+\.?\d*)%', line)
                if match:
                    percent = match.group(1)
                    self.print_info(f"[进度] {percent}%")
            elif line:
                # 普通输出
                self.print_info(line)
    
    def show_config(self):
        """显示配置信息"""
        if not self.silent_mode:
            os.system('cls' if os.name == 'nt' else 'clear')
            print()
            self.print_cyan("=" * 40)
            self.print_cyan("    WinPE 定制脚本 v3.0 (Python)    ")
            self.print_cyan("=" * 40)
            print()
            
            self.print_info(f"[系统信息] Python 版本: {sys.version.split()[0]}")
            self.print_info(f"[时间信息] 脚本启动时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            self.print_info(f"[路径配置] 工作目录: {self.work_dir}")
            self.print_info(f"[路径配置] WinPE 目录: {self.winpe_dir}")
            self.print_info(f"[路径配置] 挂载目录: {self.mount_dir}")
            self.print_info(f"[路径配置] Windows ADK 路径:")
            self.print_info(f"             {self.cab_path}")
            self.print_info(f"[路径配置] 驱动程序目录: {self.driver_path}")
            self.print_info(f"[路径配置] 附加程序目录: {self.external_apps}")
            self.print_info(f"[路径配置] 输出 ISO 文件: {self.final_iso}")
            print()
    
    def check_adk_path(self):
        """检查 Windows ADK 路径"""
        self.print_cyan("[检查中] 正在检查 Windows ADK 安装路径...")
        
        if not self.cab_path.exists():
            self.print_error("[错误] Windows ADK 路径不存在")
            self.print_error("[错误] 请先安装 Windows ADK 或修改脚本中的 cab_path 变量")
            print()
            self.print_warning("[提示] Windows ADK 下载地址:")
            self.print_warning("[提示] https://learn.microsoft.com/zh-cn/windows-hardware/get-started/adk-install")
            print()
            input("按任意键退出...")
            return False
        
        self.print_success("[通过] Windows ADK 路径检查通过")
        print()
        return True
    
    def create_winpe_environment(self):
        """创建 WinPE 工作环境"""
        if not self.enable_copype_setup:
            return True
        
        self.print_cyan("[检查中] 正在检查 WinPE 工作目录...")
        
        if self.winpe_dir.exists():
            self.print_success(f"[跳过] WinPE 工作目录已存在: {self.winpe_dir}")
            print()
            return True
        
        print()
        self.print_header("步骤 0: 创建 WinPE 工作环境")
        self.print_info("[说明] WinPE 工作目录不存在，将执行 copype 创建")
        self.print_info(f"[目标] {self.winpe_dir}")
        
        cmd = f'copype amd64 "{self.winpe_dir}"'
        exit_code = self.run_command(cmd)
        
        if exit_code != 0:
            self.print_error("[失败] copype 命令执行失败")
            input("按任意键退出...")
            return False
        
        self.print_success("[完成] WinPE 工作环境创建完成")
        print()
        return True
    
    def check_and_mount_wim(self):
        """检查并挂载 WIM 映像"""
        if not self.enable_auto_mount:
            self.print_warning("[跳过] 已禁用自动挂载功能")
            return True
        
        print()
        self.print_header("步骤 1: 检查并挂载 WIM 映像文件")
        
        boot_wim = self.winpe_dir / "media" / "sources" / "boot.wim"
        
        if not boot_wim.exists():
            self.print_error("[错误] boot.wim 文件不存在")
            self.print_error(f"[错误] 路径: {boot_wim}")
            return False
        
        # 创建挂载目录
        if not self.mount_dir.exists():
            self.print_info(f"[创建] 挂载目录不存在，正在创建: {self.mount_dir}")
            self.mount_dir.mkdir(parents=True)
            self.print_success("[完成] 挂载目录创建完成")
        
        # 检查是否已挂载
        windows_dir = self.mount_dir / "Windows"
        if windows_dir.exists():
            self.print_success("[已挂载] WIM 映像已经处于挂载状态，跳过挂载操作")
            self.print_success(f"[已挂载] 挂载点: {self.mount_dir}")
            self.print_success("[已挂载] 检测到 Windows 目录存在")
        else:
            self.print_info("[准备] 挂载目录存在但为空，准备挂载 WIM 映像...")
            self.print_info(f"[准备] WIM 文件路径: {boot_wim}")
            self.print_info(f"[准备] 挂载目标目录: {self.mount_dir}")
            
            cmd = f'dism /mount-wim /wimfile:"{boot_wim}" /index:1 /mountdir:"{self.mount_dir}"'
            exit_code = self.run_command(cmd)
            
            if exit_code != 0:
                self.print_error("[失败] WIM 映像挂载失败")
                return False
            
            self.print_success("[成功] WIM 映像挂载完成")
            
            # 验证挂载
            if windows_dir.exists():
                self.print_success("[验证] Windows 目录存在，挂载成功")
            else:
                self.print_error("[错误] Windows 目录不存在，挂载可能失败")
                return False
        
        print()
        return True
    
    def install_package(self, pkg_name, pkg_desc):
        """安装单个功能包"""
        pkg_file = self.cab_path / f"{pkg_name}.cab"
        
        if not self.silent_mode:
            print()
        self.print_cyan("=" * 42)
        
        if pkg_file.exists():
            self.print_info(f"[安装中] {pkg_desc}")
            self.print_cyan("=" * 42)
            
            cmd = f'dism /image:"{self.mount_dir}" /add-package /packagepath:"{pkg_file}"'
            
            if not self.silent_mode:
                # 命令行模式：显示命令和实时输出
                print()
                self.print_info(f"[命令] {cmd}")
                print()
                
                # 执行命令并实时过滤输出
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    bufsize=1
                )
                
                # 逐行读取输出并过滤
                last_was_progress = False
                for line in process.stdout:
                    line = line.rstrip()
                    # 检测进度条
                    if '[' in line and '%' in line and '=' in line:
                        # 在同一行显示进度条
                        print(f"\r{line}", end='', flush=True)
                        last_was_progress = True
                        continue
                    # 显示其他输出
                    if line.strip():
                        # 如果上一行是进度条，先换行
                        if last_was_progress:
                            print()
                            last_was_progress = False
                        print(line)
                
                # 如果最后一行是进度条，换行
                if last_was_progress:
                    print()
                
                process.wait()
                exit_code = process.returncode
                
                print()
            else:
                # 静默模式：捕获输出，发送到日志队列
                self.print_info(f"[命令] 正在执行 DISM...")
                
                # Windows: 隐藏窗口
                startupinfo = None
                if sys.platform == 'win32':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    bufsize=1,
                    startupinfo=startupinfo
                )
                
                # 逐行读取并发送到日志
                for line in process.stdout:
                    line = line.rstrip()
                    if not line.strip():
                        continue
                    
                    # 检测进度条
                    if '[' in line and '%' in line and '=' in line:
                        import re
                        match = re.search(r'(\d+\.?\d*)%', line)
                        if match:
                            percent = float(match.group(1))
                            # 每次都输出进度，GUI会在同一行更新
                            self.print_info(f"  进度: {percent:.1f}%")
                            self.last_progress = percent
                    else:
                        # 过滤不重要的输出
                        if any(keyword in line for keyword in ['版本:', 'Processing', 'Image Version']):
                            self.print_info(f"  {line}")
                
                process.wait()
                exit_code = process.returncode
            
            if exit_code != 0:
                self.print_error(f"==== [失败] {pkg_desc} 安装失败 ====")
            else:
                self.print_success(f"==== [成功] {pkg_desc} 安装成功 ====")
        else:
            self.print_warning(f"[跳过] {pkg_desc} - 文件不存在")
            self.print_warning(f"        包名: {pkg_name}.cab")
            self.print_cyan("=" * 42)
    
    def install_language_package(self, pkg_name, pkg_desc):
        """安装单个语言包"""
        pkg_file = self.cab_path / "zh-cn" / f"{pkg_name}.cab"
        
        if not self.silent_mode:
            print()
        self.print_cyan("=" * 42)
        
        if pkg_file.exists():
            self.print_info(f"[安装中] {pkg_desc}")
            self.print_cyan("=" * 42)
            
            cmd = f'dism /image:"{self.mount_dir}" /add-package /packagepath:"{pkg_file}"'
            
            if not self.silent_mode:
                # 命令行模式：实时显示
                print()
                self.print_info(f"[命令] {cmd}")
                print()
                
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    bufsize=1
                )
                
                last_was_progress = False
                for line in process.stdout:
                    line = line.rstrip()
                    if '[' in line and '%' in line and '=' in line:
                        print(f"\r{line}", end='', flush=True)
                        last_was_progress = True
                        continue
                    if line.strip():
                        if last_was_progress:
                            print()
                            last_was_progress = False
                        print(line)
                
                if last_was_progress:
                    print()
                
                process.wait()
                exit_code = process.returncode
                print()
            else:
                # 静默模式：捕获输出到日志
                self.print_info(f"[命令] 正在执行 DISM...")
                
                # Windows: 隐藏窗口
                startupinfo = None
                if sys.platform == 'win32':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    bufsize=1,
                    startupinfo=startupinfo
                )
                
                for line in process.stdout:
                    line = line.rstrip()
                    if not line.strip():
                        continue
                    
                    # 进度条
                    if '[' in line and '%' in line and '=' in line:
                        import re
                        match = re.search(r'(\d+\.?\d*)%', line)
                        if match:
                            percent = float(match.group(1))
                            # 每次都输出进度，GUI会在同一行更新
                            self.print_info(f"  进度: {percent:.1f}%")
                            self.last_progress = percent
                    else:
                        # 只显示重要信息
                        if any(keyword in line for keyword in ['版本:', 'Processing', 'Image Version', '操作成功', '错误']):
                            self.print_info(f"  {line}")
                
                process.wait()
                exit_code = process.returncode
            
            if exit_code != 0:
                self.print_error(f"==== [失败] {pkg_desc} 安装失败 ====")
            else:
                self.print_success(f"==== [成功] {pkg_desc} 安装成功 ====")
        else:
            self.print_warning(f"[跳过] {pkg_desc} - 文件不存在")
            self.print_warning(f"        包名: {pkg_name}.cab")
            self.print_cyan("=" * 42)
    
    def install_feature_packs(self):
        """安装功能包"""
        if not self.enable_feature_packs:
            self.print_warning("[跳过] 功能包安装模块")
            return True
        
        if not self.silent_mode:
            print()
        self.print_header("步骤 2: 安装 WinPE 功能包")
        self.print_info("[说明] 将安装 WinPE 可选功能组件")
        
        for pkg_name, pkg_desc in self.feature_packages:
            self.last_progress = -1  # 重置进度计数器
            self.install_package(pkg_name, pkg_desc)
        
        if not self.silent_mode:
            print()
        self.print_success("[总结] 功能包安装流程已完成")
        if not self.silent_mode:
            print()
        return True
    
    def install_language_packs(self):
        """安装中文语言包"""
        if not self.enable_language_packs:
            self.print_warning("[跳过] 语言包安装模块")
            return True
        
        if not self.silent_mode:
            print()
        self.print_header("步骤 3: 安装中文语言包")
        self.print_info("[说明] 为已安装的功能包添加中文界面支持")
        
        for pkg_name, pkg_desc in self.language_packages:
            self.last_progress = -1  # 重置进度计数器
            self.install_language_package(pkg_name, pkg_desc)
        
        if not self.silent_mode:
            print()
        self.print_success("[总结] 中文语言包安装流程已完成")
        if not self.silent_mode:
            print()
        return True
    
    def install_fonts_and_lp(self):
        """安装字体支持"""
        if not self.enable_fonts_lp:
            self.print_warning("[跳过] 字体支持安装模块")
            return True
        
        print()
        self.print_header("步骤 4: 安装中文字体支持")
        self.print_info("[说明] 安装中文字体和核心语言包")
        print()
        
        # 安装字体支持包
        font_pkg = self.cab_path / "WinPE-FontSupport-ZH-CN.cab"
        if font_pkg.exists():
            self.print_info("[安装] 正在安装: 中文字体支持包")
            cmd = f'dism /image:"{self.mount_dir}" /add-package /packagepath:"{font_pkg}"'
            subprocess.run(cmd, shell=True)
        else:
            self.print_warning("[跳过] 中文字体支持包 - 文件不存在")
        
        print()
        
        # 安装核心语言包
        lp_pkg = self.cab_path / "zh-cn" / "lp.cab"
        if lp_pkg.exists():
            self.print_info("[安装] 正在安装: 核心语言包")
            cmd = f'dism /image:"{self.mount_dir}" /add-package /packagepath:"{lp_pkg}"'
            subprocess.run(cmd, shell=True)
        else:
            self.print_warning("[跳过] 核心语言包 - 文件不存在")
        
        print()
        self.print_success("[完成] 字体支持安装流程已完成")
        print()
        return True
    
    def set_regional_settings(self):
        """配置区域设置"""
        if not self.enable_regional_settings:
            self.print_warning("[跳过] 区域设置配置模块")
            return True
        
        print()
        self.print_header("步骤 5: 配置区域和语言设置")
        self.print_info("[说明] 配置 WinPE 为中文区域设置")
        print()
        
        # 从 config.py 读取区域设置
        for setting, desc in config.REGIONAL_SETTINGS:
            self.print_info(f"[配置] {desc}")
            cmd = f'dism /image:"{self.mount_dir}" /{setting}'
            subprocess.run(cmd, shell=True, capture_output=True)
            print()
        
        self.print_success("[完成] 区域和语言设置配置成功")
        print()
        return True
    
    def install_drivers(self):
        """批量安装驱动程序 - 按子目录分步执行"""
        if not self.enable_drivers:
            self.print_warning("[跳过] 驱动程序安装模块")
            return True
        
        if not self.silent_mode:
            print()
        self.print_header("步骤 6: 批量安装硬件驱动程序")
        self.print_info("[说明] 扫描并安装驱动程序目录中的所有驱动")
        self.print_info(f"[路径] 驱动程序目录: {self.driver_path}")
        
        if not self.driver_path.exists():
            self.print_warning("[警告] 驱动程序目录不存在，跳过驱动安装")
            self.print_warning(f"[警告] 请确认路径: {self.driver_path}")
            if not self.silent_mode:
                print()
            return True
        
        # 扫描子目录
        subdirs = [d for d in self.driver_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if not subdirs:
            # 如果没有子目录，直接递归安装整个目录
            self.print_info("[扫描] 未发现子目录，将递归安装整个目录...")
            cmd = f'dism /image:"{self.mount_dir}" /add-driver /driver:"{self.driver_path}" /recurse'
            exit_code = self.run_command(cmd)
            
            if exit_code != 0:
                self.print_error("[失败] 驱动程序安装过程中出现错误")
            else:
                self.print_success("[完成] 驱动程序批量安装成功")
        else:
            # 按子目录分步安装
            total_dirs = len(subdirs)
            self.print_info(f"[扫描] 发现 {total_dirs} 个驱动子目录")
            
            for i, subdir in enumerate(subdirs, 1):
                percent = int((i / total_dirs) * 100)
                
                if not self.silent_mode:
                    print()
                self.print_cyan("=" * 50)
                self.print_info(f"[{i}/{total_dirs}] 正在安装: {subdir.name}")
                self.print_info(f"[进度] 总体进度: {i}/{total_dirs} ({percent}%)")
                self.print_cyan("=" * 50)
                
                # 检查是否应该停止
                if hasattr(self, 'gui_instance') and self.gui_instance and self.gui_instance.stop_requested:
                    self.print_warning("[停止] 检测到停止请求")
                    break
                
                # 安装此子目录的驱动
                cmd = f'dism /image:"{self.mount_dir}" /add-driver /driver:"{subdir}" /recurse'
                
                if self.silent_mode:
                    # 静默模式：捕获输出
                    self.print_info(f"[命令] 正在执行 DISM...")
                    
                    startupinfo = None
                    if sys.platform == 'win32':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    process = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        bufsize=1,
                        startupinfo=startupinfo
                    )
                    
                    driver_count = 0
                    for line in process.stdout:
                        line = line.rstrip()
                        if not line.strip():
                            continue
                        
                        # 统计安装的驱动数量
                        if '正在安装' in line or 'Installing' in line:
                            driver_count += 1
                            self.print_info(f"  正在安装驱动 #{driver_count}")
                        elif '操作成功' in line or 'successfully' in line:
                            self.print_info(f"  {line}")
                        elif '找到' in line and '驱动' in line:
                            self.print_info(f"  {line}")
                    
                    process.wait()
                    exit_code = process.returncode
                    
                    if exit_code == 0:
                        self.print_success(f"[✅ 完成] {subdir.name} - 安装成功")
                    else:
                        self.print_error(f"[❌ 失败] {subdir.name} - 安装失败")
                else:
                    # 命令行模式
                    exit_code = self.run_command(cmd)
                    if exit_code == 0:
                        self.print_success(f"[完成] {subdir.name} 安装成功")
                    else:
                        self.print_error(f"[失败] {subdir.name} 安装失败")
            
            self.print_success(f"[总计] 已处理 {total_dirs} 个驱动目录")
        
        if not self.silent_mode:
            print()
        return True
    
    def copy_external_apps(self):
        """复制附加程序"""
        if not self.enable_external_apps:
            self.print_warning("[跳过] 附加程序复制模块")
            return True
        
        print()
        self.print_header("步骤 7: 复制附加应用程序")
        self.print_info("[说明] 将第三方工具复制到 WinPE 系统中")
        self.print_info(f"[路径] 附加程序目录: {self.external_apps}")
        print()
        
        if not self.external_apps.exists():
            self.print_warning("[警告] 附加程序目录不存在，跳过程序复制")
            print()
            return True
        
        system32 = self.mount_dir / "Windows" / "System32"
        
        # 示例：复制 DiskGenius
        diskgenius = self.external_apps / "DiskGenius.exe"
        if diskgenius.exists():
            self.print_info("[复制] 正在复制: DiskGenius.exe")
            import shutil
            try:
                shutil.copy2(diskgenius, system32)
                self.print_success("[成功] DiskGenius.exe 复制成功")
            except Exception as e:
                self.print_error(f"[失败] DiskGenius.exe 复制失败: {e}")
        else:
            self.print_warning("[跳过] DiskGenius.exe 不存在")
        
        print()
        self.print_success("[完成] 附加程序复制流程已完成")
        print()
        return True
    
    def create_directories(self):
        """创建自定义目录结构"""
        if not self.enable_create_dirs:
            self.print_warning("[跳过] 目录创建模块")
            return True
        
        print()
        self.print_header("步骤 8: 创建自定义目录结构")
        self.print_info("[说明] 在 WinPE 中创建常用工作目录")
        print()
        
        # 从 config.py 读取目录列表
        for dir_name in config.CUSTOM_DIRECTORIES:
            dir_path = self.mount_dir / dir_name
            if not dir_path.exists():
                self.print_info(f"[创建] 正在创建目录: {dir_name}")
                dir_path.mkdir(parents=True)
            else:
                self.print_warning(f"[存在] 目录已存在: {dir_name}")
        
        print()
        self.print_success("[完成] 自定义目录结构创建成功")
        print()
        return True
    
    def make_iso(self):
        """卸载 WIM 并生成 ISO"""
        if not self.enable_make_iso:
            self.print_warning("[跳过] ISO 生成模块")
            return True
        
        print()
        self.print_header("步骤 9: 卸载 WIM 并生成 ISO 文件")
        self.print_info("[说明] 保存所有更改并生成可启动 ISO 文件")
        print()
        
        # 卸载 WIM
        self.print_cyan("[阶段 1/2] 卸载 WIM 映像并提交更改...")
        cmd = f'dism /unmount-wim /mountdir:"{self.mount_dir}" /commit'
        exit_code = self.run_command(cmd)
        
        if exit_code != 0:
            self.print_error("[失败] WIM 映像卸载失败")
            return False
        
        self.print_success("[成功] WIM 映像卸载成功")
        print()
        
        # 生成 ISO
        self.print_cyan("[阶段 2/2] 生成可启动 ISO 文件...")
        cmd = f'MakeWinPEMedia /iso "{self.winpe_dir}" "{self.final_iso}"'
        exit_code = self.run_command(cmd)
        
        if exit_code != 0:
            self.print_error("[失败] ISO 文件生成失败")
        else:
            self.print_success("[成功] ISO 文件生成成功")
        
        print()
        return True
    
    def show_summary(self):
        """显示执行摘要"""
        self.print_header("执行摘要和结果统计")
        print()
        
        if self.final_iso.exists():
            size_mb = self.final_iso.stat().st_size // (1024 * 1024)
            self.print_success("[成功] ISO 文件已成功生成")
            self.print_info(f"[信息] 文件路径: {self.final_iso}")
            self.print_info(f"[信息] 文件大小: {size_mb} MB")
            print()
            self.print_cyan("[后续] 您可以使用此 ISO 文件:")
            self.print_info("       1. 刻录到 CD/DVD 光盘")
            self.print_info("       2. 制作 USB 启动盘")
            self.print_info("       3. 在虚拟机中测试")
        else:
            self.print_warning("[注意] ISO 文件未生成")
            self.print_warning("[注意] 可能是因为 enable_make_iso 设置为 False")
        
        print()
    
    def run(self):
        """主流程"""
        try:
            # 显示配置
            self.show_config()
            
            # 检查 ADK
            if not self.check_adk_path():
                return 1
            
            # 创建 WinPE 环境
            if not self.create_winpe_environment():
                return 1
            
            # 挂载 WIM
            if not self.check_and_mount_wim():
                return 1
            
            print()
            self.print_cyan("=" * 40)
            self.print_cyan("    开始执行 WinPE 定制化流程...     ")
            self.print_cyan("=" * 40)
            print()
            
            # 执行定制流程
            if self.enable_feature_packs:
                self.print_info("[模块] 执行模块: 安装功能包")
                self.install_feature_packs()
            
            if self.enable_language_packs:
                self.print_info("[模块] 执行模块: 安装中文语言包")
                self.install_language_packs()
            
            if self.enable_fonts_lp:
                self.print_info("[模块] 执行模块: 安装字体支持")
                self.install_fonts_and_lp()
            
            if self.enable_regional_settings:
                self.print_info("[模块] 执行模块: 配置区域设置")
                self.set_regional_settings()
            
            if self.enable_drivers:
                self.print_info("[模块] 执行模块: 批量安装驱动程序")
                self.install_drivers()
            
            if self.enable_external_apps:
                self.print_info("[模块] 执行模块: 复制附加程序")
                self.copy_external_apps()
            
            if self.enable_create_dirs:
                self.print_info("[模块] 执行模块: 创建自定义目录结构")
                self.create_directories()
            
            if self.enable_make_iso:
                self.print_info("[模块] 执行模块: 卸载 WIM 并生成 ISO")
                self.make_iso()
            
            # 显示摘要
            print()
            self.print_cyan("=" * 40)
            self.print_cyan("    WinPE 定制流程已全部完成       ")
            self.print_cyan("=" * 40)
            print()
            self.show_summary()
            
            print()
            self.print_info(f"[完成] 脚本执行结束时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            return 0
            
        except KeyboardInterrupt:
            print()
            self.print_warning("\n[中断] 用户中断执行")
            return 1
        except Exception as e:
            print()
            self.print_error(f"\n[异常] 发生错误: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """主函数"""
    # 解析命令行参数
    winpe_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    # 创建定制器实例
    customizer = WinPECustomizer(winpe_dir)
    
    # 运行
    exit_code = customizer.run()
    
    # 暂停等待用户
    input("\n按 Enter 键退出...")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

