#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具下载对话框
"""

import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import urllib.request
import zipfile


class DownloadDialog:
    """下载对话框"""
    
    def __init__(self, parent, tools):
        self.tools = tools
        self.current_index = 0
        self.is_downloading = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("下载工具")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # 自动开始下载
        self.start_download()
    
    def create_widgets(self):
        """创建界面"""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 当前工具
        info_frame = ttk.LabelFrame(frame, text="下载信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.tool_label = ttk.Label(info_frame, text="准备下载...", font=('Arial', 10, 'bold'))
        self.tool_label.pack(anchor=tk.W)
        
        self.url_label = ttk.Label(info_frame, text="", foreground="gray", font=('Arial', 8))
        self.url_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 进度
        progress_frame = ttk.LabelFrame(frame, text="下载进度", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, text="等待开始...")
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.percent_label = ttk.Label(progress_frame, text="0%")
        self.percent_label.pack(anchor=tk.W)
        
        # 日志
        log_frame = ttk.LabelFrame(frame, text="下载日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        
        self.close_btn = ttk.Button(btn_frame, text="关闭", command=self.dialog.destroy, 
                                    state=tk.DISABLED, width=15)
        self.close_btn.pack(pady=5)
    
    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def start_download(self):
        """开始下载"""
        self.log("=" * 50)
        self.log(f"准备下载 {len(self.tools)} 个工具")
        self.log("=" * 50)
        
        thread = threading.Thread(target=self.download_all)
        thread.daemon = True
        thread.start()
    
    def download_all(self):
        """下载所有工具"""
        for i, tool in enumerate(self.tools, 1):
            self.current_index = i
            self.download_tool(tool, i, len(self.tools))
        
        self.dialog.after(0, lambda: self.close_btn.config(state=tk.NORMAL))
        self.dialog.after(0, lambda: messagebox.showinfo("完成", "所有工具下载完成！"))
    
    def download_tool(self, tool, index, total):
        """下载单个工具"""
        self.dialog.after(0, lambda: self.tool_label.config(text=f"[{index}/{total}] {tool['name']}"))
        self.dialog.after(0, lambda: self.url_label.config(text=tool.get('download_url', tool['url'])))
        
        self.log(f"\n[{index}/{total}] 开始下载: {tool['name']}")
        
        # 检查是否有直接下载链接
        if 'download_url' not in tool or not tool['download_url']:
            self.log(f"  ⚠️ {tool['name']} 暂不支持自动下载")
            self.log(f"  请访问: {tool['url']}")
            self.dialog.after(0, lambda: self.status_label.config(text="跳过（无下载链接）"))
            return
        
        try:
            # 创建保存目录
            external_dir = Path("../外置程序") if Path("../外置程序").exists() else Path("外置程序")
            tool_dir = external_dir / "Tools" / tool['name']
            tool_dir.mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            download_url = tool['download_url']
            filename = Path(download_url).name
            save_path = tool_dir / filename
            
            self.log(f"  下载链接: {download_url}")
            self.log(f"  保存到: {save_path}")
            
            self.dialog.after(0, lambda: self.status_label.config(text="正在下载..."))
            
            # 下载进度回调
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = int((block_num * block_size / total_size) * 100)
                    if percent > 100:
                        percent = 100
                    self.dialog.after(0, lambda: self.progress['value'] = percent)
                    self.dialog.after(0, lambda: self.percent_label.config(text=f"{percent}%"))
            
            urllib.request.urlretrieve(download_url, save_path, progress_hook)
            
            self.log(f"  ✅ 下载完成: {save_path.name}")
            
            # 如果是压缩包，尝试解压
            if save_path.suffix.lower() in ['.zip', '.7z', '.rar']:
                self.log(f"  📦 检测到压缩包，准备解压...")
                self.dialog.after(0, lambda: self.status_label.config(text="正在解压..."))
                
                if save_path.suffix.lower() == '.zip':
                    with zipfile.ZipFile(save_path, 'r') as zip_ref:
                        zip_ref.extractall(tool_dir)
                    self.log(f"  ✅ 解压完成")
                    save_path.unlink()  # 删除压缩包
                else:
                    self.log(f"  ⚠️ {save_path.suffix} 格式需要手动解压")
            
            self.dialog.after(0, lambda: self.status_label.config(text="完成"))
            
        except Exception as e:
            self.log(f"  ❌ 下载失败: {e}")
            self.dialog.after(0, lambda: self.status_label.config(text=f"失败: {e}"))


class DownloadDialogWrapper:
    """下载对话框包装器（从winpe_tools_manager调用）"""
    pass

