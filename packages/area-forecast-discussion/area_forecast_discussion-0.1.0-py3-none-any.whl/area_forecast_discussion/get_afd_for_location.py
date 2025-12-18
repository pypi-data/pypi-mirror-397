import requests
import json
from .get_forecast_office import get_forecast_office
from .generate_afd_url import generate_afd_url
from .parse_afd_html import parse_afd_html

def get_afd_for_location(latitude: float, longitude: float, glossary: bool = False, user_agent: str = "AFD Python Library") -> dict:
    """
    Orchestrates the process of fetching and parsing the Area Forecast
    Discussion for a given geographic location.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
        glossary: Whether to include glossary definitions.
        user_agent: User-Agent string for HTTP requests.

    Returns:
        A dictionary containing the parsed AFD sections or error information.
    """
    office = get_forecast_office(latitude, longitude)
    if not office:
        return {"error": "Could not retrieve the forecast office."}

    afd_url = generate_afd_url(office, glossary)
    
    try:
        headers = {'User-Agent': user_agent}
        response = requests.get(afd_url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching URL: {e}"}

    afd_sections = parse_afd_html(html_content)
    if not afd_sections:
        return {"error": "Could not parse the AFD sections from the HTML."}
    
    return afd_sections
