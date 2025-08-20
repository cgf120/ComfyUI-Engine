#!/usr/bin/env python3
"""
Test ComfyUI-Core server startup
"""

import sys
import os
import asyncio
import signal
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

async def test_server_startup():
    """Test that the server can start and respond to basic requests"""
    
    print("Testing ComfyUI-Core server startup...")
    
    # Import after path setup
    import nodes
    import server
    
    # Initialize empty node registry
    await nodes.init_external_custom_nodes()
    print(f"Loaded nodes: {len(nodes.NODE_CLASS_MAPPINGS)}")
    
    # Create server instance
    loop = asyncio.get_event_loop()
    server_instance = server.PromptServer(loop)
    
    # Start server on a test port
    test_port = 8189
    print(f"Starting server on port {test_port}...")
    
    try:
        # Start server (this will run indefinitely)
        await server_instance.start(("127.0.0.1", test_port), verbose=True)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("=" * 50)
    print("ComfyUI-Core Server Test")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Set up signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run the server test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(test_server_startup())
    except KeyboardInterrupt:
        print("\nServer test completed")
    finally:
        loop.close()

if __name__ == "__main__":
    main()