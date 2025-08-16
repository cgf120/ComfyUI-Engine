# ComfyUI Engine - 工作流执行引擎

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ComfyUI Version](https://img.shields.io/badge/ComfyUI-Compatible-2.0+-brightgreen)](https://github.com/comfyanonymous/ComfyUI)

> **这不是一个完整的AI生成工具，而是一个纯粹的工作流执行引擎**  
> 专注于提供基础执行能力，将功能实现完全交给插件系统

## 🚧 项目定位

ComfyUI Engine 是一个**工具级**的工作流执行框架，它只做一件事：可靠地执行AI工作流。就像汽车的发动机，它提供动力但不决定车辆用途。

- ✅ **只包含**：工作流编排界面、执行引擎、API服务、插件系统
- ❌ **不包含**：任何AI模型、图像处理、功能节点或具体业务逻辑

## 🆚 与原版ComfyUI的关键区别

| 特性 | ComfyUI Engine | 原版ComfyUI |
|------|---------------|------------|
| **定位** | 纯工作流执行引擎 | 完整AI生成工具 |
| **核心大小** | <500KB (仅执行框架) | 持续膨胀 |
| **内置节点** | **零** | 数十种 |
| **架构设计** | 引擎与功能完全分离 | 功能与引擎混合 |
| **启动速度** | <1秒 | 随节点增加变慢 |
| **用途** | **构建AI应用的基础** | 直接使用的工具 |

## ✨ 核心能力（仅限）

- [x] 工作流可视化编排界面（前端）
- [x] 节点连接与执行引擎
- [x] 完整API服务（加载/保存工作流、执行控制）
- [x] 执行进度跟踪与日志系统
- [x] 基础文件上传/预览支持
- [x] 插件注册与管理系统
- [x] **100%兼容现有ComfyUI工作流格式**

## 💻 安装与使用

### 安装引擎
```bash
git clone https://github.com/your-username/comfyui-engine.git
cd comfyui-engine
pip install -r requirements.txt
```

### 启动引擎
```bash
python main.py
```
访问 http://localhost:8188 查看空的工作流界面

### 安装功能插件
```bash
# 安装基础节点包
comfy-engine install comfyui-nodes-basic

# 安装SDXL支持
comfy-engine install comfyui-nodes-sdxl

# 安装ControlNet支持
comfy-engine install comfyui-nodes-controlnet
```

## 🧩 插件生态系统示例

| 插件包 | 功能 |
|--------|------|
| `comfyui-nodes-basic` | 基础图像处理节点 |
| `comfyui-nodes-sdxl` | SDXL模型支持 |
| `comfyui-nodes-controlnet` | ControlNet实现 |
| `comfyui-nodes-llm` | LLM工作流节点 |
| `comfyui-nodes-video` | 视频处理能力 |

## 🤖 开发者指南

### 创建插件示例
```python
# my_plugin/__init__.py
from comfy_engine.plugin import EnginePlugin

class MyPlugin(EnginePlugin):
    def register(self, engine):
        # 注册节点
        engine.register_node("MyCustomNode", MyCustomNode)
        
        # 注册API端点
        @engine.api.get("/myplugin/status")
        def status():
            return {"status": "ok"}
```

### 插件标准结构
```
comfyui-nodes-myplugin/
├── __init__.py    # 插件入口
├── nodes/         # 节点实现
│   └── custom.py
├── web/           # 前端扩展
│   └── my-node.js
├── config.json    # 插件元数据
└── requirements.txt
```

## 📄 许可证

本项目基于 MIT 许可证 - 请参阅 [LICENSE](LICENSE) 文件获取详细信息。

---

> ComfyUI Engine - 专注工作流执行，让功能扩展真正自由  
> *一个工具，不是解决方案。*
