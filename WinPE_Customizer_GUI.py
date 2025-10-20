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
import config
from WinPE_Customizer import WinPECustomizer


class WinPECustomizerGUI:
    """WinPE 定制工具图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WinPE Customizer v3.0 - Windows PE 定制工具")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 650)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 状态变量
        self.is_running = False
        self.output_queue = queue.Queue()
        self.customizer = None
        
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
        
        self.mount_btn = ttk.Button(mount_frame, text="📦 挂载 WIM", command=self.mount_wim, width=15)
        self.mount_btn.pack(side=tk.LEFT, padx=5)
        
        self.umount_btn = ttk.Button(mount_frame, text="💾 卸载并保存", command=self.umount_wim, width=15)
        self.umount_btn.pack(side=tk.LEFT, padx=5)
        
        self.umount_discard_btn = ttk.Button(mount_frame, text="🗑 卸载不保存", command=self.umount_wim_discard, width=15)
        self.umount_discard_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(quick_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # WinPE 目录
        dir_frame = ttk.Frame(quick_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dir_frame, text="WinPE 目录:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(dir_frame, textvariable=self.winpe_dir, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="浏览", command=lambda: self.browse_directory(self.winpe_dir)).pack(side=tk.LEFT)
        ttk.Button(dir_frame, text="📁 打开", command=self.open_winpe_dir).pack(side=tk.LEFT, padx=2)
        
        # ==================== 主控制按钮 ====================
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=1, column=0, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="▶ 开始定制", command=self.start_customization, width=18, style='Accent.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⬛ 停止", command=self.stop_customization, state=tk.DISABLED, width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(control_frame, text="🗑 清空日志", command=self.clear_log, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_log_btn = ttk.Button(control_frame, text="💾 保存日志", command=self.save_log, width=15)
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
        
        self.status_label = ttk.Label(status_frame, text="就绪", foreground="green", font=('Arial', 9, 'bold'))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
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
        ttk.Button(btn_frame, text="保存配置", command=self.save_config, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="重置为默认", command=self.reset_config, width=15).pack(side=tk.LEFT, padx=5)
    
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
        ttk.Button(btn_frame, text="全选", command=self.select_all_modules, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="全不选", command=self.deselect_all_modules, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="推荐配置", command=self.select_recommended, width=12).pack(side=tk.LEFT, padx=5)
    
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
    
    def log(self, message, tag='INFO'):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, full_message, tag)
        self.log_text.see(tk.END)
    
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
        self.progress.start(10)
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
            self.log("[警告] 用户请求停止", 'WARNING')
            self.is_running = False
    
    def run_customization(self):
        """运行定制流程"""
        try:
            # 创建自定义的 Customizer
            customizer = CustomWinPECustomizer(self.winpe_dir.get(), self.output_queue)
            
            # 运行
            exit_code = customizer.run()
            
            if exit_code == 0:
                self.output_queue.put(('SUCCESS', '[完成] WinPE 定制流程全部完成！'))
                self.root.after(0, lambda: self.status_label.config(text="完成", foreground="green"))
            else:
                self.output_queue.put(('ERROR', '[失败] WinPE 定制流程未完成'))
                self.root.after(0, lambda: self.status_label.config(text="失败", foreground="red"))
                
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
        self.progress.stop()
    
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
    
    def __init__(self, winpe_dir, output_queue):
        super().__init__(winpe_dir)
        self.output_queue = output_queue
    
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


def main():
    """主函数"""
    root = tk.Tk()
    app = WinPECustomizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

