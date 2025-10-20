#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WinPE USB 启动盘制作工具
"""

import os
import sys
import subprocess
import string
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue


class USBMakerDialog:
    """USB 制作对话框"""
    
    def __init__(self, parent, winpe_dir):
        self.winpe_dir = Path(winpe_dir)
        self.selected_drive = None
        self.is_running = False
        self.output_queue = queue.Queue()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("制作 WinPE USB 启动盘")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置图标
        self.set_icon()
        
        self.create_widgets()
        self.scan_drives()
        self.monitor_output()
    
    def set_icon(self):
        """设置图标"""
        import random
        ico_dir = Path("ico")
        if ico_dir.exists():
            ico_files = list(ico_dir.glob("*.ico"))
            if ico_files:
                try:
                    self.dialog.iconbitmap(str(random.choice(ico_files)))
                except:
                    pass
    
    def create_widgets(self):
        """创建界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 警告提示
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 15))
        
        warning_label = ttk.Label(
            warning_frame,
            text="⚠️ 警告：制作启动盘将格式化U盘，所有数据将丢失！",
            foreground="red",
            font=('Arial', 10, 'bold')
        )
        warning_label.pack()
        
        # 驱动器选择
        drive_frame = ttk.LabelFrame(main_frame, text="选择U盘驱动器", padding="10")
        drive_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 驱动器列表
        columns = ('drive', 'label', 'size', 'type')
        self.drive_tree = ttk.Treeview(drive_frame, columns=columns, show='headings', height=6)
        
        self.drive_tree.heading('drive', text='盘符')
        self.drive_tree.heading('label', text='卷标')
        self.drive_tree.heading('size', text='大小')
        self.drive_tree.heading('type', text='类型')
        
        self.drive_tree.column('drive', width=60, anchor=tk.CENTER)
        self.drive_tree.column('label', width=150)
        self.drive_tree.column('size', width=100, anchor=tk.CENTER)
        self.drive_tree.column('type', width=150)
        
        self.drive_tree.pack(fill=tk.BOTH, expand=True)
        
        # 刷新按钮
        ttk.Button(drive_frame, text="🔄 刷新列表", command=self.scan_drives).pack(pady=5)
        
        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="制作选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.format_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="格式化U盘（FAT32）", variable=self.format_var).pack(anchor=tk.W, pady=2)
        
        self.bootable_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="设置为可启动", variable=self.bootable_var).pack(anchor=tk.W, pady=2)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="制作进度", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.pack(anchor=tk.W, pady=2)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # 日志
        from tkinter import scrolledtext
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(10, 0))
        
        self.make_btn = ttk.Button(btn_frame, text="▶ 开始制作", command=self.start_make, width=15)
        self.make_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def scan_drives(self):
        """扫描可移动驱动器"""
        self.drive_tree.delete(*self.drive_tree.get_children())
        
        try:
            # 获取所有驱动器
            drives = self.get_removable_drives()
            
            if not drives:
                self.log("未检测到可移动驱动器")
                return
            
            for drive_info in drives:
                self.drive_tree.insert('', tk.END, values=(
                    drive_info['drive'],
                    drive_info['label'],
                    drive_info['size'],
                    drive_info['type']
                ))
        except Exception as e:
            self.log(f"扫描驱动器失败: {e}")
    
    def get_removable_drives(self):
        """获取可移动驱动器列表"""
        drives = []
        
        try:
            # 使用 wmic 获取驱动器信息
            cmd = 'wmic logicaldisk get deviceid,volumename,size,drivetype /format:csv'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            for line in result.stdout.split('\n'):
                if not line.strip() or 'DeviceID' in line:
                    continue
                
                parts = line.split(',')
                if len(parts) >= 4:
                    try:
                        drive_type = parts[2].strip()
                        device_id = parts[1].strip()
                        size = parts[3].strip()
                        volume_name = parts[4].strip() if len(parts) > 4 else ""
                        
                        # DriveType: 2=可移动, 3=本地磁盘
                        if drive_type == '2':  # 可移动驱动器
                            size_gb = int(size) / (1024**3) if size else 0
                            drives.append({
                                'drive': device_id,
                                'label': volume_name or "(无标签)",
                                'size': f"{size_gb:.2f} GB" if size_gb > 0 else "未知",
                                'type': "可移动磁盘"
                            })
                    except:
                        continue
        except Exception as e:
            self.log(f"获取驱动器列表失败: {e}")
        
        return drives
    
    def start_make(self):
        """开始制作"""
        selection = self.drive_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个U盘驱动器")
            return
        
        item = self.drive_tree.item(selection[0])
        drive_letter = item['values'][0]
        
        # 确认
        msg = f"确定要制作 WinPE USB 启动盘吗？\n\n"
        msg += f"目标驱动器: {drive_letter}\n"
        msg += f"WinPE 目录: {self.winpe_dir}\n\n"
        msg += "⚠️ 警告：该驱动器上的所有数据将被删除！"
        
        if not messagebox.askyesno("确认", msg, icon='warning'):
            return
        
        self.selected_drive = drive_letter
        self.make_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_label.config(text="正在制作...")
        
        # 后台执行
        thread = threading.Thread(target=self.make_usb)
        thread.daemon = True
        thread.start()
    
    def make_usb(self):
        """制作USB启动盘"""
        try:
            self.log("=" * 50)
            self.log("开始制作 WinPE USB 启动盘")
            self.log("=" * 50)
            
            # 步骤1: 格式化（如果选择）
            if self.format_var.get():
                self.log("\n[步骤 1/3] 格式化U盘...")
                self.output_queue.put(('status', '正在格式化...'))
                
                # 使用 MakeWinPEMedia 的格式化功能
                cmd = f'MakeWinPEMedia /UFD "{self.winpe_dir}" {self.selected_drive}'
                
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
                    startupinfo=startupinfo
                )
                
                for line in process.stdout:
                    self.log(line.rstrip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log("✅ 格式化完成")
                else:
                    self.log("❌ 格式化失败")
                    self.output_queue.put(('finish', False))
                    return
            
            self.log("\n✅ USB 启动盘制作完成！")
            self.output_queue.put(('status', '完成'))
            self.output_queue.put(('finish', True))
            
        except Exception as e:
            self.log(f"❌ 错误: {e}")
            self.output_queue.put(('finish', False))
    
    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def monitor_output(self):
        """监控输出"""
        try:
            while True:
                msg_type, msg_data = self.output_queue.get_nowait()
                
                if msg_type == 'status':
                    self.status_label.config(text=msg_data)
                elif msg_type == 'finish':
                    self.progress.stop()
                    self.make_btn.config(state=tk.NORMAL)
                    if msg_data:
                        messagebox.showinfo("成功", "USB 启动盘制作完成！")
                    else:
                        messagebox.showerror("失败", "USB 启动盘制作失败！")
        except queue.Empty:
            pass
        
        self.dialog.after(100, self.monitor_output)


def show_usb_maker_dialog(parent, winpe_dir):
    """显示USB制作对话框"""
    USBMakerDialog(parent, winpe_dir)


if __name__ == "__main__":
    # 测试
    root = tk.Tk()
    root.withdraw()
    
    winpe_dir = sys.argv[1] if len(sys.argv) > 1 else "D:/WinPE_amd64"
    show_usb_maker_dialog(root, winpe_dir)
    
    root.mainloop()

