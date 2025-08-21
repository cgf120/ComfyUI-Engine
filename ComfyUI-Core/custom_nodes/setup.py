#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="comfy-core-nodes",
    version="1.0.0",
    description="ComfyUI Core Nodes Package - Essential nodes for ComfyUI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ComfyUI Team",
    author_email="support@comfyui.com",
    url="https://github.com/comfyanonymous/comfy-core-nodes",
    packages=find_packages(),
    install_requires=[
        "torch",
        "torchvision", 
        "numpy",
        "Pillow",
        "transformers",
        "diffusers",
        "safetensors",
    ],
    entry_points={
        'console_scripts': [
            'install-comfy-core-nodes=comfy_core_nodes.installer:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)