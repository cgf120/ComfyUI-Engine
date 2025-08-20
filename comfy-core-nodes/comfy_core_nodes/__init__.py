"""
ComfyUI Core Nodes Package

Essential nodes for ComfyUI-Core functionality.
This package contains all the basic nodes needed for standard ComfyUI workflows.
"""

# Import all node classes
from .loaders import CheckpointLoaderSimple, VAELoader, LoraLoader, CLIPLoader
from .samplers import KSampler, KSamplerAdvanced
from .vae import VAEDecode, VAEEncode, VAEEncodeForInpaint
from .conditioning import CLIPTextEncode, ConditioningCombine, ConditioningSetArea
from .image import SaveImage, PreviewImage, LoadImage
from .latent import EmptyLatentImage, LatentUpscale

# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    # Loaders
    "CheckpointLoaderSimple": CheckpointLoaderSimple,
    "VAELoader": VAELoader,
    "LoraLoader": LoraLoader,
    "CLIPLoader": CLIPLoader,
    
    # Samplers
    "KSampler": KSampler,
    "KSamplerAdvanced": KSamplerAdvanced,
    
    # VAE
    "VAEDecode": VAEDecode,
    "VAEEncode": VAEEncode,
    "VAEEncodeForInpaint": VAEEncodeForInpaint,
    
    # Conditioning
    "CLIPTextEncode": CLIPTextEncode,
    "ConditioningCombine": ConditioningCombine,
    "ConditioningSetArea": ConditioningSetArea,
    
    # Image
    "SaveImage": SaveImage,
    "PreviewImage": PreviewImage,
    "LoadImage": LoadImage,
    
    # Latent
    "EmptyLatentImage": EmptyLatentImage,
    "LatentUpscale": LatentUpscale,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CheckpointLoaderSimple": "Load Checkpoint",
    "VAELoader": "Load VAE",
    "LoraLoader": "Load LoRA",
    "CLIPLoader": "Load CLIP",
    "KSampler": "KSampler",
    "KSamplerAdvanced": "KSampler (Advanced)",
    "VAEDecode": "VAE Decode",
    "VAEEncode": "VAE Encode",
    "VAEEncodeForInpaint": "VAE Encode (for Inpainting)",
    "CLIPTextEncode": "CLIP Text Encode (Prompt)",
    "ConditioningCombine": "Conditioning (Combine)",
    "ConditioningSetArea": "Conditioning (Set Area)",
    "SaveImage": "Save Image",
    "PreviewImage": "Preview Image",
    "LoadImage": "Load Image",
    "EmptyLatentImage": "Empty Latent Image",
    "LatentUpscale": "Upscale Latent",
}

# Package info
__version__ = "1.0.0"
__author__ = "ComfyUI Team"
__description__ = "Essential nodes for ComfyUI-Core"