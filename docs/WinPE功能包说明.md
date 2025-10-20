# WinPE 可选功能包详细说明

## 📚 官方参考文档

- [WinPE: Add packages (Optional Components Reference)](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-add-packages--optional-components-reference)
- [WinPE for Windows 11](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-intro)
- [Windows ADK for Windows 11](https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install)

---

## 📦 功能包分类

### 🔷 基础组件

#### WinPE-WMI
**Windows Management Instrumentation (Windows 管理规范)**

- **功能**: WMI 的子集，提供系统信息查询能力
- **用途**: 脚本查询硬件信息、系统状态、进程管理
- **依赖**: 无
- **大小**: ~1 MB
- **是否推荐**: ✅ 强烈推荐（很多组件依赖它）

**示例用法**:
```batch
wmic computersystem get model
wmic bios get serialnumber
```

---

#### WinPE-NetFx
**.NET Framework 运行环境**

- **功能**: .NET Framework 子集（主要是 .NET 4.x）
- **用途**: 运行 .NET 编写的应用程序
- **依赖**: WinPE-WMI
- **大小**: ~70 MB
- **是否推荐**: ✅ 推荐（很多工具需要）

**支持的功能**:
- .NET 应用程序运行
- C# 和 VB.NET 程序
- 部分 WPF 应用

---

#### WinPE-Scripting
**Windows Script Host (脚本宿主环境)**

- **功能**: WSH、VBScript、JScript 支持
- **用途**: 运行 .vbs、.js 脚本
- **依赖**: WinPE-WMI
- **大小**: ~1 MB
- **是否推荐**: ✅ 推荐

**支持的脚本**:
```vbscript
' VBScript 示例
Set objShell = CreateObject("WScript.Shell")
objShell.Run "notepad.exe"
```

---

#### WinPE-HTA
**HTML Application (HTML 应用程序)**

- **功能**: 运行 .hta 应用程序
- **用途**: 创建基于 HTML 的图形界面工具
- **依赖**: WinPE-Scripting
- **大小**: <1 MB
- **是否推荐**: ⚠️ 可选（除非有特定 HTA 工具）

---

### 🔷 PowerShell 组件

#### WinPE-PowerShell
**Windows PowerShell 运行环境**

- **功能**: PowerShell 5.1 或 7.x
- **用途**: 运行 PowerShell 脚本和命令
- **依赖**: WinPE-WMI, WinPE-NetFx, WinPE-Scripting
- **大小**: ~25 MB
- **是否推荐**: ✅ 强烈推荐（现代脚本标准）

**PowerShell 功能**:
```powershell
# 系统信息
Get-ComputerInfo
Get-Disk
Get-Volume

# 文件操作
Get-ChildItem
Copy-Item
```

---

#### WinPE-DismCmdlets
**DISM PowerShell 模块**

- **功能**: DISM 的 PowerShell Cmdlets
- **用途**: 在 PowerShell 中管理 Windows 映像
- **依赖**: WinPE-PowerShell
- **大小**: ~1 MB
- **是否推荐**: ✅ 推荐（如果使用 PowerShell）

**示例**:
```powershell
Get-WindowsImage -ImagePath C:\install.wim
Mount-WindowsImage -ImagePath C:\install.wim -Index 1 -Path C:\mount
```

---

#### WinPE-SecureBootCmdlets
**安全启动 PowerShell 模块**

- **功能**: 管理 UEFI 安全启动
- **用途**: 配置安全启动策略
- **依赖**: WinPE-PowerShell
- **大小**: <1 MB
- **是否推荐**: ⚠️ 可选（企业部署需要）

---

### 🔷 存储和安全组件

#### WinPE-StorageWMI
**存储管理 WMI 提供程序**

- **功能**: 存储管理 API
- **用途**: 管理磁盘、分区、卷
- **依赖**: WinPE-WMI
- **大小**: ~1 MB
- **是否推荐**: ✅ 推荐（磁盘操作必需）

**功能**:
- 磁盘初始化
- 分区创建和删除
- 卷格式化

---

#### WinPE-EnhancedStorage
**增强存储支持**

- **功能**: IEEE 1667 标准存储设备支持
- **用途**: 加密 USB 驱动器支持
- **依赖**: WinPE-WMI
- **大小**: <1 MB
- **是否推荐**: ⚠️ 可选（有加密设备才需要）

