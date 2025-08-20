"""
Sampler nodes for ComfyUI - Self-contained implementation
"""

# Define sampler constants directly in the plugin
SAMPLERS = [
    "euler", "euler_ancestral", "heun", "dpm_2", "dpm_2_ancestral", 
    "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral", "dpmpp_sde", 
    "dpmpp_sde_gpu", "dpmpp_2m", "dpmpp_2m_sde", "dpmpp_2m_sde_gpu", 
    "ddim", "uni_pc", "uni_pc_bh2"
]

SCHEDULERS = [
    "normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"
]

def sample_function(*args, **kwargs):
    """Placeholder sample function - implement your own sampling logic here"""
    print("Sample function called - implement your sampling logic")
    return {"samples": None}


class KSampler:
    """Basic K-Sampler for diffusion models"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01}),
                "sampler_name": (SAMPLERS,),
                "scheduler": (SCHEDULERS,),
                "positive": ("CONDITIONING", ),
                "negative": ("CONDITIONING", ),
                "latent_image": ("LATENT", ),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "sampling"

    def sample(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=1.0):
        return sample_function(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise)


class KSamplerAdvanced:
    """Advanced K-Sampler with more control options"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL",),
                "add_noise": (["enable", "disable"], ),
                "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01}),
                "sampler_name": (SAMPLERS,),
                "scheduler": (SCHEDULERS,),
                "positive": ("CONDITIONING", ),
                "negative": ("CONDITIONING", ),
                "latent_image": ("LATENT", ),
                "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                "return_with_leftover_noise": (["disable", "enable"], ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "sampling"

    def sample(self, model, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, start_at_step, end_at_step, return_with_leftover_noise, denoise=1.0):
        force_full_denoise = True
        if return_with_leftover_noise == "enable":
            force_full_denoise = False
        disable_noise = False
        if add_noise == "disable":
            disable_noise = True
        return sample_function(model, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image,
                              denoise=denoise, disable_noise=disable_noise, start_step=start_at_step, last_step=end_at_step,
                              force_full_denoise=force_full_denoise)