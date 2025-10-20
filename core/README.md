# 核心模块说明

本目录包含 WinPE Customizer 的核心引擎和配置文件。

## 📦 模块列表

### WinPE_Customizer.py - 核心引擎

WinPE 定制的核心实现，包含所有主要功能。

**主要类**:
```python
class WinPECustomizer:
    """WinPE 定制工具类"""
    
    # 环境管理
    def create_winpe_environment()  # 创建 WinPE 工作环境
    def check_and_mount_wim()       # 挂载 boot.wim
    
    # 组件安装
    def install_feature_packs()     # 安装功能包
    def install_language_packs()    # 安装语言包
    def install_fonts_and_lp()      # 安装字体支持
    def set_regional_settings()     # 配置区域设置
    
    # 驱动和程序
    def install_drivers()           # 批量安装驱动
    def copy_external_apps()        # 复制外置程序
    
    # 完成和打包
    def create_directories()        # 创建自定义目录
    def make_iso()                  # 生成 ISO
    
    # 主流程
    def run()                       # 执行完整流程
```

**使用方法**:

1. **作为模块导入**
```python
from core.WinPE_Customizer import WinPECustomizer
from core import config

# 自定义配置
config.WINPE_DIR = "D:/MyWinPE"
config.ENABLE_DRIVERS = True

# 创建定制器
customizer = WinPECustomizer("D:/MyWinPE")

# 执行
exit_code = customizer.run()
```

2. **命令行运行**
```bash
# 使用批处理文件
WinPE_Customizer.bat D:\WinPE_amd64

# 或直接运行模块
python -m core.WinPE_Customizer D:\WinPE_amd64
```

3. **被GUI调用**
```python
# WinPE_Customizer_GUI.py 中
from core.WinPE_Customizer import WinPECustomizer

class CustomWinPECustomizer(WinPECustomizer):
    # 继承核心类，重定向输出
    pass
```

---

### config.py - 配置文件

所有可配置参数的中央配置文件。

**配置分类**:

#### 1. 路径配置
```python
WINPE_DIR = "D:/WinPE_amd64"              # WinPE 工作目录
CAB_PATH = "C:/Program Files (x86)/..."  # Windows ADK 路径
DRIVER_DIR = "drive"                      # 驱动目录
EXTERNAL_APPS_DIR = "外置程序"           # 外置程序目录
OUTPUT_ISO_NAME = "MyCustomWinPE.iso"     # 输出文件名
```

#### 2. 模块开关
```python
ENABLE_COPYPE_SETUP = True       # 创建 WinPE 环境
ENABLE_AUTO_MOUNT = True         # 自动挂载
ENABLE_FEATURE_PACKS = True      # 安装功能包
ENABLE_LANGUAGE_PACKS = True     # 安装语言包
ENABLE_FONTS_LP = True           # 安装字体
ENABLE_REGIONAL_SETTINGS = True  # 配置区域
ENABLE_DRIVERS = True            # 安装驱动
ENABLE_EXTERNAL_APPS = False     # 复制程序
ENABLE_CREATE_DIRS = False       # 创建目录
ENABLE_MAKE_ISO = False          # 生成 ISO
```

#### 3. 功能包列表
```python
FEATURE_PACKAGES = [
    ("WinPE-WMI", "WMI"),
    ("WinPE-NetFx", ".NET Framework"),
    ("WinPE-PowerShell", "PowerShell"),
    # ...
]
```

#### 4. 语言包列表
```python
LANGUAGE_PACKAGES = [
    ("WinPE-WMI_zh-cn", "WMI 中文"),
    ("WinPE-NetFx_zh-cn", ".NET 中文"),
    # ...
]
```

#### 5. 其他设置
```python
# 区域设置
REGIONAL_SETTINGS = [...]

# 自定义目录
CUSTOM_DIRECTORIES = [...]

# 外置程序列表
EXTERNAL_APPS = [...]

# 高级选项
DISM_TIMEOUT = 600
VERBOSE_DISM_OUTPUT = False
```

**修改配置**:
1. 直接编辑 `core/config.py`
2. 或在图形界面中配置并保存
3. 或使用 `examples/config_example.py` 作为参考

---

### __init__.py - 模块初始化

Python 包初始化文件，使 core 成为可导入的模块。

**导出内容**:
```python
from .WinPE_Customizer import WinPECustomizer
from . import config

__all__ = ['WinPECustomizer', 'config']
__version__ = '3.0'
```

**使用**:
```python
# 方式1: 导入整个模块
import core
customizer = core.WinPECustomizer()

# 方式2: 导入特定类
from core import WinPECustomizer, config

# 方式3: 直接导入
from core.WinPE_Customizer import WinPECustomizer
```

---

## 🔧 开发指南

### 添加新功能

1. 在 `WinPE_Customizer.py` 中添加新方法:
```python
def my_custom_function(self):
    """自定义功能"""
    self.print_info("[开始] 执行自定义功能")
    # ... 实现代码
    self.print_success("[完成] 自定义功能完成")
    return True
```

2. 在 `config.py` 中添加开关:
```python
ENABLE_MY_CUSTOM = True
```

3. 在 `run()` 方法中调用:
```python
if self.enable_my_custom:
    self.my_custom_function()
```

### 修改配置

配置文件使用 Python 代码格式，易于阅读和修改：

```python
# 开启某个功能
ENABLE_FEATURE_PACKS = True

# 添加功能包
FEATURE_PACKAGES.append(("WinPE-NewPackage", "新功能包"))

# 修改路径
WINPE_DIR = "E:/MyWinPE"
```

### 调试建议

1. **查看详细日志**: 设置 `VERBOSE_DISM_OUTPUT = True`
2. **单独测试**: 创建测试脚本调用单个方法
3. **检查 DISM 日志**: `C:\WINDOWS\Logs\DISM\dism.log`

---

## 📚 参考文档

- [详细使用说明](../docs/详细使用说明.md)
- [配置说明](../docs/config配置说明.md)
- [WinPE功能包说明](../docs/WinPE功能包说明.md)

---

**核心模块是整个项目的基础，所有功能都在这里实现！**

