from bs4 import BeautifulSoup
from ..website_schema import WebsiteConfig
from app.utils.exceptions.selector_exceptions import PriceSelectorError

def parse_prices(soup: BeautifulSoup, site_config: WebsiteConfig):
    price_formatter = site_config.product.price_formatter
    actual_price = soup.select_one(site_config.product.price_selector_actual)
    if actual_price is None:
        raise PriceSelectorError(site_config.product.price_selector_actual)
    actual_price = actual_price.text
    current_price = soup.select_one(site_config.product.price_selector_current)
    if current_price is None:
        raise PriceSelectorError(site_config.product.price_selector_current)
    current_price = current_price.text
    prices = {
        'original': price_formatter(actual_price),
        'current': price_formatter(current_price),
    }
    return prices