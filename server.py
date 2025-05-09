from typing import List, Dict, Any
import httpx, datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-public-api-hub")

NAGER = "https://date.nager.at/api/v3/PublicHolidays"
OSM_SEARCH = "https://nominatim.openstreetmap.org/search"
RC = "https://restcountries.com/v3.1/name/"
PKE = "https://pokeapi.co/api/v2/pokemon/"

@mcp.tool()
async def geocode(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    params = {"q": query, "format": "json", "limit": limit}
    headers = {"User-Agent": "YourApp/1.0 (contact@example.com)"}
    async with httpx.AsyncClient(headers=headers, timeout=20) as cli:
        r = await cli.get(OSM_SEARCH, params=params)
    r.raise_for_status()
    return [
        {
            "display_name": p["display_name"],
            "lat": p["lat"],
            "lon": p["lon"],
        }
        for p in r.json()
    ]

@mcp.tool()
async def country_basic(name: str = "indonesia") -> Dict[str, Any]:
    url = f"{RC}{name}"
    params = {"fields": "name,capital,flags,population,region,subregion"}
    async with httpx.AsyncClient(timeout=15) as cli:
        r = await cli.get(url, params=params)
    r.raise_for_status()
    return r.json()[0]

@mcp.tool()
async def pokemon_info(name_or_id: str = "pikachu") -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=20) as cli:
        r = await cli.get(f"{PKE}{name_or_id.lower()}")
    r.raise_for_status()
    d = r.json()
    return {
        "id": d["id"],
        "name": d["name"].title(),
        "types": [t["type"]["name"] for t in d["types"]],
        "height_dm": d["height"],
        "weight_hg": d["weight"],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in d["stats"]},
        "sprite": d["sprites"]["front_default"],
    }


@mcp.tool()
async def upcoming_holidays(year: int = datetime.date.today().year,
                            country: str = "ID",
                            limit: int | None = 5) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(timeout=15) as cli:
        r = await cli.get(f"{NAGER}/{year}/{country.upper()}")
    r.raise_for_status()

    today = datetime.date.today().isoformat()
    future = [h for h in r.json() if h["date"] >= today]
    return future[:limit] if limit else future


if __name__ == "__main__":
    mcp.run(transport="stdio")
