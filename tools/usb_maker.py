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
import ctypes

# 导入扫描功能
sys.path.append(os.path.join(os.path.dirname(__file__)))
try:
    import scan_drives
    HAS_SCAN_DRIVES = True
except ImportError:
    HAS_SCAN_DRIVES = False
    print("警告: 无法导入scan_drives模块")

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("警告: 未安装 psutil，将使用备用检测方法")


class USBMakerDialog:
    """USB 制作对话框"""
    
    def __init__(self, parent, winpe_dir):
        self.winpe_dir = Path(winpe_dir)
        self.selected_drive = None
        self.is_running = False
        self.output_queue = queue.Queue()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("制作 WinPE USB 启动盘")
        self.dialog.geometry("600x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 窗口居中
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"600x600+{x}+{y}")
        
        # 设置图标
        self.set_icon()
        
        # 检查管理员权限
        self.check_admin_rights()
        
        self.create_widgets()
        # 先加载窗口，然后异步扫描驱动器
        self.dialog.after(100, self.scan_drives_async)
        self.monitor_output()
    
    def check_admin_rights(self):
        """检查是否有管理员权限"""
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                # 创建一个置顶的对话框
                admin_dialog = tk.Toplevel(self.dialog)
                admin_dialog.title("管理员权限")
                admin_dialog.geometry("450x200")
                admin_dialog.resizable(False, False)
                
                # 设置为最顶层窗口
                admin_dialog.attributes('-topmost', True)
                admin_dialog.lift()
                admin_dialog.focus_force()
                
                # 居中显示
                admin_dialog.update_idletasks()
                x = (admin_dialog.winfo_screenwidth() // 2) - (450 // 2)
                y = (admin_dialog.winfo_screenheight() // 2) - (200 // 2)
                admin_dialog.geometry(f"+{x}+{y}")
                
                # 内容
                main_frame = ttk.Frame(admin_dialog, padding="20")
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # 警告图标和文字
                ttk.Label(main_frame, 
                         text="⚠️ 需要管理员权限", 
                         font=('Arial', 12, 'bold'),
                         foreground='orange').pack(pady=(0, 10))
                
                ttk.Label(main_frame, 
                         text="制作USB启动盘需要管理员权限。\n\n是否以管理员身份重新运行程序？",
                         justify=tk.CENTER).pack(pady=(0, 20))
                
                # 按钮
                btn_frame = ttk.Frame(main_frame)
                btn_frame.pack()
                
                result = {'value': None}
                
                def on_yes():
                    result['value'] = True
                    admin_dialog.update()  # 立即更新
                    admin_dialog.destroy()  # 销毁窗口
                
                def on_no():
                    result['value'] = False
                    admin_dialog.update()  # 立即更新
                    admin_dialog.destroy()  # 销毁窗口
                
                ttk.Button(btn_frame, text="✅ 是，以管理员运行", 
                          command=on_yes, width=20).pack(side=tk.LEFT, padx=5)
                ttk.Button(btn_frame, text="❌ 否，继续当前权限", 
                          command=on_no, width=20).pack(side=tk.LEFT, padx=5)
                
                # 等待用户选择
                admin_dialog.wait_window()
                
                if result['value'] is True:
                    # 以管理员身份重新运行
                    self.run_as_admin()
                    self.dialog.destroy()
                    sys.exit(0)
                elif result['value'] is False:
                    # 显示警告
                    warning_dialog = tk.Toplevel(self.dialog)
                    warning_dialog.title("警告")
                    warning_dialog.geometry("400x150")
                    warning_dialog.resizable(False, False)
                    warning_dialog.attributes('-topmost', True)
                    
                    # 居中
                    warning_dialog.update_idletasks()
                    x = (warning_dialog.winfo_screenwidth() // 2) - (400 // 2)
                    y = (warning_dialog.winfo_screenheight() // 2) - (150 // 2)
                    warning_dialog.geometry(f"+{x}+{y}")
                    
                    frame = ttk.Frame(warning_dialog, padding="20")
                    frame.pack(fill=tk.BOTH, expand=True)
                    
                    ttk.Label(frame, 
                             text="⚠️ 没有管理员权限可能导致USB制作失败！",
                             font=('Arial', 10),
                             foreground='red').pack(pady=(0, 10))
                    
                    ttk.Button(frame, text="我知道了", 
                              command=warning_dialog.destroy, width=15).pack()
                    
                    warning_dialog.wait_window()
                    
        except Exception as e:
            print(f"检查管理员权限失败: {e}")
    
    def run_as_admin(self):
        """以管理员身份重新运行"""
        try:
            if sys.argv and sys.argv[0]:
                script = os.path.abspath(sys.argv[0])
                params = ' '.join([script] + sys.argv[1:])
                
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable,
                    params,
                    None,
                    1
                )
        except Exception as e:
            messagebox.showerror("错误", f"无法以管理员身份运行: {e}")
    
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
        self.drive_tree = ttk.Treeview(drive_frame, columns=columns, show='headings', height=3)
        
        self.drive_tree.heading('drive', text='盘符')
        self.drive_tree.heading('label', text='卷标')
        self.drive_tree.heading('size', text='大小')
        self.drive_tree.heading('type', text='类型')
        
        self.drive_tree.column('drive', width=60, anchor=tk.CENTER)
        self.drive_tree.column('label', width=150)
        self.drive_tree.column('size', width=100, anchor=tk.CENTER)
        self.drive_tree.column('type', width=150)
        
        self.drive_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="制作选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 分区方案和文件系统（一行）
        scheme_fs_frame = ttk.Frame(options_frame)
        scheme_fs_frame.pack(fill=tk.X, pady=2)
        
        # 分区方案
        ttk.Label(scheme_fs_frame, text="分区方案:").pack(side=tk.LEFT, padx=(0, 5))
        self.partition_scheme = tk.StringVar(value="mbr")
        ttk.Radiobutton(scheme_fs_frame, text="MBR (BIOS)", variable=self.partition_scheme, value="mbr").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(scheme_fs_frame, text="GPT (UEFI)", variable=self.partition_scheme, value="gpt").pack(side=tk.LEFT, padx=2)
        
        # 分隔
        ttk.Separator(scheme_fs_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 文件系统
        ttk.Label(scheme_fs_frame, text="文件系统:").pack(side=tk.LEFT, padx=(0, 5))
        self.filesystem = tk.StringVar(value="ntfs")
        ttk.Radiobutton(scheme_fs_frame, text="FAT32 (兼容)", variable=self.filesystem, value="fat32").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(scheme_fs_frame, text="NTFS (大文件)", variable=self.filesystem, value="ntfs").pack(side=tk.LEFT, padx=2)
        
        # 其他选项（一行）
        check_frame = ttk.Frame(options_frame)
        check_frame.pack(fill=tk.X, pady=2)
        
        self.format_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="清除所有分区并重新分区", variable=self.format_var).pack(side=tk.LEFT, padx=(0, 20))
        
        self.bootable_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(check_frame, text="设置启动引导", variable=self.bootable_var).pack(side=tk.LEFT, padx=(0, 20))
        
        # 制作方法下拉框（放在第二行）
        ttk.Label(check_frame, text="制作方法:").pack(side=tk.LEFT, padx=(0, 5))
        self.make_method = tk.StringVar(value="手动分区")
        make_method_combo = ttk.Combobox(check_frame, textvariable=self.make_method, 
                                        values=["手动分区", "MakeWinPEMedia"], state="readonly", width=15)
        make_method_combo.pack(side=tk.LEFT, padx=2)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="制作进度", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 状态和进度条（一行）
        status_progress_frame = ttk.Frame(progress_frame)
        status_progress_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(status_progress_frame, text="就绪", width=12)
        self.status_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.progress = ttk.Progressbar(status_progress_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 日志
        from tkinter import scrolledtext
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(10, 0))
        
        self.make_btn = ttk.Button(btn_frame, text="▶ 开始制作", command=self.start_make, width=15)
        self.make_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(btn_frame, text="🔄 刷新U盘", command=self.scan_drives, width=15)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def scan_drives_async(self):
        """异步扫描可移动驱动器（按照tusb.py方法实现）"""
        # 先清空列表
        self.drive_tree.delete(*self.drive_tree.get_children())
        self.log("开始扫描驱动器...")
        self.status_label.config(text="正在扫描驱动器...")
        self.progress.start(10)
        
        # 在后台线程中执行扫描
        thread = threading.Thread(target=self._scan_drives_background)
        thread.daemon = True
        thread.start()
    
    def _scan_drives_background(self):
        """后台扫描驱动器"""
        try:
            # 获取所有驱动器
            drives = self.get_removable_drives()
            
            # 在主线程中更新UI
            self.dialog.after(0, lambda: self._update_drive_list(drives))
        except Exception as e:
            self.dialog.after(0, lambda: self.log(f"扫描驱动器失败: {e}"))
            import traceback
            self.dialog.after(0, lambda: self.log(traceback.format_exc()))
    
    def _update_drive_list(self, drives):
        """更新驱动器列表"""
        self.progress.stop()
        self.status_label.config(text="扫描完成")
        self.log(f"返回了 {len(drives)} 个驱动器")
        
        if not drives:
            self.log("未检测到驱动器")
            return
        
        for drive_info in drives:
            self.log(f"添加: {drive_info['drive']} - {drive_info['type']}")
            self.drive_tree.insert('', tk.END, values=(
                drive_info['drive'],
                drive_info['label'],
                drive_info['size'],
                drive_info['type']
            ))
        
        self.log(f"列表添加完成")
    
    def scan_drives(self):
        """扫描可移动驱动器（按照tusb.py方法实现）"""
        # 保持原有接口不变，但实际调用异步方法
        self.scan_drives_async()
    
    def get_removable_drives(self):
        """获取所有驱动器列表（仅显示USB驱动器，按照tusb.py方法实现）"""
        drives = []
        
        # 优先尝试使用tools/scan_drives.py中的函数
        try:
            # 导入scan_drives模块
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__)))
            import scan_drives
            self.log("使用tools/scan_drives.py中的get_removable_drives函数")
            return scan_drives.get_removable_drives()
        except ImportError as e:
            self.log(f"无法导入scan_drives模块，使用内置实现: {e}")
            pass
        
        try:
            # 使用 PowerShell Get-Disk 获取USB磁盘（更可靠的方法）
            ps_cmd = '''
            [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
            Get-Disk | Where-Object {$_.BusType -eq 'USB'} | ForEach-Object {
                $disk = $_
                $partitions = Get-Partition -DiskNumber $disk.Number | Where-Object {$_.DriveLetter}
                foreach ($partition in $partitions) {
                    $volume = Get-Volume -DriveLetter $partition.DriveLetter
                    $sizeGB = [math]::Round($volume.Size / 1GB, 2)
                    $label = $volume.FileSystemLabel
                    if (!$label) { $label = "(无标签)" }
                    "$($partition.DriveLetter):,$label,$sizeGB,USB闪存盘"
                }
            }
            '''
            
            result = subprocess.run(['powershell', '-Command', ps_cmd],
                                  capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
            
            lines = result.stdout.strip().split('\n')
            self.log(f"PowerShell返回了 {len(lines)} 行数据")
            
            # 处理USB驱动器
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                
                self.log(f"  行{i}: {line[:50]}...")
                parts = line.split(',')
                if len(parts) >= 4:
                    try:
                        device_id = parts[0].strip()
                        volume_name = parts[1].strip()
                        size_gb = parts[2].strip()
                        device_type = parts[3].strip()
                        
                        # 只处理USB驱动器
                        if device_type == "USB闪存盘":
                            drives.append({
                                'drive': device_id,
                                'label': volume_name,
                                'size': f"{size_gb} GB",
                                'type': device_type
                            })
                            self.log(f"  添加USB驱动器: {device_id} - {volume_name} ({size_gb} GB)")
                            
                    except Exception as e:
                        self.log(f"解析USB驱动器信息失败: {e}")
                        continue
                            
        except Exception as e:
            self.log(f"获取驱动器列表失败: {e}")
            import traceback
            self.log(traceback.format_exc())
        
        self.log(f"get_removable_drives() 最终返回 {len(drives)} 个驱动器")
        return drives
    
    def get_usb_disk_numbers(self):
        """获取所有USB物理磁盘编号"""
        usb_disks = set()
        try:
            # 使用PowerShell Get-Disk 获取USB磁盘（更可靠的方法）
            ps_cmd = '''
            [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
            Get-Disk | Where-Object {$_.BusType -eq 'USB'} | ForEach-Object {
                "$($_.Number),$($_.FriendlyName),$($_.Size)"
            }
            '''
            
            result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                  capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
            
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split(',')
                if len(parts) >= 1:
                    try:
                        disk_number = parts[0].strip()
                        friendly_name = parts[1].strip() if len(parts) > 1 else ''
                        size = parts[2].strip() if len(parts) > 2 else ''
                        
                        if disk_number.isdigit():
                            usb_disks.add(int(disk_number))
                            size_gb = int(size) / (1024**3) if size.isdigit() else 0
                            self.log(f"  发现USB磁盘: Disk {disk_number} - {friendly_name} ({size_gb:.1f} GB)")
                    except:
                        continue
        except Exception as e:
            self.log(f"获取USB磁盘编号失败: {e}")
        
        return usb_disks
    
    def get_volume_label(self, drive_letter):
        """获取卷标"""
        try:
            drive_letter = drive_letter.replace(':', '')
            ps_cmd = f'[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; (Get-WmiObject -Class Win32_LogicalDisk | Where-Object {{$_.DeviceID -eq "{drive_letter}:"}}).VolumeName'
            result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                  capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
            
            label = result.stdout.strip()
            return label if label else "(无标签)"
        except:
            pass
        
        return "(无标签)"
    
    def get_partition_disk_number(self, drive_letter):
        """获取分区所在的物理磁盘编号"""
        try:
            drive_letter = drive_letter.replace(':', '')
            ps_cmd = f'Get-Partition -DriveLetter {drive_letter} | Select-Object -ExpandProperty DiskNumber'
            result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                  capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
            
            output = result.stdout.strip()
            if output.isdigit():
                return int(output)
        except:
            pass
        
        return -1
    
    def start_make(self):
        """开始制作"""
        selection = self.drive_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个U盘驱动器")
            return
        
        item = self.drive_tree.item(selection[0])
        drive_letter = item['values'][0]
        drive_label = item['values'][1]
        drive_size = item['values'][2]
        
        # 获取U盘目录信息
        drive_path = Path(f"{drive_letter}:")
        directory_info = self.get_drive_directory_info(drive_path)
        
        # 创建详细警告对话框
        self.show_warning_dialog(drive_letter, drive_label, drive_size, directory_info)
    
    def get_drive_directory_info(self, drive_path):
        """获取驱动器目录信息"""
        try:
            if not drive_path.exists():
                return "驱动器不存在"
            
            # 获取目录列表
            directories = []
            files = []
            
            for item in drive_path.iterdir():
                if item.is_dir():
                    directories.append(item.name)
                else:
                    files.append(item.name)
            
            # 限制显示数量
            if len(directories) > 10:
                directories = directories[:10] + [f"... 还有 {len(directories) - 10} 个目录"]
            if len(files) > 10:
                files = files[:10] + [f"... 还有 {len(files) - 10} 个文件"]
            
            return {
                'directories': directories,
                'files': files,
                'total_dirs': len([d for d in drive_path.iterdir() if d.is_dir()]),
                'total_files': len([f for f in drive_path.iterdir() if f.is_file()])
            }
        except Exception as e:
            return f"无法读取目录信息: {e}"
    
    def show_warning_dialog(self, drive_letter, drive_label, drive_size, directory_info):
        """显示详细警告对话框"""
        warning_dialog = tk.Toplevel(self.dialog)
        warning_dialog.title("⚠️ 制作警告")
        warning_dialog.geometry("500x400")
        warning_dialog.transient(self.dialog)
        warning_dialog.grab_set()
        
        # 窗口居中
        warning_dialog.update_idletasks()
        x = (warning_dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (warning_dialog.winfo_screenheight() // 2) - (400 // 2)
        warning_dialog.geometry(f"500x400+{x}+{y}")
        
        # 主框架
        main_frame = ttk.Frame(warning_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 警告标题
        ttk.Label(main_frame, text="⚠️ 制作 WinPE USB 启动盘", 
                 font=('Arial', 14, 'bold'), foreground='red').pack(pady=(0, 10))
        
        # 驱动器信息
        info_frame = ttk.LabelFrame(main_frame, text="目标驱动器信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"驱动器: {drive_letter}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"标签: {drive_label}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"大小: {drive_size}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"WinPE目录: {self.winpe_dir}").pack(anchor=tk.W)
        
        # 目录信息
        if isinstance(directory_info, dict):
            dir_frame = ttk.LabelFrame(main_frame, text="当前驱动器内容", padding="10")
            dir_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 创建滚动文本框
            text_frame = ttk.Frame(dir_frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, height=8, wrap=tk.WORD)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 显示目录信息
            content = f"目录数量: {directory_info['total_dirs']}\n"
            content += f"文件数量: {directory_info['total_files']}\n\n"
            
            if directory_info['directories']:
                content += "目录列表:\n"
                for dir_name in directory_info['directories']:
                    content += f"  📁 {dir_name}\n"
            
            if directory_info['files']:
                content += "\n文件列表:\n"
                for file_name in directory_info['files']:
                    content += f"  📄 {file_name}\n"
            
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
        else:
            ttk.Label(main_frame, text=f"目录信息: {directory_info}").pack(anchor=tk.W)
        
        # 警告信息
        warning_frame = ttk.LabelFrame(main_frame, text="⚠️ 重要警告", padding="10")
        warning_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(warning_frame, text="该驱动器上的所有数据将被永久删除！", 
                 font=('Arial', 10, 'bold'), foreground='red').pack()
        ttk.Label(warning_frame, text="请确保已备份重要数据。", 
                 foreground='orange').pack()
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="✅ 确认制作", 
                  command=lambda: self.confirm_make(drive_letter, warning_dialog), 
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ 取消", 
                  command=warning_dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
    
    def confirm_make(self, drive_letter, warning_dialog):
        """确认制作"""
        warning_dialog.destroy()
        
        self.selected_drive = drive_letter
        self.make_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_label.config(text="正在制作...")
        
        # 根据选择的制作方法执行不同的流程
        make_method = self.make_method.get()
        self.log("=" * 50)
        self.log(f"用户选择的制作方法: [{make_method}]")
        self.log(f"字符串长度: {len(make_method)}")
        self.log(f"是否等于'MakeWinPEMedia': {make_method == 'MakeWinPEMedia'}")
        self.log(f"是否等于'手动分区': {make_method == '手动分区'}")
        self.log("=" * 50)
        
        if make_method == "MakeWinPEMedia":
            # 使用MakeWinPEMedia
            thread = threading.Thread(target=self.make_usb_with_makewinpe)
            thread.daemon = True
            thread.start()
        else:
            # 手动分区方法
            thread = threading.Thread(target=self.make_usb)
            thread.daemon = True
            thread.start()
    
    def make_usb_with_makewinpe(self):
        """使用MakeWinPEMedia制作USB启动盘（ADK标准方法）"""
        try:
            self.log("=" * 50)
            self.log("使用 MakeWinPEMedia 制作 USB 启动盘")
            self.log("=" * 50)
            
            drive_letter = self.selected_drive.replace(':', '')
            
            # 检查WIM是否已挂载
            self.log("\n[步骤 1/3] 检查 WIM 挂载状态...")
            mount_dir = self.winpe_dir / "mount"
            if mount_dir.exists():
                # 检查是否有挂载
                check_cmd = f'dism /get-mountedwiminfo'
                result = subprocess.run(check_cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='ignore')
                
                if "mount" in result.stdout.lower() or str(mount_dir) in result.stdout:
                    self.log("  ⚠️ 检测到 WIM 已挂载，正在卸载...")
                    
                    # 卸载WIM
                    unmount_cmd = f'dism /unmount-wim /mountdir:"{mount_dir}" /discard'
                    unmount_result = subprocess.run(unmount_cmd, capture_output=True, text=True, shell=True, encoding='utf-8', errors='ignore')
                    
                    if unmount_result.returncode == 0:
                        self.log("  ✅ WIM 卸载成功")
                    else:
                        self.log("  ⚠️ WIM 卸载失败，尝试继续...")
                        self.log(f"  {unmount_result.stdout}")
                else:
                    self.log("  ✅ 未检测到挂载的 WIM")
            else:
                self.log("  ✅ mount 目录不存在，无需检查")
            
            # 检查MakeWinPEMedia是否可用
            self.log("\n[步骤 2/3] 检查 MakeWinPEMedia 工具...")
            
            # 多个可能的MakeWinPEMedia位置
            possible_paths = [
                Path("C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit/Windows Preinstallation Environment/MakeWinPEMedia.cmd"),
                Path("C:/Program Files/Windows Kits/10/Assessment and Deployment Kit/Windows Preinstallation Environment/MakeWinPEMedia.cmd"),
            ]
            
            makewinpe_path = None
            for path in possible_paths:
                if path.exists():
                    makewinpe_path = path
                    self.log(f"  找到 MakeWinPEMedia: {path}")
                    break
            
            if not makewinpe_path:
                self.log("❌ 未找到 MakeWinPEMedia.cmd")
                self.log("  请确保已安装 Windows ADK")
                self.log("  下载地址: https://learn.microsoft.com/windows-hardware/get-started/adk-install")
                self.output_queue.put(('finish', False))
                return
            
            # 关闭可能打开的资源管理器窗口
            self.log(f"\n  尝试关闭 {drive_letter}: 的资源管理器窗口...")
            try:
                # 使用PowerShell关闭资源管理器窗口
                close_cmd = f'''
                $shell = New-Object -ComObject Shell.Application
                $shell.Windows() | Where-Object {{ $_.LocationURL -like "*{drive_letter}:*" }} | ForEach-Object {{ $_.Quit() }}
                '''
                subprocess.run(['powershell', '-Command', close_cmd], capture_output=True, timeout=5)
                self.log(f"  已尝试关闭资源管理器")
            except:
                pass
            
            # 预处理：清空分区表并转换为MBR
            self.log("\n[步骤 3/5] 预处理磁盘...")
            partition_scheme = self.partition_scheme.get()
            
            # 获取磁盘编号
            disk_num = self.get_disk_number(drive_letter)
            if disk_num is None:
                self.log("❌ 无法获取磁盘编号")
                self.output_queue.put(('finish', False))
                return
            
            self.log(f"  磁盘编号: {disk_num}")
            self.log(f"  分区方案: {partition_scheme.upper()}")
            
            # 生成预处理diskpart脚本
            # MakeWinPEMedia需要一个已存在的盘符，所以clean后要创建分区并分配盘符
            # 限制分区大小为16GB，避免占用整个大容量移动硬盘
            if partition_scheme == "mbr":
                pre_script = f"""select disk {disk_num}
clean
convert mbr
create partition primary size=16000
select partition 1
active
format fs=fat32 quick label=WINPE
assign letter={drive_letter}
exit
"""
            else:  # GPT
                pre_script = f"""select disk {disk_num}
clean
convert gpt
create partition primary size=16000
select partition 1
format fs=fat32 quick label=WINPE
assign letter={drive_letter}
exit
"""
            
            # 写入临时脚本文件
            script_path = Path("temp_diskpart_pre.txt")
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(pre_script)
            
            self.log(f"  执行: clean + convert {partition_scheme}")
            
            # 执行diskpart预处理
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                ['diskpart', '/s', str(script_path)],
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
            
            # 清理临时文件
            if script_path.exists():
                script_path.unlink()
            
            if process.returncode == 0:
                self.log("✅ 磁盘预处理成功")
            else:
                self.log("❌ 磁盘预处理失败")
                self.output_queue.put(('finish', False))
                return
            
            # 执行MakeWinPEMedia命令
            self.log("\n[步骤 5/5] 制作 USB 启动盘...")
            self.output_queue.put(('status', '正在使用 MakeWinPEMedia 制作...'))
            
            # 自动回答Y确认格式化
            cmd = f'echo Y | "{makewinpe_path}" /ufd "{self.winpe_dir}" {drive_letter}:'
            self.log(f"  命令: MakeWinPEMedia /ufd \"{self.winpe_dir}\" {drive_letter}:")
            self.log(f"  警告: 此操作会格式化 {drive_letter}: 驱动器")
            self.log(f"  提示: 如果失败，请关闭 {drive_letter}: 的所有窗口和程序")
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                shell=True,
                startupinfo=startupinfo
            )
            
            # 实时输出日志
            for line in process.stdout:
                if line.strip():
                    self.log(f"  {line.rstrip()}")
            
            process.wait()
            
            if process.returncode == 0:
                self.log("\n✅ USB 启动盘制作完成！")
                self.output_queue.put(('status', '完成'))
                self.output_queue.put(('finish', True))
            else:
                self.log("\n❌ USB 启动盘制作失败！")
                self.log(f"  返回码: {process.returncode}")
                self.output_queue.put(('finish', False))
                
        except Exception as e:
            self.log(f"❌ 错误: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.output_queue.put(('finish', False))
    
    def make_usb(self):
        """制作USB启动盘（手动分区方法）"""
        try:
            self.log("=" * 50)
            self.log("开始制作 WinPE USB 启动盘")
            self.log("=" * 50)
            
            # 步骤1: 分区和格式化U盘
            self.log("\n[步骤 1/3] 分区和格式化U盘...")
            self.output_queue.put(('status', '正在分区和格式化...'))
            
            # 获取选项
            drive_letter = self.selected_drive.replace(':', '')
            disk_num = self.get_disk_number(drive_letter)
            partition_scheme = self.partition_scheme.get()
            filesystem = self.filesystem.get()
            
            self.log(f"  磁盘编号: {disk_num}")
            self.log(f"  分区方案: {partition_scheme.upper()}")
            self.log(f"  文件系统: {filesystem.upper()}")
            
            # 生成diskpart脚本
            if partition_scheme == "gpt":
                # GPT分区方案 (UEFI) - 双分区：ESP(FAT32) + 主分区(NTFS)
                diskpart_script = f"""select disk {disk_num}
clean
convert gpt
create partition efi size=300
format fs=fat32 quick label="EFI"
assign letter=S
create partition primary
format fs=ntfs quick label="WinPE"
assign
exit
"""
            else:
                # MBR分区方案 (BIOS) - 双分区：启动分区(FAT32) + 数据分区(NTFS)
                diskpart_script = f"""select disk {disk_num}
clean
convert mbr
create partition primary size=500
select partition 1
active
format fs=fat32 quick label="BOOT"
assign letter=S
create partition primary
select partition 2
format fs=ntfs quick label="WinPE"
assign
exit
"""
            
            # 写入临时脚本文件
            script_path = Path("temp_diskpart.txt")
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(diskpart_script)
            
            # 执行diskpart命令
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                ['diskpart', '/s', str(script_path)],
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
            
            # 清理临时文件
            if script_path.exists():
                script_path.unlink()
            
            if process.returncode == 0:
                self.log("✅ U盘格式化成功")
            else:
                self.log("❌ 格式化失败")
                self.output_queue.put(('finish', False))
                return
            
            # 步骤2: 复制WinPE文件
            self.log("\n[步骤 2/3] 复制WinPE文件...")
            self.output_queue.put(('status', '正在复制文件...'))
            
            if not self.winpe_dir.exists():
                self.log(f"❌ WinPE目录不存在: {self.winpe_dir}")
                self.output_queue.put(('finish', False))
                return
            
            # 双分区方案：启动文件到FAT32(S:)，主要文件到NTFS(主分区)
            import shutil
            boot_partition = Path("S:")  # FAT32启动分区
            main_partition = Path(f"{drive_letter}:")  # NTFS主分区
            
            # 查找media文件夹
            media_dir = self.winpe_dir / "media"
            if media_dir.exists():
                self.log(f"  找到media目录: {media_dir}")
                
                # 定义启动相关的目录和文件（复制到FAT32）
                boot_items = ['Boot', 'EFI', 'bootmgr', 'bootmgr.efi', 'bootmgfw.efi']
                
                # 复制media目录下的内容
                for item in media_dir.iterdir():
                    try:
                        # 判断是否是启动文件
                        is_boot_item = item.name in boot_items
                        
                        if is_boot_item and boot_partition.exists():
                            # 启动文件复制到FAT32分区
                            if item.is_file():
                                shutil.copy2(item, boot_partition / item.name)
                                self.log(f"  📄 [启动] {item.name} -> S:")
                            elif item.is_dir():
                                dest_dir = boot_partition / item.name
                                shutil.copytree(item, dest_dir, dirs_exist_ok=True)
                                self.log(f"  📁 [启动] {item.name} -> S:")
                        else:
                            # 其他文件复制到NTFS分区
                            if item.is_file():
                                shutil.copy2(item, main_partition / item.name)
                                self.log(f"  📄 {item.name} -> {drive_letter}:")
                            elif item.is_dir():
                                dest_dir = main_partition / item.name
                                shutil.copytree(item, dest_dir, dirs_exist_ok=True)
                                self.log(f"  📁 {item.name} -> {drive_letter}:")
                    except Exception as e:
                        self.log(f"  ⚠️ 复制 {item.name} 失败: {e}")
                        
                # 释放S盘符
                try:
                    remove_letter_script = f"""select volume S
remove
exit
"""
                    script_path = Path("temp_remove_letter.txt")
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(remove_letter_script)
                    subprocess.run(['diskpart', '/s', str(script_path)], 
                                 capture_output=True, shell=True)
                    if script_path.exists():
                        script_path.unlink()
                    self.log(f"  已释放临时盘符 S:")
                except:
                    pass
                    
            else:
                self.log(f"⚠️ 未找到media目录，尝试直接复制WinPE目录内容")
                # 如果没有media目录，直接复制到主分区（跳过mount目录）
                for item in self.winpe_dir.iterdir():
                    # 跳过mount目录和其他不需要的目录
                    if item.name.lower() in ['mount', 'fwfiles']:
                        self.log(f"  ⏭️ 跳过: {item.name}")
                        continue
                    
                    if item.is_file():
                        shutil.copy2(item, main_partition / item.name)
                        self.log(f"  📄 复制文件: {item.name}")
                    elif item.is_dir():
                        dest_dir = main_partition / item.name
                        shutil.copytree(item, dest_dir, dirs_exist_ok=True)
                        self.log(f"  📁 复制目录: {item.name}")
            
            # 步骤3: 设置启动引导
            self.log("\n[步骤 3/3] 设置启动引导...")
            self.output_queue.put(('status', '正在设置启动引导...'))
            # 启动扇区设置在FAT32分区（S:），但先尝试恢复S盘符
            boot_success = self.setup_boot_sector("S" if Path("S:").exists() else drive_letter)
            
            if boot_success:
                self.log("\n✅ USB 启动盘制作完成！")
                self.output_queue.put(('status', '完成'))
                self.output_queue.put(('finish', True))
            else:
                self.log("\n⚠️ USB 启动盘制作完成，但启动引导设置失败！")
                self.log("  请手动使用 bootsect.exe 设置启动扇区")
                self.log("  或使用 MakeWinPEMedia 制作方法")
                self.output_queue.put(('status', '完成（启动引导失败）'))
                self.output_queue.put(('finish', False))
            
        except Exception as e:
            self.log(f"❌ 错误: {e}")
            self.output_queue.put(('finish', False))
    
    def get_disk_number(self, drive_letter):
        """获取分区所在的物理磁盘编号"""
        try:
            # 使用PowerShell查询
            ps_cmd = f'Get-Partition -DriveLetter {drive_letter} | Select-Object -ExpandProperty DiskNumber'
            result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                  capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
            
            output = result.stdout.strip()
            if output.isdigit():
                self.log(f"  找到磁盘编号: {output}")
                return int(output)
            
            # 如果失败，返回默认值
            self.log("  ⚠️ 自动检测失败，使用默认值")
            return 1  # 默认值
            
        except Exception as e:
            self.log(f"  获取磁盘编号失败: {e}")
            return 1
    
    def setup_boot_sector(self, drive_letter):
        """设置启动扇区，返回True表示成功或可以跳过，False表示失败"""
        try:
            # 使用bootsect.exe设置启动扇区
            self.log("  使用 bootsect.exe 设置启动扇区...")
            
            # 多个可能的bootsect.exe位置
            possible_paths = [
                self.winpe_dir / "bootsect.exe",
                self.winpe_dir / "fwfiles" / "bootsect.exe",
                Path("C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit/Deployment Tools/amd64/Oscdimg/bootsect.exe"),
                Path("C:/Program Files (x86)/Windows Kits/10/Assessment and Deployment Kit/Windows Preinstallation Environment/amd64/Media/bootsect.exe"),
                Path(__file__).parent.parent / "tools" / "bootsect.exe",  # 项目tools目录（绝对路径）
                Path("tools/bootsect.exe"),  # 相对路径
                Path("bootsect.exe"),  # 当前目录
            ]
            
            bootsect_path = None
            for path in possible_paths:
                if path.exists():
                    bootsect_path = path
                    self.log(f"  ✅ 找到bootsect.exe: {path}")
                    break
            
            # 如果没找到，输出详细查找路径
            if not bootsect_path:
                self.log(f"  已查找以下位置:")
                for i, path in enumerate(possible_paths):
                    self.log(f"    [{i+1}] {path}")
            
            if bootsect_path:
                # 对于GPT/UEFI分区，可能不需要bootsect
                partition_scheme = self.partition_scheme.get()
                if partition_scheme == "gpt":
                    self.log("  GPT分区使用UEFI启动，检查EFI文件...")
                    # 检查EFI启动文件是否存在
                    efi_boot = Path(f"{drive_letter}:") / "EFI" / "Boot" / "bootx64.efi"
                    if efi_boot.exists():
                        self.log("✅ UEFI启动文件存在，无需bootsect")
                        return True
                    else:
                        self.log("⚠️ 未找到UEFI启动文件")
                
                # MBR分区或需要设置启动扇区
                cmd = f'"{bootsect_path}" /nt60 {drive_letter}: /mbr'
                self.log(f"  执行: bootsect.exe /nt60 {drive_letter}: /mbr")
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.log("✅ 启动扇区设置成功")
                    self.log(result.stdout)
                    return True
                else:
                    self.log(f"❌ 启动扇区设置失败")
                    self.log(f"  错误: {result.stderr}")
                    return False
            else:
                self.log("❌ 未找到bootsect.exe")
                self.log("  请从Windows ADK复制bootsect.exe到tools目录")
                self.log("  或确保已安装Windows ADK")
                
                # 对于UEFI，可以不用bootsect
                partition_scheme = self.partition_scheme.get()
                if partition_scheme == "gpt":
                    self.log("  GPT/UEFI分区可能不需要bootsect，检查EFI文件...")
                    efi_boot = Path(f"{drive_letter}:") / "EFI" / "Boot" / "bootx64.efi"
                    if efi_boot.exists():
                        self.log("✅ UEFI启动文件存在，应该可以启动")
                        return True
                    else:
                        self.log("❌ 缺少UEFI启动文件，U盘无法启动")
                        return False
                else:
                    self.log("❌ MBR分区必须使用bootsect，U盘无法启动")
                    return False
        except Exception as e:
            self.log(f"❌ 启动扇区设置异常: {e}")
            return False
    
    def log(self, message):
        """添加日志（线程安全）"""
        # 始终使用after在主线程中执行，避免线程安全问题
        def _log():
            try:
                self.log_text.insert(tk.END, f"{message}\n")
                self.log_text.see(tk.END)
            except:
                pass  # 窗口已关闭时忽略错误
        
        self.dialog.after(0, _log)
    
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
