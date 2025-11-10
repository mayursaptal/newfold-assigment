# AI Agent System Architecture

The Interview API implements an intelligent agent orchestration system using Microsoft's Semantic Kernel framework. This system provides specialized AI agents that can handle different types of queries and seamlessly hand off between each other.

## 🤖 Agent Overview

### System Architecture
```
User Question
     │
     ▼
┌─────────────────┐
│ HandoffService  │ ◄── Entry point for all AI requests
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Orchestration   │ ◄── Routes to appropriate agent
│   (Semantic     │
│    Kernel)      │
└─────────────────┘
     │
     ├─────────────────┐
     ▼                 ▼
┌─────────────┐   ┌─────────────┐
│SearchAgent  │   │ LLMAgent    │
│(Film Queries│   │(General Q&A)│
└─────────────┘   └─────────────┘
     │                 │
     ▼                 ▼
┌─────────────┐   ┌─────────────┐
│Film Database│   │OpenAI GPT-4 │
│   Queries   │   │   Service   │
└─────────────┘   └─────────────┘
```

## 🎯 Agent Specialization

### SearchAgent
**Purpose**: Handle film-related queries with database integration

**Capabilities**:
- Film search by title, genre, actor
- Movie recommendations
- Film details and metadata
- Database query optimization
- Structured data responses

**Example Queries**:
- "Tell me about the movie Inception"
- "Find action movies from 2010"
- "What films has Tom Hanks been in?"
- "Recommend some sci-fi movies"

### LLMAgent  
**Purpose**: Handle general knowledge questions and conversations

**Capabilities**:
- General knowledge questions
- Conversational responses
- Creative tasks
- Explanations and definitions
- Non-film related queries

**Example Queries**:
- "What is artificial intelligence?"
- "Explain quantum computing"
- "Write a short story about space travel"
- "How does machine learning work?"

## 🔄 Orchestration System

### HandoffOrchestration
The system uses Semantic Kernel's `HandoffOrchestration` for intelligent routing:

```python
# app/agents/orchestration.py
from semantic_kernel.agents import ChatCompletionAgent, HandoffOrchestration
from semantic_kernel.agents.strategies import OrchestrationHandoffs

def create_handoff_orchestration(kernel: Kernel) -> HandoffOrchestration:
    # Create specialized agents
    search_agent = create_search_agent(kernel)
    llm_agent = create_llm_agent(kernel)
    
    # Configure handoff rules
    handoffs = OrchestrationHandoffs(
        handoffs={
            search_agent: [llm_agent],  # SearchAgent can hand off to LLMAgent
            # LLMAgent doesn't hand off (terminal agent)
        }
    )
    
    # Create orchestration
    orchestration = HandoffOrchestration(
        agents=[search_agent, llm_agent],
        handoffs=handoffs
    )
    
    return orchestration
```

### Routing Logic
The orchestration automatically determines which agent should handle a query based on:

1. **Initial Analysis**: Question content and context
2. **Agent Instructions**: Each agent has specific instructions about their domain
3. **Handoff Triggers**: Agents can request handoffs when appropriate
4. **Fallback Strategy**: Default routing for ambiguous queries

## 🛠️ Agent Implementation

### SearchAgent Implementation
```python
# app/agents/search_agent.py
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function

def create_search_agent(kernel: Kernel) -> ChatCompletionAgent:
    # Add film search plugin
    film_plugin = FilmSearchPlugin(film_repository)
    kernel.add_plugin(film_plugin, "FilmSearch")
    
    # Agent instructions
    instructions = """
    You are a specialized film database agent. Your role is to:
    
    1. Handle ALL film and movie related questions
    2. Use the FilmSearch plugin to query the database
    3. Provide detailed, accurate information about films
    4. If you cannot find specific film information, hand off to the LLMAgent
    5. Always search the database before providing film information
    
    When users ask about movies, films, actors, or entertainment:
    - Use search_films function to find relevant movies
    - Provide structured, informative responses
    - Include relevant details like year, genre, description
    
    If the question is not about films or you cannot find the information:
    - Hand off to LLMAgent with a clear explanation
    """
    
    return ChatCompletionAgent(
        service_id="search_agent",
        kernel=kernel,
        name="SearchAgent",
        instructions=instructions,
        description="Specialized agent for film database queries and movie information"
    )
```

### LLMAgent Implementation
```python
# app/agents/llm_agent.py
def create_llm_agent(kernel: Kernel) -> ChatCompletionAgent:
    # Add general purpose plugins
    kernel.add_plugin_from_prompt_directory("plugins", "llm_agent")
    
    instructions = """
    You are a helpful general knowledge assistant. Your role is to:
    
    1. Answer general knowledge questions
    2. Provide explanations and educational content
    3. Handle non-film related queries
    4. Engage in helpful conversations
    5. DO NOT hand off to other agents - you are the final responder
    
    Provide clear, accurate, and helpful responses to user questions.
    If you receive a handoff from SearchAgent, acknowledge their findings
    and provide additional context or general information as appropriate.
    """
    
    return ChatCompletionAgent(
        service_id="llm_agent", 
        kernel=kernel,
        name="LLMAgent",
        instructions=instructions,
        description="General purpose conversational agent for non-film queries"
    )
```

## 🔌 Plugin Integration

### Native Function Plugins
Used by SearchAgent for database operations:

