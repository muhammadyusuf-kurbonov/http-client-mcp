import os
import json
from typing import Any, Dict, Optional
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("Universal Secure HTTP Client")

def load_predefined_headers() -> Dict[str, str]:
    """Bakes in default headers from your MCP configuration environment."""
    headers = {}
    
    # Support a simple global Authorization Bearer token 
    bearer_token = os.environ.get("HTTP_BEARER_TOKEN")
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
        
    # Support complex, multi-key setups passed as a JSON string
    custom_headers_json = os.environ.get("HTTP_DEFAULT_HEADERS")
    if custom_headers_json:
        try:
            custom_headers = json.loads(custom_headers_json)
            if isinstance(custom_headers, dict):
                headers.update({str(k): str(v) for k, v in custom_headers.items()})
        except json.JSONDecodeError:
            pass
            
    return headers

@mcp.tool()
async def send_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Sends an HTTP request. Automatically injects tokens and headers 
    predefined in the server configuration file.
    """
    method = method.upper()
    
    # Merge the predefined headers with any runtime headers the LLM generates
    merged_headers = load_predefined_headers()
    if headers:
        merged_headers.update(headers)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=merged_headers,
                json=json_data,
                params=params,
                follow_redirects=True
            )
            return f"Status Code: {response.status_code}\n\n{response.text}"
        except httpx.RequestError as exc:
            return f"An error occurred: {exc}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
