"""Handoff orchestration service.

This service handles agent orchestration using Semantic Kernel's HandoffOrchestration.
It manages conversation context and routes questions between SearchAgent and LLMAgent.
"""

from typing import Dict, Any
import asyncio
from semantic_kernel import Kernel
from semantic_kernel.agents.runtime import InProcessRuntime
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.orchestration import create_handoff_orchestration
from core.logging import get_logger


class HandoffService:
    """Service for handling agent handoff orchestration.
    
    This service manages the orchestration of SearchAgent and LLMAgent,
    maintaining conversation context and extracting responses.
    """
    
    def __init__(self, session: AsyncSession, kernel: Kernel):
        """Initialize HandoffService.
        
        Args:
            session: Database session for SearchAgent's repository
            kernel: Semantic Kernel instance for agents
        """
        self.session = session
        self.kernel = kernel
        self.logger = get_logger("ai")
    
    async def process_question(self, question: str) -> Dict[str, Any]:
        """Process a question through agent orchestration.
        
        Creates orchestration, invokes it with the question, and extracts
        the response from the appropriate agent.
        
        Args:
            question: User's question to be answered
            
        Returns:
            Dictionary with 'agent' (agent name) and 'answer' (response text)
            
        Raises:
            Exception: If orchestration fails
        """
        self.logger.info(
            "Handoff request received",
            question=question,
            question_length=len(question)
        )
        
        # Create orchestration following Microsoft documentation pattern
        orchestration, agent_tracker = create_handoff_orchestration(self.session, self.kernel)
        
        # Create and start runtime
        runtime = InProcessRuntime()
        runtime.start()
        
        try:
            self.logger.info("Invoking orchestration", question=question)
            
            # Simplified approach: let orchestration complete naturally, then extract from tracker
            self.logger.info("Invoking orchestration and waiting for completion")
            
            try:
                # Invoke orchestration with timeout
                orchestration_result = await asyncio.wait_for(
                    orchestration.invoke(task=question, runtime=runtime),
                    timeout=30.0
                )
                
                self.logger.info("Orchestration completed, getting result")
                
                # Get the final value with timeout
                final_value = await asyncio.wait_for(
                    orchestration_result.get(),
                    timeout=5.0
                )
                
                self.logger.info("Final value received, checking tracker first")
                
            except asyncio.TimeoutError:
                self.logger.error("Orchestration timed out")
                # Check tracker for any captured responses
                tracker_answer = agent_tracker.get("last_agent_response")
                if tracker_answer:
                    agent_name = agent_tracker.get("last_agent", "SearchAgent")
                    return {
                        "agent": agent_name,
                        "answer": tracker_answer.strip()
                    }
                else:
                    return {
                        "agent": "SearchAgent",
                        "answer": "I'm sorry, the request timed out. Please try again."
                    }
            except Exception as e:
                self.logger.error("Orchestration failed", error=str(e))
                # Check tracker for any captured responses
                tracker_answer = agent_tracker.get("last_agent_response")
                if tracker_answer:
                    agent_name = agent_tracker.get("last_agent", "SearchAgent")
                    return {
                        "agent": agent_name,
                        "answer": tracker_answer.strip()
                    }
                else:
                    return {
                        "agent": "SearchAgent",
                        "answer": "I'm sorry, I encountered an error processing your request."
                    }
            
            # If we reach here, orchestration completed naturally
            self.logger.info(
                "Final value received from natural completion",
                final_value_type=type(final_value).__name__ if final_value else None
            )
            
            # Get the agent name from the tracker (populated by callbacks)
            agent_name = agent_tracker.get("last_agent", "SearchAgent")
            
            # PRIORITIZE tracker response first (this contains the correct first response)
            tracker_answer = agent_tracker.get("last_agent_response")
            if tracker_answer and tracker_answer.strip():
                answer = tracker_answer
                self.logger.info("Using tracker response (first valid response)", answer_length=len(answer))
            else:
                # Fallback to extracting from final_value if tracker is empty
                answer = self._extract_answer(final_value)
                self.logger.info("Using final_value as fallback", answer_length=len(answer) if answer else 0)
            
            # If still no answer, use default message
            if not answer or not answer.strip():
                answer = "I'm sorry, I couldn't generate a response."
            
            self.logger.info(
                "Handoff response ready",
                question=question,
                agent=agent_name,
                answer_length=len(answer),
                answer_preview=answer[:200] if answer else ""
            )
            
            return {
                "agent": agent_name,
                "answer": answer.strip()
            }
            
        except Exception as e:
            # Log error and return a helpful response
            self.logger.error(
                "Handoff orchestration failed",
                question=question,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True
            )
            # Return error response
            agent_name = agent_tracker.get("last_agent", "SearchAgent")
            return {
                "agent": agent_name,
                "answer": f"I'm sorry, I encountered an error processing your request: {str(e)}"
            }
        finally:
            # Stop runtime
            try:
                runtime.stop()
            except Exception:
                try:
                    await runtime.stop_when_idle()
                except Exception:
                    pass  # Ignore errors when stopping runtime
    
    def _extract_answer(self, final_value: Any) -> str:
        """Extract answer text from orchestration result.
        
        Args:
            final_value: Result from orchestration (typically ChatMessageContent or list)
            
        Returns:
            Extracted answer text
        """
        if not final_value:
            return ""
        
        self.logger.debug(
            "Extracting answer from final_value",
            final_value_type=type(final_value).__name__,
            is_list=isinstance(final_value, list),
            has_content=hasattr(final_value, 'content') if final_value else False,
            has_text=hasattr(final_value, 'text') if final_value else False,
            has_items=hasattr(final_value, 'items') if final_value else False
        )
        
        # Handle list of messages (common case)
        if isinstance(final_value, list):
            if not final_value:
                return ""
            
            # Get the last message (most recent response)
            last_message = final_value[-1]
            self.logger.debug(
                "Processing last message from list",
                message_type=type(last_message).__name__,
                list_length=len(final_value)
            )
            return self._extract_from_message(last_message)
        
        # Handle single message
        return self._extract_from_message(final_value)
    
    def _extract_from_message(self, message: Any) -> str:
        """Extract text content from a single message object.
        
        Args:
            message: Message object (ChatMessageContent or similar)
            
        Returns:
            Extracted text content
        """
        if not message:
            return ""
        
        answer = ""
        
        # Try direct content attribute first
        if hasattr(message, 'content') and message.content:
            content = message.content
            if isinstance(content, str):
                answer = content
            else:
                answer = str(content)
            self.logger.debug("Extracted from content attribute", length=len(answer))
        
        # Try text attribute
        if not answer and hasattr(message, 'text') and message.text:
            answer = str(message.text)
            self.logger.debug("Extracted from text attribute", length=len(answer))
        
        # Try items attribute (ChatMessageContent structure)
        if not answer and hasattr(message, 'items') and message.items:
            try:
                for item in message.items:
                    if hasattr(item, 'text') and item.text:
                        answer += str(item.text)
                    elif hasattr(item, 'content') and item.content:
                        answer += str(item.content)
                    elif isinstance(item, dict):
                        if 'text' in item and item['text']:
                            answer += str(item['text'])
                        elif 'content' in item and item['content']:
                            answer += str(item['content'])
                    
                    # Stop after first item with content
                    if answer.strip():
                        break
                
                if answer:
                    self.logger.debug("Extracted from items attribute", length=len(answer))
            except (TypeError, AttributeError) as e:
                self.logger.warning("Error extracting from items", error=str(e))
        
        # Fallback: convert to string if it's not an OrchestrationResult
        if not answer:
            type_name = type(message).__name__
            if "OrchestrationResult" not in type_name and "Task" not in type_name:
                answer = str(message)
                self.logger.debug("Extracted using string conversion", length=len(answer))
            else:
                self.logger.warning(
                    "Skipping string conversion of task/result object",
                    type_name=type_name
                )
        
        return answer.strip() if answer else ""

