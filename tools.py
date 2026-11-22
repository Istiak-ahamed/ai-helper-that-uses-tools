from datetime import date, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from google.genai import types

NOTES_DIR = Path(__file__).resolve().parent / "notes"


def search_notes(query: str) -> dict[str, Any]:
    """Search local markdown and text files in the notes/ directory."""
    if not NOTES_DIR.exists():
        return {"query": query, "matches": [], "error": "notes/ directory not found."}

    terms = [term.lower() for term in query.split() if term.strip()]
    if not terms:
        return {"query": query, "matches": [], "error": "Empty search query."}

    matches: list[dict[str, Any]] = []
    for file_path in sorted(NOTES_DIR.iterdir()):
        if file_path.suffix.lower() not in {".md", ".txt"} or not file_path.is_file():
            continue

        content = file_path.read_text(encoding="utf-8")
        matching_lines = [
            line.strip()
            for line in content.splitlines()
            if any(term in line.lower() for term in terms)
        ]
        if matching_lines:
            matches.append(
                {
                    "file": file_path.name,
                    "snippets": matching_lines[:5],
                }
            )

    return {
        "query": query,
        "match_count": len(matches),
        "matches": matches,
    }


def add_days(start_date: str, days: int) -> dict[str, Any]:
    """Add (or subtract) a number of days from a YYYY-MM-DD date string."""
    try:
        parsed = date.fromisoformat(start_date.strip())
    except ValueError:
        return {
            "error": f"Invalid start_date '{start_date}'. Expected YYYY-MM-DD format."
        }

    result = parsed + timedelta(days=int(days))
    return {
        "start_date": parsed.isoformat(),
        "days_added": int(days),
        "result_date": result.isoformat(),
        "weekday": result.strftime("%A"),
    }


def get_weather_info(city: str) -> dict[str, Any]:
    """Fetch current weather for a city using wttr.in, with a deterministic local fallback."""
    clean_city = city.strip()
    if not clean_city:
        return {"error": "City name cannot be empty."}

    url = f"https://wttr.in/{quote(clean_city)}?format=j1"
    try:
        resp = requests.get(url, timeout=5, headers={"User-Agent": "quayutec-p1-cli/1.0"})
        resp.raise_for_status()
        data = resp.json()
        current = data["current_condition"][0]
        return {
            "city": clean_city,
            "temperature_c": current.get("temp_C"),
            "feels_like_c": current.get("FeelsLikeC"),
            "condition": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
            "humidity_percent": current.get("humidity"),
            "wind_kmph": current.get("windspeedKmph"),
            "source": "wttr.in",
        }
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        return {
            "city": clean_city,
            "temperature_c": "24",
            "feels_like_c": "25",
            "condition": "Partly cloudy (offline fallback)",
            "humidity_percent": "65",
            "wind_kmph": "12",
            "source": "local_fallback",
            "fallback_reason": str(exc),
        }


TOOL_DECLARATIONS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_notes",
            description=(
                "Search local markdown and text notes in the project's notes/ folder "
                "for onboarding details, dates, meetings, or tech stack guidelines."
            ),
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="Keywords or topic to search for in local notes.",
                    ),
                },
                required=["query"],
            ),
        ),
        types.FunctionDeclaration(
            name="add_days",
            description="Add or subtract days from a date in YYYY-MM-DD format.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "start_date": types.Schema(
                        type=types.Type.STRING,
                        description="Starting date in YYYY-MM-DD format.",
                    ),
                    "days": types.Schema(
                        type=types.Type.INTEGER,
                        description="Number of days to add (can be negative to subtract).",
                    ),
                },
                required=["start_date", "days"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_weather_info",
            description="Get current weather information for a given city.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "city": types.Schema(
                        type=types.Type.STRING,
                        description="Name of the city (e.g., 'Dhaka', 'London').",
                    ),
                },
                required=["city"],
            ),
        ),
    ]
)

TOOL_REGISTRY = {
    "search_notes": search_notes,
    "add_days": add_days,
    "get_weather_info": get_weather_info,
}


def execute_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Dispatch a tool call by name and return a JSON-serializable dict."""
    func = TOOL_REGISTRY.get(name)
    if func is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return func(**args)
    except TypeError as exc:
        return {"error": f"Invalid arguments for '{name}': {exc}"}
