#!/usr/bin/env python3

import os
import sys
import asyncio
import logging
import argparse
import threading
import time
import itertools
import shutil
import importlib.util
import gc

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

def apply_custom_paths():
    """Apply custom paths for models and other resources"""
    import folder_paths
    import utils.extra_config
    import itertools
    from comfy.cli_args import args
    
    # extra model paths
    extra_model_paths_config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "extra_model_paths.yaml")
    if os.path.isfile(extra_model_paths_config_path):
        utils.extra_config.load_extra_path_config(extra_model_paths_config_path)

    if args.extra_model_paths_config:
        for config_path in itertools.chain(*args.extra_model_paths_config):
            utils.extra_config.load_extra_path_config(config_path)

    # --output-directory, --input-directory, --user-directory
    if args.output_directory:
        output_dir = os.path.abspath(args.output_directory)
        logging.info(f"Setting output directory to: {output_dir}")
        folder_paths.set_output_directory(output_dir)

    # These are the default folders that checkpoints, clip and vae models will be saved to when using CheckpointSave, etc.. nodes
    folder_paths.add_model_folder_path("checkpoints", os.path.join(folder_paths.get_output_directory(), "checkpoints"))
    folder_paths.add_model_folder_path("clip", os.path.join(folder_paths.get_output_directory(), "clip"))
    folder_paths.add_model_folder_path("vae", os.path.join(folder_paths.get_output_directory(), "vae"))
    folder_paths.add_model_folder_path("diffusion_models",
                                       os.path.join(folder_paths.get_output_directory(), "diffusion_models"))
    folder_paths.add_model_folder_path("loras", os.path.join(folder_paths.get_output_directory(), "loras"))

    if args.input_directory:
        input_dir = os.path.abspath(args.input_directory)
        logging.info(f"Setting input directory to: {input_dir}")
        folder_paths.set_input_directory(input_dir)

    if args.user_directory:
        user_dir = os.path.abspath(args.user_directory)
        logging.info(f"Setting user directory to: {user_dir}")
        folder_paths.set_user_directory(user_dir)
    
    if args.temp_directory:
        temp_dir = os.path.join(os.path.abspath(args.temp_directory), "temp")
        logging.info(f"Setting temp directory to: {temp_dir}")
        folder_paths.set_temp_directory(temp_dir)

def execute_prestartup_script():
    """Execute any prestartup scripts"""
    import folder_paths
    import importlib.util
    from comfy.cli_args import args
    
    if args.disable_all_custom_nodes and len(args.whitelist_custom_nodes) == 0:
        return

    def execute_script(script_path):
        module_name = os.path.splitext(script_path)[0]
        try:
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        except Exception as e:
            logging.error(f"Failed to execute startup-script: {script_path} / {e}")
        return False

    node_paths = folder_paths.get_folder_paths("custom_nodes")
    for custom_node_path in node_paths:
        possible_modules = os.listdir(custom_node_path)
        node_prestartup_times = []

        for possible_module in possible_modules:
            module_path = os.path.join(custom_node_path, possible_module)
            if os.path.isfile(module_path) or module_path.endswith(".disabled") or module_path == "__pycache__":
                continue

            script_path = os.path.join(module_path, "prestartup_script.py")
            if os.path.exists(script_path):
                if args.disable_all_custom_nodes and possible_module not in args.whitelist_custom_nodes:
                    logging.info(f"Prestartup Skipping {possible_module} due to disable_all_custom_nodes and whitelist_custom_nodes")
                    continue
                time_before = time.perf_counter()
                success = execute_script(script_path)
                node_prestartup_times.append((time.perf_counter() - time_before, module_path, success))
    if len(node_prestartup_times) > 0:
        logging.info("\nPrestartup times for custom nodes:")
        for n in sorted(node_prestartup_times):
            if n[2]:
                import_message = ""
            else:
                import_message = " (PRESTARTUP FAILED)"
            logging.info("{:6.1f} seconds{}: {}".format(n[0], import_message, n[1]))
        logging.info("")

def cleanup_temp():
    """Clean up temporary directory"""
    import folder_paths
    import shutil
    temp_dir = folder_paths.get_temp_directory()
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)

