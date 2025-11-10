"""AI service for OpenAI operations.

This module provides the AIService class which handles AI operations using
OpenAI via the Semantic Kernel. It provides methods for
streaming chat completions and generating structured film summaries.

Example:
    ```python
    from domain.services import AIService
    from semantic_kernel import Kernel
    
    service = AIService(kernel)
    async for chunk in service.stream_chat("Hello"):
        print(chunk)
    
    summary = await service.get_film_summary(film_id=1, film_service=film_service)
    ```
"""

import json
from pathlib import Path
from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from domain.services.film_service import FilmService
from core.logging import get_logger
from core.plugin_loader import get_plugin_function


class AIService:
    """Service for AI operations using OpenAI.
    
    This class provides AI functionality using OpenAI through
    the Semantic Kernel framework. It handles streaming chat responses
    and structured JSON generation for film summaries.
    
    Attributes:
        kernel: Semantic Kernel instance configured with OpenAI
    """
    
    def __init__(self, kernel: Kernel):
        """Initialize service with Semantic Kernel.
        
        Args:
            kernel: Semantic Kernel instance configured with OpenAI
        """
        self.kernel = kernel
        self.logger = get_logger("ai")  # Automatically creates logs/ai/YYYY-MM-DD.log
    
    async def stream_chat(self, question: str):
        """
        Stream chat completion response using OpenAI.
        
        Args:
            question: User question
            
        Yields:
            Text chunks as they are generated
        """
        self.logger.info("AI chat request received", question=question[:100])
        
        try:
            # Use the stream_chat plugin (auto-registered at kernel initialization)
            chat_function = get_plugin_function(
                self.kernel,
                plugin_name="chat",
                function_name="stream_chat"
            )
            
            # Invoke with streaming
            arguments = KernelArguments(question=question)
            
            response_text = ""
            async for chunk in self.kernel.invoke_stream(
                function=chat_function,
                arguments=arguments
            ):
                # Handle different chunk types from Semantic Kernel
                chunk_text = None
                
                # Chunks can be lists - iterate through them
                if isinstance(chunk, list):
                    for item in chunk:
                        # StreamingChatMessageContent objects - try content first, then str()
                        if hasattr(item, 'content') and item.content:
                            chunk_text = str(item.content)
                            break
                        elif hasattr(item, 'text') and item.text:
                            chunk_text = str(item.text)
                            break
                        elif hasattr(item, 'value') and item.value:
                            chunk_text = str(item.value)
                            break
                        elif isinstance(item, str):
                            chunk_text = item
                            break
                        else:
                            # Fallback: convert the object to string, but skip if empty
                            temp_text = str(item) if item else None
                            if temp_text and temp_text.strip():
                                chunk_text = temp_text
                                break
                # Try different attributes that might contain the text
                elif hasattr(chunk, 'content') and chunk.content:
                    chunk_text = str(chunk.content)
                elif hasattr(chunk, 'value') and chunk.value:
                    chunk_text = str(chunk.value)
                elif hasattr(chunk, 'text') and chunk.text:
                    chunk_text = str(chunk.text)
                elif hasattr(chunk, 'choices') and chunk.choices:
                    # Handle OpenAI-style choices
                    for choice in chunk.choices:
                        if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                            chunk_text = str(choice.delta.content) if choice.delta.content else None
                        elif hasattr(choice, 'text'):
                            chunk_text = str(choice.text)
                        if chunk_text:
                            break
                elif isinstance(chunk, str):
                    chunk_text = chunk
                
                # Yield the chunk if we found text
                if chunk_text:
                    response_text += chunk_text
                    yield chunk_text
            
            # Log successful completion
            self.logger.info("AI chat response completed", 
                           question=question[:100], 
                           response_length=len(response_text))
        except Exception as e:
            self.logger.error("AI chat streaming failed", 
                            question=question[:100], 
                            error=str(e), 
                            error_type=type(e).__name__)
            yield f"I'm sorry, I encountered an error: {str(e)}"
    
    async def get_film_summary(self, film_id: int, film_service: FilmService) -> dict:
        """
        Get AI-generated summary for a film with structured JSON response.
        
        Uses Semantic Kernel's invoke method with a prompt template and JSON response format.
        
        Args:
            film_id: Film ID to summarize
            film_service: Film service instance to look up film
            
        Returns:
            Dictionary with title, rating, and recommended fields
        """
        self.logger.info("AI film summary request received", film_id=film_id)
        
        # Look up film via service layer
        film = await film_service.get_film(film_id)
        if not film:
            self.logger.error("Film not found for AI summary", film_id=film_id)
            raise ValueError(f"Film with ID {film_id} not found")
        
        # Prepare film text for prompt
        film_text = f"""Title: {film.title}
Description: {film.description or 'N/A'}
Rating: {film.rating or 'N/A'}
Release Year: {film.release_year or 'N/A'}"""

        try:
            # Use plugin loader to get the function (auto-registered at kernel initialization)
            from core.plugin_loader import get_plugin_function
            
            summarize_function = get_plugin_function(
                self.kernel,
                plugin_name="film_summary",
                function_name="summarize_tool"
            )
            
            # Get execution settings from plugin config (optional, for future use)
            # The config settings are already applied via the function's default settings
            
            # Invoke the function with film_text as input
            arguments = KernelArguments(film_text=film_text)
            
            # Invoke the function (execution settings from config.json are applied automatically)
            response = await self.kernel.invoke(
                function=summarize_function,
                arguments=arguments
            )
            
            # Get response content
            # Handle different response types from Semantic Kernel
            if response and hasattr(response, 'value'):
                response_value = response.value
                # If it's a ChatMessageContent or similar, extract the actual content
                if hasattr(response_value, 'content') and response_value.content:
                    response_text = str(response_value.content)
                elif hasattr(response_value, 'inner_content'):
                    # Try to extract from inner_content (OpenAI ChatCompletion)
                    inner = response_value.inner_content
                    if hasattr(inner, 'choices') and inner.choices:
                        # Get content from first choice
                        choice = inner.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            response_text = str(choice.message.content)
                        elif hasattr(choice, 'text'):
                            response_text = str(choice.text)
                        else:
                            response_text = str(response_value)
                    else:
                        response_text = str(response_value)
                elif hasattr(response_value, 'text'):
                    response_text = str(response_value.text)
                else:
                    response_text = str(response_value)
            else:
                response_text = str(response)
            
            # Log raw response for debugging
            self.logger.info("AI raw response", raw_response_text=response_text[:500])
            
            # Clean up response text if needed
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:].strip()
            
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()
            
            # Try to extract JSON from the response if it's embedded in text
            # Look for JSON object pattern
            import re
            json_match = re.search(r'\{[^{}]*"title"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # If still no valid JSON, try to find the first { and last }
            if not response_text.startswith('{'):
                start_idx = response_text.find('{')
                if start_idx != -1:
                    response_text = response_text[start_idx:]
            
            if not response_text.endswith('}'):
                end_idx = response_text.rfind('}')
                if end_idx != -1:
                    response_text = response_text[:end_idx + 1]
            
            response_text = response_text.strip()
            
            # Parse JSON with better error handling
            try:
                summary = json.loads(response_text)
            except json.JSONDecodeError as e:
                self.logger.error("Failed to parse AI response as JSON",
                                raw_response=response_text[:500],
                                error=str(e),
                                error_position=f"line {e.lineno}, column {e.colno}")
                # Try to fix common JSON issues
                # Remove any trailing commas
                response_text = re.sub(r',\s*}', '}', response_text)
                response_text = re.sub(r',\s*]', ']', response_text)
                try:
                    summary = json.loads(response_text)
                except json.JSONDecodeError:
                    # If still fails, raise the original error
                    raise ValueError(f"AI response is not valid JSON: {response_text[:200]}")
            
            # Log the parsed AI response for debugging
            self.logger.info("AI summary response", 
                            parsed_response=summary,
                            recommended_value=summary.get("recommended"),
                            recommended_type=type(summary.get("recommended")).__name__)
            
            # Validate and return
            # Always use the actual film rating value (enum value) for consistency
            # The film.rating is a FilmRating enum, so use its .value attribute
            if film.rating:
                rating_value = film.rating.value  # This will be "NC-17", "PG-13", etc.
            else:
                # Fallback to AI response if film has no rating
                rating_value = summary.get("rating", "N/A")
                # If AI returned an enum string representation, try to extract the value
                if isinstance(rating_value, str) and rating_value.startswith("FilmRating."):
                    enum_name = rating_value.split(".", 1)[1]
                    try:
                        from domain.models.film import FilmRating
                        rating_enum = getattr(FilmRating, enum_name, None)
                        if rating_enum:
                            rating_value = rating_enum.value
                    except:
                        pass
            
            # Parse recommended field - handle both boolean and string values
            recommended = summary.get("recommended", False)
            if isinstance(recommended, str):
                recommended = recommended.lower() in ("true", "1", "yes", "recommended")
            elif not isinstance(recommended, bool):
                recommended = bool(recommended)
            
            result = {
                "title": summary.get("title", film.title),
                "rating": rating_value,
                "recommended": recommended
            }
            
            self.logger.info("AI film summary completed", 
                           film_id=film_id,
                           film_title=film.title,
                           recommended=result["recommended"])
            
            return result
        except Exception as e:
            # Fallback response if AI fails
            self.logger.error("AI film summary failed", 
                            film_id=film_id,
                            film_title=film.title,
                            error=str(e),
                            error_type=type(e).__name__)
            # Use enum value instead of string representation
            rating_value = film.rating.value if film.rating and hasattr(film.rating, 'value') else "N/A"
            return {
                "title": film.title,
                "rating": rating_value,
                "recommended": False
            }
