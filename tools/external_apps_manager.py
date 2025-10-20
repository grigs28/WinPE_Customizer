#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
外置程序管理器 - 扫描和配置外置程序的放置位置
"""

import os
import sys
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime


class ExternalAppsManager:
    """外置程序管理器"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("外置程序管理器 - WinPE Customizer")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # 设置图标
        self.set_icon()
        
        # 数据
        self.apps_data = []  # [{"path": "", "name": "", "desktop": False, "startmenu": False, "path_env": False, "target": ""}]
        self.external_dir = Path("外置程序")
        self.config_file = Path("external_apps_config.json")
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()
    
    def set_icon(self):
        """设置窗口图标"""
        icon_files = ['../winpe_customizer.ico', '../winpe_simple.ico', 'winpe_customizer.ico', 'winpe_simple.ico']
        for icon_file in icon_files:
            icon_path = Path(icon_file)
            if icon_path.exists():
                try:
                    self.root.iconbitmap(str(icon_path))
                    break
                except:
                    continue
    
    def create_widgets(self):
        """创建界面"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(fill=tk.X, side=tk.TOP)
        
        ttk.Label(toolbar, text="外置程序目录:").pack(side=tk.LEFT, padx=5)
        self.dir_var = tk.StringVar(value=str(self.external_dir))
        ttk.Entry(toolbar, textvariable=self.dir_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="浏览", command=self.browse_dir).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔍 扫描程序", command=self.scan_apps, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
        # 主区域
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 说明
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="📋 程序列表", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text="选择每个程序的放置位置，支持多选", foreground="gray").pack(anchor=tk.W)
        
        # 表格区域
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ('name', 'path', 'desktop', 'startmenu', 'path_env', 'target')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                 yscrollcommand=scrollbar_y.set,
                                 xscrollcommand=scrollbar_x.set,
                                 selectmode='browse')
        
        # 列标题
        self.tree.heading('name', text='程序名称')
        self.tree.heading('path', text='相对路径')
        self.tree.heading('desktop', text='桌面')
        self.tree.heading('startmenu', text='开始菜单')
        self.tree.heading('path_env', text='命令行(PATH)')
        self.tree.heading('target', text='目标位置')
        
        # 列宽度
        self.tree.column('name', width=200)
        self.tree.column('path', width=250)
        self.tree.column('desktop', width=80, anchor=tk.CENTER)
        self.tree.column('startmenu', width=100, anchor=tk.CENTER)
        self.tree.column('path_env', width=120, anchor=tk.CENTER)
        self.tree.column('target', width=200)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        # 双击编辑
        self.tree.bind('<Double-1>', self.edit_item)
        
        # 右键菜单
        self.create_context_menu()
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # 底部按钮
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Button(button_frame, text="💾 保存配置", command=self.save_config, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📂 加载配置", command=self.load_config, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📝 生成config.py", command=self.generate_config_py, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="ℹ️ 帮助", command=self.show_help, width=15).pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        self.status_label = ttk.Label(button_frame, text="就绪", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=10)
    
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ 编辑", command=self.edit_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✅ 添加到桌面", command=lambda: self.toggle_option('desktop'))
        self.context_menu.add_command(label="📋 添加到开始菜单", command=lambda: self.toggle_option('startmenu'))
        self.context_menu.add_command(label="⌨️ 添加到PATH", command=lambda: self.toggle_option('path_env'))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ 从列表移除", command=self.remove_selected)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def browse_dir(self):
        """浏览目录"""
        directory = filedialog.askdirectory(title="选择外置程序目录", initialdir=self.dir_var.get())
        if directory:
            self.dir_var.set(directory)
            self.external_dir = Path(directory)
    
    def scan_apps(self):
        """扫描程序"""
        self.external_dir = Path(self.dir_var.get())
        
        if not self.external_dir.exists():
            messagebox.showerror("错误", f"目录不存在:\n{self.external_dir}")
            return
        
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.apps_data.clear()
        
        # 扫描可执行文件
        exe_files = []
        for ext in ['*.exe', '*.EXE', '*.bat', '*.cmd', '*.com']:
            exe_files.extend(self.external_dir.rglob(ext))
        
        if not exe_files:
            messagebox.showinfo("提示", "未找到可执行文件")
            return
        
        # 添加到列表
        for exe_file in exe_files:
            rel_path = exe_file.relative_to(self.external_dir)
            app_info = {
                'name': exe_file.name,
                'path': str(rel_path),
                'desktop': False,
                'startmenu': False,
                'path_env': False,
                'target': 'Windows/System32'
            }
            self.apps_data.append(app_info)
            self.add_tree_item(app_info)
        
        self.status_label.config(text=f"找到 {len(exe_files)} 个程序")
        messagebox.showinfo("完成", f"扫描完成！\n找到 {len(exe_files)} 个可执行文件")
    
    def add_tree_item(self, app_info):
        """添加到树形视图"""
        self.tree.insert('', tk.END, values=(
            app_info['name'],
            app_info['path'],
            '✓' if app_info['desktop'] else '',
            '✓' if app_info['startmenu'] else '',
            '✓' if app_info['path_env'] else '',
            app_info['target']
        ))
    
    def refresh_tree(self):
        """刷新树形视图"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for app_info in self.apps_data:
            self.add_tree_item(app_info)
    
    def edit_item(self, event):
        """双击编辑"""
        self.edit_selected()
    
    def edit_selected(self):
        """编辑选中项"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        index = self.tree.index(item_id)
        app_info = self.apps_data[index]
        
        # 创建编辑对话框
        EditDialog(self.root, app_info, self.refresh_tree)
    
    def toggle_option(self, option):
        """切换选项"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        index = self.tree.index(item_id)
        self.apps_data[index][option] = not self.apps_data[index][option]
        self.refresh_tree()
    
    def remove_selected(self):
        """移除选中项"""
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("确认", "确定要从列表中移除吗？"):
            item_id = selection[0]
            index = self.tree.index(item_id)
            del self.apps_data[index]
            self.refresh_tree()
    
    def save_config(self):
        """保存配置"""
        config_data = {
            'external_dir': str(self.external_dir),
            'apps': self.apps_data,
            'updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.status_label.config(text=f"已保存到 {self.config_file}")
            messagebox.showinfo("成功", f"配置已保存到:\n{self.config_file}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败:\n{e}")
    
    def load_config(self):
        """加载配置"""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.external_dir = Path(config_data['external_dir'])
            self.dir_var.set(str(self.external_dir))
            self.apps_data = config_data['apps']
            self.refresh_tree()
            
            self.status_label.config(text=f"已加载 {len(self.apps_data)} 个程序")
        except Exception as e:
            messagebox.showerror("错误", f"加载失败:\n{e}")
    
    def generate_config_py(self):
        """生成 config.py 配置代码"""
        if not self.apps_data:
            messagebox.showwarning("警告", "没有程序数据，请先扫描程序")
            return
        
        # 生成代码
        code_lines = [
            "# ============================================================================",
            "# 外置程序配置 - 由外置程序管理器自动生成",
            f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# ============================================================================",
            "",
            "EXTERNAL_APPS = ["
        ]
        
        for app in self.apps_data:
            if app['desktop'] or app['startmenu'] or app['path_env']:
                code_lines.append(f"    # {app['name']}")
                code_lines.append(f"    (")
                code_lines.append(f"        \"{app['path']}\",")
                code_lines.append(f"        \"{app['target']}\",")
                code_lines.append(f"        \"{app['name']}\",")
                
                options = []
                if app['desktop']:
                    options.append('desktop')
                if app['startmenu']:
                    options.append('startmenu')
                if app['path_env']:
                    options.append('path')
                
                code_lines.append(f"        # 放置: {', '.join(options)}")
                code_lines.append(f"    ),")
                code_lines.append("")
        
        code_lines.append("]")
        code_lines.append("")
        
        # 显示对话框
        ShowCodeDialog(self.root, "\n".join(code_lines))
    
    def show_help(self):
        """显示帮助"""
        help_text = """
═══════════════════════════════════════════════
        外置程序管理器 - 使用帮助
═══════════════════════════════════════════════

【功能说明】
管理要集成到 WinPE 中的外部程序，配置其放置位置。

【使用步骤】
1. 设置外置程序目录（默认: 外置程序）
2. 点击"扫描程序"自动扫描所有可执行文件
3. 双击或右键编辑每个程序的配置
4. 保存配置到 JSON 文件
5. 生成 config.py 代码片段

【配置选项】

📍 桌面 (Desktop)
  - 在 WinPE 桌面创建快捷方式
  - 适合常用工具（如 DiskGenius）

📋 开始菜单 (Start Menu)
  - 添加到开始菜单
  - 方便分类管理

⌨️ 命令行 (PATH)
  - 添加到系统 PATH 环境变量
  - 可以在命令行直接运行
  - 适合命令行工具

📁 目标位置 (Target)
  - Windows/System32: 系统目录（推荐）
  - Tools: 工具目录
  - 自定义路径

【快捷操作】
- 双击: 编辑配置
- 右键: 快速切换选项
- 批量操作: 选中后用右键菜单

【文件说明】
- external_apps_config.json: 保存的配置
- 可以手动编辑此文件
- 支持版本控制和分享

【提示】
1. 不是所有程序都需要放到桌面
2. 命令行工具建议添加到 PATH
3. 图形工具建议放到桌面或开始菜单
4. 定期保存配置以免丢失
        """
        
        dialog = tk.Toplevel(self.root)
        dialog.title("帮助")
        dialog.geometry("600x600")
        
        text = tk.Text(dialog, wrap=tk.WORD, font=('Consolas', 9))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(1.0, help_text)
        text.config(state=tk.DISABLED)
        
        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)


