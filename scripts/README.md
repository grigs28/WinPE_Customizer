# 脚本说明

本目录包含 WinPE Customizer 的辅助脚本。

## 📜 脚本列表

### s.bat - 快速启动脚本（个人配置）
快速启动 WinPE Customizer 图形界面。

**⚠️ 注意**: 此文件不会上传到 Git（包含个人路径配置）

**首次使用**:
```bash
# 1. 复制示例文件
copy s.bat.example s.bat

# 2. 编辑 s.bat，修改 Python 路径
notepad s.bat

# 3. 双击运行
s.bat
```

**配置说明**:
```batch
# 修改为您的 Python 实际路径
D:\APP\miniconda3\python.exe WinPE_Customizer_GUI.py

# 常见路径示例：
# C:\Python310\python.exe
# D:\Anaconda3\python.exe
# python.exe (如果已添加到PATH)
```

---

### s.bat.example - 启动脚本模板
启动脚本的示例模板，复制后修改使用。

**使用方法**:
```bash
# 复制为 s.bat
copy s.bat.example s.bat

# 编辑 Python 路径
notepad s.bat
```

---

### umount.bat - WIM 卸载工具
用于卸载已挂载的 WIM 映像。

**功能**:
- 检测 WIM 挂载状态
- 选择保存或丢弃更改
- 安全卸载映像

**使用方法**:
```bash
# 使用默认 WinPE 目录
umount.bat

# 指定 WinPE 目录
umount.bat D:\WinPE_amd64
```

**选项**:
1. 保存更改并卸载 (/commit)
2. 放弃更改并卸载 (/discard)
3. 取消操作

---

### cleanup.bat - 清理修复工具
清理异常的 WIM 挂载，解决挂载错误。

**功能**:
- 清理 WIM 挂载点
- 修复损坏的映像
- 强制卸载所有挂载

**使用方法**:
```bash
# 直接运行
cleanup.bat
```

**何时使用**:
- 提示"映像需要重新挂载"
- WIM 挂载失败
- DISM 操作异常中断后

**警告**: 此操作会放弃所有未保存的更改！

---

## 🔧 自定义脚本

您可以创建自己的辅助脚本并放在此目录中。

### 示例: 批量生成脚本

```batch
@echo off
REM batch_create.bat - 批量生成多个 WinPE 版本

echo 生成基础版...
cd /d "%~dp0.."
python WinPE_Customizer.py D:\WinPE_Basic

echo 生成完整版...
python WinPE_Customizer.py D:\WinPE_Full

echo 生成服务器版...
python WinPE_Customizer.py D:\WinPE_Server

echo 完成！
pause
```

### 示例: 自动备份脚本

```batch
@echo off
REM backup_config.bat - 备份配置文件

set BACKUP_DIR=backup_%date:~0,4%%date:~5,2%%date:~8,2%
mkdir %BACKUP_DIR%

copy ..\config.py %BACKUP_DIR%\
copy ..\requirements.txt %BACKUP_DIR%\

echo 配置已备份到 %BACKUP_DIR%
pause
```

---

## 💡 使用技巧

1. **首次设置**: 
   - 复制 `s.bat.example` 为 `s.bat`
   - 修改 Python 路径

2. **创建桌面快捷方式**: 
   - 右键 `s.bat` → 发送到 → 桌面快捷方式

3. **以管理员运行**: 
   - 右键脚本 → 以管理员身份运行

4. **多版本管理**:
   - 创建 `s_basic.bat`、`s_server.bat` 等
   - 用于不同的 WinPE 配置

---

## ⚠️ 注意事项

1. **s.bat 不会上传**: 此文件包含个人路径，已添加到 .gitignore
2. **管理员权限**: 所有脚本必须在"部署和映像工具环境"中运行
3. **路径正确性**: 确保 Python 路径和项目路径正确
4. **备份重要数据**: 运行前请备份重要数据

---

## 🔍 故障排除

**Q: 双击 s.bat 没反应？**
```
1. 确认 Python 路径正确
2. 在命令行中手动运行查看错误信息
3. 检查是否在"部署和映像工具环境"中
```

**Q: 提示找不到 Python？**
```
1. 打开 s.bat 检查路径
2. 使用绝对路径
3. 或将 Python 添加到系统 PATH
```

**Q: 如何找到 Python 路径？**
```bash
# 在命令行中运行
where python

# 或
python -c "import sys; print(sys.executable)"
```
