"""
Utility nodes for ComfyUI
"""

import torch
import numpy as np
from PIL import Image


class ImageScale:
    """Scale image to specified dimensions"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
                "width": ("INT", {"default": 512, "min": 1, "max": 4096}),
                "height": ("INT", {"default": 512, "min": 1, "max": 4096}),
                "crop": (["disabled", "center"], {"default": "disabled"}),
                "upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "bislerp"], {"default": "bilinear"}),
                "downscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "bislerp"], {"default": "bilinear"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "scale"
    CATEGORY = "image"

    def scale(self, image, width, height, crop, upscale_method, downscale_method):
        # Determine if we're upscaling or downscaling
        current_height, current_width = image.shape[1], image.shape[2]
        
        if width == current_width and height == current_height:
            return (image, )
        
        # Choose method based on scaling direction
        if width > current_width or height > current_height:
            method = upscale_method
        else:
            method = downscale_method
        
        # Scale the image
        scaled_image = torch.nn.functional.interpolate(
            image.permute(0, 3, 1, 2),  # Convert to BCHW format
            size=(height, width),
            mode=method.replace("-exact", ""),
            align_corners=False if method in ["bilinear", "bicubic"] else None
        ).permute(0, 2, 3, 1)  # Convert back to BHWC format
        
        return (scaled_image, )


class ImageCrop:
    """Crop image to specified dimensions"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
                "x": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "y": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "width": ("INT", {"default": 512, "min": 1, "max": 4096}),
                "height": ("INT", {"default": 512, "min": 1, "max": 4096}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "crop"
    CATEGORY = "image"

    def crop(self, image, x, y, width, height):
        # Ensure coordinates are within bounds
        x = max(0, min(x, image.shape[2] - 1))
        y = max(0, min(y, image.shape[1] - 1))
        width = min(width, image.shape[2] - x)
        height = min(height, image.shape[1] - y)
        
        # Crop the image
        cropped_image = image[:, y:y+height, x:x+width, :]
        
        return (cropped_image, )


class ImageComposite:
    """Composite two images together"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_to": ("IMAGE", ),
                "image_from": ("IMAGE", ),
                "x": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "y": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "feather": ("INT", {"default": 0, "min": 0, "max": 256}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "composite"
    CATEGORY = "image"

    def composite(self, image_to, image_from, x, y, feather):
        # Create output image
        output_image = image_to.clone()
        
        # Get dimensions
        to_height, to_width = image_to.shape[1], image_to.shape[2]
        from_height, from_width = image_from.shape[1], image_from.shape[2]
        
        # Ensure coordinates are within bounds
        x = max(0, min(x, to_width - 1))
        y = max(0, min(y, to_height - 1))
        
        # Calculate actual crop dimensions
        crop_width = min(from_width, to_width - x)
        crop_height = min(from_height, to_height - y)
        
        if crop_width <= 0 or crop_height <= 0:
            return (output_image, )
        
        # Crop the source image if needed
        if crop_width < from_width or crop_height < from_height:
            image_from = image_from[:, :crop_height, :crop_width, :]
        
        # Composite without feathering
        if feather <= 0:
            output_image[:, y:y+crop_height, x:x+crop_width, :] = image_from
        else:
            # Apply feathering
            feather_mask = torch.ones_like(image_from)
            
            # Create feathering mask
            for i in range(feather):
                feather_mask[:, i, :, :] *= (i + 1) / feather
                feather_mask[:, -i-1, :, :] *= (i + 1) / feather
                feather_mask[:, :, i, :] *= (i + 1) / feather
                feather_mask[:, :, -i-1, :] *= (i + 1) / feather
            
            # Blend with feathering
            existing = output_image[:, y:y+crop_height, x:x+crop_width, :]
            output_image[:, y:y+crop_height, x:x+crop_width, :] = (
                existing * (1 - feather_mask) + image_from * feather_mask
            )
        
        return (output_image, )


class ImageRotate:
    """Rotate image by specified angle"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
                "angle": ("FLOAT", {"default": 0.0, "min": -360.0, "max": 360.0, "step": 0.1}),
                "expand": ("BOOLEAN", {"default": False}),
                "fill_color": ("STRING", {"default": "black"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "rotate"
    CATEGORY = "image"

    def rotate(self, image, angle, expand, fill_color):
        if angle == 0:
            return (image, )
        
        # Convert to PIL Image for rotation
        pil_images = []
        for i in range(image.shape[0]):
            img_array = (image[i].cpu().numpy() * 255).astype(np.uint8)
            pil_img = Image.fromarray(img_array)
            
            # Convert fill color
            if fill_color == "black":
                fill = (0, 0, 0)
            elif fill_color == "white":
                fill = (255, 255, 255)
            else:
                fill = (128, 128, 128)  # Default gray
            
            # Rotate image
            rotated_img = pil_img.rotate(angle, expand=expand, fillcolor=fill)
            
            # Convert back to tensor
            rotated_array = np.array(rotated_img).astype(np.float32) / 255.0
            rotated_tensor = torch.from_numpy(rotated_array)[None, ]
            pil_images.append(rotated_tensor)
        
        # Stack all images
        if len(pil_images) > 1:
            rotated_image = torch.cat(pil_images, dim=0)
        else:
            rotated_image = pil_images[0]
        
        return (rotated_image, )


class ImageFlip:
    """Flip image horizontally or vertically"""
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE", ),
                "flip_method": (["horizontal", "vertical", "both"], {"default": "horizontal"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "flip"
    CATEGORY = "image"

    def flip(self, image, flip_method):
        flipped_image = image.clone()
        
        if flip_method == "horizontal":
            flipped_image = torch.flip(flipped_image, dims=[2])
        elif flip_method == "vertical":
            flipped_image = torch.flip(flipped_image, dims=[1])
        elif flip_method == "both":
            flipped_image = torch.flip(flipped_image, dims=[1, 2])
        
        return (flipped_image, )