class EditDialog:
    """编辑对话框"""
    
    def __init__(self, parent, app_info, callback):
        self.app_info = app_info
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"编辑: {app_info['name']}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # 程序名称
        ttk.Label(frame, text="程序名称:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=app_info['name'], font=('Arial', 10, 'bold')).grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # 相对路径
        ttk.Label(frame, text="相对路径:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=app_info['path'], foreground='gray').grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # 放置位置
        ttk.Label(frame, text="放置位置:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        self.desktop_var = tk.BooleanVar(value=app_info['desktop'])
        ttk.Checkbutton(frame, text="📍 添加到桌面", variable=self.desktop_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        self.startmenu_var = tk.BooleanVar(value=app_info['startmenu'])
        ttk.Checkbutton(frame, text="📋 添加到开始菜单", variable=self.startmenu_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        self.path_var = tk.BooleanVar(value=app_info['path_env'])
        ttk.Checkbutton(frame, text="⌨️ 添加到命令行 (PATH)", variable=self.path_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # 目标位置
        ttk.Label(frame, text="目标位置:").grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        self.target_var = tk.StringVar(value=app_info['target'])
        targets = ['Windows/System32', 'Tools', 'Program Files', 'Windows']
        ttk.Combobox(frame, textvariable=self.target_var, values=targets, width=30).grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        """保存"""
        self.app_info['desktop'] = self.desktop_var.get()
        self.app_info['startmenu'] = self.startmenu_var.get()
        self.app_info['path_env'] = self.path_var.get()
        self.app_info['target'] = self.target_var.get()
        
        self.callback()
        self.dialog.destroy()


class ShowCodeDialog:
    """显示代码对话框"""
    
    def __init__(self, parent, code):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("生成的 config.py 代码")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        
        # 说明
        info_frame = ttk.Frame(self.dialog, padding="10")
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, text="将以下代码复制到 config.py 中的 EXTERNAL_APPS 部分:", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # 代码区域
        from tkinter import scrolledtext
        self.text = scrolledtext.ScrolledText(self.dialog, wrap=tk.NONE, font=('Consolas', 9))
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text.insert(1.0, code)
        
        # 按钮
        btn_frame = ttk.Frame(self.dialog, padding="10")
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📋 复制到剪贴板", command=self.copy_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 保存到文件", command=self.save_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        self.code = code
    
    def copy_code(self):
        """复制到剪贴板"""
        self.dialog.clipboard_clear()
        self.dialog.clipboard_append(self.code)
        messagebox.showinfo("成功", "已复制到剪贴板")
    
    def save_file(self):
        """保存到文件"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python文件", "*.py"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile="external_apps_config.py"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.code)
                messagebox.showinfo("成功", f"已保存到:\n{filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{e}")


def main():
    """主函数"""
    root = tk.Tk()
    app = ExternalAppsManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()

