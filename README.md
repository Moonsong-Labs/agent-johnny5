# <div align="center">Agent Johnny5</div>

<pre>
<div align="center">
    🚧 UNDER CONSTRUCTION 🚧  
</div>
<div align="center">
    A minimalistic multi-agent system to analyze GitHub repositories using Google ADK and GitHub MCP.
</div>
</pre>



## System Architecture

-   **Main Agent (Orchestrator)**: Acts as the central coordinator, receives prompts and routes them to the appropriate specialized agent
-   **Specialized Agents**: Each agent has a specific purpose and expertise:
    -   **PullSage**: Provides wisdom about pull requests
    -   More agents to be added...

## Getting Started

1. Set up the environment:

    ```
    python scripts/setup.py
    ```

2. Add your API keys to the `.env` file:

    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

3. Run the multi-agent system using one of these methods:

    ```
    # Run as a standalone script
    python scripts/run_agents.py

    # Run as a FastAPI development server
    python scripts/dev.py

    # Test the ADK integration
    python test_agent.py


    # Run with ADK web interface
    cd agents
    adk web
    ```

## Project Structure

```
agent-johnny5/
├── agent.py               # Top-level entry point for ADK
├── agents/                # Agent implementations
│   ├── __init__.py        # Entry point for agent modules
│   ├── mainagent/         # Main orchestrator agent
│   ├── pullsage/          # PR analysis agent
│   └── ...                # Other specialized agents
├── shared/                # Shared utilities and models
│   ├── models/            # Data models
│   ├── utils/             # Utility functions
│   └── config/            # Configuration helpers
├── scripts/               # Utility scripts
│   ├── setup.py           # Project setup
│   ├── run_agents.py      # Run the agent system
│   └── dev.py             # Development server
├── adk.config.json        # Configuration for ADK framework
├── test_agent.py          # Script to test ADK integration
└── tests/                 # Test suite
```

## Extending the System

To add a new agent:

1. Create a new directory in the `agents/` folder
2. Implement your agent class extending the base `Agent` class
3. The Main Agent will automatically discover and load your agent

## License

[MIT License](LICENSE)
