"""
Latent processing nodes for ComfyUI
"""

import torch

try:
    import comfy.model_management
    import comfy.utils
except ImportError:
    print("Warning: ComfyUI latent modules not found. Creating stubs.")
    
    class MockModelManagement:
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