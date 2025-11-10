# Plugin System Architecture

The Interview API uses Microsoft Semantic Kernel's plugin system to extend AI agent capabilities. This document details the plugin architecture, types, and implementation patterns.

## 🔌 Plugin Overview

### Plugin Types
The system supports two types of plugins:

1. **Native Function Plugins** - Python functions exposed to AI agents
2. **Prompt-Based Plugins** - AI prompts with configuration files

### Plugin Architecture
```
Semantic Kernel
     │
     ├── Native Function Plugins
     │   └── FilmSearchPlugin (@kernel_function)
     │
     └── Prompt-Based Plugins
         ├── LLMAgent Plugin
         ├── Film Summary Plugin
         ├── Chat Plugin
         └── Orchestration Plugin
```

## 🐍 Native Function Plugins

### Purpose
Native function plugins expose Python functions directly to AI agents, allowing them to interact with databases, APIs, and other system components.

### Structure
```
plugins/
└── film_search/
    ├── __init__.py
    └── film_search_plugin.py  # Plugin implementation
```

### Implementation Pattern
```python
# plugins/film_search/film_search_plugin.py
from semantic_kernel.functions import kernel_function
from typing import Dict, Any
from domain.repositories.film_repository import FilmRepository

class FilmSearchPlugin:
    """Plugin for searching films in the database."""
    
    def __init__(self, film_repository: FilmRepository):
        """Initialize with film repository dependency."""
        self.film_repository = film_repository
    
    @kernel_function(
        name="search_films",
        description="Search for films by title, genre, or keywords. Returns film details including title, year, and description."
    )
    async def search_films(self, query: str) -> Dict[str, Any]:
        """
        Search for films in the database.
        
        Args:
            query: Search query (title, genre, keywords)
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Perform database search
            films = await self.film_repository.search_by_title(query)
            
            # Format results for AI consumption
            formatted_films = []
            for film in films[:5]:  # Limit to top 5 results
                formatted_films.append({
                    "title": film.title,
                    "year": film.release_year,
                    "description": film.description or "No description available",
                    "film_id": film.film_id
                })
            
            return {
                "success": True,
                "query": query,
                "films": formatted_films,
                "total_found": len(films),
                "showing": len(formatted_films)
            }
            
        except Exception as e:
            # Return error information for AI to handle
            return {
                "success": False,
                "error": f"Search failed: {str(e)}",
                "query": query,
                "films": []
            }
    
    @kernel_function(
        name="get_film_details",
        description="Get detailed information about a specific film by ID"
    )
    async def get_film_details(self, film_id: str) -> Dict[str, Any]:
        """Get detailed film information by ID."""
        try:
            film_id_int = int(film_id)
            film = await self.film_repository.get_by_id(film_id_int)
            
            if not film:
                return {
                    "success": False,
                    "error": f"Film with ID {film_id} not found"
                }
            
            return {
                "success": True,
                "film": {
                    "title": film.title,
                    "year": film.release_year,
                    "description": film.description,
                    "film_id": film.film_id,
                    # Add more details as needed
                }
            }
            
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid film ID: {film_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get film details: {str(e)}"
            }
```

### Registration Pattern
```python
# core/plugin_loader.py
def register_native_plugins(kernel: Kernel, film_repository: FilmRepository):
    """Register native function plugins with the kernel."""
    
    # Create and register film search plugin
    film_plugin = FilmSearchPlugin(film_repository)
    kernel.add_plugin(film_plugin, "FilmSearch")
    
    # Additional native plugins can be registered here
    # analytics_plugin = AnalyticsPlugin(analytics_service)
    # kernel.add_plugin(analytics_plugin, "Analytics")
```

### Function Decoration
The `@kernel_function` decorator exposes Python functions to AI agents:

```python
@kernel_function(
    name="function_name",           # Name used by AI agents
    description="Clear description"  # Helps AI understand when to use
)
async def my_function(self, param: str) -> dict:
    # Function implementation
    pass
```

## 📝 Prompt-Based Plugins

### Purpose
Prompt-based plugins define AI behaviors through structured prompts and configuration files.

