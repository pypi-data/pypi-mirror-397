# InfoNgen Document Search MCP Server

This is a Model Context Protocol (MCP) server that provides semantic search capabilities using the InfoNgen API. It allows AI assistants to search for documents, news, and other content indexed by InfoNgen.

## Features

- **Semantic Search**: Perform semantic searches against the InfoNgen database.
- **Document Retrieval**: Retrieves document details including headline, summary, provider, publication date, and URL.
- **Content Snippets**: Returns relevant content chunks from the documents.

## Configuration

The server requires the following configuration, which can be provided via environment variables or command-line arguments:

| Environment Variable | Command Line Argument | Description |
|----------------------|-----------------------|-------------|
| `API_BASE_URL` | `--api-base-url` | The base URL for the InfoNgen API. |
| `API_KEY` | `--api-key` | Your InfoNgen API Key. |
| `OAUTH_TOKEN_URL` | `--oauth-token-url` | The OAuth2 token endpoint URL. |
| `OAUTH_CLIENT_ID` | `--oauth-client-id` | Your OAuth2 Client ID. |
| `OAUTH_CLIENT_SECRET` | `--oauth-client-secret` | Your OAuth2 Client Secret. |
| `USER_CONTEXT` | `--user-context` | The user context string for API requests. |

## Installation

Ensure you have Python 3.11 or higher installed.

1. Clone the repository.
2. Install dependencies:

```bash
# Install dependencies and set up the environment
uv sync
```

## Usage

### Running the Server

You can run the server using `uvx`. Make sure to set the required environment variables or command line arguments first.

```bash
# Set environment variables (example for PowerShell)
$env:API_BASE_URL="https://api.infongen.com/v1"
$env:API_KEY="your-api-key"
$env:OAUTH_TOKEN_URL="https://auth.infongen.com/oauth/token"
$env:OAUTH_CLIENT_ID="your-client-id"
$env:OAUTH_CLIENT_SECRET="your-client-secret"
$env:USER_CONTEXT="your-user-context"

# Run the server
uvx --index-url https://nexus-ci.core.kuberocketci.io/repository/krci-python-group/simple/ --from epmp-igen-document-search-mcp-server mcp-server
```

### Tools

#### `search`

Performs a semantic search.

- **query** (string, required): The text to search for.
- **limit** (integer, optional): The maximum number of documents to return. Default is 10.

## Development

This project uses `mcp` and `requests` libraries. The main logic is in `main.py` which defines the MCP server and tools, and `api.py` which handles the API communication.
