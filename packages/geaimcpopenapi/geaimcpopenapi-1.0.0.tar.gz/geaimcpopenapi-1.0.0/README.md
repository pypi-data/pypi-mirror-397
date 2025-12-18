# OpenAPI MCP

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/fastmcp-2.14.0+-green.svg)](https://pypi.org/project/fastmcp/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![uv](https://img.shields.io/badge/uv-managed-blueviolet.svg)](https://github.com/astral-sh/uv)

OpenAPI based MCP that creates a [FastMCP](https://pypi.org/project/fastmcp/) server from an OpenAPI specification.

## Build and Install

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and requires Python 3.12 or higher.

### Prerequisites

1. Install Python 3.12 or higher
2. Install [uv](https://github.com/astral-sh/uv):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd openapimcp
   ```

2. Install the project in editable mode:
   ```bash
   uv pip install -e .
   ```
   
   This will:
   - Install all required dependencies (`fastmcp` and `httpx`)
   - Create the `openapimcp` command-line tool
   - Make the project available for development

3. Verify the installation:
   ```bash
   openapimcp --help
   ```

### Alternative: Using uvx

You can also run the tool directly without installation using `uvx`:

```bash
uvx openapimcp
```

This is particularly useful for the example configurations in the `examples` directory.

## Usage

The `openapimcp` command-line tool creates a FastMCP server from an OpenAPI specification. The tool is configured using environment variables.

### Configuration

The following environment variables are available for configuration:

*   `API_BASE_URL`: The base URL of the API.
*   `OPENAPI_SPEC_URL`: The URL of the OpenAPI specification.
*   `SERVER_NAME`: The name of the MCP server.
*   `BEARER_TOKEN`: The bearer token for authentication.
*   `USERNAME`: The username for basic authentication.
*   `PASSWORD`: The password for basic authentication.

### Running the server

To run the server, you can use the `openapimcp` script, which is created during the installation. You need to set the environment variables before running the script.

For example:

```bash
export API_BASE_URL="http://localhost:3000/v1"
export OPENAPI_SPEC_URL="http://localhost/local/openapi/gal-inq.json"
export SERVER_NAME="Galicia Inquiries API"
openapimcp
```

### Examples

The `examples` directory contains several example configurations that can be used to run the server. These examples are in the form of JSON files that define the environment variables for different services.

For example, to run the `gal-mock` example, you can use the environment variables defined in `examples/gal-mock/gal-inq.json`.

```json
{
    "mcpServers": {
        "galInq": {
            "command": "uvx",
            "args": [
                "openapimcp"
            ],
            "env": {
                "SERVER_NAME": "Galicia Inquiries API",
                "OPENAPI_SPEC_URL": "http://localhost/local/openapi/gal-inq.json",
                "API_BASE_URL": "http://localhost:3000/v1"
            }
        }
    }
}
```

This configuration can be used with a tool that consumes `mcpServers` definitions to start the MCP server with the specified environment.