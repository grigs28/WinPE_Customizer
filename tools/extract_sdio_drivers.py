#!/usr/bin/env python3
"""
SDIO 驱动提取工具
从 SDIO_Update 的 7z 压缩包中提取 RAID、存储、网卡驱动
"""

import os
import sys
import re
import shutil
import subprocess
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)


class SDIODriverExtractor:
    """SDIO 驱动提取器"""
    
    def __init__(self, sdio_dir, output_dir, temp_dir="temp_extract"):
        self.sdio_dir = Path(sdio_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        
        # 创建输出目录结构
        self.raid_dir = self.output_dir / "RAID"
        self.storage_dir = self.output_dir / "Storage"
        self.network_dir = self.output_dir / "Network"
        
        # 统计信息
        self.stats = {
            'raid': 0,
            'storage': 0,
            'network': 0,
            'total_processed': 0
        }
        
        # RAID 关键字
        self.raid_keywords = [
            r'\bRAID\b', r'\braid\b',
            r'\bMegaRAID\b', r'\bMegaraid\b',
            r'\bRAIDXpert\b', r'\braidxpert\b',
            r'\bNVMe RAID\b', r'\bIntel.*RST\b',
            r'\bRapidStorage\b', r'\bRST\b',
            r'\bVROC\b', r'\bvroc\b',
            r'\bSATA RAID\b', r'\bSAS RAID\b',
            r'\bPerc\b', r'\bPERC\b',
            r'\bLSI\b', r'\bAvago\b', r'\bBroadcom.*RAID\b',
            r'\bAdaptec\b', r'\bMicrosemi\b',
            r'\bHighPoint\b', r'\bRocketRAID\b',
            r'\bPromise\b', r'\bFastTrak\b',
            r'\bMarvell.*RAID\b', r'\bArrays\b'
        ]
        
        # 存储控制器关键字
        self.storage_keywords = [
            r'\bAHCI\b', r'\bahci\b',
            r'\bSATA\b', r'\bsata\b',
            r'\bSAS\b', r'\bsas\b',
            r'\bNVMe\b', r'\bnvme\b',
            r'\bIDE\b', r'\bide\b',
            r'\bATAPI\b', r'\batapi\b',
            r'\bSCSI\b', r'\bscsi\b',
            r'\bStorage Controller\b',
            r'\bHost Controller\b',
            r'\bDisk Controller\b'
        ]
        
        # 网卡关键字
        self.network_keywords = [
            r'\bEthernet\b', r'\bethernet\b',
            r'\bNetwork\b', r'\bnetwork\b',
            r'\bLAN\b', r'\blan\b',
            r'\bNIC\b', r'\bnic\b',
            r'\bWireless\b', r'\bwireless\b',
            r'\bWiFi\b', r'\bwifi\b',
            r'\bWLAN\b', r'\bwlan\b',
            r'\b802\.11\b',
            r'\bGigabit\b', r'\b10GbE\b', r'\b10Gigabit\b',
            r'\bIntel.*Network\b', r'\bRealtek.*Network\b',
            r'\bBroadcom.*Network\b', r'\bQualcomm.*Network\b'
        ]
    
    def check_extractor(self):
        """检查解压工具是否可用"""
        # 优先检查 WinRAR 主程序（支持 7z 格式）
        winrar_paths = [
            r"C:\Program Files\WinRAR\WinRAR.exe",
            r"C:\Program Files (x86)\WinRAR\WinRAR.exe"
        ]
        for path in winrar_paths:
            if Path(path).exists():
                return ('winrar', path)
        
        # 检查 7-Zip
        try:
            result = subprocess.run(['7z'], capture_output=True, text=True)
            return ('7zip', '7z')
        except FileNotFoundError:
            seven_zip_paths = [
                r"C:\Program Files\7-Zip\7z.exe",
                r"C:\Program Files (x86)\7-Zip\7z.exe"
            ]
            for path in seven_zip_paths:
                if Path(path).exists():
                    return ('7zip', path)
        
        return (None, None)
    
    def extract_7z(self, archive_path, extract_to, extractor_type, extractor_path):
        """解压 7z 文件"""
        try:
            extract_to = Path(extract_to)
            extract_to.mkdir(parents=True, exist_ok=True)
            
            if extractor_type == 'winrar':
                # WinRAR 命令: WinRAR.exe x -ibck archive.7z extract_to\
                cmd = f'"{extractor_path}" x -ibck "{archive_path}" "{extract_to}\\"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            else:  # 7zip
                cmd = [extractor_path, 'x', str(archive_path), f'-o{extract_to}', '-y']
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                print(f"{Fore.RED}[错误] 解压返回码: {result.returncode}")
                if result.stdout:
                    print(f"{Fore.YELLOW}输出: {result.stdout[:500]}")
                if result.stderr:
                    print(f"{Fore.YELLOW}错误: {result.stderr[:500]}")
            
            return result.returncode == 0
        except Exception as e:
            print(f"{Fore.RED}[错误] 解压失败: {e}")
            return False
    
    def identify_driver_type(self, inf_file):
        """识别驱动类型"""
        try:
            with open(inf_file, 'r', encoding='utf-16-le', errors='ignore') as f:
                content = f.read()
        except:
            try:
                with open(inf_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except:
                return None
        
        # 检查 RAID（优先级最高）
        for pattern in self.raid_keywords:
            if re.search(pattern, content, re.IGNORECASE):
                return 'raid'
        
        # 检查网卡
        for pattern in self.network_keywords:
            if re.search(pattern, content, re.IGNORECASE):
                return 'network'
        
        # 检查存储控制器
        for pattern in self.storage_keywords:
            if re.search(pattern, content, re.IGNORECASE):
                return 'storage'
        
        return None
    
    def copy_driver_package(self, inf_file, driver_type):
        """复制整个驱动包"""
        # 获取驱动包的根目录（包含所有相关文件）
        driver_root = inf_file.parent
        
        # 确定目标目录
        if driver_type == 'raid':
            target_base = self.raid_dir
        elif driver_type == 'storage':
            target_base = self.storage_dir
        elif driver_type == 'network':
            target_base = self.network_dir
        else:
            return False
        
        # 创建目标目录（保持原有的目录结构）
        relative_path = driver_root.relative_to(self.temp_dir)
        target_dir = target_base / relative_path
        
        if target_dir.exists():
            return True  # 已经复制过了
        
        try:
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(driver_root, target_dir, dirs_exist_ok=True)
            return True
        except Exception as e:
            print(f"{Fore.RED}[错误] 复制失败 {driver_root}: {e}")
            return False
    
    def process_archive(self, archive_path, extractor_type, extractor_path):
        """处理单个 7z 压缩包"""
        archive_name = archive_path.name
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}[处理] {archive_name}")
        print(f"{Fore.CYAN}{'='*60}")
        
        # 创建临时解压目录
        extract_dir = self.temp_dir / archive_path.stem
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        # 解压
        print(f"{Fore.YELLOW}[解压中] 正在解压...")
        if not self.extract_7z(archive_path, extract_dir, extractor_type, extractor_path):
            print(f"{Fore.RED}[失败] 解压失败")
            return
        
        # 扫描 .inf 文件
        print(f"{Fore.YELLOW}[扫描中] 正在识别驱动...")
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
        print(f"{Fore.GREEN}[完成] 本包统计:")
        print(f"  ├── RAID 驱动: {archive_stats['raid']} 个")
        print(f"  ├── 存储驱动: {archive_stats['storage']} 个")
        print(f"  ├── 网卡驱动: {archive_stats['network']} 个")
        print(f"  └── 其他驱动: {archive_stats['other']} 个")
        
        # 清理临时文件
        try:
            shutil.rmtree(extract_dir)
        except:
            pass
    
    def run(self):
        """执行提取流程"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}SDIO 驱动提取工具")
        print(f"{Fore.CYAN}{'='*60}")
        
        # 检查解压工具
        print(f"\n{Fore.YELLOW}[检查] 正在检查解压工具...")
        extractor_type, extractor_path = self.check_extractor()
        if not extractor_type:
            print(f"{Fore.RED}[错误] 未找到解压工具（WinRAR 或 7-Zip）")
            print(f"{Fore.YELLOW}请安装以下任意一个:")
            print(f"  - WinRAR: https://www.winrar.com/")
            print(f"  - 7-Zip: https://www.7-zip.org/")
            return False
        
        print(f"{Fore.GREEN}[通过] 使用 {extractor_type.upper()}: {extractor_path}")
        
        # 检查源目录
        if not self.sdio_dir.exists():
            print(f"{Fore.RED}[错误] 源目录不存在: {self.sdio_dir}")
            return False
        
        # 创建目录
        self.raid_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.network_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{Fore.CYAN}[配置]")
        print(f"  源目录: {self.sdio_dir}")
        print(f"  输出目录: {self.output_dir}")
        print(f"  临时目录: {self.temp_dir}")
        
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
            print(f"{Fore.RED}[错误] 未找到目标驱动包")
            return False
        
        print(f"\n{Fore.YELLOW}[信息] 找到 {len(target_archives)} 个目标驱动包")
        for archive in target_archives:
            print(f"  - {archive.name}")
        
        print(f"\n{Fore.GREEN}[开始] 开始提取驱动...")
        
        # 处理每个压缩包
        for i, archive in enumerate(target_archives, 1):
            print(f"\n{Fore.CYAN}【{i}/{len(target_archives)}】")
            self.process_archive(archive, extractor_type, extractor_path)
            self.stats['total_processed'] += 1
        
        # 清理临时目录
        try:
            shutil.rmtree(self.temp_dir)
            print(f"\n{Fore.GREEN}[清理] 已删除临时文件")
        except:
            print(f"\n{Fore.YELLOW}[警告] 无法删除临时目录: {self.temp_dir}")
        
        # 显示总统计
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}[完成] 驱动提取完成")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.WHITE}[总计]")
        print(f"  ├── 处理的压缩包: {self.stats['total_processed']} 个")
        print(f"  ├── RAID 驱动: {self.stats['raid']} 个")
        print(f"  ├── 存储驱动: {self.stats['storage']} 个")
        print(f"  └── 网卡驱动: {self.stats['network']} 个")
        print(f"\n{Fore.CYAN}[输出目录]")
        print(f"  ├── RAID: {self.raid_dir}")
        print(f"  ├── 存储: {self.storage_dir}")
        print(f"  └── 网卡: {self.network_dir}")
        
        return True


def main():
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}使用方法:")
        print(f"  python extract_sdio_drivers.py <SDIO驱动目录> [输出目录]")
        print(f"\n{Fore.CYAN}示例:")
        print(f'  python extract_sdio_drivers.py "外置程序\\SDIO_Update\\drivers"')
        print(f'  python extract_sdio_drivers.py "外置程序\\SDIO_Update\\drivers" "drive\\SDIO_Update"')
        return 1
    
    sdio_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "drive\\SDIO_Update"
    
    extractor = SDIODriverExtractor(sdio_dir, output_dir)
    success = extractor.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

