import re

def parse_afd_html(html_content: str) -> dict:
    """
    Parses the HTML content of a National Weather Service Area Forecast
    Discussion (AFD) page to extract the discussion sections.

        Args:
        html_content: The HTML content as a string.

    Returns:
        A dictionary with section headers as keys and their corresponding
        text as values.
    """
    # Find the pre tag
    pre_tag_match = re.search(r'<pre\s+[^>]*?id="proddiff"[^>]*?>(.+?)</pre>', html_content, re.DOTALL)
    if not pre_tag_match:
        return {"error": "No AFD found in the provided HTML content."}

# Extract the full text within the pre tag
    full_text = pre_tag_match.group(1)
    try:
        start_marker = '.SYNOPSIS...'
        end_marker = '$$'
        start_index = full_text.find(start_marker)
        end_index = full_text.rfind(end_marker)
        if start_index == -1 or end_index == -1:
            return {"error": "AFD content markers not found."}
        content = full_text[start_index:end_index]
    except ValueError:
        return {"error": "AFD content could not be extracted."}
    
    # parse sections 
    sections_dict = {}
    section_parts = re.split(r'\s*&&\s*', content)
    for section_text in section_parts:
        section_text = section_text.strip()
        if not section_text:
            continue
        lines = section_text.split('\n')
        header_line = lines[0].strip()
        if header_line.startswith('.') and header_line.endswith('...'):
            header = header_line[1:-3].strip()
            body = '\n'.join(lines[1:]).strip()
            
            # Remove HTML tags from the body
            body = re.sub(r'<.*?>', '', body)
            
            sections_dict[header] = body.strip()
    return sections_dict
