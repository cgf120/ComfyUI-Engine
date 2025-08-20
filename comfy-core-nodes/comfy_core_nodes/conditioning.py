"""
Conditioning nodes for ComfyUI
"""

try:
    import node_helpers
except ImportError:
    print("Warning: node_helpers not found. Creating stub.")
    
    class MockNodeHelpers:
        @staticmethod
        def conditioning_set_values(conditioning, values, append=False):
            return conditioning
    
    node_helpers = MockNodeHelpers()


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
        tokens = clip.tokenize(text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        return ([[cond, {"pooled_output": pooled}]], )


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