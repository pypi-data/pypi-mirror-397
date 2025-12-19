from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent
from .api import API

def tools(mcp: FastMCP, api: API):
    
    @mcp.tool(
            name="semantic_search",
            title="InfoNgen semantic search",
            description="Perform a semantic search for documents using the InfoNgen API",
            structured_output=False
    )
    def search(
        query: Annotated[str, Field(description="The query to search for.")],
        limit: Annotated[int, Field(description="The maximum number of documents to return. Default is 150.")] = 150
    ) -> CallToolResult:
        if (query == None or query.strip() == ""):
            return CallToolResult(
                content=[TextContent(type="text", text="The search query cannot be empty.")],
                isError=True
            )

        search_response = api.invoke(
            "POST", 
            "/searches/semantic?redirect_to_results=false", 
            {
                "conditions": [
                    {
                        "name": "embedding",
                        "values": [query]
                    }
                ],
                "search_settings": {
                    "date_range": "Last30Days",
                    "sorting": "relevancy",
                },
            }
        )

        results = api.invoke(
            "GET", 
            f"""/searches/semantic/{search_response['uid']}/results?show_options=documents&show_fields={','.join([
                "headline",
                "summary",
                "contributor",
                "published_at",
                "main.uris.remotecopyuri"
            ])}"""
        )
        if results.get('documents'):
            results['documents'] = results['documents'][:limit]

        if (results.get("documents_total", 0) == 0):
            return CallToolResult(
                content=[TextContent(type="text", text="No documents found for the given query.")],
                isError=True
            )
            
        contents: list[TextContent] = []
        for document in map(dict, results.get("documents", [])):
            text = ""
            text += f"Title: {document.get('headline', 'N/A')}\n"
            text += f"Summary: {document.get('summary', 'N/A')}\n"
            text += f"Provider: {document.get('contributor', 'N/A')}\n"
            text += f"Date: {document.get('published_at', 'N/A')}\n"

            urls = map(str, document.get('main.uris.remotecopyuri', []))
            text += f"URL: {next(urls, 'N/A')}\n"
            
            text += "Content: ... "
            for nested in map(dict, document.get('nested_documents', [])):
                for chunk in map(str, nested.get('chunk', [])):
                    text += f"{chunk} ... "
            
            contents.append(TextContent(type="text", text=text.strip()))

        return CallToolResult(
            content=contents,
        )
