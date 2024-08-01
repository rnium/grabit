from bs4 import BeautifulSoup

def select_with_raw_selector(soup: BeautifulSoup, raw_selector: str, many=False):
    """splits the raw selector with pipe and returns the first non-None selection
    Args:
        raw_selector: its the raw string from yaml config, 
        which actually may contain multiple selectors separated by a pipe character
    """
    selectors = raw_selector.split('|')
    for s in selectors:
        s = s.strip()
        selection = soup.select(s) if many else soup.select_one(s)
        if selection:
            return selection
    return [] if many else None
        
    