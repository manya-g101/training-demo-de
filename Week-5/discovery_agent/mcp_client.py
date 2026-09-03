import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def parse_tool_result(result: Any) -> Any:
    if result is None:
        return None

    if isinstance(result, dict):
        return result

    content = getattr(result, "content", None)
    if content is None:
        return result

    if not content:
        return None

    first_item = content[0]
    text_value = getattr(first_item, "text", None)
    if text_value is not None:
        try:
            return json.loads(text_value)
        except json.JSONDecodeError:
            return text_value

    if isinstance(first_item, dict):
        item_text = first_item.get("text")
        if item_text:
            try:
                return json.loads(item_text)
            except json.JSONDecodeError:
                return item_text

    return result


async def call_mcp_tool(tool_name: str, arguments: dict[str, Any], server_script: str | Path | None = None) -> Any:
    script_path = Path(server_script) if server_script is not None else Path(__file__).with_name("mcp_server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(script_path)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return parse_tool_result(result)


async def list_mcp_tools(server_script: str | Path | None = None) -> list[str]:
    script_path = Path(server_script) if server_script is not None else Path(__file__).with_name("mcp_server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(script_path)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tool_list = await session.list_tools()
            return [tool.name for tool in tool_list.tools]

DEFAULT_ROOT = Path(__file__).resolve().parents[1]


async def main() -> None:
    server_script = Path(__file__).with_name("mcp_server.py")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_script)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tool_list = await session.list_tools()
            print("Available tools:")
            for tool in tool_list.tools:
                print(f"- {tool.name}: {tool.description}")

            result = await session.call_tool(
                "build_discovery_report_tool",
                {
                    "root_dir": str(DEFAULT_ROOT),
                },
            )
            print("\nDiscovery report:")
            print(parse_tool_result(result))


if __name__ == "__main__":
    asyncio.run(main())
