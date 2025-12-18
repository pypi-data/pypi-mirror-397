import os
import httpx
from fastmcp import FastMCP
import base64

# Get configuration from environment variables with defaults
base_url = os.getenv("API_BASE_URL", "http://localhost:3000/v1")
openapi_spec_url = os.getenv("OPENAPI_SPEC_URL", "http://localhost/local/openapi/gal-inq.json")
server_name = os.getenv("SERVER_NAME", "Galicia Inquiries API")
bearer = os.getenv("BEARER_TOKEN","")
username = os.getenv("USERNAME","")
password = os.getenv("PASSWORD","")

# Create an HTTP client for your API
if bearer!="":
    headers = {"Authorization": f"Bearer {bearer}"}
    client = httpx.AsyncClient(base_url=base_url, headers=headers)
elif username!="" and password!="":
    user_pass = f"{username}:{password}"
    encoded_u = base64.b64encode(user_pass.encode()).decode()
    headers = {"Authorization": f"Basic {encoded_u}"}
    client = httpx.AsyncClient(base_url=base_url, headers=headers)
else:
    client = httpx.AsyncClient(base_url=base_url)

# Load your OpenAPI spec
openapi_spec = httpx.get(openapi_spec_url).json()

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name=server_name
)

# WRAP THE RUN COMMAND IN A FUNCTION
def main():
    mcp.run()

if __name__ == "__main__":
   main()