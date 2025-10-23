#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WinPE 工具包管理器
管理集成到 WinPE 的系统工具（如 Dism++、PowerShell等）
"""

import os
import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
import urllib.request
import zipfile
import threading


class WinPEToolsManager:
    """WinPE 工具包管理器"""
    
    # 工具分类
    TOOL_CATEGORIES = {
        'system': '系统管理',
        'disk': '磁盘工具',
        'compress': '压缩工具',
        'editor': '文本编辑',
        'browser': '浏览器',
        'hardware': '硬件检测',
        'network': '网络工具',
        'recovery': '数据恢复',
        'file': '文件管理',
        'bootable': '启动盘制作',
        'viewer': '文档查看',
    }
    
    # 常用WinPE工具列表
    COMMON_TOOLS = [
        {
            'name': 'Dism++',
            'desc': '强大的 Windows 映像管理工具',
            'url': 'https://github.com/Chuyu-Team/Dism-Multi-language',
            'download_url': 'https://github.com/Chuyu-Team/Dism-Multi-language/releases/download/v10.1.1002.2/Dism++10.1.1002.1B.zip',
            'exe': 'Dism++x64.exe',
            'shortcut_name': 'Dism++',
            'recommended': True,
            'context_menu': False,
            'category': 'system'
        },
        {
            'name': 'DiskGenius',
            'desc': '磁盘分区和数据恢复工具',
            'url': 'https://www.diskgenius.cn/',
            'exe': 'DiskGenius.exe',
            'shortcut_name': 'DiskGenius',
            'recommended': True,
            'context_menu': False,
            'category': 'disk'
        },
        {
            'name': 'PowerShell 7',
            'desc': '跨平台的 PowerShell 版本',
            'url': 'https://github.com/PowerShell/PowerShell',
            'exe': 'pwsh.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'system'
        },
        {
            'name': 'WinNTSetup',
            'desc': 'Windows 系统安装工具',
            'url': 'https://msfn.org/board/topic/149612-winntsetup/',
            'exe': 'WinNTSetup.exe',
            'recommended': True,
            'context_menu': False,
            'category': 'system'
        },
        {
            'name': 'CPU-Z',
            'desc': 'CPU 信息检测工具',
            'url': 'https://www.cpuid.com/softwares/cpu-z.html',
            'exe': 'cpuz.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'CrystalDiskInfo',
            'desc': '硬盘健康监测工具',
            'url': 'https://crystalmark.info/',
            'exe': 'DiskInfo64.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'Notepad++',
            'desc': '文本编辑器（支持右键菜单）',
            'url': 'https://notepad-plus-plus.org/',
            'exe': 'notepad++.exe',
            'recommended': True,
            'context_menu': True,
            'category': 'editor'
        },
        {
            'name': '7-Zip',
            'desc': '压缩解压工具（支持右键菜单）',
            'url': 'https://www.7-zip.org/',
            'download_url': 'https://www.7-zip.org/a/7z2301-x64.exe',
            'exe': '7zFM.exe',
            'shortcut_name': '7-Zip',
            'recommended': True,
            'context_menu': True,
            'category': 'compress'
        },
        {
            'name': 'SumatraPDF',
            'desc': 'PDF阅读器（支持右键菜单，轻量开源）',
            'url': 'https://www.sumatrapdfreader.org/',
            'download_url': 'https://www.sumatrapdfreader.org/files/SumatraPDF-3.5.2-64.zip',
            'exe': 'SumatraPDF.exe',
            'recommended': True,
            'context_menu': True,
            'category': 'viewer'
        },
        {
            'name': 'GreenBrowser',
            'desc': '绿色便携浏览器',
            'url': 'http://www.morequick.com/',
            'exe': 'GreenBrowser.exe',
            'recommended': True,
            'context_menu': False,
            'category': 'browser'
        },
        {
            'name': 'Firefox Portable',
            'desc': 'Firefox 便携版浏览器',
            'url': 'https://portableapps.com/apps/internet/firefox_portable',
            'exe': 'FirefoxPortable.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'browser'
        },
        {
            'name': 'VSCode Portable',
            'desc': 'Visual Studio Code 便携版',
            'url': 'https://code.visualstudio.com/docs/editor/portable',
            'exe': 'Code.exe',
            'shortcut_name': 'VSCode',
            'recommended': False,
            'context_menu': True,
            'category': 'editor'
        },
        {
            'name': 'HxD',
            'desc': '十六进制编辑器（二进制文件编辑）',
            'url': 'https://mh-nexus.de/en/hxd/',
            'download_url': 'https://mh-nexus.de/en/hxd/download/HxDSetup.zip',
            'exe': 'HxD.exe',
            'shortcut_name': 'HxD',
            'recommended': False,
            'context_menu': True,
            'category': 'editor'
        },
        {
            'name': 'HWiNFO',
            'desc': '硬件信息检测工具',
            'url': 'https://www.hwinfo.com/',
            'exe': 'HWiNFO64.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'MemTest86',
            'desc': '内存测试工具',
            'url': 'https://www.memtest86.com/',
            'exe': 'MemTest86.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'Rufus',
            'desc': 'USB启动盘制作工具',
            'url': 'https://rufus.ie/',
            'exe': 'rufus.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'bootable'
        },
        {
            'name': 'HDTune',
            'desc': '硬盘检测工具',
            'url': 'https://www.hdtune.com/',
            'exe': 'HDTune.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'TreeSize Free',
            'desc': '磁盘空间分析工具',
            'url': 'https://www.jam-software.com/treesize_free',
            'exe': 'TreeSizeFree.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'file'
        },
        {
            'name': 'PuTTY',
            'desc': 'SSH/Telnet 客户端',
            'url': 'https://www.putty.org/',
            'exe': 'putty.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'network'
        },
        {
            'name': 'WinSCP',
            'desc': 'SFTP/FTP 客户端',
            'url': 'https://winscp.net/',
            'exe': 'WinSCP.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'network'
        },
        {
            'name': 'Recuva',
            'desc': '文件恢复工具',
            'url': 'https://www.ccleaner.com/recuva',
            'exe': 'Recuva64.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'recovery'
        },
        {
            'name': 'FastCopy',
            'desc': '快速文件复制工具',
            'url': 'https://fastcopy.jp/',
            'exe': 'FastCopy.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'file'
        },
        {
            'name': 'CPU-X Portable',
            'desc': 'CPU信息检测工具（开源，类似CPU-Z）',
            'url': 'https://github.com/TheTumultuousUnicornOfDarkness/CPU-X/releases',
            'exe': 'CPU-X_win64.exe',
            'recommended': True,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'Ventoy',
            'desc': '多启动U盘制作工具（支持直接引导ISO）',
            'url': 'https://www.ventoy.net/',
            'exe': 'Ventoy2Disk.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'bootable'
        },
        {
            'name': 'Speccy',
            'desc': '系统信息查看工具',
            'url': 'https://www.ccleaner.com/speccy',
            'exe': 'Speccy64.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'GPU-Z',
            'desc': '显卡信息检测工具',
            'url': 'https://www.techpowerup.com/gpuz/',
            'exe': 'GPU-Z.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'hardware'
        },
        {
            'name': 'AS SSD Benchmark',
            'desc': 'SSD 性能测试工具',
            'url': 'https://www.alex-is.de/',
            'exe': 'AS SSD Benchmark.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'disk'
        },
        {
            'name': 'Victoria HDD',
            'desc': '硬盘诊断和修复工具',
            'url': 'https://hdd.by/victoria/',
            'exe': 'victoria.exe',
            'recommended': False,
            'context_menu': False,
            'category': 'disk'
        },
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("WinPE 工具包管理器")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置图标
        self.set_icon()
        
        # 数据
        self.tools_data = []
        self.config_file = Path("winpe_tools_config.json")
        
        # 工具变量字典 - 存储每个工具的勾选和桌面选项
        self.tool_vars = {}  # {tool_name: BooleanVar()}
        self.desktop_vars = {}  # {tool_name: BooleanVar()}
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()
    
    def set_icon(self):
        """设置图标"""
        import random
        ico_dir = Path("../ico") if Path("../ico").exists() else Path("ico")
        if ico_dir.exists():
            image_files = list(ico_dir.glob("*.ico")) + list(ico_dir.glob("*.png"))
            if image_files:
                random_image = random.choice(image_files)
                if random_image.suffix.lower() == '.ico':
                    try:
                        self.root.iconbitmap(str(random_image))
                    except:
                        pass
    
    def create_widgets(self):
        """创建界面"""
        # 标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 标签页1: 推荐工具
        recommended_tab = ttk.Frame(notebook)
        notebook.add(recommended_tab, text="推荐工具")
        self.create_recommended_tab(recommended_tab)
        
        # 标签页2: 自定义工具
        custom_tab = ttk.Frame(notebook)
        notebook.add(custom_tab, text="自定义工具")
        self.create_custom_tab(custom_tab)
        
        # 标签页3: 配置代码
        config_tab = ttk.Frame(notebook)
        notebook.add(config_tab, text="配置代码")
        self.create_config_tab(config_tab)
    
    def create_recommended_tab(self, parent):
        """创建推荐工具标签页"""
        # 顶部说明
        header_frame = ttk.Frame(parent, padding="20")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="WinPE 常用工具推荐", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # 快速操作按钮
        quick_btn_frame = ttk.Frame(header_frame)
        quick_btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(quick_btn_frame, text="✅ 全选推荐", command=self.select_recommended_tools, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_btn_frame, text="✅ 全选", command=self.select_all_tools, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_btn_frame, text="❌ 全不选", command=self.deselect_all_tools, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Separator(quick_btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(quick_btn_frame, text="⬇️ 批量自动下载", command=self.batch_download, width=18, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_btn_frame, text="📂 打开外置程序目录", command=self.open_external_dir, width=20).pack(side=tk.LEFT, padx=5)
        
        # 主内容区域 - 左右分栏布局
        main_content = ttk.Frame(parent)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 左侧：工具列表
        left_frame = ttk.Frame(main_content)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 右侧：使用说明
        right_frame = ttk.Frame(main_content, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.pack_propagate(False)  # 固定宽度
        
        # 使用说明面板
        info_frame = ttk.LabelFrame(right_frame, text="📋 使用步骤", padding="10", relief=tk.GROOVE)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="1️⃣ 勾选要集成的工具", foreground="gray", font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="2️⃣ 点击蓝色下载链接", foreground="gray", font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="3️⃣ 下载到指定目录", foreground="orange", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="   外置程序/Tools/[工具名]/", foreground="gray", font=('Consolas', 8)).pack(anchor=tk.W, padx=10)
        ttk.Label(info_frame, text="4️⃣ 保存配置到config.py", foreground="gray", font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="5️⃣ 启用外置程序模块", foreground="gray", font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        
        # 提示信息
        tip_frame = ttk.LabelFrame(right_frame, text="💡 提示", padding="10", relief=tk.GROOVE)
        tip_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tip_frame, text="• 支持自动下载和手动下载", foreground="green", font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        ttk.Label(tip_frame, text="• 推荐工具已预选", foreground="blue", font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        ttk.Label(tip_frame, text="• 可添加到桌面快捷方式", foreground="purple", font=('Arial', 9)).pack(anchor=tk.W, pady=2)
        
        # 滚动区域（只占左侧）
        scroll_container = ttk.Frame(left_frame)
        scroll_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_container, bg='white')
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 鼠标滚轮支持
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按分类组织工具
        self.tool_vars = {}
        self.desktop_vars = {}
        self.pe_context_vars = {}
        
        # 按分类分组
        tools_by_category = {}
        for tool in self.COMMON_TOOLS:
            category = tool.get('category', 'other')
            if category not in tools_by_category:
                tools_by_category[category] = []
            tools_by_category[category].append(tool)
        
        # 按分类显示
        for category_id, category_name in self.TOOL_CATEGORIES.items():
            if category_id not in tools_by_category:
                continue
            
            tools = tools_by_category[category_id]
            
            # 分类标题
            category_frame = ttk.LabelFrame(scrollable_frame, text=f"📂 {category_name}", 
                                          padding="10", relief=tk.GROOVE)
            category_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            # 分类下的工具
            for tool in tools:
                self._create_tool_item(category_frame, tool)
    
    def _create_tool_item(self, parent, tool):
        """创建单个工具项"""
        # 检查工具是否已下载
        is_downloaded = self._check_tool_downloaded(tool)
        
        # 工具框架，根据下载状态使用不同颜色
        tool_frame = ttk.Frame(parent, relief=tk.RIDGE, borderwidth=1, padding="8")
        tool_frame.pack(fill=tk.X, padx=5, pady=3)
        
        # 如果已下载，添加绿色边框效果
        if is_downloaded:
            tool_frame.configure(relief=tk.SOLID, borderwidth=2)
        
        # 上半部分：工具名称和状态
        header_frame = ttk.Frame(tool_frame)
        header_frame.pack(fill=tk.X, anchor=tk.W)
        
        # 工具名称和下载状态
        name_frame = ttk.Frame(header_frame)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 状态标识
        if is_downloaded:
            status_icon = "✅"
            status_text = "已下载"
            status_color = "green"
        else:
            status_icon = "📦"
            status_text = "未下载"
            status_color = "orange"
        
        ttk.Label(name_frame, text=f"{status_icon} {tool['name']}", 
                 font=('Arial', 10, 'bold'), foreground=status_color).pack(side=tk.LEFT)
        ttk.Label(name_frame, text=f"[{status_text}]", 
                 foreground=status_color, font=('Arial', 8)).pack(side=tk.LEFT, padx=(5, 0))
        
        # 推荐标识
        if tool.get('recommended', False):
            ttk.Label(name_frame, text="⭐ 推荐", 
                     foreground="blue", font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
        
        # 右键菜单标识
        if tool.get('context_menu', False):
            ttk.Label(name_frame, text="🖱️ 右键菜单", 
                     foreground="purple", font=('Arial', 8, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
        
        # 选项框架
        option_frame = ttk.Frame(tool_frame)
        option_frame.pack(fill=tk.X, anchor=tk.W, pady=(5, 0))
        
        # 复选框
        var = tk.BooleanVar(value=tool['recommended'])
        self.tool_vars[tool['name']] = var
        
        cb = ttk.Checkbutton(option_frame, text="✓ 集成此工具", variable=var)
        cb.pack(side=tk.LEFT)
        
        # 绑定右键菜单
        cb.bind("<Button-3>", lambda e, t=tool: self.show_tool_context_menu(e, t))
        
        # 桌面选项
        desktop_var = tk.BooleanVar(value=tool['recommended'])
        self.desktop_vars[tool['name']] = desktop_var
        
        desktop_cb = ttk.Checkbutton(option_frame, text="📌 添加到桌面", variable=desktop_var)
        desktop_cb.pack(side=tk.LEFT, padx=(20, 0))
        
        # PE右键菜单选项（仅对支持右键菜单的工具显示）
        if tool.get('context_menu', False):
            pe_context_var = tk.BooleanVar(value=False)
            self.pe_context_vars[tool['name']] = pe_context_var
            
            pe_context_cb = ttk.Checkbutton(option_frame, text="🖱️ PE右键菜单", variable=pe_context_var)
            pe_context_cb.pack(side=tk.LEFT, padx=(20, 0))
        
        # 说明
        ttk.Label(tool_frame, text=f"📝 {tool['desc']}", 
                 foreground="gray", font=('Arial', 9)).pack(anchor=tk.W, pady=(5, 0))
        
        # 文件信息
        info_frame = ttk.Frame(tool_frame)
        info_frame.pack(fill=tk.X, anchor=tk.W, pady=(3, 0))
        
        ttk.Label(info_frame, text=f"📄 可执行文件: {tool['exe']}", 
                 foreground="blue", font=('Consolas', 8)).pack(side=tk.LEFT)
        
        # 保存位置
        save_path = f"外置程序/Tools/{tool['name']}/{tool['exe']}"
        ttk.Label(tool_frame, text=f"📁 保存位置: {save_path}", 
                 foreground="orange", font=('Consolas', 8)).pack(anchor=tk.W, pady=(2, 0))
        
        # 下载链接和按钮
        link_frame = ttk.Frame(tool_frame)
        link_frame.pack(anchor=tk.W, pady=(5, 0))
        
        if not is_downloaded:
            # 未下载时显示下载按钮
            ttk.Label(link_frame, text="⚠️ ", foreground="orange").pack(side=tk.LEFT)
            ttk.Label(link_frame, text="需要下载:", foreground="orange", 
                     font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        # 手动下载链接
        ttk.Label(link_frame, text="🌐 ").pack(side=tk.LEFT)
        link_label = ttk.Label(link_frame, text="访问官网下载", foreground="blue", cursor="hand2", 
                              font=('Arial', 9, 'underline'))
        link_label.pack(side=tk.LEFT)
        link_label.bind("<Button-1>", lambda e, url=tool['url']: self.open_url(url))
        
        ttk.Label(link_frame, text=f"  ({tool['url']})", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT)
    
    def _check_tool_downloaded(self, tool):
        """检查工具是否已下载"""
        # 检查外置程序目录
        external_dir = Path("../外置程序") if Path("../外置程序").exists() else Path("外置程序")
        tool_path = external_dir / "Tools" / tool['name'] / tool['exe']
        
        return tool_path.exists()
        
    
    def create_custom_tab(self, parent):
        """创建自定义工具标签页"""
        frame = ttk.Frame(parent, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="添加自定义工具", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        # 工具信息输入
        input_frame = ttk.LabelFrame(frame, text="工具信息", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="工具名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.custom_name = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.custom_name, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(input_frame, text="可执行文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.custom_exe = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.custom_exe, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Label(input_frame, text="说明:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.custom_desc = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.custom_desc, width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        ttk.Button(input_frame, text="➕ 添加到列表", command=self.add_custom_tool).grid(row=3, column=0, columnspan=2, pady=10)
        
        # 自定义工具列表
        list_frame = ttk.LabelFrame(frame, text="已添加的自定义工具", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.custom_listbox = tk.Listbox(list_frame, height=10)
        self.custom_listbox.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="🗑️ 删除选中", command=self.remove_custom_tool, width=16).pack(side=tk.LEFT, padx=5)
    
    def create_config_tab(self, parent):
        """创建配置代码标签页"""
        frame = ttk.Frame(parent, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="生成的工具配置", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 10))
        
        # 代码显示
        self.code_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Consolas', 9), height=25)
        self.code_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 说明
        tip_frame = ttk.Frame(frame)
        tip_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tip_frame, text="💡 提示：", font=('Arial', 9, 'bold'), foreground='green').pack(anchor=tk.W)
        ttk.Label(tip_frame, text="• 点击'生成配置'查看代码", foreground="gray").pack(anchor=tk.W, padx=20)
        ttk.Label(tip_frame, text="• 点击'复制代码'复制到剪贴板，手动粘贴到 core/config.py", foreground="gray").pack(anchor=tk.W, padx=20)
        ttk.Label(tip_frame, text="• 点击'直接保存到config.py'自动写入配置文件（推荐）", foreground="green", font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="📝 生成配置", command=self.generate_config, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 复制代码", command=self.copy_config, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 直接保存到config.py", command=self.save_to_config, width=22, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
    
    def open_url(self, url):
        """打开URL"""
        import webbrowser
        webbrowser.open(url)
    
    def select_recommended_tools(self):
        """全选推荐工具"""
        for tool in self.COMMON_TOOLS:
            if tool['recommended']:
                self.tool_vars[tool['name']].set(True)
    
    def select_all_tools(self):
        """全选所有工具"""
        for var in self.tool_vars.values():
            var.set(True)
    
    def deselect_all_tools(self):
        """全不选"""
        for var in self.tool_vars.values():
            var.set(False)
    
    def add_custom_tool(self):
        """添加自定义工具"""
        name = self.custom_name.get().strip()
        exe = self.custom_exe.get().strip()
        desc = self.custom_desc.get().strip()
        
        if not name or not exe:
            messagebox.showwarning("警告", "请填写工具名称和可执行文件")
            return
        
        self.custom_listbox.insert(tk.END, f"{name} - {exe} - {desc}")
        
        # 清空输入
        self.custom_name.set("")
        self.custom_exe.set("")
        self.custom_desc.set("")
    
    def remove_custom_tool(self):
        """删除自定义工具"""
        selection = self.custom_listbox.curselection()
        if selection:
            self.custom_listbox.delete(selection[0])
    
    def generate_config(self):
        """生成配置代码"""
        code_lines = [
            "# =" * 40,
            "# WinPE 工具包配置",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# =" * 40,
            "",
            "# 说明：",
            "# 1. 将工具程序放到 外置程序/Tools/ 目录",
            "# 2. 将下面的配置添加到 core/config.py 的 EXTERNAL_APPS 列表",
            "#3. 启用'复制外置程序'模块",
            "",
            "EXTERNAL_APPS = ["
        ]
        
        # 添加选中的推荐工具
        for tool in self.COMMON_TOOLS:
            if self.tool_vars[tool['name']].get():
                code_lines.append(f"    # {tool['name']} - {tool['desc']}")
                code_lines.append(f"    (")
                code_lines.append(f"        \"Tools/{tool['name']}/{tool['exe']}\",")
                code_lines.append(f"        \"Windows/System32\",")
                code_lines.append(f"        \"{tool['name']}\",")
                code_lines.append(f"    ),")
                code_lines.append("")
        
        # 添加自定义工具
        for i in range(self.custom_listbox.size()):
            item = self.custom_listbox.get(i)
            parts = item.split(' - ')
            if len(parts) >= 2:
                name = parts[0]
                exe = parts[1]
                code_lines.append(f"    # {name}")
                code_lines.append(f"    (")
                code_lines.append(f"        \"Tools/{name}/{exe}\",")
                code_lines.append(f"        \"Windows/System32\",")
                code_lines.append(f"        \"{name}\",")
                code_lines.append(f"    ),")
                code_lines.append("")
        
        code_lines.append("]")
        code_lines.append("")
        code_lines.append("# =" * 40)
        code_lines.append("# 工具下载说明")
        code_lines.append("# =" * 40)
        code_lines.append("")
        
        for tool in self.COMMON_TOOLS:
            if self.tool_vars[tool['name']].get():
                code_lines.append(f"# {tool['name']}: {tool['url']}")
        
        code = "\n".join(code_lines)
        
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, code)
    
    def copy_config(self):
        """复制配置"""
        code = self.code_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        messagebox.showinfo("成功", "配置代码已复制到剪贴板")
    
    def save_to_config(self):
        """直接保存到config.py"""
        if not messagebox.askyesno("确认", "确定要将工具配置保存到 core/config.py 吗？\n\n这将覆盖现有的 EXTERNAL_APPS 和 7-Zip 右键菜单配置。"):
            return
        
        try:
            config_file = Path("../config.py")
            
            if not config_file.exists():
                messagebox.showerror("错误", "找不到 config.py 文件")
                return
            
            # 检查是否选择了7-Zip
            sevenzip_selected = self.tool_vars.get('7-Zip', tk.BooleanVar()).get()
            
            # 检查PE右键菜单选择
            pe_context_tools = []
            for tool in self.COMMON_TOOLS:
                if (tool.get('context_menu', False) and 
                    tool['name'] in self.pe_context_vars and 
                    self.pe_context_vars[tool['name']].get()):
                    pe_context_tools.append(tool['name'])
            
            # 读取现有配置
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 生成新的 EXTERNAL_APPS 配置
            new_apps = []
            for tool in self.COMMON_TOOLS:
                if self.tool_vars[tool['name']].get():
                    desktop = self.desktop_vars[tool['name']].get()
                    placement = []
                    if desktop:
                        placement.append("desktop")
                    
                    # 格式：(源文件路径, 目标路径, 描述, 放置选项)
                    placement_str = str(placement).replace("'", '"')
                    new_apps.append(f"    (\"{tool['name']}/{tool['exe']}\", \"Windows/System32\", \"{tool['name']}\", {placement_str}),\n")
            
            # 替换配置
            new_lines = []
            in_external_apps = False
            in_sevenzip_config = False
            skip_until_bracket = False
            skip_until_brace = False
            
            for line in lines:
                # 处理 EXTERNAL_APPS
                if 'EXTERNAL_APPS = [' in line:
                    in_external_apps = True
                    new_lines.append(line)
                    new_lines.extend(new_apps)
                    skip_until_bracket = True
                    continue
                
                if skip_until_bracket and in_external_apps:
                    if ']' in line:
                        new_lines.append(line)
                        in_external_apps = False
                        skip_until_bracket = False
                    continue
                
                # 处理 SEVENZIP_CONTEXT_MENU
                if 'SEVENZIP_CONTEXT_MENU = {' in line:
                    in_sevenzip_config = True
                    # 根据是否选择了7-Zip来设置enabled
                    new_lines.append('SEVENZIP_CONTEXT_MENU = {\n')
                    new_lines.append(f'    "enabled": {str(sevenzip_selected)},\n')
                    skip_until_brace = True
                    continue
                
                if skip_until_brace and in_sevenzip_config:
                    if line.strip().startswith('"enabled"'):
                        # 跳过旧的enabled行
                        continue
                    if '}' in line:
                        new_lines.append(line)
                        in_sevenzip_config = False
                        skip_until_brace = False
                        continue
                    # 保留其他配置行
                    new_lines.append(line)
                    continue
                
                new_lines.append(line)
            
            # 写回文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            msg = "工具配置已保存到 config.py！\n\n"
            msg += f"已配置 {len([t for t in self.COMMON_TOOLS if self.tool_vars[t['name']].get()])} 个工具\n"
            if sevenzip_selected:
                msg += "\n✓ 7-Zip 右键菜单已启用"
            else:
                msg += "\n✗ 7-Zip 右键菜单已禁用"
            
            if pe_context_tools:
                msg += f"\n✓ PE右键菜单已启用: {', '.join(pe_context_tools)}"
            else:
                msg += "\n✗ 未选择PE右键菜单工具"
            
            msg += "\n\n请确保将工具文件放到对应的目录中。"
            
            messagebox.showinfo("成功", msg)
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败:\n{e}")
    
    def load_config(self):
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 恢复选择状态
                    for tool_name, selected in data.get('selected_tools', {}).items():
                        if tool_name in self.tool_vars:
                            self.tool_vars[tool_name].set(selected)
                    # 恢复桌面选项
                    for tool_name, desktop in data.get('desktop_options', {}).items():
                        if tool_name in self.desktop_vars:
                            self.desktop_vars[tool_name].set(desktop)
            except:
                pass
    
    def save_config(self):
        """保存配置"""
        data = {
            'selected_tools': {name: var.get() for name, var in self.tool_vars.items()},
            'desktop_options': {name: var.get() for name, var in self.desktop_vars.items()},
            'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def open_external_dir(self):
        """打开外置程序目录"""
        external_dir = Path("../外置程序") if Path("../外置程序").exists() else Path("外置程序")
        tools_dir = external_dir / "Tools"
        
        # 如果Tools目录不存在，创建它
        if not tools_dir.exists():
            try:
                tools_dir.mkdir(parents=True)
            except:
                pass
        
        # 打开目录
        if tools_dir.exists():
            os.startfile(tools_dir)
        elif external_dir.exists():
            os.startfile(external_dir)
        else:
            messagebox.showinfo("提示", f"外置程序目录不存在\n\n建议创建：{external_dir.absolute()}")
    
    def show_tool_context_menu(self, event, tool):
        """显示工具右键菜单"""
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # 基本操作
        context_menu.add_command(label=f"📥 下载 {tool['name']}", 
                               command=lambda: self.auto_download_tool(tool))
        context_menu.add_command(label=f"🌐 访问官网", 
                               command=lambda: self.open_url(tool['url']))
        context_menu.add_separator()
        
        # 选择操作
        context_menu.add_command(label="✅ 选择此工具", 
                               command=lambda: self.tool_vars[tool['name']].set(True))
        context_menu.add_command(label="❌ 取消选择", 
                               command=lambda: self.tool_vars[tool['name']].set(False))
        context_menu.add_separator()
        
        # 桌面快捷方式
        context_menu.add_command(label="📌 添加到桌面", 
                               command=lambda: self.desktop_vars[tool['name']].set(True))
        context_menu.add_command(label="📌 从桌面移除", 
                               command=lambda: self.desktop_vars[tool['name']].set(False))
        context_menu.add_separator()
        
        # 工具信息
        context_menu.add_command(label=f"ℹ️ 查看详情", 
                               command=lambda: self.show_tool_info(tool))
        
        # 显示菜单
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_tool_info(self, tool):
        """显示工具详细信息"""
        info = f"工具名称: {tool['name']}\n"
        info += f"描述: {tool['desc']}\n"
        info += f"可执行文件: {tool['exe']}\n"
        info += f"官网: {tool['url']}\n"
        if 'download_url' in tool and tool['download_url']:
            info += f"下载链接: {tool['download_url']}\n"
        info += f"推荐: {'是' if tool.get('recommended', False) else '否'}\n"
        info += f"右键菜单: {'是' if tool.get('context_menu', False) else '否'}\n"
        info += f"体积: {tool.get('size', '未知')}\n"
        info += f"授权: {tool.get('license', '未知')}"
        
        messagebox.showinfo(f"{tool['name']} - 详细信息", info)
    
    def batch_download(self):
        """批量自动下载选中的工具"""
        # 获取勾选的工具
        selected_tools = [tool for tool in self.COMMON_TOOLS if self.tool_vars[tool['name']].get()]
        
        if not selected_tools:
            messagebox.showwarning("提示", "请先勾选要下载的工具")
            return
        
        # 过滤有直接下载链接的工具
        downloadable = [t for t in selected_tools if 'download_url' in t and t['download_url']]
        
        if not downloadable:
            messagebox.showinfo("提示", 
                              f"已勾选 {len(selected_tools)} 个工具\n\n"
                              "这些工具暂不支持自动下载，请手动下载：\n\n" +
                              "\n".join([f"• {t['name']}: {t['url']}" for t in selected_tools]))
            return
        
        msg = f"将自动下载以下工具到 tools 目录：\n\n"
        msg += "\n".join([f"• {t['name']}" for t in downloadable])
        msg += f"\n\n共 {len(downloadable)} 个工具\n"
        msg += "下载完成后会自动解压到对应目录"
        
        if messagebox.askyesno("确认下载", msg):
            self.start_batch_download(downloadable)
    
    def start_batch_download(self, tools):
        """开始批量下载"""
        # 创建下载对话框
        from download_dialog import DownloadDialog
        DownloadDialog(self.root, tools)
    
    def auto_download_tool(self, tool):
        """自动下载单个工具"""
        if 'download_url' not in tool or not tool['download_url']:
            messagebox.showinfo("提示", 
                              f"{tool['name']} 暂不支持自动下载\n\n"
                              f"请访问官网手动下载：\n{tool['url']}")
            return
        
        # 创建下载对话框
        from download_dialog import DownloadDialog
        DownloadDialog(self.root, [tool])
    


def main():
    root = tk.Tk()
    app = WinPEToolsManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()

