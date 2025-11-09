"""LLMAgent for general questions using Semantic Kernel.

This agent answers any question using the Semantic Kernel with the configured
LLM model (Azure OpenAI) via kernel.invoke().
"""

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from core.logging import get_logger


class LLMAgent:
    """Agent that answers general questions using Semantic Kernel.
    
    This agent handles questions that don't relate to films by using
    the Semantic Kernel to invoke the LLM model and generate responses.
    
    Attributes:
        kernel: Semantic Kernel instance configured with LLM
        logger: Logger instance for this agent
        name: Agent name for orchestration (required for OrchestrationHandoffs)
        description: Agent description (required for HandoffOrchestration)
    """
    
    def __init__(self, kernel: Kernel):
        """Initialize LLMAgent with Semantic Kernel.
        
        Args:
            kernel: Semantic Kernel instance configured with LLM
        """
        self.kernel = kernel
        self.logger = get_logger(__name__)
        self.name = "LLMAgent"  # Required for OrchestrationHandoffs
        self.description = "A customer support agent that answers general questions using an LLM."
    
    async def process(self, question: str) -> str:
        """
        Process a question and return an answer using LLM.
        
        Uses Semantic Kernel's invoke method to get a response from the
        configured LLM model.
        
        Args:
            question: User's question
            
        Returns:
            Answer string from the LLM
        """
        self.logger.info("LLMAgent processing question", question=question[:100])
        
        try:
            # Create a simple prompt function for answering questions
            prompt_template = "Answer the following question: {{$question}}"
            
            # Check if function already exists, otherwise add it
            try:
                answer_function = self.kernel.get_function_from_fully_qualified_function_name("General", "answer_question")
            except:
                answer_function = self.kernel.add_function(
                    function_name="answer_question",
                    plugin_name="General",
                    prompt=prompt_template,
                    description="Answer general questions"
                )
            
            # Invoke the function
            arguments = KernelArguments(question=question)
            response = await self.kernel.invoke(
                function=answer_function,
                arguments=arguments
            )
            
            # Get response content
            # Handle different response types from Semantic Kernel
            answer = None
            
            if hasattr(response, 'value'):
                response_value = response.value
                
                # Handle list responses (common with Semantic Kernel)
                if isinstance(response_value, list):
                    for item in response_value:
                        # Try items attribute (TextContent objects)
                        if hasattr(item, 'items') and item.items:
                            for text_item in item.items:
                                if hasattr(text_item, 'text') and text_item.text:
                                    answer = str(text_item.text)
                                    break
                            if answer:
                                break
                        
                        # Try content attribute
                        if not answer and hasattr(item, 'content') and item.content:
                            answer = str(item.content)
                            break
                        
                        # Try inner_content (OpenAI ChatCompletion)
                        if not answer and hasattr(item, 'inner_content'):
                            inner = item.inner_content
                            if hasattr(inner, 'choices') and inner.choices:
                                choice = inner.choices[0]
                                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                    answer = str(choice.message.content)
                                    break
                                elif hasattr(choice, 'text'):
                                    answer = str(choice.text)
                                    break
                        
                        # Try text attribute
                        if not answer and hasattr(item, 'text') and item.text:
                            answer = str(item.text)
                            break
                
                # Handle single object (not a list)
                else:
                    # Try items first (TextContent objects)
                    if hasattr(response_value, 'items') and response_value.items:
                        for item in response_value.items:
                            if hasattr(item, 'text') and item.text:
                                answer = str(item.text)
                                break
                    
                    # Try content attribute
                    if not answer and hasattr(response_value, 'content') and response_value.content:
                        answer = str(response_value.content)
                    
                    # Try inner_content (OpenAI ChatCompletion)
                    if not answer and hasattr(response_value, 'inner_content'):
                        inner = response_value.inner_content
                        if hasattr(inner, 'choices') and inner.choices:
                            choice = inner.choices[0]
                            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                answer = str(choice.message.content)
                            elif hasattr(choice, 'text'):
                                answer = str(choice.text)
                    
                    # Fallback to text attribute
                    if not answer and hasattr(response_value, 'text') and response_value.text:
                        answer = str(response_value.text)
                
                # Last resort: string representation
                if not answer:
                    answer = str(response_value) if not isinstance(response_value, list) else str(response_value[0]) if response_value else ""
            else:
                answer = str(response)
            
            self.logger.info("LLMAgent response generated", 
                           question=question[:100],
                           answer_length=len(answer))
            
            return answer
            
        except Exception as e:
            self.logger.error("LLMAgent processing failed",
                            question=question[:100],
                            error=str(e),
                            error_type=type(e).__name__)
            return f"I'm sorry, I encountered an error: {str(e)}"

