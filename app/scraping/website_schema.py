from pydantic import BaseModel
from typing import Callable
from .price_formatter import FORMATTER_MAPPING

class ListValues(BaseModel):
    container_selector: str
    item_selector: str
    attribute: str | None


class KeyFeatures(ListValues):
    item_splitter: str | None
    
class SpecTable(ListValues):
    """
    container selector is the specific spec group selector
    & the item selector is the item row selector
    """
    table_selector: str
    heading_selector: str
    item_key_selector: str
    item_value_selector: str


class Product(BaseModel):
    main_selector: str
    title_selector: str
    price_selector_actual: str
    price_selector_current: str
    description_selector: str
    price_formatter: Callable
    key_feature: KeyFeatures
    spec_table: SpecTable
    images: ListValues
     
        

class WebsiteConfig(BaseModel):
    sitename: str
    product: Product


def create_config(site_data) -> WebsiteConfig:
    product_config: dict = site_data['product']
    formatter_name = product_config.get('price_formatter')
    if not formatter_name:
        formatter_name = 'common_formatter'
    else:
        product_config.pop('price_formatter')
    site_product = Product(
        key_feature = KeyFeatures(**product_config.pop('key_feature')),
        spec_table = SpecTable(**product_config.pop('spec_table')),
        images = ListValues(**product_config.pop('images')),
        price_formatter = FORMATTER_MAPPING[formatter_name],
        **product_config
    )
    return WebsiteConfig(
        sitename = site_data['name'],
        product = site_product
    )