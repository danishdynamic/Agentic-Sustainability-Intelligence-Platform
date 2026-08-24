from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sustainability-data")


@mcp.tool()
def get_emissions_data(year: int) -> dict:
    return {
        "year": year,
        "scope_1_tco2e": 4200,
        "scope_2_tco2e": 3100,
        "scope_3_tco2e": 18400,
    }


@mcp.tool()
def get_energy_data(year: int) -> dict:
    return {
        "year": year,
        "energy_consumption_mwh": 12000,
        "renewable_percentage": 90 if year >= 2026 else 70 if year == 2025 else 50,
    }


@mcp.tool()
def get_water_data(year: int) -> dict:
    return {"year": year, "water_withdrawal_m3": 82000, "recycled_percentage": 38}


if __name__ == "__main__":
    mcp.run()
