# from langchain_google_genai import GoogleGenerativeAI Import relevant functionality
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import AIMessage
from contextlib import asynccontextmanager
import os
from pydantic import SecretStr

# from calendar_tool import CalendarToolFunction
# from spotifiy_tool import spotify_tools
from typing import Annotated
from rich.console import Console
from rich.markdown import Markdown

console = Console()

api_key = open("google_api_key.secret").read().strip()
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=SecretStr(api_key),
)

memory = MemorySaver()

trimmer = trim_messages(
    max_tokens=300,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

mcp_definitions = {
    "spotify": {
        "url": "http://localhost:8001/sse",
        "transport": "sse",
    },
}


async def input_output_loop(agent_executor, config):
    user_input = input(">>> ")
    response = await agent_executor.ainvoke(
        {"messages": [HumanMessage(content=user_input)]}, config
    )
    chunk = response["messages"][-1]
    if type(chunk) is AIMessage:
        message = chunk
        print("message ->", message)
        if message.content:
            if type(message.content) is list:
                for m in message.content:
                    console.print(Markdown(m))
            else:
                console.print(Markdown(message.content))
        if message.tool_calls:
            for tool in message.tool_calls:
                print("tool ->", tool["name"], tool["args"])


async def run_model():
    async with MultiServerMCPClient(mcp_definitions) as client:
        agent_executor = create_react_agent(model, client.get_tools())
        config = {"configurable": {"thread_id": "abc123"}}
        while True:
            await input_output_loop(agent_executor, config)


# Ensure the script runs the async main function
if __name__ == "__main__":
    import asyncio

    asyncio.run(run_model())