---

#### WinPE-SecureStartup
**BitLocker 支持**

- **功能**: BitLocker 驱动器加密
- **用途**: 解锁 BitLocker 加密的驱动器
- **依赖**: WinPE-WMI, WinPE-EnhancedStorage
- **大小**: ~1 MB
- **是否推荐**: ✅ 推荐（访问加密磁盘需要）

**用途**:
```batch
manage-bde -unlock C: -password
manage-bde -status C:
```

---

### 🔷 网络组件

#### WinPE-PPPoE
**PPPoE 拨号上网支持**

- **功能**: Point-to-Point Protocol over Ethernet
- **用途**: ADSL/PPPoE 拨号连接
- **依赖**: 无
- **大小**: ~1 MB
- **是否推荐**: ⚠️ 可选（特定网络环境）

---

#### WinPE-dot3svc
**有线 802.1X 认证**

- **功能**: IEEE 802.1X 有线网络认证
- **用途**: 企业网络认证
- **依赖**: 无
- **大小**: <1 MB
- **是否推荐**: ⚠️ 可选（企业环境需要）

---

#### WinPE-RNDIS
**RNDIS 网络支持 (USB 网络)**

- **功能**: Remote NDIS (USB 网络设备)
- **用途**: 通过 USB 进行网络连接
- **依赖**: 无
- **大小**: <1 MB
- **是否推荐**: ⚠️ 可选（移动设备共享网络）

**应用场景**:
- 手机 USB 网络共享
- USB 转以太网适配器

---

### 🔷 部署和安装组件

#### WinPE-Setup
**Windows 安装程序核心**

- **功能**: Windows Setup 核心组件
- **用途**: Windows 系统安装
- **依赖**: WinPE-WMI, WinPE-SecureStartup
- **大小**: ~5 MB
- **是否推荐**: ⚠️ 可选（仅安装盘需要）

---

#### WinPE-Setup-Client
**客户端安装程序支持**

- **功能**: Windows 客户端（家庭版、专业版）安装
- **用途**: 安装 Windows 10/11 客户端版本
- **依赖**: WinPE-Setup
- **大小**: ~1 MB
- **是否推荐**: ⚠️ 可选（仅安装盘需要）

---

#### WinPE-Setup-Server
**服务器安装程序支持**

- **功能**: Windows Server 安装
- **用途**: 安装 Windows Server
- **依赖**: WinPE-Setup
- **大小**: ~1 MB
- **是否推荐**: ⚠️ 可选（仅服务器安装盘需要）

---

#### WinPE-WDS-Tools
**Windows 部署服务工具**

- **功能**: WDS 客户端工具
- **用途**: 网络批量部署
- **依赖**: WinPE-WMI
- **大小**: ~1 MB
- **是否推荐**: ⚠️ 可选（企业批量部署）

---

### 🔷 其他组件

#### WinPE-FMAPI
**文件管理 API**

- **功能**: 文件管理 API 子集
- **用途**: 高级文件操作
- **依赖**: 无
- **大小**: <1 MB
- **是否推荐**: ⚠️ 可选

---

#### WinPE-MDAC
**数据库访问组件**

- **功能**: Microsoft Data Access Components
- **用途**: 数据库连接（SQL Server、Access）
- **依赖**: WinPE-NetFx
- **大小**: ~2 MB
- **是否推荐**: ⚠️ 可选（数据库操作需要）

---

#### WinPE-LegacySetup
**旧版安装程序支持**

- **功能**: 旧版 Windows 安装支持
- **用途**: 安装 Windows 7/8.1
- **依赖**: WinPE-Setup
- **大小**: <1 MB
- **是否推荐**: ❌ 不推荐（除非需要安装旧系统）

---

#### WinPE-SRT
**系统恢复工具 (SRT)**

- **功能**: 系统恢复工具集
- **用途**: 启动修复、系统还原
- **依赖**: WinPE-WMI, WinPE-SecureStartup
- **大小**: ~2 MB
- **是否推荐**: ✅ 推荐（系统维护盘）

---

#### WinPE-Rejuv
**Windows 恢复环境 (WinRE)**

- **功能**: WinRE 组件
- **用途**: 创建恢复环境
- **依赖**: WinPE-SRT
- **大小**: <1 MB
- **是否推荐**: ⚠️ 可选

---

## 📊 推荐配置方案

