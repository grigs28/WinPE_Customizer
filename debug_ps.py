#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

# 测试PowerShell命令
ps_cmd = '''
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-Disk | Where-Object {$_.BusType -eq 'USB'} | ForEach-Object {
    $disk = $_
    Write-Host "Disk Number: $($disk.Number)"
    Write-Host "FriendlyName: $($disk.FriendlyName)"
    Write-Host "BusType: $($disk.BusType)"
    $partitions = Get-Partition -DiskNumber $disk.Number | Where-Object {$_.DriveLetter}
    Write-Host "Partitions count: $($partitions.Count)"
    foreach ($partition in $partitions) {
        Write-Host "  Partition DriveLetter: $($partition.DriveLetter)"
        $volume = Get-Volume -DriveLetter $partition.DriveLetter
        Write-Host "  Volume Label: $($volume.FileSystemLabel)"
        Write-Host "  Volume Size: $($volume.Size)"
    }
}
'''

print("测试PowerShell命令...")
try:
    result = subprocess.run(['powershell', '-Command', ps_cmd],
                          capture_output=True, text=True, shell=True, encoding='utf-8', errors='replace')
    
    print("STDOUT:")
    print(repr(result.stdout))
    print("\nSTDERR:")
    print(repr(result.stderr))
    print(f"\nReturn code: {result.returncode}")
    
except Exception as e:
    print(f"错误: {e}")
