"""Semantic Kernel factory and configuration."""

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from typing import Optional, Any
from core.settings import settings
from core.logging import get_logger

logger = get_logger(__name__)


def create_kernel(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    model: Optional[str] = None,
    memory_store: Optional[Any] = None,
) -> Kernel:
    """
    Create and configure a Semantic Kernel instance.
    
    Args:
        api_key: OpenAI API key (defaults to settings)
        endpoint: API endpoint (defaults to settings)
        model: Model name (defaults to settings)
        memory_store: Optional memory store for TextMemoryPlugin
        
    Returns:
        Configured Kernel instance
    """
    kernel = Kernel()
    
    # Use provided values or fall back to settings
    api_key = api_key or settings.semantic_kernel_api_key
    endpoint = endpoint or settings.semantic_kernel_endpoint
    model = model or settings.semantic_kernel_model
    
    if not api_key:
        logger.warning("Semantic Kernel API key not provided. AI features may not work.")
        return kernel
    
    # Add OpenAI chat completion service
    service = OpenAIChatCompletion(
        service_id="default",
        ai_model_id=model,
        api_key=api_key,
        endpoint=endpoint,
    )
    
    kernel.add_service(service)
    
    # Add memory plugin if memory store is provided
    # Note: MemoryStoreBase import may vary by Semantic Kernel version
    if memory_store:
        try:
            from semantic_kernel.core_plugins import TextMemoryPlugin
            kernel.add_plugin(TextMemoryPlugin(memory_store), "memory")
        except ImportError:
            logger.warning("TextMemoryPlugin not available in this Semantic Kernel version")
    
    logger.info("Semantic Kernel initialized", model=model, endpoint=endpoint)
    
    return kernel


def get_default_kernel() -> Kernel:
    """Get a default kernel instance with settings."""
    return create_kernel()

