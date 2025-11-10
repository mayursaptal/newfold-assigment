"""Plugin loader for Semantic Kernel plugins.

This module provides automatic discovery and registration of Semantic Kernel
plugins from the plugins directory using Semantic Kernel's built-in methods.

Plugin Structure (Semantic Kernel compatible):
    plugins/
        plugin_name/
            function_name/              # Function subdirectory
                skprompt.txt            # Prompt template (or function_name.skprompt)
                config.json             # Function configuration (optional)

The plugin loader uses Semantic Kernel's built-in `add_plugin` method with
`parent_directory` parameter to automatically load plugins from directories.
This leverages Semantic Kernel's native plugin loading capabilities.

Example:
    plugins/
        chat/
            stream_chat/
                skprompt.txt
                config.json
        film_summary/
            summarize_tool/
                skprompt.txt
                config.json
"""

from pathlib import Path
from typing import Dict, List, Optional
from semantic_kernel.functions import KernelFunction
from semantic_kernel import Kernel
from core.logging import get_logger

logger = get_logger(__name__)

# Default plugins directory (relative to project root)
PLUGINS_DIR = Path("plugins")


def register_all_plugins(
    kernel: Kernel, plugins_dir: Optional[Path] = None, force_reload: bool = False
) -> Dict[str, List[str]]:
    """
    Discover and register all plugins with the kernel using Semantic Kernel's built-in methods.

    Uses `kernel.add_plugin()` with `parent_directory` parameter to automatically
    load plugins from directories. This leverages Semantic Kernel's native plugin
    loading capabilities which expects the structure:

    plugins/
        plugin_name/
            function_name/
                skprompt.txt (or function_name.skprompt)
                config.json

    Args:
        kernel: Semantic Kernel instance
        plugins_dir: Path to plugins directory (defaults to PLUGINS_DIR)
        force_reload: If True, remove existing plugins before registering

    Returns:
        Dictionary mapping plugin names to lists of registered function names
        Format: {plugin_name: [function_name, ...]}
    """
    if plugins_dir is None:
        plugins_dir = PLUGINS_DIR

    # Resolve absolute path
    plugins_dir = Path(plugins_dir).resolve()

    if not plugins_dir.exists():
        logger.warning("Plugins directory not found", plugins_dir=str(plugins_dir))
        return {}

    registered: Dict[str, List[str]] = {}

    # Iterate through plugin directories
    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("__"):
            continue

        plugin_name = plugin_dir.name

        # Remove existing plugin if force_reload is True
        if force_reload:
            try:
                existing_plugin = kernel.get_plugin(plugin_name)
                if existing_plugin:
                    del kernel.plugins[plugin_name]
                    logger.info("Removed existing plugin for reload", plugin=plugin_name)
            except Exception:
                pass  # Plugin doesn't exist, continue

        # Use Semantic Kernel's built-in add_plugin with parent_directory
        try:
            # parent_directory should be the parent of the plugin directory
            # e.g., if plugin is at plugins/chat/, parent_directory should be "plugins" (absolute path)
            parent_dir = str(plugins_dir)

            # Add plugin using Semantic Kernel's native method
            # This will automatically discover all functions in subdirectories
            plugin = kernel.add_plugin(
                plugin_name=plugin_name, parent_directory=parent_dir, encoding="utf-8"
            )

            # Get function names from the registered plugin
            if plugin:
                # Plugin is a KernelPlugin object, access functions via ._functions or iterate
                function_names = []
                if hasattr(plugin, "_functions"):
                    function_names = list(plugin._functions.keys())
                elif hasattr(plugin, "functions"):
                    function_names = list(plugin.functions.keys())
                elif hasattr(plugin, "__iter__"):
                    # Try to iterate if it's iterable
                    try:
                        function_names = [name for name in plugin]
                    except (TypeError, AttributeError):
                        pass

                registered[plugin_name] = function_names
                logger.info(
                    "Registered plugin using Semantic Kernel's add_plugin",
                    plugin=plugin_name,
                    functions=function_names,
                    parent_directory=parent_dir,
                )
            else:
                logger.warning("Plugin registration returned None", plugin=plugin_name)

        except Exception as e:
            logger.error(
                "Failed to register plugin using Semantic Kernel's add_plugin",
                plugin=plugin_name,
                error=str(e),
                error_type=type(e).__name__,
            )

    logger.info(
        "Plugin registration complete",
        plugins_registered=len(registered),
        total_functions=sum(len(funcs) for funcs in registered.values()),
    )

    return registered


def get_plugin_function(
    kernel: Kernel, plugin_name: str, function_name: str
) -> KernelFunction | None:
    """
    Get a registered plugin function from the kernel.

    Args:
        kernel: Semantic Kernel instance
        plugin_name: Name of the plugin
        function_name: Name of the function

    Returns:
        KernelFunction object, or None if not found
    """
    try:
        plugin = kernel.get_plugin(plugin_name)
        if plugin:
            return plugin.get(function_name)
    except Exception as e:
        logger.error(
            "Failed to get plugin function",
            plugin=plugin_name,
            function=function_name,
            error=str(e),
        )
    return None
