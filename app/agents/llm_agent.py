"""LLMAgent for general questions using Semantic Kernel ChatCompletionAgent.

This agent uses Semantic Kernel's ChatCompletionAgent to provide thoughtful,
accurate answers to general questions using the configured LLM model.
"""

from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import KernelArguments
from core.logging import get_logger
from core.plugin_loader import get_plugin_function


class LLMAgent:
    """Agent that answers general questions using Semantic Kernel ChatCompletionAgent.
    
    This agent handles questions that don't relate to films by using
    Semantic Kernel's ChatCompletionAgent with the llm_agent plugin to generate responses.
    
    Attributes:
        agent: ChatCompletionAgent instance configured with LLM and llm_agent plugin
        kernel: Semantic Kernel instance configured with LLM
        logger: Logger instance for this agent
        name: Agent name for orchestration (required for OrchestrationHandoffs)
        description: Agent description (required for HandoffOrchestration)
    """
    
    def __init__(self, kernel: Kernel, instructions: Optional[str] = None):
        """Initialize LLMAgent with Semantic Kernel.
        
        Args:
            kernel: Semantic Kernel instance configured with LLM (plugins already registered)
            instructions: Optional custom instructions for the agent
                         (defaults to general question answering)
        """
        self.kernel = kernel
        self.logger = get_logger("ai")  # Use "ai" logger for file logging
        self.name = "LLMAgent"  # Required for OrchestrationHandoffs
        self.description = "A customer support agent that answers general questions using an LLM."
        
        # Get the llm_agent plugin from kernel (already registered)
        llm_plugin = None
        try:
            llm_plugin = kernel.get_plugin("llm_agent")
            if llm_plugin:
                self.logger.info("Using llm_agent plugin with ChatCompletionAgent")
        except Exception as e:
            self.logger.warning("llm_agent plugin not found, agent will use instructions only",
                              error=str(e))
        
        # Default instructions for the agent
        # IMPORTANT: This agent should ANSWER QUESTIONS directly, not complete tasks or provide summaries
        default_instructions = (
            "You are a helpful customer support assistant. "
            "Your role is to ANSWER QUESTIONS directly and conversationally. "
            "When a user asks a question, provide a direct, helpful answer. "
            "\n\nCRITICAL RULES: "
            "1. Do NOT provide task completion summaries. "
            "2. Do NOT say 'Task is completed' or 'Task is completed with summary'. "
            "3. Do NOT treat questions as tasks to complete. "
            "4. Simply answer the question as if you are having a conversation. "
            "5. Answer clearly, accurately, and concisely. "
            "6. If you don't know something, say so honestly. "
            "7. Always respond to the user's question directly, no matter what it is. "
            "\n\nRemember: You are answering questions, not completing tasks. "
            "Provide direct answers, not summaries of what you did."
        )
        
        # Create ChatCompletionAgent with llm_agent plugin
        # The plugin provides the answer_question function
        self.agent = ChatCompletionAgent(
            kernel=kernel,
            name=self.name,
            instructions=instructions or default_instructions,
            arguments=KernelArguments(),
            plugins=[llm_plugin] if llm_plugin else None
        )
