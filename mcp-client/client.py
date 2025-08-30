import asyncio
from fastmcp import Client

async def main():
    # Connect to the MCP server we just created
    async with Client("mcp-server/server.py") as client:
        
        # tools = await client.list_tools()
        # print("Generated Tools:")
        # for tool in tools:
        #     print(f"- {tool.name}")

        # resources = await client.list_resources()
        # print("Generated Resources:")
        # for resource in resources:
        #     print(f"- {resource.name}")


        prompts = await client.list_prompts()
        for prompt in prompts:
            print(f"Prompt: {prompt.name}")
            print(f"Description: {prompt.description}")
            if prompt.arguments:
                print(f"Arguments: {[arg.name for arg in prompt.arguments]}")
            # Access tags and other metadata
            if hasattr(prompt, '_meta') and prompt._meta:
                fastmcp_meta = prompt._meta.get('_fastmcp', {})
                print(f"Tags: {fastmcp_meta.get('tags', [])}")
            
        print("\n\nCalling tool 'add'...")
        user = await client.call_tool("add", {"a": 1, "b": 2    })
        print(f"Result:\n{user.data}")

        content = await client.read_resource('resource://config')
        print(f"\n\nReading resource 'resource://config'...\n{content[0].text}")

        content_hello = await client.read_resource('greetings://Alice')
        print(f"\n\nReading resource 'greetings://Alice'...\n{content_hello[0].text}")

        messages = await client.get_prompt("analyze_data", {"data_points": [1, 2, 3]})
        print(messages.messages)

if __name__ == "__main__":
    asyncio.run(main())