"""HandoffOrchestration for routing questions to appropriate agents.

This module implements intelligent orchestration using Semantic Kernel to
analyze questions and route them to the appropriate agent (SearchAgent or LLMAgent).

The orchestration uses an AI-powered routing plugin to intelligently decide
which agent should handle each question based on the question's intent and content.
"""

import json
import re
from semantic_kernel import Kernel
from semantic_kernel.agents import OrchestrationHandoffs
from semantic_kernel.functions import KernelArguments
from app.agents.search_agent import SearchAgent
from app.agents.llm_agent import LLMAgent
from core.logging import get_logger
from core.plugin_loader import get_plugin_function


class HandoffOrchestration:
    """Intelligent orchestration agent that routes questions to appropriate agents.
    
    This class uses Semantic Kernel with an AI-powered routing plugin to analyze
    questions and intelligently decide which agent (SearchAgent or LLMAgent) should
    handle each question. It combines AI-based routing with fallback logic.
    
    Attributes:
        search_agent: SearchAgent instance for film questions
        llm_agent: LLMAgent instance for general questions
        kernel: Semantic Kernel instance for AI-powered routing
        handoffs: OrchestrationHandoffs configuration (for documentation)
        logger: Logger instance for orchestration
    """
    
    def __init__(self, search_agent: SearchAgent, llm_agent: LLMAgent, kernel: Kernel = None):
        """Initialize HandoffOrchestration with both agents and kernel.
        
        Args:
            search_agent: SearchAgent instance (front-desk agent)
            llm_agent: LLMAgent instance (fallback agent)
            kernel: Semantic Kernel instance for AI-powered routing (optional)
        """
        self.search_agent = search_agent
        self.llm_agent = llm_agent
        self.kernel = kernel or search_agent.kernel or llm_agent.kernel
        self.logger = get_logger(__name__)
        
        # Build OrchestrationHandoffs configuration for documentation
        self.handoffs = (
            OrchestrationHandoffs()
            .add(
                source_agent=search_agent.name,
                target_agent=llm_agent.name,
                description="Transfer to this agent if the question is not film-related or no film match is found"
            )
            .add(
                source_agent=llm_agent.name,
                target_agent=search_agent.name,
                description="Transfer to this agent if the question is film-related"
            )
        )
        
    
    async def _ai_route_question(self, question: str) -> dict:
        """
        Use AI to analyze question and determine which agent should handle it.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with routing decision:
            {"agent": "SearchAgent" | "LLMAgent", "confidence": float, "reasoning": str}
        """
        try:
            # Get routing function (auto-registered at kernel initialization)
            route_function = get_plugin_function(
                self.kernel,
                plugin_name="orchestration",
                function_name="route_question"
            )
            
            # Invoke routing function
            arguments = KernelArguments(question=question)
            response = await self.kernel.invoke(
                function=route_function,
                arguments=arguments
            )
            
            # Extract response content
            response_text = ""
            if hasattr(response, 'value'):
                response_value = response.value
                
                # Handle list responses
                if isinstance(response_value, list):
                    for item in response_value:
                        if hasattr(item, 'content') and item.content:
                            response_text = str(item.content)
                            break
                        elif hasattr(item, 'inner_content'):
                            inner = item.inner_content
                            if hasattr(inner, 'choices') and inner.choices:
                                choice = inner.choices[0]
                                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                    response_text = str(choice.message.content)
                                    break
                # Handle single object
                else:
                    if hasattr(response_value, 'content') and response_value.content:
                        response_text = str(response_value.content)
                    elif hasattr(response_value, 'inner_content'):
                        inner = response_value.inner_content
                        if hasattr(inner, 'choices') and inner.choices:
                            choice = inner.choices[0]
                            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                response_text = str(choice.message.content)
            
            # Clean up response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:].strip()
            
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{[^{}]*"agent"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            
            # Parse JSON
            routing_decision = json.loads(response_text)
            
            # Validate agent name
            agent = routing_decision.get("agent", "").strip()
            if agent not in ["SearchAgent", "LLMAgent"]:
                self.logger.warning("Invalid agent name from AI routing",
                                  agent=agent,
                                  defaulting_to="LLMAgent")
                return None
            
            self.logger.info("AI routing decision",
                           agent=agent,
                           confidence=routing_decision.get("confidence", 0.0),
                           reasoning=routing_decision.get("reasoning", ""))
            
            return routing_decision
            
        except Exception as e:
            self.logger.warning("AI routing failed, will use fallback logic",
                              error=str(e),
                              error_type=type(e).__name__)
            return None
    
    def _fallback_route_question(self, question: str) -> str:
        """
        Fallback routing logic when AI routing is unavailable.
        
        Uses simple heuristics to determine routing.
        
        Args:
            question: User's question
            
        Returns:
            Agent name: "SearchAgent" or "LLMAgent"
        """
        question_lower = question.lower()
        contains_film_keyword = "film" in question_lower or "movie" in question_lower
        
        # Check for capitalized words (potential film titles)
        words = question.split()
        capitalized_words = [w for w in words if w and w[0].isupper() and len(w) > 2]
        might_be_film_question = contains_film_keyword or len(capitalized_words) >= 1
        
        if might_be_film_question:
            return "SearchAgent"
        return "LLMAgent"
    
    async def process(self, question: str) -> dict:
        """
        Process a question and intelligently route it to the appropriate agent.
        
        Uses AI-powered routing to analyze the question and determine which agent
        should handle it. Falls back to heuristic-based routing if AI routing fails.
        
        Routing logic:
        1. Use AI-powered routing plugin to analyze question intent
        2. If AI routing succeeds, use the recommended agent
        3. If AI routing fails, use fallback heuristics
        4. Try SearchAgent first if routed to it
        5. If SearchAgent finds no match, hand off to LLMAgent
        6. If routed to LLMAgent, use it directly
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with agent name and answer:
            {"agent": "SearchAgent" | "LLMAgent", "answer": str}
        """
        self.logger.info("HandoffOrchestration processing question", question=question[:100])
        
        # Try AI-powered routing first
        routing_decision = await self._ai_route_question(question)
        
        # Determine which agent to use
        if routing_decision:
            selected_agent = routing_decision.get("agent", "LLMAgent")
            confidence = routing_decision.get("confidence", 0.0)
            reasoning = routing_decision.get("reasoning", "")
            
            self.logger.info("AI routing selected agent",
                           agent=selected_agent,
                           confidence=confidence,
                           reasoning=reasoning)
        else:
            # Use fallback routing
            selected_agent = self._fallback_route_question(question)
            self.logger.info("Using fallback routing", agent=selected_agent)
        
        # Route to SearchAgent
        if selected_agent == "SearchAgent":
            self.logger.info("Routing to SearchAgent")
            answer = await self.search_agent.process(question)
            
            # If SearchAgent found a match, return its answer
            if answer:
                self.logger.info("SearchAgent found match", answer=answer[:100])
                return {
                    "agent": "SearchAgent",
                    "answer": answer
                }
            
            # If no match found, hand off to LLMAgent
            self.logger.info("SearchAgent found no match, handing off to LLMAgent")
            answer = await self.llm_agent.process(question)
            return {
                "agent": "LLMAgent",
                "answer": answer
            }
        
        # Route to LLMAgent
        self.logger.info("Routing to LLMAgent")
        answer = await self.llm_agent.process(question)
        return {
            "agent": "LLMAgent",
            "answer": answer
        }
