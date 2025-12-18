import requests

def get_forecast_office(latitude: float, longitude: float, user_agent="AFD Python Package: user@example.com") -> str | None:
    """
    Queries the NWS API for a given set of coordinates to find the
    responsible forecast office (CWA).

    Args:
        latitude: The latitude for the location.
        longitude: The longitude for the location.
        user_agent: The User-Agent string to use for requests.

    Returns:
        The forecast office ID (e.g., 'LWX') or None if not found.
    """
    api_url = f"https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}"
    
    headers = {
        'User-Agent': user_agent
    }

    response = requests.get(api_url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    office = data.get('properties', {}).get('cwa')
    return office
