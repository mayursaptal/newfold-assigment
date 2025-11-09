"""AI service for Gemini operations.

This module provides the AIService class which handles AI operations using
Google's Gemini API via the Semantic Kernel. It provides methods for
streaming chat completions and generating structured film summaries.

Example:
    ```python
    from domain.services import AIService
    from semantic_kernel import Kernel
    
    service = AIService(kernel)
    async for chunk in service.stream_chat("Hello"):
        print(chunk)
    
    summary = await service.get_film_summary(film_id=1)
    ```
"""

from semantic_kernel import Kernel
from domain.repositories.film_repository import FilmRepository
from core.db import get_async_session
from core.logging import get_logger


class AIService:
    """Service for AI operations using Gemini.
    
    This class provides AI functionality using Google's Gemini API through
    the Semantic Kernel framework. It handles streaming chat responses
    and structured JSON generation for film summaries.
    
    Attributes:
        kernel: Semantic Kernel instance configured with Gemini API
    """
    
    def __init__(self, kernel: Kernel):
        """Initialize service with Semantic Kernel.
        
        Args:
            kernel: Semantic Kernel instance configured with Gemini API
        """
        self.kernel = kernel
        self.logger = get_logger("ai")  # Automatically creates logs/ai/YYYY-MM-DD.log
    
    async def stream_chat(self, question: str):
        """
        Stream chat completion response using Google Generative AI.
        
        Args:
            question: User question
            
        Yields:
            Text chunks as they are generated
        """
        self.logger.info("AI chat request received", question=question[:100])  # Log first 100 chars
        
        try:
            # Check if Gemini is configured
            if not hasattr(self.kernel, '_gemini_configured') or not self.kernel._gemini_configured:
                self.logger.error("AI chat service not available", reason="Gemini not configured")
                yield "Error: No AI chat service available. Please check your Gemini API key configuration."
                return
            
            import google.generativeai as genai
            from core.settings import settings
            
            # Get model name and API key
            model_name = getattr(self.kernel, '_gemini_model', settings.gemini_model)
            api_key = getattr(self.kernel, '_gemini_api_key', settings.gemini_api_key)
            
            # Configure if not already done
            genai.configure(api_key=api_key)
            
            # Get the model
            model = genai.GenerativeModel(model_name)
            
            # Generate content with streaming
            response = await model.generate_content_async(
                question,
                stream=True
            )
            
            # Stream the response chunks
            response_text = ""
            async for chunk in response:
                if chunk.text:
                    response_text += chunk.text
                    yield chunk.text
            
            # Log successful completion
            self.logger.info("AI chat response completed", 
                           question=question[:100], 
                           response_length=len(response_text))
        except Exception as e:
            self.logger.error("AI chat streaming failed", 
                            question=question[:100], 
                            error=str(e), 
                            error_type=type(e).__name__)
            # Fallback: try non-streaming
            try:
                import google.generativeai as genai
                from core.settings import settings
                
                model_name = getattr(self.kernel, '_gemini_model', settings.gemini_model)
                api_key = getattr(self.kernel, '_gemini_api_key', settings.gemini_api_key)
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                
                response = await model.generate_content_async(question)
                
                if response.text:
                    self.logger.info("AI chat fallback response completed", 
                                   question=question[:100],
                                   response_length=len(response.text))
                    yield response.text
                else:
                    self.logger.error("AI chat fallback failed - no response", 
                                    question=question[:100])
                    yield f"I'm sorry, I couldn't generate a response. Error: {str(e)}"
            except Exception as e2:
                self.logger.error("AI chat fallback exception", 
                                question=question[:100],
                                error=str(e2),
                                error_type=type(e2).__name__)
                yield f"Error: {str(e2)}"
    
    async def get_film_summary(self, film_id: int) -> dict:
        """
        Get AI-generated summary for a film with structured JSON response.
        
        Args:
            film_id: Film ID to summarize
            
        Returns:
            Dictionary with title, rating, and recommended fields
        """
        self.logger.info("AI film summary request received", film_id=film_id)
        
        # Get film details from database
        async for session in get_async_session():
            film_repo = FilmRepository(session)
            film = await film_repo.get_by_id(film_id)
            break
        
        if not film:
            self.logger.error("Film not found for AI summary", film_id=film_id)
            raise ValueError(f"Film with ID {film_id} not found")
        
        # Create prompt for structured JSON response
        prompt = f"""Analyze this film and provide a summary in JSON format with exactly these keys: title, rating, recommended (boolean).

Film details:
- Title: {film.title}
- Description: {film.description or 'N/A'}
- Rating: {film.rating or 'N/A'}
- Release Year: {film.release_year or 'N/A'}

Respond ONLY with valid JSON in this exact format:
{{"title": "...", "rating": "...", "recommended": true/false}}"""

        try:
            # Use Google Generative AI SDK directly
            import google.generativeai as genai
            from core.settings import settings
            
            # Get model name and API key
            model_name = getattr(self.kernel, '_gemini_model', settings.gemini_model)
            api_key = getattr(self.kernel, '_gemini_api_key', settings.gemini_api_key)
            
            # Configure if not already done
            genai.configure(api_key=api_key)
            
            # Create prompt with JSON schema instruction
            json_prompt = f"""{prompt}

IMPORTANT: You must respond with ONLY valid JSON. No markdown, no code blocks, just pure JSON.
The JSON must have exactly these keys: "title", "rating", "recommended" (boolean)."""
            
            # Get the model
            model = genai.GenerativeModel(model_name)
            
            # Generate content
            response = await model.generate_content_async(json_prompt)
            
            # Parse JSON response
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Clean up response text if needed
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            import json
            summary = json.loads(response_text)
            
            # Validate and return
            result = {
                "title": summary.get("title", film.title),
                "rating": summary.get("rating", str(film.rating) if film.rating else "N/A"),
                "recommended": bool(summary.get("recommended", False))
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
            return {
                "title": film.title,
                "rating": str(film.rating) if film.rating else "N/A",
                "recommended": False
            }

