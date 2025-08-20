"""
VAE nodes for ComfyUI
"""

import torch
import numpy as np
from PIL import Image

try:
    import comfy.model_management
    import comfy.utils
except ImportError:
    print("Warning: ComfyUI VAE modules not found. Creating stubs.")
    
    class MockModelManagement:
        @staticmethod
        def get_torch_device():
            return "cpu"
        
        @staticmethod
        def intermediate_device():
            return "cpu"
    
    class MockUtils:
        @staticmethod
        def common_upscale(*args, **kwargs):
            return None
    
    comfy = type('MockComfy', (), {
        'model_management': MockModelManagement(),
        'utils': MockUtils()
    })()


class VAEDecode:
    """Decode latent to image using VAE"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "samples": ("LATENT", ), 
                "vae": ("VAE", )
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "decode"
    CATEGORY = "latent"

    def decode(self, vae, samples):
        return (vae.decode(samples["samples"]), )


class VAEEncode:
    """Encode image to latent using VAE"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "pixels": ("IMAGE", ), 
                "vae": ("VAE", )
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "encode"
    CATEGORY = "latent"

    def encode(self, vae, pixels):
        t = vae.encode(pixels[:,:,:,:3])
        return ({"samples":t}, )


class VAEEncodeForInpaint:
    """Encode image for inpainting using VAE"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "pixels": ("IMAGE", ), 
                "vae": ("VAE", ), 
                "mask": ("MASK", )
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "encode"
    CATEGORY = "latent"

    def encode(self, vae, pixels, mask):
        x = (pixels.shape[1] // vae.downscale_ratio) * vae.downscale_ratio
        y = (pixels.shape[2] // vae.downscale_ratio) * vae.downscale_ratio
        mask = torch.nn.functional.interpolate(mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])), size=(pixels.shape[1], pixels.shape[2]), mode="bilinear")

        pixels = pixels.clone()
        if pixels.shape[1] != x or pixels.shape[2] != y:
            x_offset = (pixels.shape[1] % vae.downscale_ratio) // 2
            y_offset = (pixels.shape[2] % vae.downscale_ratio) // 2
            pixels = pixels[:,x_offset:x + x_offset, y_offset:y + y_offset,:]
            mask = mask[:,:,x_offset:x + x_offset, y_offset:y + y_offset]

        #grow mask by a few pixels to keep things seamless in latent space
        kernel_tensor = torch.ones((1, 1, 6, 6))
        mask_erosion = torch.clamp(torch.nn.functional.conv2d(mask.round(), kernel_tensor, padding=3), 0, 1)

        m = (1.0 - mask.round()).squeeze(1)
        for i in range(3):
            pixels[:,:,:,i] -= 0.5
            pixels[:,:,:,i] *= m
            pixels[:,:,:,i] += 0.5
        t = vae.encode(pixels)

        return ({"samples":t, "noise_mask": (mask_erosion[:,:,:x,:y].round())}, )