#!/usr/bin/env python3
"""
SDIO 驱动提取工具 - 图形界面版本
"""

import os
import sys
import threading
import queue
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from extract_sdio_drivers import SDIODriverExtractor


class SDIODriverExtractorGUI:
    """SDIO 驱动提取工具 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("SDIO 驱动提取工具")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置图标
        self.set_icon()
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # 状态变量
        self.is_running = False
        self.extractor = None
        self.output_queue = queue.Queue()
        
        # 创建界面
        self.create_widgets()
        
        # 启动输出监控
        self.monitor_output()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # ==================== 设置面板 ====================
        settings_frame = ttk.LabelFrame(main_frame, text="设置", padding="10")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # 源目录
        ttk.Label(settings_frame, text="源目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_dir = tk.StringVar(value=r"外置程序\SDIO_Update\drivers")
        source_entry = ttk.Entry(settings_frame, textvariable=self.source_dir, width=50)
        source_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(settings_frame, text="浏览...", command=self.browse_source).grid(row=0, column=2)
        
        # 输出目录
        ttk.Label(settings_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_dir = tk.StringVar(value=r"drive\SDIO_Update")
        output_entry = ttk.Entry(settings_frame, textvariable=self.output_dir, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(settings_frame, text="浏览...", command=self.browse_output).grid(row=1, column=2)
        
        # 临时目录
        ttk.Label(settings_frame, text="临时目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.temp_dir = tk.StringVar(value="temp_extract")
        temp_entry = ttk.Entry(settings_frame, textvariable=self.temp_dir, width=50)
        temp_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # ==================== 控制按钮 ====================
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="▶ 开始提取", command=self.start_extraction, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⬛ 停止", command=self.stop_extraction, state=tk.DISABLED, width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(control_frame, text="🗑 清空日志", command=self.clear_log, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_output_btn = ttk.Button(control_frame, text="📁 打开输出目录", command=self.open_output_dir, width=15)
        self.open_output_btn.pack(side=tk.LEFT, padx=5)
        
        # ==================== 进度信息 ====================
        progress_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(1, weight=1)
        
        # 当前状态
        ttk.Label(progress_frame, text="状态:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.status_label = ttk.Label(progress_frame, text="就绪", foreground="green")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 当前命令
        ttk.Label(progress_frame, text="当前操作:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.command_label = ttk.Label(progress_frame, text="等待开始...", foreground="gray")
        self.command_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # 统计信息
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.stats_labels = {}
        stats_info = [
            ("processed", "已处理包", "0"),
            ("raid", "RAID驱动", "0"),
            ("storage", "存储驱动", "0"),
            ("network", "网卡驱动", "0")
        ]
        
        for i, (key, label, value) in enumerate(stats_info):
            frame = ttk.Frame(stats_frame)
            frame.pack(side=tk.LEFT, padx=10)
            ttk.Label(frame, text=label+":").pack(side=tk.LEFT)
            self.stats_labels[key] = ttk.Label(frame, text=value, font=('Arial', 10, 'bold'), foreground="blue")
            self.stats_labels[key].pack(side=tk.LEFT, padx=3)
        
        # 进度条
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # ==================== 输出日志 ====================
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20,
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#d4d4d4'
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置日志颜色标签
        self.log_text.tag_config('INFO', foreground='#4ec9b0')
        self.log_text.tag_config('SUCCESS', foreground='#4ec9b0', font=('Consolas', 9, 'bold'))
        self.log_text.tag_config('WARNING', foreground='#dcdcaa')
        self.log_text.tag_config('ERROR', foreground='#f48771')
        self.log_text.tag_config('COMMAND', foreground='#569cd6')
        self.log_text.tag_config('SEPARATOR', foreground='#858585')
        
        self.log("[系统] SDIO 驱动提取工具已启动", 'SUCCESS')
    
    def browse_source(self):
        """浏览源目录"""
        directory = filedialog.askdirectory(title="选择 SDIO 驱动源目录")
        if directory:
            self.source_dir.set(directory)
    
    def browse_output(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
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
    
    def open_output_dir(self):
        """打开输出目录"""
        output_path = Path(self.output_dir.get())
        if output_path.exists():
            os.startfile(output_path)
        else:
            messagebox.showwarning("警告", "输出目录不存在")
    
    def update_status(self, status, command=""):
        """更新状态"""
        self.status_label.config(text=status)
        if command:
            self.command_label.config(text=command)
    
    def update_stats(self, stats):
        """更新统计信息"""
        self.stats_labels['processed'].config(text=str(stats.get('total_processed', 0)))
        self.stats_labels['raid'].config(text=str(stats.get('raid', 0)))
        self.stats_labels['storage'].config(text=str(stats.get('storage', 0)))
        self.stats_labels['network'].config(text=str(stats.get('network', 0)))
    
    def start_extraction(self):
        """开始提取"""
        if self.is_running:
            return
        
        # 验证输入
        source = self.source_dir.get().strip()
        output = self.output_dir.get().strip()
        temp = self.temp_dir.get().strip()
        
        if not source or not output:
            messagebox.showerror("错误", "请设置源目录和输出目录")
            return
        
        if not Path(source).exists():
            messagebox.showerror("错误", f"源目录不存在:\n{source}")
            return
        
        # 更新界面状态
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start(10)
        
        self.log("="*60, 'SEPARATOR')
        self.log("[开始] 启动驱动提取任务", 'SUCCESS')
        self.log(f"[配置] 源目录: {source}", 'INFO')
        self.log(f"[配置] 输出目录: {output}", 'INFO')
        self.log(f"[配置] 临时目录: {temp}", 'INFO')
        self.log("="*60, 'SEPARATOR')
        
        self.update_status("运行中...", "正在初始化...")
        
        # 在后台线程运行
        thread = threading.Thread(target=self.run_extraction, args=(source, output, temp))
        thread.daemon = True
        thread.start()
    
    def stop_extraction(self):
        """停止提取（暂不实现完整的中断逻辑）"""
        if messagebox.askyesno("确认", "确定要停止吗？\n注意：当前正在处理的文件会继续完成。"):
            self.log("[警告] 用户请求停止（等待当前任务完成）", 'WARNING')
            self.is_running = False
    
    def run_extraction(self, source, output, temp):
        """运行提取任务"""
        try:
            # 创建自定义的 Extractor，重定向输出
            extractor = CustomSDIOExtractor(source, output, temp, self.output_queue)
            
            # 运行提取
            success = extractor.run()
            
            # 更新统计
            self.root.after(0, self.update_stats, extractor.stats)
            
            if success:
                self.output_queue.put(('SUCCESS', '[完成] 驱动提取成功完成！'))
                self.root.after(0, self.update_status, "完成", "任务成功")
            else:
                self.output_queue.put(('ERROR', '[失败] 驱动提取未完成'))
                self.root.after(0, self.update_status, "失败", "任务失败")
                
        except Exception as e:
            self.output_queue.put(('ERROR', f'[异常] {str(e)}'))
            self.root.after(0, self.update_status, "错误", str(e))
        finally:
            self.root.after(0, self.finish_extraction)
    
    def finish_extraction(self):
        """完成提取"""
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()
        self.command_label.config(text="等待开始...")
    
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


class CustomSDIOExtractor(SDIODriverExtractor):
    """自定义的提取器，输出重定向到队列"""
    
    def __init__(self, sdio_dir, output_dir, temp_dir, output_queue):
        super().__init__(sdio_dir, output_dir, temp_dir)
        self.output_queue = output_queue
    
    def print_log(self, message, tag='INFO'):
        """输出日志到队列"""
        self.output_queue.put((tag, message))
    
    def run(self):
        """执行提取流程（重写以重定向输出）"""
        self.print_log("="*60, 'SEPARATOR')
        self.print_log("SDIO 驱动提取工具", 'SUCCESS')
        self.print_log("="*60, 'SEPARATOR')
        
        # 检查解压工具
        self.print_log("[检查] 正在检查解压工具...", 'INFO')
        extractor_type, extractor_path = self.check_extractor()
        if not extractor_type:
            self.print_log("[错误] 未找到解压工具（WinRAR 或 7-Zip）", 'ERROR')
            self.print_log("请安装以下任意一个:", 'WARNING')
            self.print_log("  - WinRAR: https://www.winrar.com/", 'INFO')
            self.print_log("  - 7-Zip: https://www.7-zip.org/", 'INFO')
            return False
        
        self.print_log(f"[通过] 使用 {extractor_type.upper()}: {extractor_path}", 'SUCCESS')
        
        # 检查源目录
        if not self.sdio_dir.exists():
            self.print_log(f"[错误] 源目录不存在: {self.sdio_dir}", 'ERROR')
            return False
        
        # 创建目录
        self.raid_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.network_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.print_log("[配置]", 'INFO')
        self.print_log(f"  源目录: {self.sdio_dir}", 'INFO')
        self.print_log(f"  输出目录: {self.output_dir}", 'INFO')
        self.print_log(f"  临时目录: {self.temp_dir}", 'INFO')
        
        # 获取所有 7z 文件
        archives = list(self.sdio_dir.glob("*.7z"))
        
        # 过滤：只处理关键的驱动包
        target_archives = []
        target_patterns = [
            'DP_MassStorage',  # 大容量存储（包含 RAID）
            'DP_LAN',          # 网卡驱动
            'DP_Chipset'       # 芯片组（可能包含存储控制器）
        ]
        
        for archive in archives:
            for pattern in target_patterns:
                if pattern in archive.name:
                    target_archives.append(archive)
                    break
        
        if not target_archives:
            self.print_log("[错误] 未找到目标驱动包", 'ERROR')
            return False
        
        self.print_log(f"[信息] 找到 {len(target_archives)} 个目标驱动包", 'INFO')
        for archive in target_archives:
            self.print_log(f"  - {archive.name}", 'INFO')
        
        self.print_log("[开始] 开始提取驱动...", 'SUCCESS')
        
        # 处理每个压缩包
        for i, archive in enumerate(target_archives, 1):
            self.print_log(f"【{i}/{len(target_archives)}】 处理: {archive.name}", 'COMMAND')
            self.process_archive_custom(archive, extractor_type, extractor_path)
            self.stats['total_processed'] += 1
        
        # 清理临时目录
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
            self.print_log("[清理] 已删除临时文件", 'SUCCESS')
        except:
            self.print_log(f"[警告] 无法删除临时目录: {self.temp_dir}", 'WARNING')
        
        # 显示总统计
        self.print_log("="*60, 'SEPARATOR')
        self.print_log("[完成] 驱动提取完成", 'SUCCESS')
        self.print_log("="*60, 'SEPARATOR')
        self.print_log("[总计]", 'INFO')
        self.print_log(f"  ├── 处理的压缩包: {self.stats['total_processed']} 个", 'INFO')
        self.print_log(f"  ├── RAID 驱动: {self.stats['raid']} 个", 'INFO')
        self.print_log(f"  ├── 存储驱动: {self.stats['storage']} 个", 'INFO')
        self.print_log(f"  └── 网卡驱动: {self.stats['network']} 个", 'INFO')
        self.print_log("[输出目录]", 'INFO')
        self.print_log(f"  ├── RAID: {self.raid_dir}", 'INFO')
        self.print_log(f"  ├── 存储: {self.storage_dir}", 'INFO')
        self.print_log(f"  └── 网卡: {self.network_dir}", 'INFO')
        
        return True
    
    def process_archive_custom(self, archive_path, extractor_type, extractor_path):
        """处理单个 7z 压缩包"""
        import shutil
        from pathlib import Path
        
        archive_name = archive_path.name
        
        # 创建临时解压目录
        extract_dir = self.temp_dir / archive_path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        # 解压
        self.print_log(f"  [解压中] 正在解压...", 'INFO')
        if not self.extract_7z(archive_path, extract_dir, extractor_type, extractor_path):
            self.print_log(f"  [失败] 解压失败", 'ERROR')
            return
        
        # 扫描 .inf 文件
        self.print_log(f"  [扫描中] 正在识别驱动...", 'INFO')
        inf_files = list(extract_dir.rglob("*.inf"))
        
        archive_stats = {'raid': 0, 'storage': 0, 'network': 0, 'other': 0}
        
        for inf_file in inf_files:
            driver_type = self.identify_driver_type(inf_file)
            
            if driver_type in ['raid', 'storage', 'network']:
                if self.copy_driver_package(inf_file, driver_type):
                    archive_stats[driver_type] += 1
                    self.stats[driver_type] += 1
            else:
                archive_stats['other'] += 1
        
        # 显示统计
        self.print_log(f"  [完成] 本包统计:", 'SUCCESS')
        self.print_log(f"    ├── RAID 驱动: {archive_stats['raid']} 个", 'INFO')
        self.print_log(f"    ├── 存储驱动: {archive_stats['storage']} 个", 'INFO')
        self.print_log(f"    ├── 网卡驱动: {archive_stats['network']} 个", 'INFO')
        self.print_log(f"    └── 其他驱动: {archive_stats['other']} 个", 'INFO')
        
        # 清理临时文件
        try:
            shutil.rmtree(extract_dir)
        except:
            pass


def main():
    """主函数"""
    root = tk.Tk()
    app = SDIODriverExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

