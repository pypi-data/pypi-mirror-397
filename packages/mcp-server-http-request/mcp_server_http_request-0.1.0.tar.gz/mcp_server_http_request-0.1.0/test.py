import asyncio
import json

import yaml
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ThinkingPart,
    ThinkingPartDelta,
)
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown


async def test_http_request_agent(prompt: str, verbose: bool = True):
    """Test the HTTP Request MCP server with pydantic-ai agent.

    Parameters
    ----------
    prompt : str
        Natural language instruction for HTTP requests
    verbose : bool, default True
        Whether to show live AI reasoning and tool calls
    """

    server = MCPServerStdio(
        "uv",
        args=["run", "mcp-server-http-request"],
        max_retries=3,
        timeout=30,
    )

    agent = Agent(
        model="anthropic:claude-sonnet-4-5",
        toolsets=[server],
        output_retries=3,
        retries=3,
    )

    console = Console()

    if verbose:
        with Live(console=console, vertical_overflow="visible", auto_refresh=True) as live:
            accumulated_content = ""

            def update_display(content: str):
                live.update(Markdown(content))

            async with agent.iter(prompt) as run:
                async for node in run:
                    if Agent.is_model_request_node(node):
                        async with node.stream(run.ctx) as model_stream:
                            async for event in model_stream:
                                if isinstance(event, PartStartEvent):
                                    if isinstance(event.part, (TextPart | ThinkingPart)):
                                        accumulated_content += f"\n{event.part.content}"
                                        update_display(accumulated_content)
                                elif isinstance(event, PartDeltaEvent) and isinstance(
                                    event.delta, (TextPartDelta | ThinkingPartDelta)
                                ):
                                    accumulated_content += event.delta.content_delta or ""
                                    update_display(accumulated_content)

                    elif Agent.is_call_tools_node(node):
                        async with node.stream(run.ctx) as handle_stream:
                            async for event in handle_stream:
                                if isinstance(event, FunctionToolCallEvent):
                                    try:
                                        args_str = (
                                            event.part.args
                                            if isinstance(event.part.args, str)
                                            else str(event.part.args)
                                        )
                                        accumulated_content += f"\n\n>Called tool `{event.part.tool_name}` with args:\n\n```yaml\n{yaml.dump(json.loads(args_str))}\n```\n\n"
                                    except Exception:
                                        accumulated_content += str(event.part.args)
                                    update_display(accumulated_content)
                                elif isinstance(event, FunctionToolResultEvent):
                                    accumulated_content += f"\n\n>Tool `{event.result.tool_name}` returned:\n\n```markdown\n{event.result.content}\n```\n\n"
                                    update_display(accumulated_content)

                    elif Agent.is_end_node(node):
                        return node.data.output
    else:
        async with agent.iter(prompt) as run:
            async for node in run:
                if Agent.is_end_node(node):
                    return node.data.output


if __name__ == "__main__":
    # Test with a simple HTTP GET request
    result = asyncio.run(
        test_http_request_agent(
            "How much did emily spend? http://127.0.0.1:8001",
            verbose=True,
        )
    )
    print(f"\n\nFinal result: {result}")
