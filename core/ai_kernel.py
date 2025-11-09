"""Semantic Kernel factory and configuration for OpenAI.

This module provides factory functions for creating and configuring
Semantic Kernel instances with OpenAI integration. It handles
API key configuration and model setup for AI operations.

Example:
    ```python
    from core.ai_kernel import get_default_kernel
    
    kernel = get_default_kernel()
    # Kernel is configured with OpenAI
    ```
"""

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from typing import Optional, Any
from core.settings import settings
from core.logging import get_logger

logger = get_logger(__name__)

# Singleton kernel instance
_kernel_instance: Optional[Kernel] = None


def create_kernel(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    org_id: Optional[str] = None,
    memory_store: Optional[Any] = None,
) -> Kernel:
    """
    Create and configure a Semantic Kernel instance with OpenAI.
    
    Args:
        api_key: OpenAI API key (defaults to settings)
        model: OpenAI model name (defaults to settings)
        org_id: OpenAI organization ID (defaults to settings, optional)
        memory_store: Optional memory store for TextMemoryPlugin
        
    Returns:
        Configured Kernel instance
    """
    kernel = Kernel()
    
    # Use provided values or fall back to settings
    api_key = api_key or settings.openai_api_key
    model = model or settings.openai_model
    org_id = org_id or settings.openai_org_id
    
    if not api_key:
        logger.warning("OpenAI configuration incomplete. AI features may not work.")
        return kernel
    
    try:
        # Add OpenAI chat completion service to kernel
        # Don't specify service_id - it will use model name as service_id by default
        # This ensures functions can find the service automatically
        service_kwargs = {
            "ai_model_id": model,
            "api_key": api_key,
        }
        
        # Add org_id if provided
        if org_id:
            service_kwargs["org_id"] = org_id
        
        openai_chat_service = OpenAIChatCompletion(**service_kwargs)
        
        kernel.add_service(openai_chat_service)
        
        logger.info("OpenAI configured", 
                   model=model,
                   org_id=org_id[:10] + "..." if org_id else None)
    except ImportError:
        logger.error("OpenAI connector not available. Install semantic-kernel with OpenAI support.")
        return kernel
    except Exception as e:
        logger.error(f"Failed to configure OpenAI: {str(e)}")
        return kernel
    
    # Add memory plugin if memory store is provided
    if memory_store:
        try:
            from semantic_kernel.core_plugins import TextMemoryPlugin
            kernel.add_plugin(TextMemoryPlugin(memory_store), "memory")
        except ImportError:
            logger.warning("TextMemoryPlugin not available in this Semantic Kernel version")
    
    # Auto-register all plugins from plugins directory
    try:
        from core.plugin_loader import register_all_plugins
        register_all_plugins(kernel)
    except Exception as e:
        logger.warning("Failed to register plugins", error=str(e))
    
    return kernel


def get_default_kernel() -> Kernel:
    """Get a default kernel instance with settings.
    
    Creates a singleton Semantic Kernel instance using application settings
    for OpenAI configuration. The kernel is cached after first creation,
    but will be recreated if it has no services (e.g., if settings weren't loaded
    on first creation).
    
    Returns:
        Kernel: Configured kernel instance with OpenAI settings
        
    Example:
        ```python
        kernel = get_default_kernel()
        # Use kernel for AI operations
        ```
    """
    global _kernel_instance
    
    # Return cached instance if it exists and has services
    if _kernel_instance is not None and len(_kernel_instance.services) > 0:
        return _kernel_instance
    
    # Create new kernel instance (or recreate if previous one had no services)
    _kernel_instance = create_kernel()
    
    # If still no services after creation, log warning but return kernel
    if len(_kernel_instance.services) == 0:
        logger.warning("Kernel created but no services were added. Check OpenAI configuration.")
    
    return _kernel_instance
