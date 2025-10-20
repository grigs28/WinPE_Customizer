#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WinPE Customizer 配置示例文件
复制到根目录并重命名为 config.py 使用
"""

from pathlib import Path

# ============================================================================
# 示例 1: 最小化配置 - 仅创建基础 WinPE
# ============================================================================
"""
WINPE_DIR = "D:/WinPE_Basic"
ENABLE_COPYPE_SETUP = True
ENABLE_AUTO_MOUNT = True
ENABLE_FEATURE_PACKS = False
ENABLE_LANGUAGE_PACKS = False
ENABLE_FONTS_LP = False
ENABLE_REGIONAL_SETTINGS = False
ENABLE_DRIVERS = False
ENABLE_EXTERNAL_APPS = False
ENABLE_CREATE_DIRS = False
ENABLE_MAKE_ISO = True
"""

# ============================================================================
# 示例 2: 标准中文 WinPE
# ============================================================================
"""
WINPE_DIR = "D:/WinPE_Chinese"
ENABLE_COPYPE_SETUP = True
ENABLE_AUTO_MOUNT = True
ENABLE_FEATURE_PACKS = True
ENABLE_LANGUAGE_PACKS = True
ENABLE_FONTS_LP = True
ENABLE_REGIONAL_SETTINGS = True
ENABLE_DRIVERS = False
ENABLE_EXTERNAL_APPS = False
ENABLE_CREATE_DIRS = False
ENABLE_MAKE_ISO = True

# 只安装必需功能包
FEATURE_PACKAGES = [
    ("WinPE-WMI", "WMI"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-Scripting", "脚本宿主"),
    ("WinPE-PowerShell", "PowerShell"),
]
"""

# ============================================================================
# 示例 3: 完整服务器维护 WinPE（含驱动）
# ============================================================================
"""
WINPE_DIR = "D:/WinPE_Server"
CAB_PATH = "C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit/Windows Preinstallation Environment/amd64/WinPE_OCs"
DRIVER_DIR = "drive"
EXTERNAL_APPS_DIR = "外置程序"
OUTPUT_ISO_NAME = "ServerMaintenancePE.iso"

# 启用所有模块
ENABLE_COPYPE_SETUP = True
ENABLE_AUTO_MOUNT = True
ENABLE_FEATURE_PACKS = True
ENABLE_LANGUAGE_PACKS = True
ENABLE_FONTS_LP = True
ENABLE_REGIONAL_SETTINGS = True
ENABLE_DRIVERS = True          # 安装驱动
ENABLE_EXTERNAL_APPS = True    # 添加工具
ENABLE_CREATE_DIRS = True      # 创建工作目录
ENABLE_MAKE_ISO = True

# 服务器常用功能包
FEATURE_PACKAGES = [
    ("WinPE-WMI", "WMI"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-Scripting", "脚本宿主"),
    ("WinPE-PowerShell", "PowerShell"),
    ("WinPE-DismCmdlets", "DISM PowerShell"),
    ("WinPE-StorageWMI", "存储管理"),
    ("WinPE-SecureStartup", "BitLocker"),
    ("WinPE-WDS-Tools", "WDS 工具"),
]

# 服务器工具
EXTERNAL_APPS = [
    ("磁盘光盘/DiskGenius.exe", "Windows/System32", "DiskGenius"),
    ("备份还原/GhostExp.exe", "Tools", "Ghost Express"),
]

# 工作目录
CUSTOM_DIRECTORIES = [
    "Tools",
    "Logs",
    "Backup",
    "Temp",
]
"""

# ============================================================================
# 示例 4: 网络部署 WinPE
# ============================================================================
"""
WINPE_DIR = "D:/WinPE_Network"
OUTPUT_ISO_NAME = "NetworkDeployment.iso"

ENABLE_COPYPE_SETUP = True
ENABLE_AUTO_MOUNT = True
ENABLE_FEATURE_PACKS = True
ENABLE_LANGUAGE_PACKS = True
ENABLE_FONTS_LP = True
ENABLE_REGIONAL_SETTINGS = True
ENABLE_DRIVERS = True          # 重要：安装网卡驱动
ENABLE_EXTERNAL_APPS = False
ENABLE_CREATE_DIRS = False
ENABLE_MAKE_ISO = True

# 网络相关功能包
FEATURE_PACKAGES = [
    ("WinPE-WMI", "WMI"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-Scripting", "脚本宿主"),
    ("WinPE-PowerShell", "PowerShell"),
    ("WinPE-PPPoE", "PPPoE 拨号"),
    ("WinPE-dot3svc", "有线认证"),
    ("WinPE-RNDIS", "USB 网络"),
    ("WinPE-WDS-Tools", "部署服务工具"),
]

# 只安装网卡驱动
DRIVER_DIR = "drive/Network"
"""

# ============================================================================
# 示例 5: 数据恢复 WinPE
# ============================================================================
"""
WINPE_DIR = "D:/WinPE_Recovery"
OUTPUT_ISO_NAME = "DataRecoveryPE.iso"

ENABLE_COPYPE_SETUP = True
ENABLE_AUTO_MOUNT = True
ENABLE_FEATURE_PACKS = True
ENABLE_LANGUAGE_PACKS = True
ENABLE_FONTS_LP = True
ENABLE_REGIONAL_SETTINGS = True
ENABLE_DRIVERS = True          # 识别更多硬件
ENABLE_EXTERNAL_APPS = True    # 添加恢复工具
ENABLE_CREATE_DIRS = True
ENABLE_MAKE_ISO = True

# 基础功能包
FEATURE_PACKAGES = [
    ("WinPE-WMI", "WMI"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-Scripting", "脚本宿主"),
    ("WinPE-PowerShell", "PowerShell"),
    ("WinPE-StorageWMI", "存储管理"),
    ("WinPE-EnhancedStorage", "增强存储"),
]

# 数据恢复工具
EXTERNAL_APPS = [
    ("磁盘光盘/DiskGenius.exe", "Windows/System32", "DiskGenius"),
    ("文件工具/Recuva.exe", "Tools", "Recuva 恢复"),
    ("文件工具/易我数据恢复V2.1.0.exe", "Tools", "易我恢复"),
]

# 工作目录
CUSTOM_DIRECTORIES = [
    "Recovery",
    "Backup",
    "Temp",
]
"""

# ============================================================================
# 高级选项说明
# ============================================================================
"""
# DISM 命令超时（秒）
DISM_TIMEOUT = 600

# 是否显示详细输出
VERBOSE_DISM_OUTPUT = False

# 出错时自动重试
AUTO_RETRY_ON_ERROR = False
MAX_RETRY_COUNT = 3

# 颜色输出
USE_COLORS = True

# 日志配置
ENABLE_LOGGING = True
LOG_FILE = "WinPE_Customizer.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
"""

# ============================================================================
# 使用说明
# ============================================================================
"""
1. 复制本文件到项目根目录
2. 重命名为 config.py
3. 取消注释所需的配置示例
4. 根据实际情况修改路径和选项
5. 运行 WinPE_Customizer_GUI.py 或 WinPE_Customizer.py

注意：
- 路径中使用正斜杠 / 或双反斜杠 \\
- 确保 Windows ADK 路径正确
- 驱动和外置程序目录需要实际存在
"""

