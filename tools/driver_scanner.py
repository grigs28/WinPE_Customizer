#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
驱动扫描和导出工具
自动扫描系统驱动并导出到指定目录
"""

import os
import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from datetime import datetime
import threading
import shutil


class DriverScanner:
    """驱动扫描工具"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("驱动扫描和导出工具")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # 设置图标
        self.set_icon()
        
        # 变量
        self.output_dir = tk.StringVar(value=str(Path("../drive").absolute()))
        self.is_scanning = False
        self.drivers_list = []
        
        # 创建界面
        self.create_widgets()
    
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
        # 顶部说明
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="驱动扫描和导出工具", 
                 font=('Arial', 14, 'bold')).pack(anchor=tk.W)
        ttk.Label(header_frame, text="扫描系统已安装的驱动程序并导出到指定目录", 
                 foreground="gray").pack(anchor=tk.W, pady=(5, 0))
        
        # 配置区域
        config_frame = ttk.LabelFrame(self.root, text="配置", padding="15")
        config_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # 输出目录
        dir_frame = ttk.Frame(config_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="导出目录:", width=12).pack(side=tk.LEFT)
        ttk.Entry(dir_frame, textvariable=self.output_dir, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(dir_frame, text="浏览...", command=self.browse_output_dir, 
                  width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(dir_frame, text="📁 打开", command=self.open_output_dir, 
                  width=10).pack(side=tk.LEFT, padx=2)
        
        # 操作按钮
        btn_frame = ttk.Frame(config_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 5))
        
        self.scan_btn = ttk.Button(btn_frame, text="🔍 扫描驱动", 
                                   command=self.start_scan, width=20, 
                                   style='Accent.TButton')
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(btn_frame, text="📤 导出选中驱动", 
                                     command=self.export_drivers, width=20,
                                     state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_all_btn = ttk.Button(btn_frame, text="📦 导出全部驱动", 
                                        command=self.export_all_drivers, width=20,
                                        state=tk.DISABLED)
        self.export_all_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🔄 刷新", command=self.refresh_list, 
                  width=12).pack(side=tk.LEFT, padx=5)
        
        # 驱动列表
        list_frame = ttk.LabelFrame(self.root, text="驱动列表", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建 Treeview
        columns = ('driver', 'provider', 'class', 'date', 'version')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', 
                                selectmode='extended', height=15)
        
        # 设置列
        self.tree.heading('#0', text='√')
        self.tree.heading('driver', text='驱动名称')
        self.tree.heading('provider', text='提供商')
        self.tree.heading('class', text='类别')
        self.tree.heading('date', text='日期')
        self.tree.heading('version', text='版本')
        
        self.tree.column('#0', width=40, anchor=tk.CENTER)
        self.tree.column('driver', width=300)
        self.tree.column('provider', width=150)
        self.tree.column('class', width=120)
        self.tree.column('date', width=100)
        self.tree.column('version', width=120)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # 绑定双击事件
        self.tree.bind('<Double-Button-1>', self.toggle_selection)
        
        # 统计信息
        stats_frame = ttk.Frame(list_frame)
        stats_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
        
        self.stats_label = ttk.Label(stats_frame, text="未扫描", foreground="gray")
        self.stats_label.pack(side=tk.LEFT)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, 
                                                  font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置标签颜色
        self.log_text.tag_config('INFO', foreground='black')
        self.log_text.tag_config('SUCCESS', foreground='green')
        self.log_text.tag_config('ERROR', foreground='red')
        self.log_text.tag_config('WARNING', foreground='orange')
    
    def log(self, message, tag='INFO'):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
        self.log_text.see(tk.END)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择驱动导出目录")
        if directory:
            self.output_dir.set(directory)
    
    def open_output_dir(self):
        """打开输出目录"""
        output_path = Path(self.output_dir.get())
        if output_path.exists():
            os.startfile(output_path)
        else:
            messagebox.showwarning("提示", "目录不存在")
    
    def toggle_selection(self, event):
        """切换选择状态"""
        item = self.tree.identify('item', event.x, event.y)
        if item:
            current_value = self.tree.item(item, 'text')
            new_value = '' if current_value == '☑' else '☑'
            self.tree.item(item, text=new_value)
    
    def start_scan(self):
        """开始扫描"""
        if self.is_scanning:
            messagebox.showwarning("警告", "正在扫描中，请等待...")
            return
        
        self.log("开始扫描系统驱动...", 'INFO')
        self.scan_btn.config(state=tk.DISABLED)
        self.is_scanning = True
        
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        thread = threading.Thread(target=self.scan_drivers)
        thread.daemon = True
        thread.start()
    
    def scan_drivers(self):
        """扫描驱动"""
        try:
            self.root.after(0, lambda: self.log("执行: dism /online /get-drivers", 'INFO'))
            
            # 执行 DISM 命令
            result = subprocess.run(
                'dism /online /get-drivers',
                shell=True,
                capture_output=True,
                text=True,
                encoding='gbk',
                errors='ignore'
            )
            
            if result.returncode == 0:
                # 解析输出
                drivers = self.parse_driver_list(result.stdout)
                self.drivers_list = drivers
                
                # 显示到界面
                self.root.after(0, lambda: self.display_drivers(drivers))
                self.root.after(0, lambda: self.log(f"扫描完成，找到 {len(drivers)} 个驱动", 'SUCCESS'))
            else:
                self.root.after(0, lambda: self.log(f"扫描失败: {result.stderr}", 'ERROR'))
                
        except Exception as e:
            self.root.after(0, lambda: self.log(f"扫描出错: {e}", 'ERROR'))
        finally:
            self.is_scanning = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
    
    def parse_driver_list(self, output):
        """解析驱动列表"""
        drivers = []
        lines = output.split('\n')
        
        current_driver = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('发布的名称'):
                if current_driver:
                    drivers.append(current_driver)
                current_driver = {'name': line.split(':', 1)[1].strip()}
            elif line.startswith('原始文件名'):
                current_driver['original'] = line.split(':', 1)[1].strip()
            elif line.startswith('提供商名称'):
                current_driver['provider'] = line.split(':', 1)[1].strip()
            elif line.startswith('类名称'):
                current_driver['class'] = line.split(':', 1)[1].strip()
            elif line.startswith('驱动程序版本'):
                current_driver['version'] = line.split(':', 1)[1].strip()
            elif line.startswith('日期'):
                current_driver['date'] = line.split(':', 1)[1].strip()
        
        if current_driver:
            drivers.append(current_driver)
        
        return drivers
    
    def display_drivers(self, drivers):
        """显示驱动列表"""
        for driver in drivers:
            self.tree.insert('', tk.END, text='',
                           values=(
                               driver.get('name', ''),
                               driver.get('provider', ''),
                               driver.get('class', ''),
                               driver.get('date', ''),
                               driver.get('version', '')
                           ))
        
        # 更新统计
        self.stats_label.config(text=f"共 {len(drivers)} 个驱动程序")
        
        # 启用导出按钮
        self.export_btn.config(state=tk.NORMAL)
        self.export_all_btn.config(state=tk.NORMAL)
    
    def refresh_list(self):
        """刷新列表"""
        self.start_scan()
    
    def export_drivers(self):
        """导出选中的驱动"""
        # 获取选中的项
        selected_items = []
        for item in self.tree.get_children():
            if self.tree.item(item, 'text') == '☑':
                selected_items.append(item)
        
        if not selected_items:
            messagebox.showwarning("提示", "请先勾选要导出的驱动\n\n双击驱动名称可勾选")
            return
        
        if messagebox.askyesno("确认", f"确定要导出 {len(selected_items)} 个驱动吗？"):
            self.do_export_drivers(selected_items)
    
    def export_all_drivers(self):
        """导出全部驱动"""
        if not self.drivers_list:
            messagebox.showwarning("提示", "请先扫描驱动")
            return
        
        if messagebox.askyesno("确认", f"确定要导出全部 {len(self.drivers_list)} 个驱动吗？\n\n这可能需要较长时间..."):
            # 选中所有项
            for item in self.tree.get_children():
                self.tree.item(item, text='☑')
            
            self.do_export_drivers(self.tree.get_children())
    
    def do_export_drivers(self, items):
        """执行导出"""
        output_path = Path(self.output_dir.get())
        
        # 创建输出目录
        if not output_path.exists():
            output_path.mkdir(parents=True)
            self.log(f"创建目录: {output_path}", 'INFO')
        
        self.log(f"开始导出 {len(items)} 个驱动...", 'INFO')
        
        # 禁用按钮
        self.export_btn.config(state=tk.DISABLED)
        self.export_all_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.DISABLED)
        
        def export_thread():
            try:
                success_count = 0
                fail_count = 0
                
                for item in items:
                    values = self.tree.item(item, 'values')
                    driver_name = values[0]  # 发布的名称
                    
                    self.root.after(0, lambda d=driver_name: self.log(f"导出: {d}", 'INFO'))
                    
                    # 创建驱动子目录
                    driver_dir = output_path / driver_name.replace('/', '_').replace('\\', '_')
                    driver_dir.mkdir(exist_ok=True)
                    
                    # 使用 pnputil 导出驱动
                    cmd = f'pnputil /export-driver "{driver_name}" "{driver_dir}"'
                    
                    result = subprocess.run(cmd, shell=True, capture_output=True, 
                                          text=True, encoding='gbk', errors='ignore')
                    
                    if result.returncode == 0:
                        success_count += 1
                        self.root.after(0, lambda d=driver_name: 
                                      self.log(f"✓ {d}", 'SUCCESS'))
                    else:
                        fail_count += 1
                        self.root.after(0, lambda d=driver_name: 
                                      self.log(f"✗ {d} - 失败", 'ERROR'))
                
                self.root.after(0, lambda: self.log(
                    f"导出完成！成功: {success_count}, 失败: {fail_count}", 'SUCCESS'))
                self.root.after(0, lambda: messagebox.showinfo(
                    "完成", f"驱动导出完成！\n\n成功: {success_count}\n失败: {fail_count}\n\n导出位置:\n{output_path}"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"导出出错: {e}", 'ERROR'))
            finally:
                self.root.after(0, lambda: self.export_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.export_all_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
        
        thread = threading.Thread(target=export_thread)
        thread.daemon = True
        thread.start()


def main():
    root = tk.Tk()
    app = DriverScanner(root)
    root.mainloop()


if __name__ == "__main__":
    main()

