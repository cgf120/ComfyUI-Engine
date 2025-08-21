#!/usr/bin/env python3
"""
ComfyUI Core Nodes Installer

Automatically installs the core nodes package to ComfyUI's custom_nodes directory.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path


def find_comfyui_path():
    """Find ComfyUI installation directory"""
    
    # Check environment variable first
    if 'COMFYUI_PATH' in os.environ:
        path = os.environ['COMFYUI_PATH']
        if os.path.exists(os.path.join(path, 'main.py')):
            return path
    
    # Check common installation locations
    possible_paths = [
        # Current directory and parent directories
        '.',
        '..',
        '../..',
        
        # Common installation paths
        os.path.expanduser('~/ComfyUI'),
        os.path.expanduser('~/ComfyUI-Core'),
        './ComfyUI',
        './ComfyUI-Core',
        '../ComfyUI',
        '../ComfyUI-Core',
        
        # Check if we're already in a ComfyUI directory
        os.getcwd(),
        os.path.dirname(os.getcwd()),
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            # Check for main.py (ComfyUI marker)
            if os.path.exists(os.path.join(path, 'main.py')):
                return os.path.abspath(path)
            
            # Check for custom_nodes directory (might be ComfyUI)
            if os.path.exists(os.path.join(path, 'custom_nodes')):
                return os.path.abspath(path)
    
    return None


def install_to_custom_nodes(comfyui_path, package_path, force=False):
    """Install package to ComfyUI's custom_nodes directory"""
    
    custom_nodes_dir = os.path.join(comfyui_path, 'custom_nodes')
    target_dir = os.path.join(custom_nodes_dir, 'comfy-core-nodes')
    
    # Create custom_nodes directory if it doesn't exist
    if not os.path.exists(custom_nodes_dir):
        os.makedirs(custom_nodes_dir)
        print(f"Created custom_nodes directory: {custom_nodes_dir}")
    
    # Remove existing installation if force is True
    if os.path.exists(target_dir):
        if force:
            print(f"Removing existing installation: {target_dir}")
            shutil.rmtree(target_dir)
        else:
            print(f"Installation already exists: {target_dir}")
            print("Use --force to overwrite existing installation")
            return False
    
    # Copy package files
    print(f"Installing comfy-core-nodes to: {target_dir}")
    shutil.copytree(package_path, target_dir)
    
    # Create __init__.py if it doesn't exist
    init_file = os.path.join(target_dir, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('# ComfyUI Core Nodes Package\n')
            f.write('from .comfy_core_nodes import *\n')
    
    print("✅ Installation completed successfully!")
    print("\nNext steps:")
    print("1. Restart ComfyUI-Core")
    print("2. Check that nodes are loaded in the interface")
    
    return True


def main():
    """Main installer function"""
    
    parser = argparse.ArgumentParser(description='Install ComfyUI Core Nodes')
    parser.add_argument('--comfyui-path', help='Path to ComfyUI installation')
    parser.add_argument('--force', action='store_true', help='Overwrite existing installation')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actually doing it')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("ComfyUI Core Nodes Installer")
    print("=" * 50)
    
    # Find ComfyUI installation
    if args.comfyui_path:
        comfyui_path = args.comfyui_path
    else:
        print("Searching for ComfyUI installation...")
        comfyui_path = find_comfyui_path()
    
    if not comfyui_path:
        print("❌ ComfyUI installation not found!")
        print("\nPlease specify the path manually:")
        print("  install-comfy-core-nodes --comfyui-path /path/to/ComfyUI")
        print("\nOr set the COMFYUI_PATH environment variable:")
        print("  export COMFYUI_PATH=/path/to/ComfyUI")
        return False
    
    print(f"✅ Found ComfyUI at: {comfyui_path}")
    
    # Find package path (where this script is located)
    package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"📦 Package path: {package_path}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No changes will be made")
        target_dir = os.path.join(comfyui_path, 'custom_nodes', 'comfy-core-nodes')
        print(f"Would install to: {target_dir}")
        return True
    
    # Install the package
    success = install_to_custom_nodes(comfyui_path, package_path, args.force)
    
    if success:
        print("\n🎉 ComfyUI Core Nodes installed successfully!")
        return True
    else:
        print("\n❌ Installation failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)