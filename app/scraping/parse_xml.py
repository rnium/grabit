import requests
from xml.dom import minidom
from typing import List
from pydantic import HttpUrl, ValidationError
from app.utils.exceptions.site_exceptions import UnSupportedSiteError
from .websites import get_site_config

def parse_sitemap_xml(xml_link: str) -> List[str]:
    site_config = get_site_config(xml_link)
    if not site_config:
        raise UnSupportedSiteError()
    res = requests.get(xml_link)
    dom = minidom.parseString(res.text)
    locs = dom.getElementsByTagName('loc')
    links = []
    for l in locs:
        try:
            f_child = l.firstChild
            link_text = HttpUrl(f_child.nodeValue)
            links.append(str(link_text))
        except ValidationError:
            pass
    print(len(links), flush=1)
    return links, site_config
    