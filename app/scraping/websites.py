import re
from .website_schema import WebsiteConfig, create_config
import yaml
from app.config.settings import BASE_DIR

try:
    with open(BASE_DIR / 'sites.yaml') as file:
        site_list = list(yaml.load_all(file, Loader=yaml.FullLoader))
except FileNotFoundError:
    site_list = []




sites = [
    {
        'patterns': data['urlpatterns'],
        'config': create_config(data)
    }
    for data in site_list
]

def get_site_config(url: str) -> WebsiteConfig:
    config = None
    for site in sites:
        for pattern in site['patterns']:
            if re.search(str(pattern), url):
                config = site['config']
                break
    return config