### Directory Structure
```
plugins/
├── llm_agent/
│   └── answer_question/
│       ├── skprompt.txt    # Prompt template
│       └── config.json     # Function configuration
├── film_short_summary/
│   └── generate_summary/
│       ├── skprompt.txt
│       └── config.json
├── film_summary/
│   └── summarize_tool/
│       ├── skprompt.txt
│       └── config.json
├── chat/
│   └── stream_chat/
│       ├── skprompt.txt
│       └── config.json
└── orchestration/
    └── route_question/
        ├── skprompt.txt
        └── config.json
```

### Prompt Template Format
```
# plugins/llm_agent/answer_question/skprompt.txt
You are a helpful and knowledgeable assistant. Your role is to provide accurate, informative, and engaging responses to user questions.

Guidelines:
- Provide clear and comprehensive answers
- Use examples when helpful
- Be conversational but professional
- If you're unsure about something, acknowledge it
- Focus on being helpful and educational

User Question: {{$input}}

Please provide a thoughtful response to the user's question.
```

### Configuration Format
```json
// plugins/llm_agent/answer_question/config.json
{
  "schema": 1,
  "description": "Answers general knowledge questions with helpful and accurate information",
  "execution_settings": {
    "default": {
      "max_tokens": 1000,
      "temperature": 0.7,
      "top_p": 0.9
    }
  },
  "input_variables": [
    {
      "name": "input",
      "description": "The user's question or query",
      "required": true
    }
  ]
}
```

### Film Summary Plugin Example
```
# plugins/film_summary/summarize_tool/skprompt.txt
You are a film analysis expert. Create a comprehensive summary of the given film information.

Film Information:
{{$film_data}}

Please provide:
1. A brief plot summary (2-3 sentences)
2. Key themes and genres
3. Notable aspects (direction, acting, cinematography)
4. Cultural impact or significance (if applicable)
5. Target audience recommendations

Keep the summary informative but engaging, suitable for someone deciding whether to watch the film.
```

```json
// plugins/film_summary/summarize_tool/config.json
{
  "schema": 1,
  "description": "Creates comprehensive film summaries with plot, themes, and recommendations",
  "execution_settings": {
    "default": {
      "max_tokens": 800,
      "temperature": 0.6,
      "top_p": 0.8
    }
  },
  "input_variables": [
    {
      "name": "film_data",
      "description": "Structured film information including title, year, description, and metadata",
      "required": true
    }
  ]
}
```

## 🔄 Plugin Loading System

### Automatic Plugin Discovery
```python
# core/plugin_loader.py
from semantic_kernel import Kernel
from pathlib import Path

def load_prompt_plugins(kernel: Kernel, plugins_directory: str = "plugins"):
    """
    Automatically load all prompt-based plugins from the plugins directory.
    
    Args:
        kernel: Semantic Kernel instance
        plugins_directory: Path to plugins directory
    """
    plugins_path = Path(plugins_directory)
    
    if not plugins_path.exists():
        print(f"Plugins directory {plugins_directory} not found")
        return
    
    # Discover and load plugins
    for plugin_dir in plugins_path.iterdir():
        if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
            try:
                # Load plugin from directory
                kernel.add_plugin_from_prompt_directory(
                    plugin_directory_path=str(plugins_path),
                    plugin_name=plugin_dir.name
                )
                print(f"Loaded plugin: {plugin_dir.name}")
                
            except Exception as e:
                print(f"Failed to load plugin {plugin_dir.name}: {e}")

def register_all_plugins(kernel: Kernel, film_repository=None):
    """Register both native and prompt-based plugins."""
    
    # Register native function plugins
    if film_repository:
        register_native_plugins(kernel, film_repository)
    
    # Load prompt-based plugins
    load_prompt_plugins(kernel)
```

### Plugin Integration in Agents
```python
# app/agents/search_agent.py
def create_search_agent(kernel: Kernel) -> ChatCompletionAgent:
    """Create SearchAgent with film search capabilities."""
    
    # Native plugins are already registered with kernel
    # Agent can use them through function calling
    
    instructions = """
    You are a specialized film database agent with access to film search functions.
    
    Available Functions:
    - search_films(query): Search for films by title, genre, or keywords
    - get_film_details(film_id): Get detailed information about a specific film
    
    Always use these functions to provide accurate film information.
    """
    
    return ChatCompletionAgent(
        service_id="search_agent",
        kernel=kernel,
        name="SearchAgent", 
        instructions=instructions
    )
```

## 🛠️ Plugin Development Guidelines

### Native Function Plugin Best Practices

