#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
驱动扫描工具
扫描指定目录，识别硬盘、RAID、网卡等驱动类型
"""

import os
import sys
import re
import datetime
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)


class DriverScanner:
    """驱动扫描器"""
    
    # 驱动类型关键字
    STORAGE_KEYWORDS = [
        'storage', 'disk', 'sata', 'ahci', 'ide', 'scsi', 'sas',
        'nvme', 'hdd', 'ssd', 'storahci', 'stornvme'
    ]
    
    RAID_KEYWORDS = [
        'raid', 'megaraid', 'perc', 'smart array', 'smartarray',
        'iastor', 'rst', 'rcraid', 'mrsas', 'lsi', 'adaptec',
        'vroc', 'vmd', 'rste', 'intel raid', 'amd raid'
    ]
    
    NETWORK_KEYWORDS = [
        'network', 'ethernet', 'net', 'lan', 'nic', 'gigabit',
        'realtek', 'intel', 'broadcom', 'e1000', 'e1g', 'rtl',
        'bcm', 'i210', 'i219', 'i225', 'x710', 'mellanox'
    ]
    
    def __init__(self, scan_dir):
        """初始化"""
        self.scan_dir = Path(scan_dir)
        self.storage_drivers = []
        self.raid_drivers = []
        self.network_drivers = []
        self.other_drivers = []
    
    def scan(self):
        """扫描驱动目录"""
        if not self.scan_dir.exists():
            print(f"{Fore.RED}[错误] 目录不存在: {self.scan_dir}{Style.RESET_ALL}")
            return False
        
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}    驱动扫描工具 - 正在扫描...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print()
        print(f"{Fore.WHITE}[扫描] 目录: {self.scan_dir}{Style.RESET_ALL}")
        print()
        
        # 递归查找所有 .inf 文件
        inf_files = list(self.scan_dir.rglob("*.inf"))
        
        print(f"{Fore.GREEN}[发现] 找到 {len(inf_files)} 个 .inf 驱动文件{Style.RESET_ALL}")
        print()
        
        # 分析每个 .inf 文件
        for inf_file in inf_files:
            self.analyze_inf(inf_file)
        
        return True
    
    def analyze_inf(self, inf_file):
        """分析 .inf 文件内容"""
        try:
            # 读取文件内容
            with open(inf_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            # 获取相对路径
            rel_path = inf_file.relative_to(self.scan_dir)
            
            # 提取驱动信息
            driver_info = {
                'file': inf_file,
                'rel_path': rel_path,
                'name': inf_file.stem,
                'dir': inf_file.parent.name,
            }
            
            # 尝试提取描述
            desc_match = re.search(r'driverdesc\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            if desc_match:
                driver_info['desc'] = desc_match.group(1)
            else:
                driver_info['desc'] = ''
            
            # 判断驱动类型
            file_content = str(rel_path).lower() + ' ' + content
            
            is_raid = any(keyword in file_content for keyword in self.RAID_KEYWORDS)
            is_storage = any(keyword in file_content for keyword in self.STORAGE_KEYWORDS)
            is_network = any(keyword in file_content for keyword in self.NETWORK_KEYWORDS)
            
            # 分类
            if is_raid:
                self.raid_drivers.append(driver_info)
            elif is_storage:
                self.storage_drivers.append(driver_info)
            elif is_network:
                self.network_drivers.append(driver_info)
            else:
                self.other_drivers.append(driver_info)
        
        except Exception as e:
            pass  # 忽略无法读取的文件
    
    def print_results(self):
        """显示扫描结果"""
        print()
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}    扫描结果统计{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print()
        
        # RAID 驱动
        self.print_category("RAID 控制器驱动", self.raid_drivers, Fore.RED)
        
        # 存储驱动
        self.print_category("硬盘/存储驱动", self.storage_drivers, Fore.YELLOW)
        
        # 网卡驱动
        self.print_category("网络适配器驱动", self.network_drivers, Fore.GREEN)
        
        # 其他驱动
        self.print_category("其他驱动", self.other_drivers, Fore.CYAN)
        
        # 总计
        total = len(self.raid_drivers) + len(self.storage_drivers) + len(self.network_drivers) + len(self.other_drivers)
        print()
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}[总计] 共扫描到 {total} 个驱动文件{Style.RESET_ALL}")
        print(f"{Fore.RED}  ├── RAID 驱动: {len(self.raid_drivers)} 个{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  ├── 存储驱动: {len(self.storage_drivers)} 个{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  ├── 网卡驱动: {len(self.network_drivers)} 个{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  └── 其他驱动: {len(self.other_drivers)} 个{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print()
    
    def print_category(self, category_name, drivers, color):
        """打印某一类驱动"""
        if not drivers:
            return
        
        print(f"{color}{'─' * 60}{Style.RESET_ALL}")
        print(f"{color}【{category_name}】 共 {len(drivers)} 个{Style.RESET_ALL}")
        print(f"{color}{'─' * 60}{Style.RESET_ALL}")
        
        for idx, driver in enumerate(drivers, 1):
            print(f"{Fore.WHITE}  [{idx:3d}] {driver['rel_path']}{Style.RESET_ALL}")
            if driver['desc']:
                print(f"{Fore.CYAN}        描述: {driver['desc']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}        目录: {driver['dir']}{Style.RESET_ALL}")
            print()
    
    def export_report(self, output_file="driver_scan_report.txt"):
        """导出扫描报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("驱动扫描报告\n")
            f.write(f"扫描目录: {self.scan_dir}\n")
            f.write(f"扫描时间: {datetime.datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            
            self.write_category(f, "RAID 控制器驱动", self.raid_drivers)
            self.write_category(f, "硬盘/存储驱动", self.storage_drivers)
            self.write_category(f, "网络适配器驱动", self.network_drivers)
            self.write_category(f, "其他驱动", self.other_drivers)
            
            total = len(self.raid_drivers) + len(self.storage_drivers) + len(self.network_drivers) + len(self.other_drivers)
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"总计: {total} 个驱动文件\n")
            f.write(f"  RAID 驱动: {len(self.raid_drivers)} 个\n")
            f.write(f"  存储驱动: {len(self.storage_drivers)} 个\n")
            f.write(f"  网卡驱动: {len(self.network_drivers)} 个\n")
            f.write(f"  其他驱动: {len(self.other_drivers)} 个\n")
            f.write("=" * 60 + "\n")
        
        print(f"{Fore.GREEN}[导出] 报告已保存到: {output_file}{Style.RESET_ALL}")
    
    def write_category(self, f, category_name, drivers):
        """写入某一类驱动到文件"""
        if not drivers:
            return
        
        f.write("\n" + "-" * 60 + "\n")
        f.write(f"【{category_name}】 共 {len(drivers)} 个\n")
        f.write("-" * 60 + "\n\n")
        
        for idx, driver in enumerate(drivers, 1):
            f.write(f"  [{idx:3d}] {driver['rel_path']}\n")
            if driver['desc']:
                f.write(f"        描述: {driver['desc']}\n")
            f.write(f"        目录: {driver['dir']}\n")
            f.write("\n")


def main():
    """主函数"""
    import sys
    import datetime
    
    # 获取扫描目录
    if len(sys.argv) > 1:
        scan_dir = sys.argv[1]
    else:
        # 默认扫描目录
        scan_dir = input("请输入要扫描的目录路径: ").strip()
        if not scan_dir:
            scan_dir = r"外置程序\SDIO_Update\drivers"
    
    # 创建扫描器
    scanner = DriverScanner(scan_dir)
    
    # 执行扫描
    if not scanner.scan():
        return 1
    
    # 显示结果
    scanner.print_results()
    
    # 询问是否导出报告
    export = input(f"{Fore.YELLOW}是否导出报告到文件? (Y/N): {Style.RESET_ALL}").strip().upper()
    if export == 'Y':
        output_file = input(f"{Fore.WHITE}报告文件名 (默认: driver_scan_report.txt): {Style.RESET_ALL}").strip()
        if not output_file:
            output_file = "driver_scan_report.txt"
        scanner.export_report(output_file)
    
    print()
    input("按 Enter 键退出...")
    return 0


if __name__ == "__main__":
    sys.exit(main())

