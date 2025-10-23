#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
USB驱动器扫描工具
用于扫描和识别USB驱动器
"""

import subprocess
import sys
import json
from pathlib import Path

def get_removable_drives():
    """获取所有USB驱动器列表 - 使用与usb_maker.py相同的实现方法"""
    drives = []
    
    try:
        # 直接使用与usb_maker.py中相同的实现方法，但简化一些
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
                              capture_output=True, text=True, shell=False, encoding='utf-8', errors='replace')
        
        lines = result.stdout.strip().split('\n')
        print(f"PowerShell返回了 {len(lines)} 行数据")
        print(f"Return code: {result.returncode}")
        if result.stderr.strip():
            print(f"STDERR: {repr(result.stderr)}")
        
        # 处理USB驱动器
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            print(f"  行{i}: {line[:50]}...")
            parts = line.split(',')
            if len(parts) >= 4:
                try:
                    device_id = parts[0].strip()
                    volume_name = parts[1].strip()
                    size_gb = parts[2].strip()
                    device_type = parts[3].strip()
                    print(f"    解析结果: {device_id}, {volume_name}, {size_gb}, {device_type}")
                    
                    # 只处理USB驱动器
                    if device_type == "USB闪存盘":
                        drives.append({
                            'drive': device_id,
                            'label': volume_name,
                            'size': f"{size_gb} GB",
                            'type': device_type
                        })
                        print(f"  添加USB驱动器: {device_id} - {volume_name} ({size_gb} GB)")
                        
                except Exception as e:
                    print(f"解析USB驱动器信息失败: {e}")
                    import traceback
                    print(traceback.format_exc())
                    continue
                        
    except Exception as e:
        print(f"获取驱动器列表失败: {e}")
        import traceback
        print(traceback.format_exc())
    
    print(f"get_removable_drives() 最终返回 {len(drives)} 个驱动器")
    return drives

def simple_usb_detection():
    """简单的USB硬盘检测（参考tusb.py）"""
    
    print("USB硬盘检测")
    print("=" * 40)
    
    # 获取USB磁盘信息
    print("1. USB磁盘信息:")
    ps_cmd1 = "Get-Disk | Where-Object {$_.BusType -eq 'USB'} | Format-Table Number, FriendlyName, Size, HealthStatus, OperationalStatus -AutoSize"
    subprocess.run(['powershell', '-Command', ps_cmd1])
    
    # 获取USB磁盘的分区信息
    print("\n2. USB磁盘分区信息:")
    ps_cmd2 = """
    Get-Disk | Where-Object {$_.BusType -eq 'USB'} | ForEach-Object {
        $disk = $_
        Write-Host "磁盘 $($disk.Number): $($disk.FriendlyName)" -ForegroundColor Green
        Get-Partition -DiskNumber $disk.Number | Format-Table PartitionNumber, DriveLetter, Size, Type -AutoSize
    }
    """
    subprocess.run(['powershell', '-Command', ps_cmd2])
    
    # 获取USB驱动器的使用情况
    print("\n3. USB驱动器使用情况:")
    ps_cmd3 = """
    Get-Disk | Where-Object {$_.BusType -eq 'USB'} | ForEach-Object {
        $partitions = Get-Partition -DiskNumber $_.Number | Where-Object {$_.DriveLetter}
        foreach ($partition in $partitions) {
            $volume = Get-Volume -DriveLetter $partition.DriveLetter
            $usedGB = [math]::Round(($volume.Size - $volume.SizeRemaining) / 1GB, 2)
            $totalGB = [math]::Round($volume.Size / 1GB, 2)
            $freeGB = [math]::Round($volume.SizeRemaining / 1GB, 2)
            $percent = [math]::Round($usedGB / $totalGB * 100, 1)
            
            Write-Host "驱动器 $($partition.DriveLetter):" -ForegroundColor Yellow
            Write-Host "  卷标: $($volume.FileSystemLabel)"
            Write-Host "  文件系统: $($volume.FileSystem)"
            Write-Host "  总大小: $totalGB GB"
            Write-Host "  已用: $usedGB GB ($percent%)"
            Write-Host "  可用: $freeGB GB"
            Write-Host ""
        }
    }
    """
    subprocess.run(['powershell', '-Command', ps_cmd3])


if __name__ == "__main__":
    # 测试函数
    print("测试USB驱动器扫描功能...")
    drives = get_removable_drives()
    print(f"\n发现 {len(drives)} 个USB驱动器:")
    for drive in drives:
        print(f"  {drive['drive']} - {drive['label']} ({drive['size']})")
