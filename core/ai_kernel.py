"""Semantic Kernel factory and configuration."""

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.core_plugins import TextMemoryPlugin
from semantic_kernel.memory import MemoryStoreBase
from typing import Optional
from core.settings import settings
from core.logging import get_logger

logger = get_logger(__name__)


def create_kernel(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    model: Optional[str] = None,
    memory_store: Optional[MemoryStoreBase] = None,
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
    if memory_store:
        kernel.add_plugin(TextMemoryPlugin(memory_store), "memory")
    
    logger.info("Semantic Kernel initialized", model=model, endpoint=endpoint)
    
    return kernel


def get_default_kernel() -> Kernel:
    """Get a default kernel instance with settings."""
    return create_kernel()

