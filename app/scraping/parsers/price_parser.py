from bs4 import BeautifulSoup
from ..website_schema import WebsiteConfig
from app.utils.exceptions.selector_exceptions import PriceSelectorError
from .utils import select_with_raw_selector

def parse_prices(soup: BeautifulSoup, site_config: WebsiteConfig):
    price_formatter = site_config.product.price_formatter
    actual_price = select_with_raw_selector(soup, site_config.product.price_selector_actual)
    if actual_price is None:
        raise PriceSelectorError(site_config.product.price_selector_actual)
    current_price = select_with_raw_selector(soup, site_config.product.price_selector_current)
    if current_price is None:
        raise PriceSelectorError(site_config.product.price_selector_current)
    prices = {
        'original': price_formatter(actual_price.text),
        'current': price_formatter(current_price.text),
    }
    return prices