# NovaPaw 快速启动指南

## 快速启动（3 种方式）

### 方式 1: 使用 Python 启动脚本（推荐）
```powershell
cd c:\LingLong\NovaStudio\CoPaw
python start.py
```

### 方式 2: 使用批处理文件（最简单）
双击 `start.bat` 或在命令行运行：
```powershell
.\start.bat
```

### 方式 3: 使用命令行
```powershell
# 激活虚拟环境
.\env\Scripts\Activate

# 启动服务
novapaw app
```

## 启动脚本参数

`start.py` 支持以下参数：

```powershell
# 基本启动（仅后端）
python start.py

# 开发模式（前后端同时启动）
python start.py --dev

# 先构建前端再启动
python start.py --build

# 调试模式
python start.py --debug

# 重新安装依赖
python start.py --reinstall

# 查看帮助
python start.py --help
```

## 访问地址

启动成功后，访问以下地址：

- **后端 API**: http://localhost:8088
- **前端界面** (开发模式): http://localhost:5173
- **前端界面** (生产模式): http://localhost:8088

## 常见问题

### 1. 虚拟环境未激活
```powershell
.\env\Scripts\Activate
```

### 2. 依赖未安装
```powershell
pip install -e ".[dev]"
```

### 3. 前端未构建
```powershell
cd console
npm install
npm run build
```

### 4. 端口被占用
修改端口（如果支持）：
```powershell
# 后端端口默认 8088
# 前端开发服务器端口默认 5173
```

## 停止服务

按 `Ctrl+C` 停止服务。

## 日志位置

日志文件位于：`logs/` 目录

## 配置文件

- 主配置：`~/.novapaw/config.json`
- 环境变量：`.env` 文件（如需要）