### 🟢 最小配置（基础维护）
```python
FEATURE_PACKAGES = [
    ("WinPE-WMI", "WMI"),
    ("WinPE-StorageWMI", "存储管理"),
]
```
**大小**: ~2 MB  
**用途**: 基本磁盘操作

---

### 🟡 标准配置（系统维护）
```python
FEATURE_PACKAGES = [
    ("WinPE-WMI", "WMI"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-Scripting", "脚本宿主"),
    ("WinPE-PowerShell", "PowerShell"),
    ("WinPE-StorageWMI", "存储管理"),
    ("WinPE-SecureStartup", "BitLocker"),
]
```
**大小**: ~100 MB  
**用途**: 日常系统维护、磁盘管理

---

### 🔴 完整配置（专业维护）
```python
FEATURE_PACKAGES = [
    # 基础组件
    ("WinPE-WMI", "WMI"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-Scripting", "脚本宿主"),
    ("WinPE-HTA", "HTML 应用程序"),
    
    # PowerShell
    ("WinPE-PowerShell", "PowerShell"),
    ("WinPE-DismCmdlets", "DISM PowerShell"),
    ("WinPE-SecureBootCmdlets", "安全启动"),
    
    # 存储和安全
    ("WinPE-StorageWMI", "存储管理"),
    ("WinPE-EnhancedStorage", "增强存储"),
    ("WinPE-SecureStartup", "BitLocker"),
    
    # 网络
    ("WinPE-PPPoE", "PPPoE"),
    ("WinPE-dot3svc", "802.1X"),
    ("WinPE-RNDIS", "USB 网络"),
    
    # 其他
    ("WinPE-FMAPI", "文件管理"),
    ("WinPE-MDAC", "数据库"),
    ("WinPE-WDS-Tools", "部署工具"),
    ("WinPE-SRT", "系统恢复"),
]
```
**大小**: ~150 MB  
**用途**: 企业级系统维护和部署

---

## 🔍 依赖关系图

```
WinPE-WMI (基础)
 ├─ WinPE-NetFx
 │   └─ WinPE-PowerShell
 │       ├─ WinPE-DismCmdlets
 │       └─ WinPE-SecureBootCmdlets
 ├─ WinPE-Scripting
 │   └─ WinPE-HTA
 ├─ WinPE-StorageWMI
 ├─ WinPE-EnhancedStorage
 │   └─ WinPE-SecureStartup
 └─ WinPE-Setup
     ├─ WinPE-Setup-Client
     └─ WinPE-Setup-Server
```

---

## 💡 选择建议

### ✅ 必装组件
1. **WinPE-WMI** - 基础依赖
2. **WinPE-StorageWMI** - 磁盘管理
3. **WinPE-SecureStartup** - BitLocker 支持

### 🟢 强烈推荐
1. **WinPE-NetFx** - 很多工具需要
2. **WinPE-PowerShell** - 现代脚本标准
3. **WinPE-Scripting** - 脚本支持

### 🟡 按需选择
1. **WinPE-PPPoE** - 特定网络环境
2. **WinPE-WDS-Tools** - 批量部署
3. **WinPE-MDAC** - 数据库操作

### ❌ 不推荐
1. **WinPE-LegacySetup** - 仅旧系统需要
2. **WinPE-Rejuv** - 特殊用途

---

## 📐 大小对比

| 组件 | 大小 | 占比 |
|------|------|------|
| WinPE-NetFx | ~70 MB | 最大 |
| WinPE-PowerShell | ~25 MB | 较大 |
| WinPE-Setup | ~5 MB | 中等 |
| WinPE-MDAC | ~2 MB | 小 |
| WinPE-WMI | ~1 MB | 小 |
| 其他组件 | <1 MB | 很小 |

---

## 🔗 参考链接

### 官方文档
- [WinPE Optional Components](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-add-packages--optional-components-reference)
- [WinPE: Mount and Customize](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-mount-and-customize)
- [Windows ADK](https://learn.microsoft.com/en-us/windows-hardware/get-started/adk-install)

### 相关工具
- [DISM Documentation](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/dism---deployment-image-servicing-and-management-technical-reference-for-windows)
- [PowerShell in WinPE](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-adding-powershell-support-to-windows-pe)

---

**文档版本**: v1.0  
**更新日期**: 2025-10-20  
**适用于**: Windows ADK for Windows 10/11

