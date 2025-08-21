"""
Sampler nodes for ComfyUI
"""

import torch
import comfy.samplers
import comfy.sample
import comfy.model_management


class KSampler:
    """KSampler for Stable Diffusion"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                     "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                     "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01}),
                     "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                     "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                     "positive": ("CONDITIONING", ),
                     "negative": ("CONDITIONING", ),
                     "latent_image": ("LATENT", ),
                     "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                     "model": ("MODEL", ),
                     "positive_2": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "negative_2": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "positive_3": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "negative_3": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "positive_4": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "negative_4": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "positive_5": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "negative_5": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "positive_6": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "negative_6": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "positive_7": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "negative_7": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "positive_8": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "negative_8": ("CONDITIONING", {"default": None, "forceInput": False}),
                     "add_noise": ("BOOLEAN", {"default": True}),
                     "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                     "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                     "return_with_leftover_noise": ("BOOLEAN", {"default": False}),
                     }
                }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "sampling"

    def sample(self, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise, model, positive_2=None, negative_2=None, positive_3=None, negative_3=None, positive_4=None, negative_4=None, positive_5=None, negative_5=None, positive_6=None, negative_6=None, positive_7=None, negative_7=None, positive_8=None, negative_8=None, add_noise=True, start_at_step=0, end_at_step=10000, return_with_leftover_noise=False):
        # Collect all positive and negative conditionings
        positive_conditionings = [positive]
        negative_conditionings = [negative]
        
        for pos, neg in [(positive_2, negative_2), (positive_3, negative_3), (positive_4, negative_4), 
                         (positive_5, negative_5), (positive_6, negative_6), (positive_7, negative_7), 
                         (positive_8, negative_8)]:
            if pos is not None:
                positive_conditionings.append(pos)
            if neg is not None:
                negative_conditionings.append(neg)
        
        # Combine all conditionings
        if len(positive_conditionings) > 1:
            positive = positive_conditionings[0]
            for pos in positive_conditionings[1:]:
                positive = positive + pos
        
        if len(negative_conditionings) > 1:
            negative = negative_conditionings[0]
            for neg in negative_conditionings[1:]:
                negative = negative + neg
        
        # Create sampler
        sampler = comfy.samplers.KSampler(model, steps=steps, device=comfy.model_management.get_torch_device(), sampler=sampler_name, scheduler=scheduler, denoise=denoise, model_options={"transformer_options": {"cond_overrides": None}})
        
        # Sample
        samples = sampler.sample(model, seed, positive, negative, latent_image, denoise=denoise, add_noise=add_noise, start_at_step=start_at_step, end_at_step=end_at_step, return_with_leftover_noise=return_with_leftover_noise)
        
        return (samples, )


class KSamplerAdvanced:
    """Advanced KSampler with more options"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                     "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                     "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01}),
                     "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                     "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                     "positive": ("CONDITIONING", ),
                     "negative": ("CONDITIONING", ),
                     "latent_image": ("LATENT", ),
                     "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                     "model": ("MODEL", ),
                     "add_noise": ("BOOLEAN", {"default": True}),
                     "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                     "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                     "return_with_leftover_noise": ("BOOLEAN", {"default": False}),
                     "preview_method": (["auto", "latent2rgb", "taesd", "none"], ),
                     "vae_decode": ("BOOLEAN", {"default": True}),
                     "vae": ("VAE", {"default": None, "forceInput": False}),
                     }
                }

    RETURN_TYPES = ("LATENT", "IMAGE")
    FUNCTION = "sample"
    CATEGORY = "sampling"

    def sample(self, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise, model, add_noise=True, start_at_step=0, end_at_step=10000, return_with_leftover_noise=False, preview_method="auto", vae_decode=True, vae=None):
        # Create sampler
        sampler = comfy.samplers.KSampler(model, steps=steps, device=comfy.model_management.get_torch_device(), sampler=sampler_name, scheduler=scheduler, denoise=denoise, model_options={"transformer_options": {"cond_overrides": None}})
        
        # Sample
        samples = sampler.sample(model, seed, positive, negative, latent_image, denoise=denoise, add_noise=add_noise, start_at_step=start_at_step, end_at_step=end_at_step, return_with_leftover_noise=return_with_leftover_noise)
        
        # Preview image
        preview_image = None
        if vae_decode and vae is not None:
            preview_image = vae.decode(samples["samples"])
            if len(preview_image.shape) == 5:  # Combine batches
                preview_image = preview_image.reshape(-1, preview_image.shape[-3], preview_image.shape[-2], preview_image.shape[-1])
        
        return (samples, preview_image)


class KSamplerWithRefiner:
    """KSampler with refiner support"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                     "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                     "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01}),
                     "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                     "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                     "positive": ("CONDITIONING", ),
                     "negative": ("CONDITIONING", ),
                     "latent_image": ("LATENT", ),
                     "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                     "model": ("MODEL", ),
                     "refiner_strength": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                     "refiner_model": ("MODEL", ),
                     "refiner_positive": ("CONDITIONING", ),
                     "refiner_negative": ("CONDITIONING", ),
                     "add_noise": ("BOOLEAN", {"default": True}),
                     }
                }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "sampling"

    def sample(self, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise, model, refiner_strength, refiner_model, refiner_positive, refiner_negative, add_noise=True):
        # First pass with base model
        sampler = comfy.samplers.KSampler(model, steps=steps, device=comfy.model_management.get_torch_device(), sampler=sampler_name, scheduler=scheduler, denoise=denoise, model_options={"transformer_options": {"cond_overrides": None}})
        samples = sampler.sample(model, seed, positive, negative, latent_image, denoise=denoise, add_noise=add_noise)
        
        # Second pass with refiner if strength > 0
        if refiner_strength > 0 and refiner_model is not None:
            refiner_sampler = comfy.samplers.KSampler(refiner_model, steps=steps, device=comfy.model_management.get_torch_device(), sampler=sampler_name, scheduler=scheduler, denoise=refiner_strength, model_options={"transformer_options": {"cond_overrides": None}})
            samples = refiner_sampler.sample(refiner_model, seed, refiner_positive, refiner_negative, samples, denoise=refiner_strength, add_noise=False)
        
        return (samples, )