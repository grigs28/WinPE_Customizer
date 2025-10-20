#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WinPE Customizer 配置文件
所有可配置参数都在这里
"""

from pathlib import Path

# ============================================================================
# 路径配置
# ============================================================================

# WinPE 工作目录（默认值，可通过命令行参数覆盖）
WINPE_DIR = "D:/WinPE_amd64"

# Windows ADK 可选组件路径
CAB_PATH = "C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit/Windows Preinstallation Environment/amd64/WinPE_OCs"

# 附加程序目录（相对于脚本目录）
EXTERNAL_APPS_DIR = "外置程序"

# 驱动程序目录（相对于脚本目录）
DRIVER_DIR = "drive"

# 输出 ISO 文件名
OUTPUT_ISO_NAME = "MyCustomWinPE.iso"

# ============================================================================
# 模块开关（True=启用，False=禁用）
# ============================================================================

ENABLE_COPYPE_SETUP = True       # 是否自动创建 WinPE 工作目录
ENABLE_AUTO_MOUNT = True         # 是否自动挂载 boot.wim
ENABLE_FEATURE_PACKS = True      # 是否安装功能包
ENABLE_LANGUAGE_PACKS = True     # 是否安装中文语言包
ENABLE_FONTS_LP = True           # 是否安装中文字体支持
ENABLE_REGIONAL_SETTINGS = True  # 是否配置区域设置
ENABLE_DRIVERS = True            # 是否批量安装驱动程序
ENABLE_EXTERNAL_APPS = True      # 是否复制附加程序
ENABLE_CREATE_DIRS = False        # 是否创建自定义目录结构
ENABLE_MAKE_ISO = True           # 是否卸载 WIM 并生成 ISO

# ============================================================================
# 功能包列表
# ============================================================================

FEATURE_PACKAGES = [
    # 基础组件
    ("WinPE-WMI", "WMI (Windows 管理规范)"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-Scripting", "脚本宿主环境"),
    ("WinPE-HTA", "HTML 应用程序"),
    
    # PowerShell 组件
    ("WinPE-PowerShell", "PowerShell"),
    ("WinPE-DismCmdlets", "DISM PowerShell 模块"),
    ("WinPE-SecureBootCmdlets", "安全启动 PowerShell 模块"),
    
    # 存储和安全组件
    ("WinPE-StorageWMI", "存储管理 WMI"),
    ("WinPE-EnhancedStorage", "增强存储支持"),
    ("WinPE-SecureStartup", "BitLocker 支持"),
    
    # 网络和数据库组件
    ("WinPE-PPPoE", "PPPoE 拨号上网"),
    ("WinPE-dot3svc", "有线 802.1X 认证"),
    ("WinPE-FMAPI", "文件管理 API"),
    ("WinPE-MDAC", "数据库访问组件"),
    
    # 安装程序支持组件（服务器 + PC）
    ("WinPE-Setup", "Windows 安装程序核心"),
    ("WinPE-Setup-Client", "客户端安装程序支持"),
    ("WinPE-Setup-Server", "服务器安装程序支持"),
    
    # 网络和恢复组件
    ("WinPE-RNDIS", "RNDIS 网络支持 (USB 网络)"),
    ("WinPE-WDS-Tools", "Windows 部署服务工具"),
    ("WinPE-LegacySetup", "旧版安装程序支持"),
    ("WinPE-SRT", "系统恢复工具 (SRT)"),
    ("WinPE-Rejuv", "Windows 恢复环境 (WinRE)"),
]

# ============================================================================
# 中文语言包列表
# ============================================================================

LANGUAGE_PACKAGES = [
    ("WinPE-WMI_zh-cn", "WMI 中文语言包"),
    ("WinPE-NetFx_zh-cn", ".NET Framework 中文语言包"),
    ("WinPE-Scripting_zh-cn", "脚本宿主 中文语言包"),
    ("WinPE-HTA_zh-cn", "HTML 应用程序 中文语言包"),
    ("WinPE-PowerShell_zh-cn", "PowerShell 中文语言包"),
    ("WinPE-DismCmdlets_zh-cn", "DISM PowerShell 中文语言包"),
    ("WinPE-SecureBootCmdlets_zh-cn", "安全启动 中文语言包"),
    ("WinPE-StorageWMI_zh-cn", "存储管理 中文语言包"),
    ("WinPE-EnhancedStorage_zh-cn", "增强存储 中文语言包"),
    ("WinPE-SecureStartup_zh-cn", "BitLocker 中文语言包"),
    ("WinPE-PPPoE_zh-cn", "PPPoE 中文语言包"),
    ("WinPE-dot3svc_zh-cn", "802.1X 中文语言包"),
    ("WinPE-MDAC_zh-cn", "数据库组件 中文语言包"),
]

# ============================================================================
# 字体和核心语言包
# ============================================================================

FONT_PACKAGES = [
    ("WinPE-FontSupport-ZH-CN", "中文字体支持包"),
    ("zh-cn/lp", "核心语言包"),
]

# ============================================================================
# 区域设置配置
# ============================================================================

REGIONAL_SETTINGS = [
    ("set-uilang:zh-cn", "设置用户界面语言为简体中文"),
    ("set-syslocale:zh-cn", "设置系统区域设置为中国"),
    ("set-userlocale:zh-cn", "设置用户区域设置为中国"),
    ("set-inputlocale:0804:00000804", "设置输入法为简体中文"),
    ('set-timezone:"China Standard Time"', "设置时区为中国标准时间"),
    ("set-SKUIntlDefaults:zh-cn", "设置国际化默认值为中国"),
]

# ============================================================================
# 自定义目录结构
# ============================================================================

CUSTOM_DIRECTORIES = [
    "Tools",
    "Temp/Logs",
    "Data/Backup",
]

# ============================================================================
# 附加程序列表（要复制到 WinPE 的程序）
# ============================================================================

EXTERNAL_APPS = [
    # (源文件相对路径, 目标路径, 描述)
    ("DiskGenius.exe", "Windows/System32", "DiskGenius 磁盘工具"),
    # 可以添加更多程序
    # ("备份还原/GhostExp.exe", "Tools", "Ghost 备份工具"),
]

# ============================================================================
# 高级选项
# ============================================================================

# DISM 命令超时时间（秒）
DISM_TIMEOUT = 600

# 是否显示详细的 DISM 输出
VERBOSE_DISM_OUTPUT = False

# 是否在出错时自动重试
AUTO_RETRY_ON_ERROR = False

# 最大重试次数
MAX_RETRY_COUNT = 3

# ============================================================================
# 颜色配置（使用 colorama）
# ============================================================================

USE_COLORS = True  # 是否使用彩色输出

# ============================================================================
# 日志配置
# ============================================================================

ENABLE_LOGGING = True              # 是否启用日志
LOG_FILE = "WinPE_Customizer.log"  # 日志文件名
LOG_LEVEL = "INFO"                 # 日志级别：DEBUG, INFO, WARNING, ERROR

