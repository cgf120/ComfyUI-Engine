"""
Latent processing nodes for ComfyUI
"""

import torch

# 导入真实的ComfyUI模块
import comfy.model_management
import comfy.utils


class EmptyLatentImage:
    """Create empty latent image"""
    
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "width": ("INT", {"default": 512, "min": 16, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 512, "min": 16, "max": 4096, "step": 8}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096})
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "generate"
    CATEGORY = "latent"

    def generate(self, width, height, batch_size=1):
        latent = torch.zeros([batch_size, 4, height // 8, width // 8], device=self.device)
        return ({"samples":latent}, )


class LatentUpscale:
    """Upscale latent image"""
    
    upscale_methods = ["nearest-exact", "bilinear", "area", "bicubic", "bislerp"]
    crop_methods = ["disabled", "center"]

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "samples": ("LATENT",), 
                "upscale_method": (s.upscale_methods,),
                "width": ("INT", {"default": 512, "min": 0, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 512, "min": 0, "max": 4096, "step": 8}),
                "crop": (s.crop_methods,)
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "upscale"
    CATEGORY = "latent"

    def upscale(self, samples, upscale_method, width, height, crop):
        if width == 0 and height == 0:
            s = samples
        else:
            s = samples.copy()
            
            if width == 0:
                width = max(1, round(samples["samples"].shape[3] * height / samples["samples"].shape[2]))
            elif height == 0:
                height = max(1, round(samples["samples"].shape[2] * width / samples["samples"].shape[3]))

            s["samples"] = comfy.utils.common_upscale(samples["samples"], width // 8, height // 8, upscale_method, crop)
        return (s,)


class LatentComposite:
    """Composite latent images"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "samples_to": ("LATENT", ),
                "samples_from": ("LATENT", ),
                "x": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 8}),
                "y": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 8}),
                "feather": ("INT", {"default": 0, "min": 0, "max": 256, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "composite"
    CATEGORY = "latent"

    def composite(self, samples_to, samples_from, x, y, feather):
        samples_out = samples_to.copy()
        samples_out["samples"] = samples_to["samples"].clone()
        
        if feather <= 0:
            samples_out["samples"][:,:,y:y+samples_from["samples"].shape[2],x:x+samples_from["samples"].shape[3]] = samples_from["samples"]
        else:
            # Feathering
            samples_out["samples"][:,:,y:y+samples_from["samples"].shape[2],x:x+samples_from["samples"].shape[3]] = samples_from["samples"]
            # Apply feathering mask
            feather_mask = torch.ones_like(samples_from["samples"])
            for i in range(feather):
                feather_mask[:,:,i,:] *= (i + 1) / feather
                feather_mask[:,:,-i-1,:] *= (i + 1) / feather
                feather_mask[:,:,:,i] *= (i + 1) / feather
                feather_mask[:,:,:,-i-1] *= (i + 1) / feather
            
            # Blend with feathering
            samples_out["samples"][:,:,y:y+samples_from["samples"].shape[2],x:x+samples_from["samples"].shape[3]] = (
                samples_out["samples"][:,:,y:y+samples_from["samples"].shape[2],x:x+samples_from["samples"].shape[3]] * (1 - feather_mask) +
                samples_from["samples"] * feather_mask
            )
        
        return (samples_out,)


class LatentRotate:
    """Rotate latent image"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "samples": ("LATENT", ),
                "rotation": (["none", "90°", "180°", "270°"], ),
                "method": (["nearest", "bilinear", "bicubic"], {"default": "bilinear"}),
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "rotate"
    CATEGORY = "latent"

    def rotate(self, samples, rotation, method):
        if rotation == "none":
            return (samples, )
        
        s = samples.copy()
        samples_out = s["samples"]
        
        if rotation == "90°":
            samples_out = torch.rot90(samples_out, k=1, dims=[2, 3])
        elif rotation == "180°":
            samples_out = torch.rot90(samples_out, k=2, dims=[2, 3])
        elif rotation == "270°":
            samples_out = torch.rot90(samples_out, k=3, dims=[2, 3])
        
        s["samples"] = samples_out
        return (s,)


class LatentFlip:
    """Flip latent image"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "samples": ("LATENT", ),
                "flip_method": (["x-axis", "y-axis", "x-axis y-axis"], ),
            }
        }
    
    RETURN_TYPES = ("LATENT",)
    FUNCTION = "flip"
    CATEGORY = "latent"

    def flip(self, samples, flip_method):
        s = samples.copy()
        samples_out = s["samples"]
        
        if "x-axis" in flip_method:
            samples_out = torch.flip(samples_out, dims=[2])
        if "y-axis" in flip_method:
            samples_out = torch.flip(samples_out, dims=[3])
        
        s["samples"] = samples_out
        return (s,)