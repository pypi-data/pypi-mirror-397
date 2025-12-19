from mcp.server.fastmcp import FastMCP
from .api import API
from .options import Options
from .tools import tools

def main() -> None:
    options = Options.from_env_and_args()
    mcp = FastMCP("InfoNgen document search")
    api = API(options)

    tools(mcp, api)

    mcp.run()  

if __name__ == "__main__":
    main()