#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
import argparse
import threading
import time

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

def apply_custom_paths():
    """Apply custom paths for models and other resources"""
    import folder_paths
    # Initialize folder paths - folder_names_and_paths is already initialized in folder_paths.py
    # No need to reassign it here as it's already properly set up

def execute_prestartup_script():
    """Execute any prestartup scripts"""
    pass

async def start_comfyui_core(asyncio_loop=None, args=None):
    """Start ComfyUI Core - minimal runtime without built-in nodes"""
    
    # Apply custom paths
    apply_custom_paths()
    
    # Execute prestartup script
    execute_prestartup_script()
    
    # Import core modules
    import nodes
    import server
    
    # Initialize empty node mappings - all nodes will be loaded via custom_nodes
    print("ComfyUI-Core: Starting with empty node registry...")
    print(f"Built-in nodes: {len(nodes.NODE_CLASS_MAPPINGS)}")
    
    # Load custom nodes (this is where all functionality comes from)
    await nodes.init_external_custom_nodes()
    print(f"Total nodes after loading custom_nodes: {len(nodes.NODE_CLASS_MAPPINGS)}")
    
    # Start the server
    if asyncio_loop is None:
        asyncio_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(asyncio_loop)
    
    server_instance = server.PromptServer(asyncio_loop)
    
    # Use provided args or defaults
    listen_addr = args.listen if args else "127.0.0.1"
    port = args.port if args else 8188
    verbose = args.verbose if args else False
    
    await server_instance.start(listen_addr, port, verbose=verbose)
    
    # Keep the server running
    print(f"ComfyUI-Core server started on {listen_addr}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Keep the event loop running indefinitely
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Server shutdown requested")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ComfyUI Core - Minimal Runtime')
    parser.add_argument('--listen', type=str, default="127.0.0.1", metavar="IP", nargs="?", const="0.0.0.0", help="Specify the IP address to listen on (default: 127.0.0.1). If --listen is provided without an argument, it defaults to 0.0.0.0. (listens on all)")
    parser.add_argument('--port', type=int, default=8188, help="Set the listen port.")
    parser.add_argument('--verbose', action='store_true', help="Enables more debug prints.")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    print("=" * 50)
    print("ComfyUI-Core: Minimal Runtime Starting...")
    print("This version contains NO built-in nodes.")
    print("Install node packages via custom_nodes to add functionality.")
    print("=" * 50)
    
    # Start the async event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(start_comfyui_core(loop, args))
    except KeyboardInterrupt:
        print("\nShutting down ComfyUI-Core...")
    finally:
        loop.close()

if __name__ == "__main__":
    main()