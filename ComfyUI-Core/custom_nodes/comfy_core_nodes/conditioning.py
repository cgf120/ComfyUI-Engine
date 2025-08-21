"""
Conditioning nodes for ComfyUI
"""

# 导入真实的ComfyUI模块
import node_helpers


class CLIPTextEncode:
    """Encode text using CLIP"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": True}), 
                "clip": ("CLIP", )
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "encode"
    CATEGORY = "conditioning"

    def encode(self, clip, text):
        if clip is None:
            raise RuntimeError("ERROR: clip input is invalid: None\n\nIf the clip is from a checkpoint loader node your checkpoint does not contain a valid clip or text encoder model.")
        tokens = clip.tokenize(text)
        return (clip.encode_from_tokens_scheduled(tokens), )


class ConditioningCombine:
    """Combine two conditioning inputs"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_1": ("CONDITIONING", ), 
                "conditioning_2": ("CONDITIONING", )
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "combine"
    CATEGORY = "conditioning"

    def combine(self, conditioning_1, conditioning_2):
        return (conditioning_1 + conditioning_2, )


class ConditioningSetArea:
    """Set area for conditioning"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning": ("CONDITIONING", ),
                "width": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 8}),
                "height": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 8}),
                "x": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 8}),
                "y": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 8}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "append"
    CATEGORY = "conditioning"

    def append(self, conditioning, width, height, x, y, strength):
        c = node_helpers.conditioning_set_values(conditioning, {"area": (height // 8, width // 8, y // 8, x // 8), "strength": strength, "min_sigma": 0.0, "max_sigma": 99.0})
        return (c, )


class ConditioningAverage:
    """Average two conditioning inputs"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_to": ("CONDITIONING", ), 
                "conditioning_from": ("CONDITIONING", ),
                "conditioning_to_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01})
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "addWeighted"
    CATEGORY = "conditioning"

    def addWeighted(self, conditioning_to, conditioning_from, conditioning_to_strength):
        out = []
        if len(conditioning_from) > 1:
            conditioning_to_strength = conditioning_to_strength * 0.5
        for i in range(len(conditioning_to)):
            c1 = conditioning_to[i]
            c2 = conditioning_from[i] if i < len(conditioning_from) else conditioning_from[-1]
            if len(c1) != len(c2):
                c1 = c1[0]
                c2 = c2[0]
            out.append([c1, c2, conditioning_to_strength])
        return (out, )


class CLIPSetLastLayer:
    """Set last layer for CLIP"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "clip": ("CLIP", ),
                "stop_at_clip_layer": ("INT", {"default": -1, "min": -24, "max": -1, "step": 1}),
            }
        }
    
    RETURN_TYPES = ("CLIP",)
    FUNCTION = "set_last_layer"
    CATEGORY = "conditioning"

    def set_last_layer(self, clip, stop_at_clip_layer):
        clip = clip.clone()
        clip.clip_layer(stop_at_clip_layer)
        return (clip,)