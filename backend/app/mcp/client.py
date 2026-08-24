from app.mcp.sustainability_data_server import (
    get_energy_data,
    get_emissions_data,
    get_water_data,
)


async def call_stdio_tool(
    command: str, args: list[str], tool: str, arguments: dict
) -> object:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    server = StdioServerParameters(command=command, args=args)
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            return result.content


def call_data_tool(tool: str, year: int) -> dict:
    tools = {
        "get_energy_data": get_energy_data,
        "get_emissions_data": get_emissions_data,
        "get_water_data": get_water_data,
    }
    if tool not in tools:
        raise ValueError(f"Unknown MCP tool: {tool}")
    return tools[tool](year)
