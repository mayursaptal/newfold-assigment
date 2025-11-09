# Semantic Kernel Plugins

This directory contains all Semantic Kernel plugins organized by functionality. Plugins are automatically discovered and registered when the kernel is initialized.

## Plugin Structure

Plugins can be organized in two ways:

### Flat Structure (Recommended)
```
plugins/
    plugin_name/
        function_name.skprompt    # Prompt template
        config.json               # Function configuration (optional)
```

### Nested Structure
```
plugins/
    plugin_name/
        function_name/
            function_name.skprompt  # Prompt template
            config.json            # Function configuration
```

## Plugin Configuration

Each plugin can have a `config.json` file with the following structure:

```json
{
  "schema": 1,
  "type": "completion",
  "description": "Plugin description",
  "completion": {
    "max_tokens": 200,
    "temperature": 0.3,
    "top_p": 1.0,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0
  },
  "input": {
    "parameters": [
      {
        "name": "parameter_name",
        "description": "Parameter description",
        "defaultValue": ""
      }
    ]
  }
}
```

## Current Plugins

### film_summary
- **Function**: `summarize_tool`
- **Description**: Generate a structured JSON summary for a film with title, rating, and recommended field
- **Input Parameters**: `film_text` (film details including title, description, rating, and release year)
- **Output**: JSON object with `title`, `rating`, and `recommended` (boolean) fields

### film_short_summary
- **Function**: `generate_summary`
- **Description**: Generate a short, engaging text summary for a film (2-3 sentences)
- **Input Parameters**: `film_info` (film details including title, description, category, rating, and release year)
- **Output**: Plain text summary (2-3 sentences)

### chat
- **Function**: `stream_chat`
- **Description**: Stream chat completion for answering user questions
- **Input Parameters**: `question` (user's question to be answered)
- **Output**: Streaming text response

### llm_agent
- **Function**: `answer_question`
- **Description**: Answer general questions using LLM
- **Input Parameters**: `question` (user's question to be answered)
- **Output**: Text response

## Adding New Plugins

1. Create a new directory under `plugins/` with your plugin name
2. Add your `.skprompt` file(s) with the prompt template(s)
3. Optionally add a `config.json` file with execution settings
4. Plugins are automatically discovered and registered on kernel initialization

## Usage

Plugins are automatically registered when the kernel is created. To use a plugin function:

```python
from core.plugin_loader import get_plugin_function
from core.ai_kernel import get_default_kernel

kernel = get_default_kernel()
function = get_plugin_function(kernel, plugin_name="film_summary", function_name="summarize_tool")

# Use the function
response = await kernel.invoke(function=function, arguments=KernelArguments(...))
```

