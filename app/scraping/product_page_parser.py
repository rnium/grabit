from .website_schema import WebsiteConfig
from .parsers.key_features_parser import parse_keyfeatures
from .parsers.price_parser import parse_prices
from .parsers.spec_table_parser import parse_tables
from .parsers.list_value_parser import parse_lv
from bs4 import BeautifulSoup
from app.models import Product
from app.schemas.product import ProductData
from app.utils.exceptions.site_exceptions import NotAProductError
from app.utils.exceptions.selector_exceptions import ProductInfoSelectorError
import requests


def parse_product_page(url: str, site_config: WebsiteConfig) -> ProductData:
    res = requests.get(url)
    content = res.text
    soup = BeautifulSoup(content, 'html.parser')
    if soup.select_one(site_config.product.main_selector) is None:
        raise NotAProductError(site_config.sitename)
    title = soup.select_one(site_config.product.title_selector)
    if title is None:
        raise ProductInfoSelectorError(site_config.product.title_selector)
    else:
        title = title.text.strip()
    key_f = parse_keyfeatures(soup, site_config)
    prices = parse_prices(soup, site_config)
    spec_tables = parse_tables(soup, site_config)
    images = parse_lv(soup, site_config.product.images)
    description_bs4 = soup.select_one(site_config.product.description_selector)
    if description_bs4 is None:
        raise ProductInfoSelectorError(site_config.product.description_selector)
    product_data = ProductData(
        title = title,
        prices = prices,
        key_features = key_f,
        images = images,
        spec_tables = spec_tables,
        description = description_bs4.decode_contents() if description_bs4 else ''
    )
    return product_data
    