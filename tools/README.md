# 工具说明

本目录包含 WinPE Customizer 的辅助工具集。

## 🔧 工具列表

### extract_sdio_drivers_gui.py - SDIO 驱动提取工具（图形界面）
从 SDIO_Update 驱动包中提取和分类驱动程序。

**功能**:
- 智能识别驱动类型（RAID/存储/网卡）
- 批量处理 7z 压缩包
- 自动分类整理驱动
- 实时进度显示

**使用方法**:
```bash
python extract_sdio_drivers_gui.py
```

**配置**:
- 源目录: SDIO 驱动包目录（包含 .7z 文件）
- 输出目录: 提取后的驱动存放位置
- 临时目录: 解压过程使用的临时空间

---

### extract_sdio_drivers.py - SDIO 驱动提取工具（命令行）
命令行版本的 SDIO 驱动提取工具，适合脚本自动化。

**使用方法**:
```bash
# 基本用法
python extract_sdio_drivers.py <源目录> [输出目录]

# 示例
python extract_sdio_drivers.py "外置程序\SDIO_Update\drivers"
python extract_sdio_drivers.py "外置程序\SDIO_Update\drivers" "drive\SDIO_Update"
```

**前置条件**:
- 安装 WinRAR 或 7-Zip
- Python 3.8+
- colorama 库

---

### scan_drivers.py - 驱动扫描工具
扫描和分析驱动程序目录，生成详细报告。

**功能**:
- 递归扫描驱动目录
- 识别驱动类型和架构
- 生成统计报告
- 检测重复和冲突

**使用方法**:
```bash
# 扫描指定目录
python scan_drivers.py <驱动目录>

# 示例
python scan_drivers.py drive
python scan_drivers.py D:\Drivers
```

**输出信息**:
- 驱动文件总数
- 按类型分类统计
- 架构分布（x64/x86）
- INF 文件列表
- 潜在问题警告

---

## 💡 使用场景

### 场景 1: 准备 SDIO 驱动包
```bash
# 1. 下载最新 SDIO_Update
# 2. 解压到 外置程序\SDIO_Update

# 3. 提取所需驱动
python extract_sdio_drivers_gui.py
# 源目录: 外置程序\SDIO_Update\drivers
# 输出目录: drive\SDIO_Update

# 4. 扫描提取结果
python scan_drivers.py drive\SDIO_Update
```

### 场景 2: 整理现有驱动
```bash
# 扫描现有驱动目录
python scan_drivers.py drive

# 查看统计信息，决定是否需要整理
```

### 场景 3: 批量处理
```python
# batch_extract.py - 批量提取示例
import os
from extract_sdio_drivers import SDIODriverExtractor

sources = [
    "外置程序\\SDIO_Update\\drivers",
    "E:\\Drivers\\SDIO_R817"
]

for source in sources:
    if os.path.exists(source):
        extractor = SDIODriverExtractor(source, "drive\\merged")
        extractor.run()
```

---

## 🔍 驱动识别规则

### RAID 驱动关键字
- RAID, MegaRAID, RAIDXpert
- Intel RST, VROC
- LSI, Avago, Broadcom RAID
- Adaptec, HighPoint
- PERC (Dell)

### 存储驱动关键字
- AHCI, SATA, SAS, NVMe
- IDE, ATAPI, SCSI
- Storage Controller
- Host Controller

### 网卡驱动关键字
- Ethernet, Network, LAN, NIC
- Wireless, WiFi, WLAN, 802.11
- Gigabit, 10GbE, 10Gigabit
- Intel/Realtek/Broadcom Network

---

## ⚙️ 配置选项

### extract_sdio_drivers.py 配置

可以在脚本中修改以下变量：

```python
# 临时目录
temp_dir = "temp_extract"

# 目标驱动包模式
target_patterns = [
    'DP_MassStorage',  # 大容量存储
    'DP_LAN',          # 网卡
    'DP_Chipset'       # 芯片组
]
```

### 添加自定义关键字

```python
# 添加到 raid_keywords 列表
self.raid_keywords.append(r'\bCustomRAID\b')

# 添加到 network_keywords 列表
self.network_keywords.append(r'\bCustomNIC\b')
```

---

## 📊 输出示例

### SDIO 驱动提取输出
```
[处理] DP_MassStorage_23H2_R2310.7z
  [完成] 本包统计:
    ├── RAID 驱动: 45 个
    ├── 存储驱动: 123 个
    ├── 网卡驱动: 0 个
    └── 其他驱动: 89 个

[总计]
  ├── 处理的压缩包: 3 个
  ├── RAID 驱动: 45 个
  ├── 存储驱动: 256 个
  └── 网卡驱动: 189 个
```

### 驱动扫描输出
```
[扫描结果]
  驱动目录: drive
  ├── RAID/     45 个驱动包
  ├── Storage/  256 个驱动包
  └── Network/  189 个驱动包

[架构分布]
  ├── x64: 421 个
  ├── x86: 69 个
  └── 通用: 0 个

[文件统计]
  ├── INF 文件: 490 个
  ├── SYS 文件: 1234 个
  └── CAT 文件: 490 个
```

---

## 🛠️ 故障排除

**Q: 提示找不到解压工具？**
```bash
# 安装 7-Zip
powershell -ExecutionPolicy Bypass -File ..\install_7zip.ps1

# 或手动安装 WinRAR/7-Zip
```

**Q: 驱动识别不准确？**
```
检查 INF 文件内容，添加新的关键字到识别规则中
```

**Q: 处理速度慢？**
```
- 使用 SSD 存储
- 关闭实时杀毒软件
- 减少处理的压缩包数量
```

---

## 📝 开发说明

如需开发自定义工具，可参考现有工具的结构：

```python
class CustomTool:
    def __init__(self, source, target):
        self.source = Path(source)
        self.target = Path(target)
    
    def run(self):
        # 主流程
        pass
    
    def process_file(self, file_path):
        # 处理单个文件
        pass
```

---

## 🤝 贡献

欢迎提交新工具或改进现有工具！

提交前请确保：
1. 代码符合 PEP 8 规范
2. 添加必要的注释和文档
3. 测试通过

