import asyncio
import os
import sys
from dotenv import load_dotenv
from fastmcp import Client

load_dotenv()

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
print(MCP_SERVER_URL)
client = Client(MCP_SERVER_URL)
async def main():
    async with client:
        print("Client connected.")
        tools = await client.list_tools()
        print("Available tools:", tools)    
        # Ping the server to confirm connection
        # response = await client.ping()
        # print(f"Ping successful. Server says: {response}")

        # # Example: Call a tool from the server
        # status = await client.get_server_status()
        # print(f"Server Status: {status}")

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the main async function
    asyncio.run(main())
