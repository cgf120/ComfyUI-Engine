#!/usr/bin/env python3
"""
Test ComfyUI-Core API endpoints
"""

import asyncio
import aiohttp
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

async def test_api_endpoints():
    """Test basic API endpoints"""
    
    base_url = "http://127.0.0.1:8189"
    
    async with aiohttp.ClientSession() as session:
        
        # Test /object_info endpoint
        print("Testing /object_info endpoint...")
        try:
            async with session.get(f"{base_url}/object_info") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ /object_info returned {len(data)} nodes")
                    if len(data) == 0:
                        print("✓ Empty node registry as expected")
                    else:
                        print(f"Available nodes: {list(data.keys())}")
                else:
                    print(f"✗ /object_info failed with status {response.status}")
                    return False
        except Exception as e:
            print(f"✗ /object_info error: {e}")
            return False
        
        # Test /queue endpoint
        print("Testing /queue endpoint...")
        try:
            async with session.get(f"{base_url}/queue") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ /queue returned: {data}")
                else:
                    print(f"✗ /queue failed with status {response.status}")
                    return False
        except Exception as e:
            print(f"✗ /queue error: {e}")
            return False
        
        # Test /history endpoint
        print("Testing /history endpoint...")
        try:
            async with session.get(f"{base_url}/history") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ /history returned: {len(data)} items")
                else:
                    print(f"✗ /history failed with status {response.status}")
                    return False
        except Exception as e:
            print(f"✗ /history error: {e}")
            return False
        
        # Test /system_stats endpoint
        print("Testing /system_stats endpoint...")
        try:
            async with session.get(f"{base_url}/system_stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✓ /system_stats returned system info")
                else:
                    print(f"✗ /system_stats failed with status {response.status}")
                    return False
        except Exception as e:
            print(f"✗ /system_stats error: {e}")
            return False
    
    return True

async def main():
    """Main test function"""
    print("=" * 50)
    print("ComfyUI-Core API Test")
    print("Make sure the server is running on port 8189")
    print("=" * 50)
    
    # Wait a bit for server to be ready
    await asyncio.sleep(2)
    
    success = await test_api_endpoints()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ All API tests passed!")
        print("✅ ComfyUI-Core is working correctly with empty node registry")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Some API tests failed")
        print("=" * 50)
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)