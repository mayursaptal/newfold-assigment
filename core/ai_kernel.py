"""Semantic Kernel factory and configuration for Gemini."""

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
    """Get a default kernel instance with settings."""
    return create_kernel()

