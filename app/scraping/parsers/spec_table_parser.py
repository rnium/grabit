from bs4 import BeautifulSoup
from ..website_schema import WebsiteConfig
from app.utils.exceptions.selector_exceptions import SpecTableSelectorError

def parse_tables(soup: BeautifulSoup, site_config: WebsiteConfig):
    table_config = site_config.product.spec_table
    table_container = soup.select_one(table_config.table_selector)
    if not table_container:
        raise SpecTableSelectorError(table_config.table_selector)
    heading_texts = [h.text.strip() for h in table_container.select(table_config.heading_selector)]
    spec_groups = []
    
    groups = table_container.select(table_config.container_selector)
    for group in groups:
        specs = {}
        for item in group.select(table_config.item_selector):
            key = item.select_one(table_config.item_key_selector).text.replace('\n', ' ').strip()
            val = item.select_one(table_config.item_value_selector).text.replace('\n', ' ').strip()
            specs[str(key)] = str(val)
        spec_groups.append(specs)
    spec_tables = {}
    for i in range(len(heading_texts)):
        spec_tables[heading_texts[i]] = spec_groups[i] if i < len(spec_groups) else {}
    return spec_tables