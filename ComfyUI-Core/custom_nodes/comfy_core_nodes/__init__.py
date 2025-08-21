"""
ComfyUI Core Nodes Package
"""

import sys
import logging

# 设置日志
logger = logging.getLogger(__name__)

def check_comfy_modules():
    """检查ComfyUI核心模块是否可用"""
    missing_modules = []
    
    required_modules = [
        'comfy.sd',
        'comfy.utils', 
        'comfy.model_management',
        'comfy.samplers',
        'folder_paths',
        'node_helpers'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def safe_import_nodes():
    """安全地导入节点，处理缺失模块的情况"""
    missing_modules = check_comfy_modules()
    
    if missing_modules:
        logger.warning(f"以下ComfyUI模块不可用: {missing_modules}")
        logger.warning("节点包将以受限模式运行，某些功能可能不可用")
        
        # 返回空的映射，避免加载失败
        return {}, {}
    
    try:
        # 导入所有节点类
        from .vae import VAEDecode, VAEEncode, VAEEncodeForInpaint, VAELoader
        from .image import LoadImage, SaveImage, PreviewImage, LoadImageMask
        from .loaders import CheckpointLoaderSimple, VAELoader as LoaderVAELoader, LoraLoader, CLIPLoader, DiffusersLoader, unCLIPCheckpointLoader
        from .conditioning import CLIPTextEncode, ConditioningCombine, ConditioningSetArea, ConditioningAverage, CLIPSetLastLayer
        from .latent import EmptyLatentImage, LatentUpscale, LatentComposite, LatentRotate, LatentFlip
        from .samplers import KSampler, KSamplerAdvanced, KSamplerWithRefiner
        from .utils import ImageScale, ImageCrop, ImageComposite, ImageRotate, ImageFlip
        
        # 创建 NODE_CLASS_MAPPINGS
        NODE_CLASS_MAPPINGS = {
            # VAE nodes
            "VAEDecode": VAEDecode,
            "VAEEncode": VAEEncode,
            "VAEEncodeForInpaint": VAEEncodeForInpaint,
            "VAELoader": VAELoader,
            
            # Image nodes
            "LoadImage": LoadImage,
            "SaveImage": SaveImage,
            "PreviewImage": PreviewImage,
            "LoadImageMask": LoadImageMask,
            
            # Loader nodes
            "CheckpointLoaderSimple": CheckpointLoaderSimple,
            "VAELoader": LoaderVAELoader,  # Alias to avoid conflict
            "LoraLoader": LoraLoader,
            "CLIPLoader": CLIPLoader,
            "DiffusersLoader": DiffusersLoader,
            "unCLIPCheckpointLoader": unCLIPCheckpointLoader,
            
            # Conditioning nodes
            "CLIPTextEncode": CLIPTextEncode,
            "ConditioningCombine": ConditioningCombine,
            "ConditioningSetArea": ConditioningSetArea,
            "ConditioningAverage": ConditioningAverage,
            "CLIPSetLastLayer": CLIPSetLastLayer,
            
            # Latent nodes
            "EmptyLatentImage": EmptyLatentImage,
            "LatentUpscale": LatentUpscale,
            "LatentComposite": LatentComposite,
            "LatentRotate": LatentRotate,
            "LatentFlip": LatentFlip,
            
            # Sampler nodes
            "KSampler": KSampler,
            "KSamplerAdvanced": KSamplerAdvanced,
            "KSamplerWithRefiner": KSamplerWithRefiner,
            
            # Utility nodes
            "ImageScale": ImageScale,
            "ImageCrop": ImageCrop,
            "ImageComposite": ImageComposite,
            "ImageRotate": ImageRotate,
            "ImageFlip": ImageFlip,
        }
        
        # 创建 NODE_DISPLAY_NAME_MAPPINGS
        NODE_DISPLAY_NAME_MAPPINGS = {
            "VAEDecode": "VAE Decode",
            "VAEEncode": "VAE Encode",
            "VAEEncodeForInpaint": "VAE Encode (Inpaint)",
            "VAELoader": "VAE Loader",
            "LoadImage": "Load Image",
            "SaveImage": "Save Image",
            "PreviewImage": "Preview Image",
            "LoadImageMask": "Load Image Mask",
            "CheckpointLoaderSimple": "Checkpoint Loader",
            "LoraLoader": "LoRA Loader",
            "CLIPLoader": "CLIP Loader",
            "DiffusersLoader": "Diffusers Loader",
            "unCLIPCheckpointLoader": "unCLIP Checkpoint Loader",
            "CLIPTextEncode": "CLIP Text Encode",
            "ConditioningCombine": "Conditioning Combine",
            "ConditioningSetArea": "Conditioning Set Area",
            "ConditioningAverage": "Conditioning Average",
            "CLIPSetLastLayer": "CLIP Set Last Layer",
            "EmptyLatentImage": "Empty Latent Image",
            "LatentUpscale": "Latent Upscale",
            "LatentComposite": "Latent Composite",
            "LatentRotate": "Latent Rotate",
            "LatentFlip": "Latent Flip",
            "KSampler": "K Sampler",
            "KSamplerAdvanced": "K Sampler (Advanced)",
            "KSamplerWithRefiner": "K Sampler (Refiner)",
            "ImageScale": "Image Scale",
            "ImageCrop": "Image Crop",
            "ImageComposite": "Image Composite",
            "ImageRotate": "Image Rotate",
            "ImageFlip": "Image Flip",
        }
        
        logger.info(f"成功加载 {len(NODE_CLASS_MAPPINGS)} 个节点")
        return NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
        
    except Exception as e:
        logger.error(f"导入节点时发生错误: {e}")
        logger.error("节点包将无法正常工作")
        return {}, {}

# 尝试导入节点
NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = safe_import_nodes()

# Package metadata
__version__ = "1.0.0"
__author__ = "ComfyUI Engine Team"
__description__ = "Core nodes for ComfyUI - VAE, Image, Loaders, Conditioning, Latent, and Sampler nodes"