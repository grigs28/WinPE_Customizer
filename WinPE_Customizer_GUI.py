#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WinPE Customizer v3.0 - 图形界面版本
用途: 自动化创建、定制和打包 Windows PE 启动映像
"""

import os
import sys
import threading
import queue
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess

# 导入配置和核心类
from core import config
from core.WinPE_Customizer import WinPECustomizer


class WinPECustomizerGUI:
    """WinPE 定制工具图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WinPE Customizer v3.0 - Windows PE 定制工具")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 650)
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 状态变量
        self.is_running = False
        self.stop_requested = False
        self.output_queue = queue.Queue()
        self.customizer = None
        
        # 工作目录
        self.work_dir = Path(__file__).parent.absolute()
        
        # 配置变量
        self.winpe_dir = tk.StringVar(value=config.WINPE_DIR)
        self.cab_path = tk.StringVar(value=config.CAB_PATH)
        self.driver_dir = tk.StringVar(value=config.DRIVER_DIR)
        self.external_apps_dir = tk.StringVar(value=config.EXTERNAL_APPS_DIR)
        self.output_iso = tk.StringVar(value=config.OUTPUT_ISO_NAME)
        
        # 模块开关变量
        self.enable_copype = tk.BooleanVar(value=config.ENABLE_COPYPE_SETUP)
        self.enable_auto_mount = tk.BooleanVar(value=config.ENABLE_AUTO_MOUNT)
        self.enable_feature_packs = tk.BooleanVar(value=config.ENABLE_FEATURE_PACKS)
        self.enable_language_packs = tk.BooleanVar(value=config.ENABLE_LANGUAGE_PACKS)
        self.enable_fonts = tk.BooleanVar(value=config.ENABLE_FONTS_LP)
        self.enable_regional = tk.BooleanVar(value=config.ENABLE_REGIONAL_SETTINGS)
        self.enable_drivers = tk.BooleanVar(value=config.ENABLE_DRIVERS)
        self.enable_external_apps = tk.BooleanVar(value=config.ENABLE_EXTERNAL_APPS)
        self.enable_create_dirs = tk.BooleanVar(value=config.ENABLE_CREATE_DIRS)
        self.enable_make_iso = tk.BooleanVar(value=config.ENABLE_MAKE_ISO)
        
        # 创建界面
        self.create_widgets()
        
        # 启动输出监控
        self.monitor_output()
        
        # 显示欢迎信息
        self.log("="*60, 'CYAN')
        self.log("WinPE Customizer v3.0 - Windows PE 定制工具", 'SUCCESS')
        self.log("="*60, 'CYAN')
        self.log("[提示] 请确保以管理员身份运行 '部署和映像工具环境'", 'WARNING')
    
    def set_window_icon(self):
        """设置窗口图标 - 随机从ico目录选择"""
        import random
        
        # 首先检查ico目录
        ico_dir = Path("ico")
        random_icon = None
        
        if ico_dir.exists():
            # 扫描ico目录中的所有图片
            image_files = []
            for ext in ['*.ico', '*.png', '*.jpg', '*.jpeg', '*.bmp']:
                image_files.extend(ico_dir.glob(ext))
            
            if image_files:
                # 随机选择一个
                random_image = random.choice(image_files)
                
                # 如果是ico文件，直接使用
                if random_image.suffix.lower() == '.ico':
                    try:
                        self.root.iconbitmap(str(random_image))
                        self.log(f"[图标] 使用随机图标: {random_image.name}", 'INFO')
                        return
                    except:
                        pass
                else:
                    # 如果是其他图片格式，转换为ico
                    try:
                        from PIL import Image
                        img = Image.open(random_image)
                        # 调整大小为标准图标尺寸
                        img = img.resize((32, 32), Image.Resampling.LANCZOS)
                        # 保存为临时ico文件
                        temp_ico = Path("temp_icon.ico")
                        img.save(temp_ico, format='ICO')
                        self.root.iconbitmap(str(temp_ico))
                        self.log(f"[图标] 使用随机图标: {random_image.name}", 'INFO')
                        return
                    except:
                        pass
        
        # 如果ico目录没有图片，使用默认图标
        icon_files = ['ico/winpe_customizer.ico', 'ico/winpe_simple.ico', 'winpe_customizer.ico', 'icon.ico']
        
        for icon_file in icon_files:
            icon_path = Path(icon_file)
            if icon_path.exists():
                try:
                    self.root.iconbitmap(str(icon_path))
                    break
                except Exception as e:
                    continue
        
        # 如果没有找到 .ico 文件，使用 tkinter 内置方法创建简单图标
        # (Windows 10+ 支持 PNG 作为图标)
        try:
            # 创建一个简单的内存图标
            import base64
            from io import BytesIO
            
            # 这是一个简单的 16x16 蓝色图标的 base64 编码
            icon_data = """
            iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlz
            AAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFcSURB
            VDiNpZK/S8NAGMXfXZOmadJGbdFqVXBQcHBwcnJzEgcHBwf/Bgf/AAcHBwcHJycHBx0cFBQHBxUH
            Fax1aH+lP5I2P5r0LldFLYqD33Lvfe+9x8G9AxERAP8mBQCIiJgZmRmZGYiIiIiY+ddEzMzMzMRE
            REREzPxrImZmZmZiIiIiImL+NREzMzMzERERERH/NTEzMzPzP01MTExMTExMTExMTExMTExMTExM
            TExM/zQxMzMzExERERER8a+JmJmZmYmIiIiI+K+JmJmZmYmIiIiIiPiviZiZmZmJiIiIiIj/moiZ
            mZmZiIiIiIj4r4mYmZmZiYiIiIiI/5qImZmZmYiIiIiIiP+aiJmZmZmIiIiIiPiviZiZmZmJiIiI
            iIj4r4mYmZmZiIiIiIiI+K+JmJmZmYmIiIiIiP+aiJmZmZmJiIiIiIj/moiZmZmZiIiIiIiI/wHr
            +3K5YQAAAABJRU5ErkJggg==
            """
            
            # 注意：这只是示例，在某些 Windows 版本可能不工作
            # 最好的方法还是使用 .ico 文件
        except:
            pass
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器 - 使用 Notebook 实现标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ==================== 标签页1: 主控制面板 ====================
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="主控制面板")
        
        self.create_main_tab(main_tab)
        
        # ==================== 标签页2: 路径配置 ====================
        config_tab = ttk.Frame(notebook)
        notebook.add(config_tab, text="路径配置")
        
        self.create_config_tab(config_tab)
        
        # ==================== 标签页3: 模块设置 ====================
        modules_tab = ttk.Frame(notebook)
        notebook.add(modules_tab, text="模块设置")
        
        self.create_modules_tab(modules_tab)
        
        # ==================== 标签页4: 功能包说明 ====================
        packages_tab = ttk.Frame(notebook)
        notebook.add(packages_tab, text="功能包说明")
        
        self.create_packages_tab(packages_tab)
    
    def create_main_tab(self, parent):
        """创建主控制面板标签页"""
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(2, weight=1)
        
        # ==================== 快速操作区 ====================
        quick_frame = ttk.LabelFrame(parent, text="快速操作", padding="10")
        quick_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(10, 5))
        
        # Mount/Umount 按钮
        mount_frame = ttk.Frame(quick_frame)
        mount_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mount_frame, text="映像管理:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        btn_width = 20  # 统一按钮宽度
        
        self.mount_btn = ttk.Button(mount_frame, text="📦 挂载 WIM 映像", command=self.mount_wim, width=btn_width)
        self.mount_btn.pack(side=tk.LEFT, padx=3)
        
        self.umount_btn = ttk.Button(mount_frame, text="💾 卸载并保存", command=self.umount_wim, width=btn_width)
        self.umount_btn.pack(side=tk.LEFT, padx=3)
        
        self.umount_discard_btn = ttk.Button(mount_frame, text="🗑️ 卸载不保存", command=self.umount_wim_discard, width=btn_width)
        self.umount_discard_btn.pack(side=tk.LEFT, padx=3)
        
        # 第二行：工具管理
        tools_frame = ttk.Frame(quick_frame)
        tools_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(tools_frame, text="工具管理:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(tools_frame, text="📦 外置程序管理器", command=self.open_apps_manager, width=btn_width).pack(side=tk.LEFT, padx=3)
        ttk.Button(tools_frame, text="🛠️ WinPE 工具包", command=self.open_tools_manager, width=btn_width).pack(side=tk.LEFT, padx=3)
        ttk.Button(tools_frame, text="🔧 SDIO 驱动提取", command=self.open_sdio_extractor, width=btn_width).pack(side=tk.LEFT, padx=3)
        ttk.Button(tools_frame, text="🔍 驱动扫描", command=self.open_driver_scanner, width=btn_width).pack(side=tk.LEFT, padx=3)
        
        # 第三行：制作工具（包含清理和制作）
        make_frame = ttk.Frame(quick_frame)
        make_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(make_frame, text="制作工具:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        ttk.Button(make_frame, text="🧹 清理临时文件", command=self.cleanup_temp, width=btn_width).pack(side=tk.LEFT, padx=3)
        ttk.Button(make_frame, text="🔧 清理 WIM", command=self.cleanup_wim, width=btn_width).pack(side=tk.LEFT, padx=3)
        ttk.Button(make_frame, text="💿 生成 ISO 镜像", command=self.make_iso_image, width=btn_width).pack(side=tk.LEFT, padx=3)
        ttk.Button(make_frame, text="💾 制作 USB 启动盘", command=self.make_usb_disk, width=btn_width).pack(side=tk.LEFT, padx=3)
        
        ttk.Separator(quick_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # WinPE 目录
        dir_frame = ttk.Frame(quick_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dir_frame, text="WinPE 目录:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(dir_frame, textvariable=self.winpe_dir, width=60).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="浏览...", command=lambda: self.browse_directory(self.winpe_dir), width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(dir_frame, text="📁 打开", command=self.open_winpe_dir, width=12).pack(side=tk.LEFT, padx=2)
        
        # ==================== 主控制按钮 ====================
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=1, column=0, pady=10)
        
        control_btn_width = 20  # 控制按钮宽度
        
        self.start_btn = ttk.Button(control_frame, text="▶ 开始定制", command=self.start_customization, width=control_btn_width, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⬛ 停止", command=self.stop_customization, state=tk.DISABLED, width=control_btn_width)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(control_frame, text="🗑️ 清空日志", command=self.clear_log, width=control_btn_width)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_log_btn = ttk.Button(control_frame, text="💾 保存日志", command=self.save_log, width=control_btn_width)
        self.save_log_btn.pack(side=tk.LEFT, padx=5)
        
        # ==================== 输出日志 ====================
        log_frame = ttk.LabelFrame(parent, text="运行日志", padding="5")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(5, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=100,
            height=25,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置日志颜色标签
        self.log_text.tag_config('INFO', foreground='#d4d4d4')
        self.log_text.tag_config('SUCCESS', foreground='#4ec9b0', font=('Consolas', 9, 'bold'))
        self.log_text.tag_config('WARNING', foreground='#dcdcaa')
        self.log_text.tag_config('ERROR', foreground='#f48771')
        self.log_text.tag_config('COMMAND', foreground='#569cd6')
        self.log_text.tag_config('HEADER', foreground='#4ec9b0', font=('Consolas', 9, 'bold'))
        self.log_text.tag_config('CYAN', foreground='#4ec9b0')
        
        # 状态栏
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        
        # 状态信息
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(status_frame, text="就绪", foreground="green", font=('Arial', 9, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 进度信息
        ttk.Label(status_frame, text="进度:").pack(side=tk.LEFT, padx=5)
        self.progress_label = ttk.Label(status_frame, text="0/0", font=('Arial', 9))
        self.progress_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(status_frame, mode='determinate', length=300)
        self.progress.pack(side=tk.LEFT, padx=5)
        
        self.progress_percent = ttk.Label(status_frame, text="0%", font=('Arial', 9))
        self.progress_percent.pack(side=tk.LEFT, padx=5)
    
    def create_config_tab(self, parent):
        """创建路径配置标签页"""
        parent.columnconfigure(1, weight=1)
        
        config_frame = ttk.Frame(parent, padding="20")
        config_frame.pack(fill=tk.BOTH, expand=True)
        config_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # WinPE 工作目录
        ttk.Label(config_frame, text="WinPE 工作目录:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8)
        row += 1
        entry_frame = ttk.Frame(config_frame)
        entry_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        entry_frame.columnconfigure(0, weight=1)
        ttk.Entry(entry_frame, textvariable=self.winpe_dir).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(entry_frame, text="浏览...", command=lambda: self.browse_directory(self.winpe_dir)).grid(row=0, column=1)
        row += 1
        
        # Windows ADK 路径
        ttk.Label(config_frame, text="Windows ADK 组件路径:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8)
        row += 1
        entry_frame = ttk.Frame(config_frame)
        entry_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        entry_frame.columnconfigure(0, weight=1)
        ttk.Entry(entry_frame, textvariable=self.cab_path).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(entry_frame, text="浏览...", command=lambda: self.browse_directory(self.cab_path)).grid(row=0, column=1)
        row += 1
        
        # 驱动程序目录
        ttk.Label(config_frame, text="驱动程序目录:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8)
        row += 1
        entry_frame = ttk.Frame(config_frame)
        entry_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        entry_frame.columnconfigure(0, weight=1)
        ttk.Entry(entry_frame, textvariable=self.driver_dir).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(entry_frame, text="浏览...", command=lambda: self.browse_directory(self.driver_dir)).grid(row=0, column=1)
        row += 1
        
        # 外置程序目录
        ttk.Label(config_frame, text="外置程序目录:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8)
        row += 1
        entry_frame = ttk.Frame(config_frame)
        entry_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        entry_frame.columnconfigure(0, weight=1)
        ttk.Entry(entry_frame, textvariable=self.external_apps_dir).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(entry_frame, text="浏览...", command=lambda: self.browse_directory(self.external_apps_dir)).grid(row=0, column=1)
        row += 1
        
        # 输出 ISO 文件名
        ttk.Label(config_frame, text="输出 ISO 文件名:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=8)
        row += 1
        ttk.Entry(config_frame, textvariable=self.output_iso, width=50).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        row += 1
        
        # 按钮
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="💾 保存路径配置", command=self.save_config, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 重置为默认", command=self.reset_config, width=18).pack(side=tk.LEFT, padx=5)
    
    def create_modules_tab(self, parent):
        """创建模块设置标签页"""
        modules_frame = ttk.Frame(parent, padding="20")
        modules_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(modules_frame, text="选择要执行的模块:", font=('Arial', 11, 'bold')).pack(anchor=tk.W, pady=(0, 15))
        
        # 模块列表
        modules = [
            (self.enable_copype, "创建 WinPE 工作环境", "如果目录不存在，自动创建 WinPE 基础环境"),
            (self.enable_auto_mount, "自动挂载 boot.wim", "自动挂载 WIM 映像以便进行修改"),
            (self.enable_feature_packs, "安装 WinPE 功能包", "安装 PowerShell、.NET Framework 等组件"),
            (self.enable_language_packs, "安装中文语言包", "为功能包添加中文界面支持"),
            (self.enable_fonts, "安装中文字体支持", "安装中文字体和核心语言包"),
            (self.enable_regional, "配置区域和语言设置", "设置系统语言、时区、输入法为中文"),
            (self.enable_drivers, "批量安装硬件驱动", "从驱动目录递归安装所有驱动"),
            (self.enable_external_apps, "复制外置程序", "将第三方工具复制到 WinPE"),
            (self.enable_create_dirs, "创建自定义目录结构", "创建常用工作目录"),
            (self.enable_make_iso, "卸载 WIM 并生成 ISO", "保存更改并生成可启动 ISO 文件"),
        ]
        
        for var, title, desc in modules:
            frame = ttk.Frame(modules_frame)
            frame.pack(fill=tk.X, pady=5)
            
            cb = ttk.Checkbutton(frame, text=title, variable=var)
            cb.pack(anchor=tk.W)
            
            desc_label = ttk.Label(frame, text=f"    {desc}", foreground="gray")
            desc_label.pack(anchor=tk.W)
        
        # 快速选择按钮
        btn_frame = ttk.Frame(modules_frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="全选", command=self.select_all_modules, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全不选", command=self.deselect_all_modules, width=14).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="推荐配置", command=self.select_recommended, width=14).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Button(btn_frame, text="💾 保存模块设置", command=self.save_module_config, width=18, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
    
    def create_packages_tab(self, parent):
        """创建功能包说明标签页"""
        from tkinter import scrolledtext
        
        # 创建滚动文本框
        text_widget = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            width=100,
            height=35,
            font=('Microsoft YaHei UI', 10),
            bg='#f5f5f5',
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 读取功能包说明文档
        doc_path = Path("docs/WinPE功能包说明.md")
        if doc_path.exists():
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                text_widget.insert(1.0, content)
            except:
                text_widget.insert(1.0, "无法加载功能包说明文档")
        else:
            text_widget.insert(1.0, "功能包说明文档不存在")
        
        text_widget.config(state=tk.DISABLED)  # 只读
        
        # 按钮栏
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="📂 打开文档目录", command=self.open_docs_dir, width=18).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🌐 访问微软官方文档", command=self.open_ms_packages_docs, width=20).pack(side=tk.LEFT, padx=5)
    
    def open_docs_dir(self):
        """打开文档目录"""
        docs_path = Path("docs")
        if docs_path.exists():
            os.startfile(docs_path)
        else:
            messagebox.showinfo("提示", "docs 目录不存在")
    
    def open_ms_packages_docs(self):
        """打开微软功能包文档"""
        import webbrowser
        webbrowser.open("https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-add-packages--optional-components-reference")
    
    def browse_directory(self, var):
        """浏览目录"""
        directory = filedialog.askdirectory(title="选择目录", initialdir=var.get())
        if directory:
            var.set(directory)
    
    def open_winpe_dir(self):
        """打开 WinPE 目录"""
        path = Path(self.winpe_dir.get())
        if path.exists():
            os.startfile(path)
        else:
            messagebox.showwarning("警告", "目录不存在")
    
    def open_apps_manager(self):
        """打开外置程序管理器"""
        import subprocess
        import sys
        
        script_path = Path("tools/external_apps_manager.py")
        if not script_path.exists():
            messagebox.showerror("错误", "找不到外置程序管理器\n路径: tools/external_apps_manager.py")
            return
        
        try:
            # 在新进程中启动
            subprocess.Popen([sys.executable, str(script_path)])
            self.log("[工具] 已启动外置程序管理器", 'SUCCESS')
        except Exception as e:
            messagebox.showerror("错误", f"启动失败:\n{e}")
    
    def open_tools_manager(self):
        """打开WinPE工具包管理器"""
        import subprocess
        import sys
        
        script_path = Path("tools/winpe_tools_manager.py")
        if not script_path.exists():
            messagebox.showerror("错误", "找不到WinPE工具包管理器\n路径: tools/winpe_tools_manager.py")
            return
        
        try:
            subprocess.Popen([sys.executable, str(script_path)])
            self.log("[工具] 已启动WinPE工具包管理器", 'SUCCESS')
        except Exception as e:
            messagebox.showerror("错误", f"启动失败:\n{e}")
    
    def open_sdio_extractor(self):
        """打开SDIO驱动提取工具"""
        import subprocess
        import sys
        
        script_path = Path("tools/extract_sdio_drivers_gui.py")
        if not script_path.exists():
            messagebox.showerror("错误", "找不到SDIO驱动提取工具\n路径: tools/extract_sdio_drivers_gui.py")
            return
        
        try:
            subprocess.Popen([sys.executable, str(script_path)])
            self.log("[工具] 已启动SDIO驱动提取工具", 'SUCCESS')
        except Exception as e:
            messagebox.showerror("错误", f"启动失败:\n{e}")
    
    def open_driver_scanner(self):
        """打开驱动扫描工具"""
        import subprocess
        import sys
        
        script_path = Path("tools/scan_drivers.py")
        if not script_path.exists():
            messagebox.showerror("错误", "找不到驱动扫描工具\n路径: tools/scan_drivers.py")
            return
        
        # 扫描工具是命令行的，在新窗口运行
        try:
            drive_path = Path(self.driver_dir.get())
            if drive_path.exists():
                subprocess.Popen(['cmd', '/k', sys.executable, str(script_path), str(drive_path)])
            else:
                subprocess.Popen(['cmd', '/k', sys.executable, str(script_path)])
            self.log("[工具] 已启动驱动扫描工具", 'SUCCESS')
        except Exception as e:
            messagebox.showerror("错误", f"启动失败:\n{e}")
    
    def make_iso_image(self):
        """生成 ISO 镜像"""
        if self.is_running:
            messagebox.showwarning("警告", "有任务正在运行，请等待完成")
            return
        
        winpe_dir = Path(self.winpe_dir.get())
        mount_dir = winpe_dir / "mount"
        
        # 检查是否已挂载
        if (mount_dir / "Windows").exists():
            if not messagebox.askyesno("提示", "WIM 仍处于挂载状态。\n\n需要先卸载并保存 WIM 才能生成 ISO。\n\n是否现在卸载并保存？"):
                return
            
            # 先卸载
            self.log("="*60, 'CYAN')
            self.log("[操作] 卸载并保存 WIM", 'HEADER')
            self.log("="*60, 'CYAN')
            
            thread = threading.Thread(target=self._do_umount_and_make_iso, args=(True,))
            thread.daemon = True
            thread.start()
        else:
            # 直接生成ISO
            self.log("="*60, 'CYAN')
            self.log("[操作] 生成 ISO 镜像", 'HEADER')
            self.log("="*60, 'CYAN')
            
            thread = threading.Thread(target=self._do_make_iso)
            thread.daemon = True
            thread.start()
    
    def _do_make_iso(self):
        """执行生成ISO"""
        self.is_running = True
        self.root.after(0, lambda: self.progress.start(10))
        
        try:
            winpe_dir = Path(self.winpe_dir.get())
            iso_name = self.output_iso.get() if self.output_iso.get() else "MyCustomWinPE.iso"
            iso_path = self.work_dir / iso_name
            
            self.output_queue.put(('INFO', f'[执行] 生成 ISO 文件...'))
            self.output_queue.put(('INFO', f'[目标] {iso_path}'))
            self.output_queue.put(('COMMAND', f'MakeWinPEMedia /iso "{winpe_dir}" "{iso_path}"'))
            
            cmd = f'MakeWinPEMedia /iso "{winpe_dir}" "{iso_path}"'
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, 
                                   encoding='utf-8', errors='ignore', startupinfo=startupinfo)
            
            if result.returncode == 0:
                self.output_queue.put(('SUCCESS', f'[✅ 成功] ISO 文件生成成功'))
                self.output_queue.put(('SUCCESS', f'[路径] {iso_path}'))
                self.root.after(0, lambda: messagebox.showinfo("成功", f"ISO 文件生成成功！\n\n{iso_path}"))
            else:
                self.output_queue.put(('ERROR', f'[❌ 失败] ISO 生成失败'))
                if result.stdout:
                    self.output_queue.put(('INFO', result.stdout))
        except Exception as e:
            self.output_queue.put(('ERROR', f'[异常] {e}'))
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.progress.stop())
    
    def _do_umount_and_make_iso(self, commit=True):
        """卸载后生成ISO"""
        # 先卸载
        self._do_umount(commit)
        # 再生成ISO
        import time
        time.sleep(2)  # 等待卸载完成
        self._do_make_iso()
    
    def cleanup_temp(self):
        """清理临时文件"""
        self.log("开始清理临时文件...", "INFO")
        
        # 清理项目
        cleanup_items = [
            ("temp_7zip_menu.reg", "7-Zip注册表临时文件"),
            ("temp_7zip_menu_modified.reg", "7-Zip注册表修改文件"),
            ("temp_extract", "驱动提取临时目录"),
        ]
        
        cleaned_count = 0
        
        try:
            for item, desc in cleanup_items:
                path = self.work_dir / item
                if path.exists():
                    try:
                        if path.is_file():
                            path.unlink()
                            self.log(f"删除: {desc}", "INFO")
                            cleaned_count += 1
                        elif path.is_dir():
                            import shutil
                            shutil.rmtree(path)
                            self.log(f"删除: {desc}", "INFO")
                            cleaned_count += 1
                    except Exception as e:
                        self.log(f"删除失败 {desc}: {e}", "WARNING")
            
            # 清理Python缓存
            for pycache in self.work_dir.glob("**/__pycache__"):
                try:
                    import shutil
                    shutil.rmtree(pycache)
                    self.log(f"删除: Python缓存 {pycache.name}", "INFO")
                    cleaned_count += 1
                except:
                    pass
            
            if cleaned_count > 0:
                self.log(f"清理完成，共删除 {cleaned_count} 项", "SUCCESS")
                messagebox.showinfo("完成", f"临时文件清理完成！\n\n共清理 {cleaned_count} 项")
            else:
                self.log("没有需要清理的临时文件", "INFO")
                messagebox.showinfo("提示", "没有需要清理的临时文件")
                
        except Exception as e:
            self.log(f"清理临时文件时出错: {e}", "ERROR")
            messagebox.showerror("错误", f"清理失败: {e}")
    
    def cleanup_wim(self):
        """清理 WIM 挂载（DISM /Cleanup-Wim）"""
        if messagebox.askyesno("确认", "此操作将清理所有未正常卸载的 WIM 挂载。\n\n这可能会丢失未保存的更改。\n\n是否继续？"):
            self.log("开始清理 WIM 挂载...", "INFO")
            
            try:
                cmd = "dism /Cleanup-Wim"
                self.log(f"执行命令: {cmd}", "INFO")
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    self.log("WIM 清理成功", "SUCCESS")
                    messagebox.showinfo("成功", "WIM 挂载已清理完成")
                else:
                    self.log(f"清理失败: {result.stderr}", "ERROR")
                    messagebox.showerror("失败", "WIM 清理失败，请查看日志")
                    
            except Exception as e:
                self.log(f"清理 WIM 时出错: {e}", "ERROR")
                messagebox.showerror("错误", str(e))
    
    def open_driver_scanner(self):
        """打开驱动扫描工具"""
        try:
            import subprocess
            python_exe = sys.executable
            scanner_path = self.work_dir / "tools" / "driver_scanner.py"
            
            if scanner_path.exists():
                subprocess.Popen([python_exe, str(scanner_path)])
                self.log("已启动驱动扫描工具", "INFO")
            else:
                messagebox.showerror("错误", f"找不到驱动扫描工具\n\n{scanner_path}")
        except Exception as e:
            messagebox.showerror("错误", f"启动驱动扫描工具失败:\n{e}")
    
    def make_usb_disk(self):
        """制作 USB 启动盘"""
        if self.is_running:
            messagebox.showwarning("警告", "有任务正在运行，请等待完成")
            return
        
        winpe_dir = Path(self.winpe_dir.get())
        
        if not winpe_dir.exists():
            messagebox.showerror("错误", f"WinPE 目录不存在:\n{winpe_dir}")
            return
        
        # 导入USB制作对话框
        from tools.usb_maker import show_usb_maker_dialog
        show_usb_maker_dialog(self.root, winpe_dir)
    
    def log(self, message, tag='INFO'):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 检测进度信息（格式：  进度: 50.0%）
        if message.strip().startswith('进度:'):
            # 检查最后一行是否也是进度信息
            last_line = self.log_text.get("end-2l", "end-1l").strip()
            if '进度:' in last_line:
                # 删除最后一行（之前的进度）
                self.log_text.delete("end-2l", "end-1l")
            
            # 插入新的进度（同一行更新）
            full_message = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, full_message, tag)
        else:
            # 普通消息，正常插入
            full_message = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, full_message, tag)
        
        self.log_text.see(tk.END)
        
        # 解析进度信息
        self.parse_progress(message)
    
    def parse_progress(self, message):
        """解析进度信息"""
        import re
        
        # 解析百分比进度 (例: [50%], 50%, Progress: 50%)
        percent_match = re.search(r'(\d+)%', message)
        if percent_match:
            percent = int(percent_match.group(1))
            self.update_progress(percent, percent)
        
        # 解析步骤进度 (例: [3/10], 3/10, Step 3 of 10)
        step_match = re.search(r'(\d+)[/\s]+(\d+)', message)
        if step_match:
            current = int(step_match.group(1))
            total = int(step_match.group(2))
            self.update_progress(current, total)
    
    def update_progress(self, current, total=100):
        """更新进度条"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress['value'] = percent
            self.progress_percent.config(text=f"{percent}%")
            
            if total != 100:  # 如果不是百分比，显示步骤
                self.progress_label.config(text=f"{current}/{total}")
            else:
                self.progress_label.config(text=f"{percent}%")
    
    def reset_progress(self):
        """重置进度条"""
        self.progress['value'] = 0
        self.progress_percent.config(text="0%")
        self.progress_label.config(text="0/0")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("[系统] 日志已清空", 'INFO')
    
    def save_log(self):
        """保存日志"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("日志文件", "*.log"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"WinPE_Customizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log(f"[成功] 日志已保存到: {filename}", 'SUCCESS')
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败:\n{e}")
    
    def mount_wim(self):
        """挂载 WIM 映像"""
        if self.is_running:
            messagebox.showwarning("警告", "有任务正在运行，请等待完成")
            return
        
        self.log("="*60, 'CYAN')
        self.log("[操作] 挂载 WIM 映像", 'HEADER')
        self.log("="*60, 'CYAN')
        
        thread = threading.Thread(target=self._do_mount)
        thread.daemon = True
        thread.start()
    
    def _do_mount(self):
        """执行挂载操作"""
        self.is_running = True
        self.root.after(0, lambda: self.mount_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.progress.start(10))
        
        try:
            winpe_dir = Path(self.winpe_dir.get())
            mount_dir = winpe_dir / "mount"
            boot_wim = winpe_dir / "media" / "sources" / "boot.wim"
            
            if not boot_wim.exists():
                self.output_queue.put(('ERROR', f'[错误] boot.wim 不存在: {boot_wim}'))
                return
            
            # 创建挂载目录
            mount_dir.mkdir(parents=True, exist_ok=True)
            
            # 检查是否已挂载
            if (mount_dir / "Windows").exists():
                self.output_queue.put(('WARNING', '[提示] WIM 已处于挂载状态'))
                return
            
            self.output_queue.put(('INFO', f'[执行] 挂载 WIM 文件...'))
            self.output_queue.put(('COMMAND', f'dism /mount-wim /wimfile:"{boot_wim}" /index:1 /mountdir:"{mount_dir}"'))
            
            cmd = f'dism /mount-wim /wimfile:"{boot_wim}" /index:1 /mountdir:"{mount_dir}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                self.output_queue.put(('SUCCESS', '[成功] WIM 映像挂载成功'))
            else:
                self.output_queue.put(('ERROR', f'[失败] 挂载失败 (代码: {result.returncode})'))
                if result.stdout:
                    self.output_queue.put(('INFO', result.stdout))
        except Exception as e:
            self.output_queue.put(('ERROR', f'[异常] {e}'))
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.mount_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress.stop())
    
    def umount_wim(self):
        """卸载并保存 WIM"""
        if self.is_running:
            messagebox.showwarning("警告", "有任务正在运行，请等待完成")
            return
        
        if not messagebox.askyesno("确认", "确定要卸载并保存 WIM 映像吗？\n所有更改将被保存。"):
            return
        
        self.log("="*60, 'CYAN')
        self.log("[操作] 卸载并保存 WIM 映像", 'HEADER')
        self.log("="*60, 'CYAN')
        
        thread = threading.Thread(target=self._do_umount, args=(True,))
        thread.daemon = True
        thread.start()
    
    def umount_wim_discard(self):
        """卸载不保存 WIM"""
        if self.is_running:
            messagebox.showwarning("警告", "有任务正在运行，请等待完成")
            return
        
        if not messagebox.askyesno("确认", "确定要卸载并丢弃更改吗？\n所有更改将丢失！", icon='warning'):
            return
        
        self.log("="*60, 'CYAN')
        self.log("[操作] 卸载 WIM 映像（不保存）", 'HEADER')
        self.log("="*60, 'CYAN')
        
        thread = threading.Thread(target=self._do_umount, args=(False,))
        thread.daemon = True
        thread.start()
    
    def _do_umount(self, commit=True):
        """执行卸载操作"""
        self.is_running = True
        self.root.after(0, lambda: self.umount_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.umount_discard_btn.config(state=tk.DISABLED))
        self.root.after(0, lambda: self.progress.start(10))
        
        try:
            winpe_dir = Path(self.winpe_dir.get())
            mount_dir = winpe_dir / "mount"
            
            if not (mount_dir / "Windows").exists():
                self.output_queue.put(('WARNING', '[提示] WIM 未处于挂载状态'))
                return
            
            action = "保存" if commit else "丢弃"
            flag = "/commit" if commit else "/discard"
            
            self.output_queue.put(('INFO', f'[执行] 卸载 WIM 映像（{action}更改）...'))
            self.output_queue.put(('COMMAND', f'dism /unmount-wim /mountdir:"{mount_dir}" {flag}'))
            
            cmd = f'dism /unmount-wim /mountdir:"{mount_dir}" {flag}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                self.output_queue.put(('SUCCESS', f'[成功] WIM 映像卸载成功（已{action}更改）'))
            else:
                self.output_queue.put(('ERROR', f'[失败] 卸载失败 (代码: {result.returncode})'))
                if result.stdout:
                    self.output_queue.put(('INFO', result.stdout))
        except Exception as e:
            self.output_queue.put(('ERROR', f'[异常] {e}'))
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.umount_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.umount_discard_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress.stop())
    
    def start_customization(self):
        """开始定制"""
        if self.is_running:
            return
        
        # 更新配置
        self.update_config_from_ui()
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.reset_progress()
        self.status_label.config(text="运行中...", foreground="orange")
        
        self.log("="*60, 'CYAN')
        self.log("[开始] 启动 WinPE 定制流程", 'SUCCESS')
        self.log("="*60, 'CYAN')
        
        # 在后台线程运行
        thread = threading.Thread(target=self.run_customization)
        thread.daemon = True
        thread.start()
    
    def stop_customization(self):
        """停止定制"""
        if messagebox.askyesno("确认", "确定要停止吗？\n当前操作会继续完成。"):
            self.log("[⚠️ 警告] 用户请求停止，等待当前操作完成...", 'WARNING')
            self.stop_requested = True
            self.status_label.config(text="正在停止...", foreground="orange")
    
    def run_customization(self):
        """运行定制流程"""
        try:
            # 重置停止标志
            self.stop_requested = False
            
            # 创建自定义的 Customizer
            customizer = CustomWinPECustomizer(self.winpe_dir.get(), self.output_queue, self)
            
            # 运行
            exit_code = customizer.run()
            
            # 设置进度为100%
            self.root.after(0, lambda: self.update_progress(100, 100))
            
            if exit_code == 2 or self.stop_requested:
                self.output_queue.put(('WARNING', '='*60))
                self.output_queue.put(('WARNING', '[⚠️ 已停止] 用户中断执行'))
                self.output_queue.put(('WARNING', '='*60))
                self.root.after(0, lambda: self.status_label.config(text="⚠️ 已停止", foreground="orange"))
            elif exit_code == 0:
                self.output_queue.put(('SUCCESS', '='*60))
                self.output_queue.put(('SUCCESS', '[✅ 完成] WinPE 定制流程全部完成！'))
                self.output_queue.put(('SUCCESS', '='*60))
                self.root.after(0, lambda: self.status_label.config(text="✅ 完成", foreground="green"))
            else:
                self.output_queue.put(('ERROR', '='*60))
                self.output_queue.put(('ERROR', '[❌ 失败] WinPE 定制流程未完成'))
                self.output_queue.put(('ERROR', '='*60))
                self.root.after(0, lambda: self.status_label.config(text="❌ 失败", foreground="red"))
                
        except Exception as e:
            self.output_queue.put(('ERROR', f'[异常] {str(e)}'))
            self.root.after(0, lambda: self.status_label.config(text="错误", foreground="red"))
        finally:
            self.root.after(0, self.finish_customization)
    
    def finish_customization(self):
        """完成定制"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def update_config_from_ui(self):
        """从UI更新配置"""
        config.WINPE_DIR = self.winpe_dir.get()
        config.CAB_PATH = self.cab_path.get()
        config.DRIVER_DIR = self.driver_dir.get()
        config.EXTERNAL_APPS_DIR = self.external_apps_dir.get()
        config.OUTPUT_ISO_NAME = self.output_iso.get()
        
        config.ENABLE_COPYPE_SETUP = self.enable_copype.get()
        config.ENABLE_AUTO_MOUNT = self.enable_auto_mount.get()
        config.ENABLE_FEATURE_PACKS = self.enable_feature_packs.get()
        config.ENABLE_LANGUAGE_PACKS = self.enable_language_packs.get()
        config.ENABLE_FONTS_LP = self.enable_fonts.get()
        config.ENABLE_REGIONAL_SETTINGS = self.enable_regional.get()
        config.ENABLE_DRIVERS = self.enable_drivers.get()
        config.ENABLE_EXTERNAL_APPS = self.enable_external_apps.get()
        config.ENABLE_CREATE_DIRS = self.enable_create_dirs.get()
        config.ENABLE_MAKE_ISO = self.enable_make_iso.get()
    
    def save_config(self):
        """保存配置到文件"""
        self.update_config_from_ui()
        messagebox.showinfo("提示", "配置已更新\n重启程序后生效")
    
    def reset_config(self):
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置为默认配置吗？"):
            # 重新加载默认值
            import importlib
            importlib.reload(config)
            
            self.winpe_dir.set(config.WINPE_DIR)
            self.cab_path.set(config.CAB_PATH)
            self.driver_dir.set(config.DRIVER_DIR)
            self.external_apps_dir.set(config.EXTERNAL_APPS_DIR)
            self.output_iso.set(config.OUTPUT_ISO_NAME)
            
            self.enable_copype.set(config.ENABLE_COPYPE_SETUP)
            self.enable_auto_mount.set(config.ENABLE_AUTO_MOUNT)
            self.enable_feature_packs.set(config.ENABLE_FEATURE_PACKS)
            self.enable_language_packs.set(config.ENABLE_LANGUAGE_PACKS)
            self.enable_fonts.set(config.ENABLE_FONTS_LP)
            self.enable_regional.set(config.ENABLE_REGIONAL_SETTINGS)
            self.enable_drivers.set(config.ENABLE_DRIVERS)
            self.enable_external_apps.set(config.ENABLE_EXTERNAL_APPS)
            self.enable_create_dirs.set(config.ENABLE_CREATE_DIRS)
            self.enable_make_iso.set(config.ENABLE_MAKE_ISO)
            
            self.log("[系统] 配置已重置为默认值", 'SUCCESS')
    
    def select_all_modules(self):
        """全选模块"""
        for var in [self.enable_copype, self.enable_auto_mount, self.enable_feature_packs,
                    self.enable_language_packs, self.enable_fonts, self.enable_regional,
                    self.enable_drivers, self.enable_external_apps, self.enable_create_dirs,
                    self.enable_make_iso]:
            var.set(True)
    
    def deselect_all_modules(self):
        """全不选模块"""
        for var in [self.enable_copype, self.enable_auto_mount, self.enable_feature_packs,
                    self.enable_language_packs, self.enable_fonts, self.enable_regional,
                    self.enable_drivers, self.enable_external_apps, self.enable_create_dirs,
                    self.enable_make_iso]:
            var.set(False)
    
    def select_recommended(self):
        """推荐配置"""
        self.enable_copype.set(True)
        self.enable_auto_mount.set(True)
        self.enable_feature_packs.set(True)
        self.enable_language_packs.set(True)
        self.enable_fonts.set(True)
        self.enable_regional.set(True)
        self.enable_drivers.set(True)
        self.enable_external_apps.set(False)
        self.enable_create_dirs.set(False)
        self.enable_make_iso.set(False)
        
        self.log("[系统] 已选择推荐配置", 'SUCCESS')
    
    def save_module_config(self):
        """保存模块配置到 config.py"""
        if not messagebox.askyesno("确认", "确定要保存当前模块设置到配置文件吗？\n这将修改 core/config.py"):
            return
        
        try:
            config_file = Path("core/config.py")
            
            # 读取现有配置
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新模块开关
            import re
            
            replacements = [
                ('ENABLE_COPYPE_SETUP', self.enable_copype.get()),
                ('ENABLE_AUTO_MOUNT', self.enable_auto_mount.get()),
                ('ENABLE_FEATURE_PACKS', self.enable_feature_packs.get()),
                ('ENABLE_LANGUAGE_PACKS', self.enable_language_packs.get()),
                ('ENABLE_FONTS_LP', self.enable_fonts.get()),
                ('ENABLE_REGIONAL_SETTINGS', self.enable_regional.get()),
                ('ENABLE_DRIVERS', self.enable_drivers.get()),
                ('ENABLE_EXTERNAL_APPS', self.enable_external_apps.get()),
                ('ENABLE_CREATE_DIRS', self.enable_create_dirs.get()),
                ('ENABLE_MAKE_ISO', self.enable_make_iso.get()),
            ]
            
            for var_name, value in replacements:
                pattern = f'{var_name}\\s*=\\s*(True|False)'
                replacement = f'{var_name} = {value}'
                content = re.sub(pattern, replacement, content)
            
            # 写回文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log("[✅ 成功] 模块设置已保存到 core/config.py", 'SUCCESS')
            messagebox.showinfo("成功", "模块设置已保存到配置文件！\n\n下次启动程序时将使用新配置。")
            
        except Exception as e:
            self.log(f"[❌ 错误] 保存失败: {e}", 'ERROR')
            messagebox.showerror("错误", f"保存配置文件失败:\n{e}")
    
    def monitor_output(self):
        """监控输出队列"""
        try:
            while True:
                tag, message = self.output_queue.get_nowait()
                self.log(message, tag)
        except queue.Empty:
            pass
        
        # 继续监控
        self.root.after(100, self.monitor_output)


class CustomWinPECustomizer(WinPECustomizer):
    """自定义的定制器，输出重定向到队列"""
    
    def __init__(self, winpe_dir, output_queue, gui_instance=None):
        super().__init__(winpe_dir, silent_mode=True)  # 启用静默模式，不输出到控制台
        self.output_queue = output_queue
        self.gui_instance = gui_instance
        self.total_steps = 0
        self.current_step = 0
        
        # 统计启用的模块数量
        self.count_enabled_modules()
    
    def should_stop(self):
        """检查是否应该停止"""
        if self.gui_instance and self.gui_instance.stop_requested:
            self.print_warning("[⚠️ 停止] 检测到停止请求，当前操作完成后将停止")
            return True
        return False
    
    def count_enabled_modules(self):
        """统计启用的模块数量"""
        modules = [
            self.enable_copype_setup,
            self.enable_auto_mount,
            self.enable_feature_packs,
            self.enable_language_packs,
            self.enable_fonts_lp,
            self.enable_regional_settings,
            self.enable_drivers,
            self.enable_external_apps,
            self.enable_create_dirs,
            self.enable_make_iso,
        ]
        self.total_steps = sum(modules)
    
    def report_step_start(self, step_name):
        """报告步骤开始"""
        self.current_step += 1
        self.output_queue.put(('CYAN', f"[进度 {self.current_step}/{self.total_steps}] 开始: {step_name}"))
    
    def report_step_end(self, step_name, success=True):
        """报告步骤结束"""
        if success:
            self.output_queue.put(('SUCCESS', f"[✅ 完成] {step_name}"))
        else:
            self.output_queue.put(('ERROR', f"[❌ 失败] {step_name}"))
    
    def print_header(self, text):
        """打印标题"""
        self.output_queue.put(('CYAN', "="*50))
        self.output_queue.put(('HEADER', text))
        self.output_queue.put(('CYAN', "="*50))
    
    def print_info(self, text):
        """打印普通信息"""
        self.output_queue.put(('INFO', text))
    
    def print_success(self, text):
        """打印成功信息"""
        self.output_queue.put(('SUCCESS', text))
    
    def print_error(self, text):
        """打印错误信息"""
        self.output_queue.put(('ERROR', text))
    
    def print_warning(self, text):
        """打印警告信息"""
        self.output_queue.put(('WARNING', text))
    
    def print_cyan(self, text):
        """打印青色信息"""
        self.output_queue.put(('CYAN', text))
    
    def run(self):
        """主流程（重写以添加进度报告）"""
        try:
            # 显示配置
            self.print_cyan("="*40)
            self.print_cyan(f"总计 {self.total_steps} 个模块将被执行")
            self.print_cyan("="*40)
            
            # 检查 ADK
            if not self.check_adk_path():
                return 1
            
            # 创建 WinPE 环境
            if self.enable_copype_setup:
                self.report_step_start("创建 WinPE 工作环境")
                result = self.create_winpe_environment()
                self.report_step_end("创建 WinPE 工作环境", result)
                if not result:
                    return 1
            
            # 挂载 WIM
            if self.enable_auto_mount:
                self.report_step_start("挂载 boot.wim")
                result = self.check_and_mount_wim()
                self.report_step_end("挂载 boot.wim", result)
                if not result:
                    return 1
            
            # 执行定制流程
            if self.enable_feature_packs:
                if self.should_stop():
                    return 2
                self.report_step_start("安装功能包")
                result = self.install_feature_packs()
                self.report_step_end("安装功能包", result)
            
            if self.enable_language_packs:
                if self.should_stop():
                    return 2
                self.report_step_start("安装中文语言包")
                result = self.install_language_packs()
                self.report_step_end("安装中文语言包", result)
            
            if self.enable_fonts_lp:
                if self.should_stop():
                    return 2
                self.report_step_start("安装字体支持")
                result = self.install_fonts_and_lp()
                self.report_step_end("安装字体支持", result)
            
            if self.enable_regional_settings:
                if self.should_stop():
                    return 2
                self.report_step_start("配置区域设置")
                result = self.set_regional_settings()
                self.report_step_end("配置区域设置", result)
            
            if self.enable_drivers:
                if self.should_stop():
                    return 2
                self.report_step_start("批量安装驱动程序")
                result = self.install_drivers()
                self.report_step_end("批量安装驱动程序", result)
            
            if self.enable_external_apps:
                if self.should_stop():
                    return 2
                self.report_step_start("复制附加程序")
                result = self.copy_external_apps()
                self.report_step_end("复制附加程序", result)
            
            if self.enable_create_dirs:
                if self.should_stop():
                    return 2
                self.report_step_start("创建自定义目录结构")
                result = self.create_directories()
                self.report_step_end("创建自定义目录结构", result)
            
            if self.enable_make_iso:
                if self.should_stop():
                    return 2
                self.report_step_start("卸载 WIM 并生成 ISO")
                result = self.make_iso()
                self.report_step_end("卸载 WIM 并生成 ISO", result)
            
            # 显示摘要
            self.print_cyan("="*40)
            self.print_cyan("WinPE 定制流程已全部完成")
            self.print_cyan("="*40)
            self.show_summary()
            
            return 0
            
        except KeyboardInterrupt:
            self.print_warning("\n[中断] 用户中断执行")
            return 1
        except Exception as e:
            self.print_error(f"\n[异常] 发生错误: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """主函数"""
    root = tk.Tk()
    app = WinPECustomizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

