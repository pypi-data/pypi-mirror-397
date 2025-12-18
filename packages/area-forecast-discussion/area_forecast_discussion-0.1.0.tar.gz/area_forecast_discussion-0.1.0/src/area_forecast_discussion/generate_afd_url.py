def generate_afd_url(office: str, glossary: bool = False) -> str:
    """
    Generates the URL for the Area Forecast Discussion product page
    for a given NWS forecast office.

        Args:
        office: The forecast office ID (e.g., 'LWX').
        glossary: Whether to include glossary terms in the product.

            Returns:
        The URL string for the AFD product page.
    """
    return (
        f"https://forecast.weather.gov/product.php?site={office}&issuedby={office}"
        f"&product=AFD&format=CI&version=1&glossary={ 1 if glossary else 0 }&highlight=off"
    )