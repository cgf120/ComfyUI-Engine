"""
ComfyUI-Core nodes.py - Minimal node registry
All nodes are loaded via custom_nodes mechanism
"""

import os
import sys
import importlib
import logging
from typing import Dict, Any
import comfy.model_management

# Empty node mappings - all nodes loaded via custom_nodes
NODE_CLASS_MAPPINGS: Dict[str, Any] = {}
NODE_DISPLAY_NAME_MAPPINGS: Dict[str, str] = {}

# Web directory mappings for custom nodes
EXTENSION_WEB_DIRS = {}

# Loaded module directories for custom node manager
LOADED_MODULE_DIRS = {}

def get_module_name(module_path):
    """Get module name from path"""
    return os.path.basename(module_path)

async def load_custom_node(module_path, ignore=set(), module_parent="custom_nodes"):
    """Load a custom node module - compatible with existing mechanism"""
    module_name = get_module_name(module_path)
    
    try:
        # Add to Python path
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        
        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(module_path, "__init__.py"))
        if spec is None:
            # Try importing as a package
            spec = importlib.util.spec_from_file_location(module_name, module_path)
        
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Register node classes
            if hasattr(module, "NODE_CLASS_MAPPINGS"):
                for name, node_cls in module.NODE_CLASS_MAPPINGS.items():
                    if name not in ignore:
                        NODE_CLASS_MAPPINGS[name] = node_cls
                        node_cls.RELATIVE_PYTHON_MODULE = f"{module_parent}.{module_name}"
                        print(f"Loaded node: {name}")
            
            # Register display names
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
            
            # Register web directories
            if hasattr(module, "WEB_DIRECTORY"):
                web_dir = os.path.abspath(os.path.join(module_path, getattr(module, "WEB_DIRECTORY")))
                if os.path.isdir(web_dir):
                    EXTENSION_WEB_DIRS[module_name] = web_dir
            
            return True
            
    except Exception as e:
        logging.error(f"Failed to load custom node {module_path}: {e}")
        return False
    
    return False

async def init_external_custom_nodes():
    """Initialize external custom nodes"""
    custom_nodes_path = os.path.join(os.path.dirname(__file__), "custom_nodes")
    
    if not os.path.exists(custom_nodes_path):
        os.makedirs(custom_nodes_path)
        print(f"Created custom_nodes directory: {custom_nodes_path}")
        return
    
    print(f"Loading custom nodes from: {custom_nodes_path}")
    
    # Load all custom node directories
    for item in os.listdir(custom_nodes_path):
        item_path = os.path.join(custom_nodes_path, item)
        if os.path.isdir(item_path):
            # Check if it's a valid custom node (has __init__.py or .py files)
            if (os.path.exists(os.path.join(item_path, "__init__.py")) or 
                any(f.endswith('.py') for f in os.listdir(item_path))):
                print(f"Loading custom node: {item}")
                await load_custom_node(item_path)

def get_object_info():
    """Get information about all loaded nodes"""
    out = {}
    for x in NODE_CLASS_MAPPINGS:
        try:
            out[x] = {
                "input": NODE_CLASS_MAPPINGS[x].INPUT_TYPES(),
                "output": NODE_CLASS_MAPPINGS[x].RETURN_TYPES,
                "output_is_list": getattr(NODE_CLASS_MAPPINGS[x], "OUTPUT_IS_LIST", [False] * len(NODE_CLASS_MAPPINGS[x].RETURN_TYPES)),
                "output_name": getattr(NODE_CLASS_MAPPINGS[x], "RETURN_NAMES", None),
                "name": NODE_DISPLAY_NAME_MAPPINGS.get(x, x),
                "display_name": NODE_DISPLAY_NAME_MAPPINGS.get(x, x),
                "description": getattr(NODE_CLASS_MAPPINGS[x], "DESCRIPTION", ""),
                "category": getattr(NODE_CLASS_MAPPINGS[x], "CATEGORY", ""),
                "output_node": getattr(NODE_CLASS_MAPPINGS[x], "OUTPUT_NODE", False),
            }
        except Exception as e:
            logging.error(f"Error getting info for node {x}: {e}")
    
    return out

def before_node_execution():
    """Called before node execution - for interrupt checking"""
    comfy.model_management.throw_exception_if_processing_interrupted()

def interrupt_processing(value=True):
    """Interrupt processing - compatible with ComfyUI"""
    comfy.model_management.interrupt_current_processing(value)

# Initialize with empty mappings
print("ComfyUI-Core nodes.py: Initialized with empty node registry")
print("All nodes will be loaded via custom_nodes mechanism")