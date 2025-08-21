"""
VAE nodes for ComfyUI
"""

import torch
import numpy as np
from PIL import Image

# 导入真实的ComfyUI模块
import comfy.model_management
import comfy.utils


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
        images = vae.decode(samples["samples"])
        if len(images.shape) == 5:  # Combine batches
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
        return (images, )


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
                "mask": ("MASK", ),
                "grow_mask_by": ("INT", {"default": 6, "min": 0, "max": 64, "step": 1})
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "encode"
    CATEGORY = "latent/inpaint"

    def encode(self, vae, pixels, mask, grow_mask_by=6):
        x = (pixels.shape[1] // vae.downscale_ratio) * vae.downscale_ratio
        y = (pixels.shape[2] // vae.downscale_ratio) * vae.downscale_ratio
        mask = torch.nn.functional.interpolate(mask.reshape((-1, 1, mask.shape[-2], mask.shape[-1])), size=(pixels.shape[1], pixels.shape[2]), mode="bilinear")

        pixels = pixels.clone()
        if pixels.shape[1] != x or pixels.shape[2] != y:
            x_offset = (pixels.shape[1] % vae.downscale_ratio) // 2
            y_offset = (pixels.shape[2] % vae.downscale_ratio) // 2
            pixels = pixels[:,x_offset:x + x_offset, y_offset:y + y_offset,:]
            mask = mask[:,:,x_offset:x + x_offset, y_offset:y + y_offset]

        # Grow mask by a few pixels to keep things seamless in latent space
        kernel_tensor = torch.ones((1, 1, grow_mask_by * 2 + 1, grow_mask_by * 2 + 1))
        mask_erosion = torch.clamp(torch.nn.functional.conv2d(mask.round(), kernel_tensor, padding=grow_mask_by), 0, 1)

        m = (1.0 - mask.round()).squeeze(1)
        for i in range(3):
            pixels[:,:,:,i] -= 0.5
            pixels[:,:,:,i] *= m
            pixels[:,:,:,i] += 0.5
        t = vae.encode(pixels)

        return ({"samples":t, "noise_mask": (mask_erosion[:,:,:x,:y].round())}, )


class VAELoader:
    """Load VAE model"""
    
    @staticmethod
    def vae_list():
        import folder_paths
        return folder_paths.get_filename_list("vae")
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "vae_name": (s.vae_list(), ),
            }
        }
    
    RETURN_TYPES = ("VAE",)
    FUNCTION = "load_vae"
    CATEGORY = "loaders"

    def load_vae(self, vae_name):
        import folder_paths
        import comfy.sd
        vae_path = folder_paths.get_full_path("vae", vae_name)
        vae = comfy.sd.VAE(ckpt_path=vae_path)
        return (vae,)