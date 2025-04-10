# Agent Johnny5

An intelligent agent system for code repository analysis and management.

## Project Structure

```
root/
├── agents/
│   ├── gitminer/             # Git history analyzer agent
│   ├── pullsage/             # PR summarization agent
│   ├── codeweaver/           # Code structure and symbol analysis
│   ├── indexer/              # Embedding + vector search manager
│   └── mainagent/            # Query router / master agent
│
├── shared/
│   ├── models/               # Shared data schemas (e.g. PRs, Commits, Symbols)
│   ├── utils/                # Common helper functions (e.g. git parsing, LLM wrappers)
│   └── config/               # Agent SDK config, secrets, environment files
│
├── scripts/                  # CLI tools, dataset downloaders, setup scripts
│
├── tests/                    # Shared integration or end-to-end tests
│
├── .env                      # Common environment file
├── Makefile                  # Standard commands (e.g. `make dev`, `make test`)
└── requirements.txt          # Python dependencies
```

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Unix) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your configuration

## Usage

Run commands using the Makefile:

```bash
make dev     # Start development environment
make test    # Run tests
make lint    # Run linters
```

## License

[MIT](LICENSE)
