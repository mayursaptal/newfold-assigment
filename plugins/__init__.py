"""Semantic Kernel plugins package.

This package contains all Semantic Kernel plugins for the Interview API.
Plugins are automatically discovered and registered by the plugin loader
when the kernel is initialized.

Plugin Types:
    - Native Function Plugins: Python functions exposed as AI tools
    - Prompt-based Plugins: AI functions using prompt templates

Structure:
    plugins/
        plugin_name/
            function_name/
                skprompt.txt    # Prompt template
                config.json     # Function configuration (optional)

Available Plugins:
    - film_search: Native function plugin for database film searches
    - llm_agent: Prompt-based plugin for general question answering
    - film_summary: Prompt-based plugin for structured film summaries
    - film_short_summary: Prompt-based plugin for brief film summaries
    - chat: Prompt-based plugin for streaming chat responses

Example:
    ```python
    from core.ai_kernel import get_default_kernel

    # Plugins are automatically registered
    kernel = get_default_kernel()

    # Access registered plugins
    film_search = kernel.get_plugin("film_search")
    ```
"""
