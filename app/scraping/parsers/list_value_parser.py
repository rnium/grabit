from bs4 import BeautifulSoup
from ..website_schema import ListValues
from app.utils.exceptions.selector_exceptions import ListItemSelectorError
from .utils import select_with_raw_selector

def parse_lv(soup: BeautifulSoup, lv_config: ListValues):
    itm_container = select_with_raw_selector(soup, lv_config.container_selector)
    if itm_container is None:
        raise ListItemSelectorError(lv_config.container_selector)
    items_fragment = select_with_raw_selector(itm_container, lv_config.item_selector, many=True)
    items = [i[lv_config.attribute] if lv_config.attribute else i.text for i in items_fragment]
    return items