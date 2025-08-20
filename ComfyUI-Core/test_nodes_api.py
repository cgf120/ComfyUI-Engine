#!/usr/bin/env python3
"""
Test that ComfyUI-Core API returns loaded nodes
"""

import sys
import os
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

def test_object_info_api():
    """Test /object_info API with loaded nodes"""
    
    print("Testing /object_info API with loaded nodes...")
    
    # Import after path setup
    import nodes
    import asyncio
    
    async def test_load_and_info():
        # Load custom nodes
        await nodes.init_external_custom_nodes()
        print(f"Loaded {len(nodes.NODE_CLASS_MAPPINGS)} nodes")
        
        # Get object info (same as API endpoint)
        object_info = nodes.get_object_info()
        
        print(f"Object info contains {len(object_info)} node types")
        
        # Check some expected nodes
        expected_nodes = [
            "CheckpointLoaderSimple",
            "KSampler", 
            "VAEDecode",
            "CLIPTextEncode",
            "SaveImage",
            "EmptyLatentImage"
        ]
        
        missing_nodes = []
        for node_name in expected_nodes:
            if node_name in object_info:
                print(f"✓ {node_name} found in object_info")
            else:
                print(f"✗ {node_name} missing from object_info")
                missing_nodes.append(node_name)
        
        if missing_nodes:
            print(f"❌ Missing nodes: {missing_nodes}")
            return False
        
        # Print sample node info
        if "CheckpointLoaderSimple" in object_info:
            print("\nSample node info (CheckpointLoaderSimple):")
            print(json.dumps(object_info["CheckpointLoaderSimple"], indent=2))
        
        return True
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_load_and_info())
        loop.close()
        return result
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

def main():
    print("=" * 50)
    print("ComfyUI-Core Nodes API Test")
    print("=" * 50)
    
    success = test_object_info_api()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ All node API tests passed!")
        print("✅ ComfyUI-Core can serve node information correctly")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Node API tests failed")
        print("=" * 50)
    
    return success

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)