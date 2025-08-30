from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name} from My MCP Server!"


if __name__ == "__main__":
    mcp.run()

