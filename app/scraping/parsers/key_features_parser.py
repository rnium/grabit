from bs4 import BeautifulSoup
import sys
import io
from ..website_schema import WebsiteConfig
from app.utils.exceptions.selector_exceptions import KeyFeatureSelectorError

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_keyfeatures(soup: BeautifulSoup, site_config: WebsiteConfig):
    container = soup.select_one(site_config.product.key_feature.container_selector)
    if container is None:
        raise KeyFeatureSelectorError(site_config.product.key_feature.container_selector)
    features_elem = container.find_all(site_config.product.key_feature.item_selector)
    features_dict = {}
    features_arr = []
    for f in features_elem:
        txt = f.text
        if splitter:= site_config.product.key_feature.item_splitter:
            split_arr = txt.split(splitter)
            features_dict[split_arr[0].strip()] = splitter.join(split_arr[1:]).strip()
        else:
            features_arr.append(txt.strip())
    return features_dict or features_arr