```python
# plugins/film_search/film_search_plugin.py
class FilmSearchPlugin:
    def __init__(self, film_repository: FilmRepository):
        self.film_repository = film_repository
    
    @kernel_function(
        name="search_films",
        description="Search for films by title, genre, or keywords"
    )
    async def search_films(self, query: str) -> dict:
        """Search films in the database."""
        try:
            films = await self.film_repository.search_by_title(query)
            
            return {
                "success": True,
                "films": [
                    {
                        "title": film.title,
                        "year": film.release_year,
                        "description": film.description
                    }
                    for film in films[:5]  # Limit results
                ],
                "count": len(films)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "films": []
            }
```

### Prompt-Based Plugins
Used by LLMAgent for general responses:

```
plugins/llm_agent/answer_question/skprompt.txt
```
```
You are a helpful assistant that provides accurate and informative answers.

User Question: {{$input}}

Please provide a clear, comprehensive answer to the user's question.
Focus on accuracy and helpfulness.
```

## 🔄 Handoff Workflow

### 1. Question Processing Flow
```
User Question → HandoffService → Orchestration → Initial Agent Selection
                                      ↓
Agent Processing → Plugin Execution → Response Generation
                                      ↓
Handoff Decision → Target Agent → Final Response → User
```

### 2. Handoff Scenarios

#### Scenario 1: Film Query Success
```
User: "Tell me about Inception"
→ SearchAgent selected
→ FilmSearch plugin finds movie
→ SearchAgent responds with film details
→ No handoff needed
```

#### Scenario 2: Film Query with Handoff
```
User: "What's the meaning behind Inception's ending?"
→ SearchAgent selected
→ FilmSearch plugin finds basic film info
→ SearchAgent recognizes need for interpretation
→ Hands off to LLMAgent for analysis
→ LLMAgent provides interpretation
```

#### Scenario 3: General Query
```
User: "What is artificial intelligence?"
→ LLMAgent selected initially
→ LLMAgent responds with AI explanation
→ No handoff needed (terminal agent)
```

## 📊 Response Processing

### HandoffService Implementation
```python
# domain/services/handoff_service.py
class HandoffService:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.orchestration = create_handoff_orchestration(kernel)
        self.final_agent = None
    
    async def process_question(self, question: str) -> str:
        """Process a question through the agent orchestration system."""
        chat_history = ChatHistory()
        chat_history.add_user_message(question)
        
        # Track which agent provides the final response
        def agent_response_callback(agent, message):
            self.final_agent = agent.name
        
        # Execute orchestration with streaming
        final_response = ""
        async for response in self.orchestration.invoke_stream(
            kernel=self.kernel,
            chat_history=chat_history,
            agent_response_callback=agent_response_callback
        ):
            if hasattr(response, 'content') and response.content:
                final_response = response.content
        
        return final_response or "I apologize, but I couldn't generate a response."
```

### Response Extraction
The service handles multiple response formats from Semantic Kernel:

```python
def extract_response_content(self, response) -> str:
    """Extract content from various Semantic Kernel response types."""
    if hasattr(response, 'content') and response.content:
        return response.content
    elif hasattr(response, 'message') and response.message:
        return response.message
    elif isinstance(response, str):
        return response
    else:
        return str(response)
```

## 🧪 Testing Strategy

### Agent Testing
```python
# tests/test_ai.py
async def test_search_agent_film_query():
    """Test SearchAgent handles film queries correctly."""
    service = HandoffService(kernel)
    
    response = await service.process_question("Tell me about Inception")
    
    assert "Inception" in response
    assert service.final_agent == "SearchAgent"

async def test_llm_agent_general_query():
    """Test LLMAgent handles general queries."""
    service = HandoffService(kernel)
    
    response = await service.process_question("What is artificial intelligence?")
    
    assert "artificial intelligence" in response.lower()
    assert service.final_agent == "LLMAgent"
```

### Plugin Testing
```python
async def test_film_search_plugin():
    """Test FilmSearchPlugin functionality."""
    plugin = FilmSearchPlugin(mock_repository)
    
    result = await plugin.search_films("Inception")
    
    assert result["success"] is True
    assert len(result["films"]) > 0
    assert "Inception" in result["films"][0]["title"]
```

## 🔧 Configuration

### Environment Variables
```bash
# AI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
OPENAI_ORG_ID=your_org_id  # Optional

# Agent Configuration
AGENT_TIMEOUT=30  # Seconds
MAX_HANDOFFS=3    # Maximum handoff chain length
```

### Kernel Configuration
```python
# core/ai_kernel.py
def create_kernel() -> Kernel:
    settings = get_settings()
    
    kernel = Kernel()
    
    # Add OpenAI service
    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id=settings.openai_model,
            api_key=settings.openai_api_key,
            org_id=settings.openai_org_id,
        )
    )
    
    return kernel
```

## 🚀 Performance Considerations

### Optimization Strategies
1. **Plugin Caching**: Cache database query results
2. **Connection Pooling**: Reuse database connections
3. **Timeout Management**: Prevent hanging requests
4. **Response Streaming**: Stream responses for better UX
5. **Error Recovery**: Graceful fallback strategies

### Monitoring
- **Agent Selection Metrics**: Track which agent handles queries
- **Response Times**: Monitor orchestration performance
- **Handoff Frequency**: Analyze handoff patterns
- **Error Rates**: Track plugin and agent failures

This AI agent system provides intelligent, specialized responses while maintaining flexibility and extensibility for future enhancements.