async def start_comfyui_core(asyncio_loop=None, args=None):
    """Start ComfyUI Core - minimal runtime without built-in nodes"""
    import folder_paths
    import threading
    import execution
    import time
    import gc
    import comfy.model_management
    
    # Apply custom paths (includes temp directory setup)
    apply_custom_paths()
    
    # Clean up temp directory
    cleanup_temp()
    
    # Execute prestartup script
    execute_prestartup_script()
    
    # Ensure temp directory exists
    os.makedirs(folder_paths.get_temp_directory(), exist_ok=True)
    
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
    
    # Start the prompt worker thread (this was missing!)
    def prompt_worker(q, server_instance):
        current_time: float = 0.0
        cache_type = execution.CacheType.CLASSIC
        if args and hasattr(args, 'cache_lru') and args.cache_lru > 0:
            cache_type = execution.CacheType.LRU
        elif args and hasattr(args, 'cache_none') and args.cache_none:
            cache_type = execution.CacheType.DEPENDENCY_AWARE

        e = execution.PromptExecutor(server_instance, cache_type=cache_type, 
                                   cache_size=getattr(args, 'cache_lru', 0) if args else 0)
        last_gc_collect = 0
        need_gc = False
        gc_collect_interval = 10.0

        while True:
            timeout = 1000.0
            if need_gc:
                timeout = max(gc_collect_interval - (current_time - last_gc_collect), 0.0)

            queue_item = q.get(timeout=timeout)
            if queue_item is not None:
                item, item_id = queue_item
                execution_start_time = time.perf_counter()
                prompt_id = item[1]
                server_instance.last_prompt_id = prompt_id

                e.execute(item[2], prompt_id, item[3], item[4])
                need_gc = True
                q.task_done(item_id,
                            e.history_result,
                            status=execution.PromptQueue.ExecutionStatus(
                                status_str='success' if e.success else 'error',
                                completed=e.success,
                                messages=e.status_messages))
                if server_instance.client_id is not None:
                    server_instance.send_sync("executing", {"node": None, "prompt_id": prompt_id}, server_instance.client_id)

                current_time = time.perf_counter()
                execution_time = current_time - execution_start_time

                # Log Time in a more readable way after 10 minutes
                if execution_time > 600:
                    execution_time = time.strftime("%H:%M:%S", time.gmtime(execution_time))
                    logging.info(f"Prompt executed in {execution_time}")
                else:
                    logging.info("Prompt executed in {:.2f} seconds".format(execution_time))

            flags = q.get_flags()
            free_memory = flags.get("free_memory", False)

            if flags.get("unload_models", free_memory):
                comfy.model_management.unload_all_models()
                need_gc = True
                last_gc_collect = 0

            if free_memory:
                e.reset()
                need_gc = True
                last_gc_collect = 0

            if need_gc:
                current_time = time.perf_counter()
                if (current_time - last_gc_collect) > gc_collect_interval:
                    gc.collect()
                    comfy.model_management.soft_empty_cache()
                    last_gc_collect = current_time
                    need_gc = False

    # Setup progress hook
    def hijack_progress(server_instance):
        import comfy.utils
        from comfy_execution.progress import get_progress_state
        from comfy_execution.utils import get_executing_context
        from comfy_api import feature_flags
        from protocol import BinaryEventTypes
        
        def hook(value, total, preview_image, prompt_id=None, node_id=None):
            executing_context = get_executing_context()
            if prompt_id is None and executing_context is not None:
                prompt_id = executing_context.prompt_id
            if node_id is None and executing_context is not None:
                node_id = executing_context.node_id
            comfy.model_management.throw_exception_if_processing_interrupted()
            if prompt_id is None:
                prompt_id = getattr(server_instance, 'last_prompt_id', None)
            if node_id is None:
                node_id = getattr(server_instance, 'last_node_id', None)
            progress = {"value": value, "max": total, "prompt_id": prompt_id, "node": node_id}
            get_progress_state().update_progress(node_id, value, total, preview_image)

            server_instance.send_sync("progress", progress, server_instance.client_id)
            if preview_image is not None:
                # Only send old method if client doesn't support preview metadata
                if not feature_flags.supports_feature(
                    server_instance.sockets_metadata,
                    server_instance.client_id,
                    "supports_preview_metadata",
                ):
                    server_instance.send_sync(
                        BinaryEventTypes.UNENCODED_PREVIEW_IMAGE,
                        preview_image,
                        server_instance.client_id,
                    )

        comfy.utils.set_progress_bar_global_hook(hook)

    # Setup progress hook
    hijack_progress(server_instance)
    
    # Add routes
    server_instance.add_routes()
    
    # Start the prompt worker thread
    threading.Thread(target=prompt_worker, daemon=True, args=(server_instance.prompt_queue, server_instance,)).start()
    print("ComfyUI-Core: Prompt worker thread started")
    
    # Setup server
    await server_instance.setup()
    
    # Use provided args or defaults
    listen_addr = args.listen if args else "127.0.0.1"
    port = args.port if args else 8188
    verbose = (args.verbose != 'ERROR') if args else True
    
    # Start server and publish loop concurrently
    async def run_server():
        await asyncio.gather(
            server_instance.start(listen_addr, port, verbose=verbose),
            server_instance.publish_loop()
        )
    
    # Keep the server running
    print(f"ComfyUI-Core server starting on {listen_addr}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        await run_server()
    except asyncio.CancelledError:
        print("Server shutdown requested")
        raise

def main():
    """Main entry point"""
    # Enable argument parsing and use the global args from comfy.cli_args
    import comfy.options
    comfy.options.enable_args_parsing()
    from comfy.cli_args import args
    
    # Setup logging based on args
    if args.verbose == 'DEBUG':
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose == 'INFO':
        logging.basicConfig(level=logging.INFO)
    elif args.verbose == 'WARNING':
        logging.basicConfig(level=logging.WARNING)
    elif args.verbose == 'ERROR':
        logging.basicConfig(level=logging.ERROR)
    elif args.verbose == 'CRITICAL':
        logging.basicConfig(level=logging.CRITICAL)
    else:
        logging.basicConfig(level=logging.INFO)
    
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