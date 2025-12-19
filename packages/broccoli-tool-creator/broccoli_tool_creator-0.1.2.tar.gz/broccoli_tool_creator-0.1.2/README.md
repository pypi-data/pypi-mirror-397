# Broccoli Tool Creator

Automated tool creation for Broccoli Backend from FastAPI endpoints.

## Installation

```bash
pip install broccoli-tool-creator
```

## Features

- **AST-based Extraction**: Automatically extracts metadata from FastAPI endpoints including docstrings, parameters, and response models.
- **Cognito Integration**: Handles authentication with AWS Cognito SRP.
- **Broccoli Integration**: Automatically creates and updates tools on the Broccoli platform.
- **Interactive UI**: Injects "Create Tool" buttons directly into your FastAPI Swagger UI.

## Quick Start

```python
from fastapi import FastAPI
from broccoli_tool_creator import setup_tool_creator, ToolCreatorConfig

app = FastAPI()

config = ToolCreatorConfig(
    broccoli_api_url="https://api.broccoli.com",
    cognito_client_id="...",
    cognito_pool_id="...",
    cognito_username="...",
    cognito_password="...",
    owner_id="..."
)

setup_tool_creator(app, config)
```

## License

MIT