1. **Clear Function Names**: Use descriptive names that indicate purpose
2. **Comprehensive Descriptions**: Help AI understand when to use the function
3. **Error Handling**: Return structured error information
4. **Type Hints**: Use proper Python type hints
5. **Async Operations**: Use async/await for I/O operations
6. **Result Formatting**: Return structured data that AI can easily process

```python
@kernel_function(
    name="search_films_by_genre",
    description="Search for films by specific genre. Returns films matching the genre with ratings and year information."
)
async def search_films_by_genre(self, genre: str, limit: str = "10") -> Dict[str, Any]:
    """
    Search films by genre with proper error handling and formatting.
    
    Args:
        genre: Film genre (e.g., 'Action', 'Comedy', 'Drama')
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Structured dictionary with films and metadata
    """
    try:
        limit_int = int(limit)
        films = await self.film_repository.search_by_genre(genre, limit_int)
        
        return {
            "success": True,
            "genre": genre,
            "films": [self._format_film(film) for film in films],
            "count": len(films)
        }
    except ValueError:
        return {"success": False, "error": f"Invalid limit: {limit}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Prompt-Based Plugin Best Practices

1. **Clear Instructions**: Provide specific, actionable instructions
2. **Input Variables**: Clearly define expected inputs
3. **Output Format**: Specify desired output structure
4. **Examples**: Include examples when helpful
5. **Constraints**: Set appropriate token limits and temperature

```
# Good prompt example
You are a film recommendation expert. Based on the user's preferences, recommend 3-5 films.

User Preferences: {{$preferences}}

For each recommendation, provide:
- Film title and year
- Brief description (1-2 sentences)  
- Why it matches their preferences
- Content rating if known

Format as a numbered list for easy reading.
```

## 🧪 Plugin Testing

### Native Function Plugin Tests
```python
# tests/test_plugins.py
import pytest
from plugins.film_search.film_search_plugin import FilmSearchPlugin

@pytest.mark.asyncio
async def test_film_search_plugin_success():
    """Test successful film search."""
    mock_repo = Mock()
    mock_repo.search_by_title.return_value = [
        Mock(title="Inception", release_year=2010, description="Dream heist film")
    ]
    
    plugin = FilmSearchPlugin(mock_repo)
    result = await plugin.search_films("Inception")
    
    assert result["success"] is True
    assert len(result["films"]) == 1
    assert result["films"][0]["title"] == "Inception"

@pytest.mark.asyncio 
async def test_film_search_plugin_error():
    """Test error handling in film search."""
    mock_repo = Mock()
    mock_repo.search_by_title.side_effect = Exception("Database error")
    
    plugin = FilmSearchPlugin(mock_repo)
    result = await plugin.search_films("test")
    
    assert result["success"] is False
    assert "error" in result
```

### Prompt Plugin Integration Tests
```python
@pytest.mark.asyncio
async def test_prompt_plugin_loading():
    """Test that prompt plugins load correctly."""
    kernel = Kernel()
    load_prompt_plugins(kernel, "plugins")
    
    # Verify plugins are loaded
    plugins = kernel.plugins
    assert "llm_agent" in plugins
    assert "film_summary" in plugins
```

## 📊 Plugin Performance

### Optimization Strategies
1. **Caching**: Cache frequent database queries
2. **Connection Pooling**: Reuse database connections  
3. **Batch Operations**: Group related operations
4. **Async Processing**: Use async/await throughout
5. **Result Limiting**: Limit result set sizes

### Monitoring
- **Function Call Frequency**: Track which functions are used most
- **Execution Times**: Monitor plugin performance
- **Error Rates**: Track plugin failures
- **Cache Hit Rates**: Monitor caching effectiveness

## 🔧 Configuration Management

### Plugin Configuration
```python
# core/settings.py
class Settings(BaseSettings):
    # Plugin settings
    plugins_directory: str = "plugins"
    max_plugin_results: int = 10
    plugin_timeout: int = 30
    
    # AI settings
    openai_api_key: str
    openai_model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7
```

### Environment Variables
```bash
# Plugin Configuration
PLUGINS_DIRECTORY=plugins
MAX_PLUGIN_RESULTS=10
PLUGIN_TIMEOUT=30

# AI Configuration  
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
MAX_TOKENS=1000
TEMPERATURE=0.7
```

This plugin system provides a flexible, extensible foundation for adding new capabilities to AI agents while maintaining clean separation of concerns and testability.
