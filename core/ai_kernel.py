"""Semantic Kernel factory and configuration for Gemini.

This module provides factory functions for creating and configuring
Semantic Kernel instances with Google Gemini integration. It handles
API key configuration and model setup for AI operations.

Note:
    Semantic Kernel doesn't have a native Google connector, so this
    module configures the Google Generative AI SDK directly and stores
    configuration in the kernel instance for use by services.

Example:
    ```python
    from core.ai_kernel import get_default_kernel
    
    kernel = get_default_kernel()
    # Kernel is configured with Gemini API key and model
    ```
"""

from semantic_kernel import Kernel
from typing import Optional, Any
from core.settings import settings
from core.logging import get_logger

logger = get_logger(__name__)


def create_kernel(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    memory_store: Optional[Any] = None,
) -> Kernel:
    """
    Create and configure a Semantic Kernel instance with Gemini.
    
    Args:
        api_key: Gemini API key (defaults to settings)
        model: Model name (defaults to settings)
        memory_store: Optional memory store for TextMemoryPlugin
        
    Returns:
        Configured Kernel instance
    """
    kernel = Kernel()
    
    # Use provided values or fall back to settings
    api_key = api_key or settings.gemini_api_key
    model = model or settings.gemini_model
    
    if not api_key:
        logger.warning("Gemini API key not provided. AI features may not work.")
        return kernel
    
    # Use Google Generative AI SDK directly
    try:
        import google.generativeai as genai
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Store the model name and API key for direct use
        # Note: Semantic Kernel doesn't have a native Google connector,
        # so we'll use the Google SDK directly in the service layer
        kernel._gemini_api_key = api_key
        kernel._gemini_model = model
        kernel._gemini_configured = True
        
        logger.info("Gemini API configured", model=model)
    except ImportError:
        logger.error("google-generativeai package not installed. Install it with: pip install google-generativeai")
        return kernel
    except Exception as e:
        logger.error(f"Failed to configure Gemini: {str(e)}")
        return kernel
    
    # Add memory plugin if memory store is provided
    if memory_store:
        try:
            from semantic_kernel.core_plugins import TextMemoryPlugin
            kernel.add_plugin(TextMemoryPlugin(memory_store), "memory")
        except ImportError:
            logger.warning("TextMemoryPlugin not available in this Semantic Kernel version")
    
    return kernel


def get_default_kernel() -> Kernel:
    """Get a default kernel instance with settings.
    
    Creates a Semantic Kernel instance using application settings
    for API key and model configuration.
    
    Returns:
        Kernel: Configured kernel instance with Gemini API settings
        
    Example:
        ```python
        kernel = get_default_kernel()
        # Use kernel for AI operations
        ```
    """
    return create_kernel()

