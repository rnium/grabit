from bs4 import BeautifulSoup
from ..website_schema import ListValues
from app.utils.exceptions.selector_exceptions import ListItemSelectorError


def parse_lv(soup: BeautifulSoup, lv_config: ListValues):
    itm_container = soup.select_one(lv_config.container_selector)
    if itm_container is None:
        raise ListItemSelectorError(lv_config.container_selector)
    items_fragment = itm_container.select(lv_config.item_selector)
    items = [i[lv_config.attribute] if lv_config.attribute else i.text for i in items_fragment]
    return items