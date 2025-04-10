# automcp

## 🚀 Overview

automcp allows you to easily convert tool, agents and orchestrators from existing agent frameworks [MCP](https://modelcontextprotocol.io/introduction) servers, that can then be accessed by standardized interfaces via clients like Cursor and Claude Desktop.

We currently support deployment of agents, tools, and orchestrators as MCP servers for the following agent frameworks:

1. CrewAI
2. LangGraph
3. Llama Index
4. OpenAI Agents SDK
5. Pydantic AI
6. mcp-agent

## 🔧 Installation

Install from PyPI:

```bash
# Basic installation
pip install automcp
```

Or install from source:

```bash
git clone https://github.com/napthaai/automcp.git
cd automcp
uv venv 
source .venv/bin/activate
pip install -e .
```

## 🧩 Quick Start

Create a new MCP server for your project:

Navigate to your project directory with your agent implementation:

```bash
cd your-project-directory
```

Generate the MCP server files via CLI with one of the following flags (crewai_orchestrator, crewai_agent, crewai_tool, langgraph_agent, langchain_tool, llamaindex_agent, openai_agent, pydantic_agent, mcp_agent):

```bash
automcp init -f crewai_orchestrator
```

Edit the generated `run_automcp.py` file to configure your agent:

```python
# Replace these imports with your actual agent classes
from your_module import YourCrewClass

# Define the input schema
class InputSchema(BaseModel):
    parameter1: str
    parameter2: str

# Set your agent details
name = "<YOUR_AGENT_NAME>"
description = "<YOUR_AGENT_DESCRIPTION>"

# For CrewAI projects
mcp_crewai_orchestrator = create_crewai_orchestrator_adapter(
    orchestrator_instance=YourCrewClass().crew(),
    name=name,
    description=description,
    input_schema=InputSchema,
)
```

Install dependencies and run your MCP server:

```bash
automcp serve -t sse
```

## 📁 Generated Files

When you run `automcp init -f <FRAMEWORK>`, the following file is generated:

### run_automcp.py

This is the main file that sets up and runs your MCP server. It contains:

- Server initialization code
- STDIO and SSE transport handlers
- A placeholder for your agent implementation
- Utilities to suppress warnings that might corrupt the STDIO protocol

You'll need to edit this file to:

- Import your agent/crew classes
- Define your input schema (the parameters your agent accepts)
- Configure the adapter with your agent


## 🔍 Examples

### Running the examples

The repository includes examples for each supported framework:

```bash
# Clone the repository
git clone https://github.com/NapthaAI/automcp.git
cd automcp

# Install automcp in development mode
pip install -e .

# Navigate to an example directory
cd examples/crewai/marketing_agents

# Generate the MCP server files (use the appropriate framework)
automcp init -f crewai_orchestrator

# Edit the generated run_automcp.py file to import and configure the example agent
# (See the specific example's README for details)

# Add a .env file with necessary environmental variables

# Install dependencies and run
automcp serve -t sse
```

Each example follows the same workflow as a regular project:

1. Run `automcp init -f <FRAMEWORK>` to generate the server files
2. Edit `run_automcp.py` to import and configure the example agent
3. Add a .env file with necessary environmental variables
4. Install dependencies and serve using `automcp serve -t sse`

### CrewAI example
Here's what a typical configured `run_automcp.py` looks like for a CrewAI example:

```python
import warnings
from typing import Any
from automcp.adapters.crewai import create_crewai_orchestrator_adapter
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP Server")

warnings.filterwarnings("ignore")

from crew import MarketingPostsCrew

class InputSchema(BaseModel):
    project_description: str
    customer_domain: str

name = "marketing_posts_crew"
description = "A crew that posts marketing posts to a social media platform"

# Create an adapter for crewai_orchestrator
mcp_crewai_orchestrator = create_crewai_orchestrator_adapter(
    orchestrator_instance=MarketingPostsCrew().crew(),
    name=name,
    description=description,
    input_schema=InputSchema,
)
mcp.add_tool(
    mcp_crewai_orchestrator,
    name=name,
    description=description
)

# Server entrypoints
def serve_sse():
    mcp.run(transport="sse")

def serve_stdio():
    # Redirect stderr to suppress warnings that bypass the filters
    import os
    import sys

    class NullWriter:
        def write(self, *args, **kwargs):
            pass
        def flush(self, *args, **kwargs):
            pass

    # Save the original stderr
    original_stderr = sys.stderr

    # Replace stderr with our null writer to prevent warnings from corrupting STDIO
    sys.stderr = NullWriter()

    # Set environment variable to ignore Python warnings
    os.environ["PYTHONWARNINGS"] = "ignore"

    try:
        mcp.run(transport="stdio")
    finally:
        # Restore stderr for normal operation
        sys.stderr = original_stderr

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        serve_sse()
    else:
        serve_stdio()
```

## 🔄 Running Your MCP Server

After setting up your files, you can run your server using one of these methods:

```bash
# Using the automcp CLI
automcp serve -t stdio    # STDIO transport
automcp serve -t sse      # SSE transport

# Or run the Python file directly
python run_automcp.py       # STDIO transport
python run_automcp.py sse   # SSE transport

# Or with uv run (if configured in pyproject.toml)
uv run serve_stdio
uv run serve_sse
```

**Note about transport modes:**
- **STDIO**: You don't need to run the server manually - it will be started by the client (Cursor)
- **SSE**: This is a two-step process:
  1. Start the server separately: `python run_automcp.py sse` or `automcp serve -t sse`
  2. Add the mcp.json configuration to connect to the running server

If you want to use the `uv run` commands, add the following to your `pyproject.toml`:

```toml
[tool.uv.scripts]
serve_stdio = "python run_automcp.py"
serve_sse = "python run_automcp.py sse"
```

## 🔌 Using with MCP Clients

### Cursor

To integrate with Cursor IDE, create a `.cursor` folder in your project root and add an `mcp.json` file with the following configuration:

```json
{
    "mcpServers": {
        "crew-name-stdio": {
            "type": "stdio",
            "command": "/absolute/path/to/your/.venv/bin/uv",
            "args": [
                "--directory",
                "/absolute/path/to/your/project_dir",
                "run",
                "serve_stdio"
            ],
            "env": {
                "OPENAI_API_KEY": "sk-",
                "SERPER_API_KEY": ""
            }
        },
        
        "crew-name-python": {
            "type": "stdio",
            "command": "/absolute/path/to/your/.venv/bin/python",
            "args": [
                "/absolute/path/to/your/project_dir/run_automcp.py"
            ],
            "env": {
                "OPENAI_API_KEY": "sk-",
                "SERPER_API_KEY": ""
            }
        },
        
        "crew-name-automcp": {
            "type": "stdio",
            "command": "/absolute/path/to/your/.venv/bin/automcp",
            "args": [
                "serve",
                "-t",
                "stdio"
            ],
            "cwd": "/absolute/path/to/your/project_dir",
            "env": {
                "OPENAI_API_KEY": "sk-",
                "SERPER_API_KEY": ""
            }
        },
        
        "crew-name-sse": {
            "type": "sse",
            "url": "http://localhost:8000/sse"
        }
    }
}
```

**Note:** Be sure to replace all placeholder paths with absolute paths to your actual files and directories.

### Direct GitHub Execution

Push your project to GitHub and use:

```json
{
   "mcpServers": {
       "My Agent": {
           "command": "uvx",
           "args": [
               "--from",
               "git+https://github.com/your-username/your-repo",
               "serve_stdio"
           ],
           "env": {
               "OPENAI_API_KEY": "your-key-here"
           }
       }
   }
}
```

## 🛠️ Creating New Adapters

Want to add support for a new agent framework? Here's how:

1. Create a new adapter file in automcp/adapters/ (or add to an existing framework file):

```python
# automcp/adapters/framework.py
import json
import contextlib
import io
from typing import Any, Callable, Type
from pydantic import BaseModel

def create_framework_agent_adapter(
    agent_instance: Any,
    name: str,
    description: str,
    input_schema: Type[BaseModel],
) -> Callable:
    """Doc string for your function"""
    
    # Get the field names and types from the input schema
    schema_fields = input_schema.model_fields

    # Create the parameter string for the function signature
    params_str = ", ".join(
        f"{field_name}: {field_info.annotation.__name__}"
        for field_name, field_info in schema_fields.items()
    )

    # Create the function body that constructs the input schema
    # Note: You may need to adjust the method calls (kickoff, model_dump_json)
    # to match your framework's specific API
    body_str = f"""def run_agent({params_str}):
        inputs = input_schema({', '.join(f'{name}={name}' for name in schema_fields)})
        with contextlib.redirect_stdout(io.StringIO()):
            result = agent_instance.framework_specific_run(inputs=inputs.model_dump())
        return result.framework_specific_result()
    """

    # Create a namespace for the function
    namespace = {
        "input_schema": input_schema,
        "orchestrator_instance": agent_instance,
        "json": json,
        "contextlib": contextlib,
        "io": io,
    }

    # Execute the function definition in the namespace
    exec(body_str, namespace)

    # Get the created function
    run_orchestrator = namespace["run_orchestrator"]

    # Add proper function metadata
    run_orchestrator.__name__ = name
    run_orchestrator.__doc__ = description

    return run_orchestrator
```

2. Create an example in examples/your_framework/

## 📝 Notes

- When working with STDIO transport, be careful with print statements in your agent code as they can corrupt the protocol
- The MCP Inspector can be used for debugging: `npx @modelcontextprotocol/inspector`
- Remember that for STDIO mode, the client (like Cursor) will start the server for you
- For SSE mode, you need to manually start the server and then configure the client to connect to it