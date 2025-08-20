# ComfyUI-Core

**极简ComfyUI运行时平台 - 无内置节点版本**

## 🎯 概述

ComfyUI-Core是ComfyUI的极简运行时版本，包含：
- ✅ 完整的Web服务器和API
- ✅ 工作流执行引擎
- ✅ WebSocket实时通信
- ✅ 模型管理和设备管理
- ❌ **零内置节点** - 所有功能通过节点包提供

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务器
```bash
python main.py
```

服务器将在 http://127.0.0.1:8188 启动，但**节点面板为空**。

### 3. 安装节点包
```bash
# 安装基础节点包
pip install comfy-core-nodes
install-comfy-core-nodes

# 重启服务器，现在就有完整的ComfyUI功能了
python main.py
```

## 📦 可用节点包

| 包名 | 功能 | 大小 |
|------|------|------|
| `comfy-core-nodes` | 基础节点 (CheckpointLoader, KSampler等) | ~500MB |
| `comfy-controlnet-nodes` | ControlNet功能 | ~100MB |
| `comfy-lora-nodes` | LoRA支持 | ~50MB |
| `comfy-3d-nodes` | 3D模型处理 | ~100MB |
| `comfy-audio-nodes` | 音频处理 | ~150MB |

## 🧪 测试

### 测试基础功能
```bash
python test_startup.py
```

### 测试服务器启动
```bash
# 终端1: 启动服务器
python test_server.py

# 终端2: 测试API
python test_api.py
```

## 📊 体积对比

```
原版ComfyUI:     ~2GB   (包含所有节点和模型)
ComfyUI-Core:    ~50MB  (只有运行时)
+ 基础节点包:     +500MB (按需安装)
```

## 🔧 开发

### 目录结构
```
ComfyUI-Core/
├── main.py              # 启动入口
├── server.py            # Web服务器
├── execution.py         # 执行引擎
├── nodes.py             # 空节点注册表
├── comfy/               # 核心运行时
├── custom_nodes/        # 节点包安装目录
└── requirements.txt     # 最小依赖
```

### 添加自定义节点
1. 将节点包安装到 `custom_nodes/` 目录
2. 重启服务器自动加载

## 🎯 设计理念

- **极简核心**: 只包含运行时必需功能
- **按需扩展**: 通过节点包添加功能
- **完全兼容**: 支持所有现有工作流和插件
- **零破坏**: 现有开发方式继续有效

## 📝 API兼容性

所有ComfyUI API端点完全兼容：
- `/object_info` - 返回已安装节点信息
- `/prompt` - 工作流提交
- `/queue` - 队列管理
- `/history` - 执行历史
- `/system_stats` - 系统状态

## 🔗 相关项目

- [ComfyUI-Core-Frontend](../ComfyUI-Core-Frontend/) - 配套前端
- [comfy-core-nodes](https://pypi.org/project/comfy-core-nodes/) - 基础节点包
- [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) - 节点包管理器