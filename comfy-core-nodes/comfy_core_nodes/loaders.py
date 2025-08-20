"""
Core loader nodes for ComfyUI
"""

import os
import sys

# Add ComfyUI modules to path (assuming they're available)
try:
    import comfy.sd
    import comfy.utils
    import folder_paths
except ImportError:
    # If ComfyUI modules not available, create stubs
    print("Warning: ComfyUI modules not found. Creating stubs for development.")
    
    class MockComfy:
        class sd:
            @staticmethod
            def load_checkpoint_guess_config(*args, **kwargs):
                return None, None, None
        
        class utils:
            pass
    
    class MockFolderPaths:
        @staticmethod
        def get_filename_list(folder_type):
            return []
    
    comfy = MockComfy()
    folder_paths = MockFolderPaths()


class CheckpointLoaderSimple:
    """Load Stable Diffusion checkpoint"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"), ),
            }
        }
    
    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load_checkpoint"
    CATEGORY = "loaders"

    def load_checkpoint(self, ckpt_name, output_vae=True, output_clip=True):
        ckpt_path = folder_paths.get_full_path("checkpoints", ckpt_name)
        out = comfy.sd.load_checkpoint_guess_config(
            ckpt_path, 
            output_vae=output_vae, 
            output_clip=output_clip, 
            embedding_directory=folder_paths.get_folder_paths("embeddings")
        )
        return out[:3]


class VAELoader:
    """Load VAE model"""
    
    @staticmethod
    def vae_list():
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
        vae_path = folder_paths.get_full_path("vae", vae_name)
        vae = comfy.sd.VAE(ckpt_path=vae_path)
        return (vae,)


class LoraLoader:
    """Load LoRA model"""
    
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "model": ("MODEL",),
                "clip": ("CLIP", ),
                "lora_name": (folder_paths.get_filename_list("loras"), ),
                "strength_model": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
                "strength_clip": ("FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}),
            }
        }
    
    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "load_lora"
    CATEGORY = "loaders"

    def load_lora(self, model, clip, lora_name, strength_model, strength_clip):
        if strength_model == 0 and strength_clip == 0:
            return (model, clip)

        lora_path = folder_paths.get_full_path("loras", lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path:
                lora = self.loaded_lora[1]
            else:
                temp = self.loaded_lora
                self.loaded_lora = None
                del temp

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            self.loaded_lora = (lora_path, lora)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)
        return (model_lora, clip_lora)


class CLIPLoader:
    """Load CLIP text encoder"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "clip_name": (folder_paths.get_filename_list("clip"), ),
            }
        }
    
    RETURN_TYPES = ("CLIP",)
    FUNCTION = "load_clip"
    CATEGORY = "loaders"

    def load_clip(self, clip_name):
        clip_path = folder_paths.get_full_path("clip", clip_name)
        clip = comfy.sd.load_clip(ckpt_paths=[clip_path], embedding_directory=folder_paths.get_folder_paths("embeddings"))
        return (clip,)