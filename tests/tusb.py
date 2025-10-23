import subprocess

def simple_usb_detection():
    """简单的USB硬盘检测"""
    
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

# 运行简单检测
simple_usb_detection()