import os
from google import genai
from fastmcp import Client
from typing import AsyncGenerator

async def generate_gemini_response(
    prompt: str, 
    gemini_client: genai.Client, 
    mcp_client: Client
) -> AsyncGenerator[str, None]:
    """
    Generates a streaming response from the Gemini model using the low-level API,
    which correctly handles tool calling with the FastMCP client.
    """
    try:
        system_instruction = "You are a helpful AI assistant. Answer general knowledge questions using your own knowledge. Only use the provided tools when the question explicitly requires their functionality, such as performing a calculation or accessing specific external data."
        
        # Use the streaming method and pass the mcp_client object directly
        response_stream = await gemini_client.aio.models.generate_content_stream(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                temperature=0,
                tools=[mcp_client.session],
                system_instruction=system_instruction,
            ),
        )

        is_tool_based = False

        # Asynchronously iterate over the streaming chunks
        async for chunk in response_stream:
            # Check if the response includes a tool call
            if chunk.automatic_function_calling_history:
                is_tool_based = True
            
            if chunk.text:
                yield chunk.text

        # Yield a final message to indicate tool usage
        if is_tool_based:
            yield "\n\n(Tool-based.)"
            
    except Exception as e:
        print(f"Error calling the Gemini API with FastMCP: {e}")
        yield "Sorry, I am unable to generate a response at this time."