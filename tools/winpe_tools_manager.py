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


class WinPEToolsManager:
    """WinPE 工具包管理器"""
    
    # 常用WinPE工具列表
    COMMON_TOOLS = [
        {
            'name': 'Dism++',
            'desc': '强大的 Windows 映像管理工具',
            'url': 'https://github.com/Chuyu-Team/Dism-Multi-language',
            'exe': 'Dism++x64.exe',
            'recommended': True
        },
        {
            'name': 'DiskGenius',
            'desc': '磁盘分区和数据恢复工具',
            'url': 'https://www.diskgenius.cn/',
            'exe': 'DiskGenius.exe',
            'recommended': True
        },
        {
            'name': 'PowerShell 7',
            'desc': '跨平台的 PowerShell 版本',
            'url': 'https://github.com/PowerShell/PowerShell',
            'exe': 'pwsh.exe',
            'recommended': False
        },
        {
            'name': 'WinNTSetup',
            'desc': 'Windows 系统安装工具',
            'url': 'https://msfn.org/board/topic/149612-winntsetup/',
            'exe': 'WinNTSetup.exe',
            'recommended': True
        },
        {
            'name': 'CPU-Z',
            'desc': 'CPU 信息检测工具',
            'url': 'https://www.cpuid.com/softwares/cpu-z.html',
            'exe': 'cpuz.exe',
            'recommended': False
        },
        {
            'name': 'CrystalDiskInfo',
            'desc': '硬盘健康监测工具',
            'url': 'https://crystalmark.info/',
            'exe': 'DiskInfo64.exe',
            'recommended': False
        },
        {
            'name': 'Notepad++',
            'desc': '文本编辑器',
            'url': 'https://notepad-plus-plus.org/',
            'exe': 'notepad++.exe',
            'recommended': True
        },
        {
            'name': '7-Zip',
            'desc': '压缩解压工具',
            'url': 'https://www.7-zip.org/',
            'exe': '7zFM.exe',
            'recommended': True
        },
        {
            'name': 'GreenBrowser',
            'desc': '绿色便携浏览器',
            'url': 'http://www.morequick.com/',
            'exe': 'GreenBrowser.exe',
            'recommended': True
        },
        {
            'name': 'Firefox Portable',
            'desc': 'Firefox 便携版浏览器',
            'url': 'https://portableapps.com/apps/internet/firefox_portable',
            'exe': 'FirefoxPortable.exe',
            'recommended': False
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
        ttk.Label(header_frame, text="⚠️ 注意：工具需要手动下载，程序不会自动下载", 
                 foreground="red", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(header_frame, text="勾选要集成的工具 → 点击下载链接获取工具 → 放到对应目录 → 生成配置", 
                 foreground="gray").pack(anchor=tk.W, pady=(0, 10))
        
        # 滚动区域
        scroll_container = ttk.Frame(parent)
        scroll_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
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
        
        # 工具列表
        self.tool_vars = {}
        for tool in self.COMMON_TOOLS:
            tool_frame = ttk.LabelFrame(scrollable_frame, text=tool['name'], padding="10")
            tool_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 复选框
            var = tk.BooleanVar(value=tool['recommended'])
            self.tool_vars[tool['name']] = var
            
            cb = ttk.Checkbutton(tool_frame, text=f"集成此工具 {' (推荐)' if tool['recommended'] else ''}", 
                               variable=var)
            cb.pack(anchor=tk.W)
            
            # 说明
            ttk.Label(tool_frame, text=f"说明: {tool['desc']}", foreground="gray").pack(anchor=tk.W, pady=(5, 0))
            ttk.Label(tool_frame, text=f"可执行文件: {tool['exe']}", foreground="blue", font=('Consolas', 9)).pack(anchor=tk.W)
            
            # 下载链接
            link_frame = ttk.Frame(tool_frame)
            link_frame.pack(anchor=tk.W, pady=(5, 0))
            ttk.Label(link_frame, text="📥 ").pack(side=tk.LEFT)
            link_label = ttk.Label(link_frame, text="点击下载", foreground="blue", cursor="hand2", 
                                  font=('Arial', 9, 'underline'))
            link_label.pack(side=tk.LEFT)
            link_label.bind("<Button-1>", lambda e, url=tool['url']: self.open_url(url))
            
            ttk.Label(link_frame, text=f"  ({tool['url']})", foreground="gray", font=('Arial', 8)).pack(side=tk.LEFT)
        
        # 底部按钮
        btn_frame = ttk.Frame(parent, padding="10")
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="✅ 全选推荐", command=self.select_recommended_tools, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ 全不选", command=self.deselect_all_tools, width=16).pack(side=tk.LEFT, padx=5)
    
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
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="📝 生成配置", command=self.generate_config, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 复制代码", command=self.copy_config, width=16).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 直接保存到config.py", command=self.save_to_config, width=22).pack(side=tk.LEFT, padx=5)
    
    def open_url(self, url):
        """打开URL"""
        import webbrowser
        webbrowser.open(url)
    
    def select_recommended_tools(self):
        """全选推荐工具"""
        for tool in self.COMMON_TOOLS:
            if tool['recommended']:
                self.tool_vars[tool['name']].set(True)
    
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
        if not messagebox.askyesno("确认", "确定要将工具配置保存到 core/config.py 吗？\n\n这将覆盖现有的 EXTERNAL_APPS 配置。"):
            return
        
        try:
            config_file = Path("../core/config.py") if Path("../core/config.py").exists() else Path("core/config.py")
            
            if not config_file.exists():
                messagebox.showerror("错误", "找不到 config.py 文件")
                return
            
            # 读取现有配置
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 生成新的 EXTERNAL_APPS 配置
            new_apps = []
            for tool in self.COMMON_TOOLS:
                if self.tool_vars[tool['name']].get():
                    new_apps.append(f"    (\"{tool['name']}/{tool['exe']}\", \"Windows/System32\", \"{tool['name']}\"),\n")
            
            # 替换 EXTERNAL_APPS 部分
            new_lines = []
            in_external_apps = False
            skip_until_bracket = False
            
            for line in lines:
                if 'EXTERNAL_APPS = [' in line:
                    in_external_apps = True
                    new_lines.append(line)
                    # 添加新配置
                    new_lines.extend(new_apps)
                    skip_until_bracket = True
                    continue
                
                if skip_until_bracket:
                    if ']' in line and in_external_apps:
                        new_lines.append(line)
                        in_external_apps = False
                        skip_until_bracket = False
                    # 跳过旧的配置
                    continue
                
                new_lines.append(line)
            
            # 写回文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            messagebox.showinfo("成功", "工具配置已保存到 core/config.py！\n\n请确保将工具文件放到对应的目录中。")
            
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
            except:
                pass
    
    def save_config(self):
        """保存配置"""
        data = {
            'selected_tools': {name: var.get() for name, var in self.tool_vars.items()},
            'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    root = tk.Tk()
    app = WinPEToolsManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()

