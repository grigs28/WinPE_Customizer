# WinPE Customizer

<div align="center">

**Windows PE 定制工具 - Professional WinPE Customization Tool**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-Educational-green.svg)](#)

[English](#english) | [中文](#chinese)

</div>

---

<a name="chinese"></a>

## 📖 简介

WinPE Customizer 是一款专业的 Windows PE 定制工具套件，提供图形化界面和命令行两种操作方式，可以自动化创建、定制和打包 Windows PE 启动映像。

### 核心功能

- 🎯 **一键式流程** - 全自动化创建和定制 WinPE
- 🔧 **分步执行** - 灵活控制每个定制步骤
- 🖥️ **图形界面** - 直观易用的 GUI 操作
- 📦 **驱动集成** - 批量安装 RAID、存储、网卡驱动
- 🌏 **中文支持** - 完整的中文界面和字体支持
- 🔌 **插件扩展** - 支持 PowerShell、.NET Framework 等组件
- 💾 **ISO生成** - 直接生成可启动 ISO 文件

### 工具套件

| 工具 | 说明 | 用途 |
|------|------|------|
| **WinPE_Customizer_GUI.py** | 主程序（图形界面） | WinPE 定制和管理 |
| **WinPE_Customizer.py** | 核心引擎（命令行） | 自动化脚本集成 |
| **extract_sdio_drivers_gui.py** | SDIO 驱动提取工具 | 从 SDIO 包提取驱动 |
| **scan_drivers.py** | 驱动扫描工具 | 分析驱动兼容性 |

## 🚀 快速开始

### 前置要求

⚠️ **重要**: 必须在"部署和映像工具环境"中以管理员身份运行

1. **安装 Windows ADK**
   - 下载地址: [Microsoft Windows ADK](https://learn.microsoft.com/zh-cn/windows-hardware/get-started/adk-install)
   - 确保安装 "部署工具" 和 "Windows PE 附加组件"

2. **Python 环境**
   ```bash
   # Python 3.8 或更高版本
   python --version
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **解压工具** (任选其一)
   - WinRAR: https://www.winrar.com/
   - 7-Zip: https://www.7-zip.org/

### 启动程序

#### 方式 1: 图形界面（推荐）

```bash
# 在"部署和映像工具环境"中运行
python WinPE_Customizer_GUI.py

# 或使用自定义 Python 路径
D:\APP\miniconda3\python.exe WinPE_Customizer_GUI.py
```

#### 方式 2: 命令行

```bash
python WinPE_Customizer.py [WinPE工作目录]
```

#### 方式 3: 批处理文件

```bash
# 双击运行（需管理员权限）
WinPE_Customizer.bat
```

## 📁 项目结构

```
WinPE_work/
├── WinPE_Customizer_GUI.py      # 主程序（图形界面）
├── WinPE_Customizer.py          # 核心引擎（命令行）
├── config.py                     # 配置文件
├── requirements.txt              # Python 依赖
│
├── extract_sdio_drivers.py       # SDIO 驱动提取（CLI）
├── extract_sdio_drivers_gui.py   # SDIO 驱动提取（GUI）
├── scan_drivers.py               # 驱动扫描工具
│
├── umount.bat                    # WIM 卸载工具
├── cleanup.bat                   # 清理工具
│
├── docs/                         # 📚 文档目录
│   ├── 快速参考手册.md
│   ├── 详细使用说明.md
│   ├── 配置说明.md
│   └── 常见问题.md
│
├── 外置程序/                    # 外部工具（不上传）
│   └── SDIO_Update/             # SDIO 驱动包
│
└── drive/                        # 驱动输出（不上传）
    ├── RAID/                     # RAID 驱动
    ├── Storage/                  # 存储控制器
    └── Network/                  # 网卡驱动
```

## 💡 使用示例

### 1. 一键创建中文 WinPE

```python
# 启动 WinPE Customizer
python WinPE_Customizer_GUI.py

# 在图形界面中:
# 1. 配置 WinPE 工作目录
# 2. 选择要安装的模块
# 3. 点击 "一键执行全流程"
```

### 2. 提取 SDIO 驱动

```python
# 启动驱动提取工具
python extract_sdio_drivers_gui.py

# 设置源目录和输出目录
# 点击开始提取
```

### 3. 分步定制流程

在 WinPE Customizer 中切换到"分步执行"标签页：

1. **创建环境** - 初始化 WinPE 工作目录
2. **挂载 WIM** - 挂载 boot.wim 进行编辑
3. **安装功能** - 添加 PowerShell、.NET 等组件
4. **中文化** - 安装语言包和字体
5. **添加驱动** - 集成硬件驱动
6. **生成 ISO** - 创建可启动镜像

## ⚙️ 配置说明

编辑 `config.py` 自定义设置：

```python
# 路径配置
WINPE_DIR = "D:/WinPE_amd64"                 # WinPE 工作目录
DRIVER_DIR = "drive"                          # 驱动目录
OUTPUT_ISO_NAME = "MyCustomWinPE.iso"         # 输出文件名

# 模块开关
ENABLE_FEATURE_PACKS = True      # 安装功能包
ENABLE_LANGUAGE_PACKS = True     # 安装语言包
ENABLE_DRIVERS = True            # 安装驱动
ENABLE_MAKE_ISO = False          # 生成 ISO
```

详细配置说明请查看: [docs/配置说明.md](docs/配置说明.md)

## 📚 文档

- [快速参考手册](docs/快速参考手册.md) - 常用操作速查
- [详细使用说明](docs/详细使用说明.md) - 完整功能说明
- [配置说明](docs/config配置说明.md) - 参数详解
- [常见问题](docs/常见问题.md) - 问题排查
- [驱动管理](docs/推荐驱动清单.md) - 驱动集成指南

## 🛠️ 主要功能

### WinPE 定制

- ✅ 自动创建 WinPE 工作环境
- ✅ 安装 20+ 可选组件（PowerShell、.NET、WMI等）
- ✅ 完整中文化（界面、字体、输入法）
- ✅ 区域设置（时区、语言、键盘布局）
- ✅ 批量驱动集成（递归扫描安装）
- ✅ 自定义程序集成
- ✅ ISO 镜像生成

### 驱动管理

- 🔍 SDIO 驱动包智能提取
- 📊 驱动类型自动识别（RAID/存储/网卡）
- 🏷️ 驱动分类整理
- ⚡ 批量处理 7z 压缩包

### 图形界面

- 📋 主控制面板 - 一键操作
- 🔧 分步执行 - 精细控制
- ⚙️ 配置管理 - 参数设置
- 📝 实时日志 - 过程监控
- 💾 快捷操作 - 挂载/卸载/清理

## 🎯 典型应用场景

1. **系统维护启动盘** - 包含驱动和工具的救援系统
2. **批量部署** - 企业网络部署使用的 WinPE
3. **硬件测试** - 集成诊断工具的测试环境
4. **数据恢复** - 带数据恢复工具的启动盘
5. **服务器维护** - 集成 RAID 驱动的服务器管理盘

## ⚠️ 注意事项

1. **管理员权限** - 必须以管理员身份运行"部署和映像工具环境"
2. **磁盘空间** - 建议至少 10GB 可用空间
3. **Windows ADK** - 必须安装且路径配置正确
4. **驱动兼容性** - 确保驱动与目标系统架构匹配（x64/x86）
5. **保存更改** - 卸载 WIM 时选择 "提交" 以保存修改

## 🔧 故障排除

**Q: 提示 "WIM 需要重新挂载"？**
```bash
# 运行清理工具
cleanup.bat
# 或使用界面中的 "清理 WIM" 按钮
```

**Q: 找不到 Windows ADK？**
- 确认已安装 Windows ADK
- 检查 config.py 中的 CAB_PATH 路径
- 确保路径指向 WinPE_OCs 目录

**Q: 驱动安装失败？**
- 检查驱动架构是否匹配（x64/x86）
- 确认驱动目录包含有效的 .inf 文件
- 查看日志了解具体错误

更多问题请查看: [docs/常见问题.md](docs/常见问题.md)

## 📝 更新日志

### v3.0 (2025-10-20)
- ✨ 新增图形界面 (WinPE_Customizer_GUI.py)
- ✨ 支持分步执行模式
- ✨ 集成 SDIO 驱动提取工具
- ✨ 添加快捷操作按钮（挂载/卸载/清理）
- ✨ 内置帮助文档和使用说明
- 🔧 优化日志输出和颜色显示
- 🔧 改进错误处理和异常捕获

查看完整更新: [docs/更新说明.md](docs/更新说明.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目仅供学习和研究使用。

Windows PE 及相关工具版权归 Microsoft 所有。

---

<a name="english"></a>

## English

### 📖 Description

WinPE Customizer is a professional Windows PE customization tool suite with both GUI and CLI interfaces for automated creation, customization, and packaging of Windows PE boot images.

### 🚀 Quick Start

```bash
# Prerequisites
# 1. Install Windows ADK
# 2. Run in "Deployment and Imaging Tools Environment" (Administrator)

# Install dependencies
pip install -r requirements.txt

# Launch GUI
python WinPE_Customizer_GUI.py

# Or CLI version
python WinPE_Customizer.py
```

### 📚 Documentation

- English documentation: See `docs/` directory
- Microsoft Docs: [WinPE Introduction](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-intro)

### ⚙️ Configuration

Edit `config.py` to customize settings:
- Work directory paths
- Module enable/disable switches
- Feature package lists
- Regional settings

### 🛠️ Features

- ✅ One-click WinPE creation
- ✅ Step-by-step execution mode
- ✅ Driver integration (RAID/Storage/Network)
- ✅ Chinese localization
- ✅ Custom program integration
- ✅ ISO generation

### ⚠️ Requirements

1. **Administrator** - Must run in "Deployment and Imaging Tools Environment" as Administrator
2. **Windows ADK** - Required for DISM and WinPE components
3. **Disk Space** - Minimum 10GB recommended
4. **Python** - Version 3.8 or higher

### 📧 Support

For issues and questions, please open an issue on GitHub.

---

<div align="center">

**Made with ❤️ for System Administrators and IT Professionals**

</div>
