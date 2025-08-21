# ComfyUI Core Nodes

Essential nodes package for ComfyUI-Core.

## 包含的节点

### 基础加载器
- `CheckpointLoaderSimple` - 加载Stable Diffusion检查点
- `VAELoader` - 加载VAE模型
- `LoraLoader` - 加载LoRA模型
- `CLIPLoader` - 加载CLIP文本编码器

### 采样器
- `KSampler` - 基础采样器
- `KSamplerAdvanced` - 高级采样器

### 图像处理
- `LoadImage` - 加载图像
- `SaveImage` - 保存图像
- `PreviewImage` - 预览图像

### VAE操作
- `VAEDecode` - VAE解码
- `VAEEncode` - VAE编码
- `VAEEncodeForInpaint` - 修复用VAE编码

### 条件控制
- `CLIPTextEncode` - CLIP文本编码
- `ConditioningCombine` - 条件组合
- `ConditioningSetArea` - 设置条件区域

### Latent操作
- `EmptyLatentImage` - 创建空Latent
- `LatentUpscale` - Latent放大

## 安装

```bash
pip install comfy-core-nodes
install-comfy-core-nodes
```

## 使用

安装后重启ComfyUI-Core，所有基础节点将自动可用。

## 依赖

- torch
- torchvision
- numpy
- Pillow
- transformers
- diffusers
- safetensors