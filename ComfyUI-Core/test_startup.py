#!/usr/bin/env python3
"""
Test script to verify ComfyUI-Core can start without any nodes
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing core module imports...")
    
    try:
        import nodes
        print(f"✓ nodes.py imported - NODE_CLASS_MAPPINGS: {len(nodes.NODE_CLASS_MAPPINGS)}")
    except Exception as e:
        print(f"✗ Failed to import nodes: {e}")
        return False
    
    try:
        import folder_paths
        print("✓ folder_paths imported")
    except Exception as e:
        print(f"✗ Failed to import folder_paths: {e}")
        return False
    
    try:
        import execution
        print("✓ execution imported")
    except Exception as e:
        print(f"✗ Failed to import execution: {e}")
        return False
    
    try:
        import server
        print("✓ server imported")
    except Exception as e:
        print(f"✗ Failed to import server: {e}")
        return False
    
    return True

def test_node_loading():
    """Test custom node loading mechanism"""
    print("\nTesting custom node loading...")
    
    import nodes
    import asyncio
    
    async def test_load():
        await nodes.init_external_custom_nodes()
        print(f"Nodes loaded: {len(nodes.NODE_CLASS_MAPPINGS)}")
        return True
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_load())
        loop.close()
        return result
    except Exception as e:
        print(f"✗ Failed to load custom nodes: {e}")
        return False

def main():
    print("=" * 50)
    print("ComfyUI-Core Startup Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("❌ Import test failed")
        return False
    
    # Test node loading
    if not test_node_loading():
        print("❌ Node loading test failed")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! ComfyUI-Core is ready.")
    print("✅ Server should be able to start with empty node registry.")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)