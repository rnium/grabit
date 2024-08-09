[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
# GrabIT: IT Product Data Scraper

GrabIT is a simple FastAPI based web scraping tool designed to scrape and store IT product data from various e-commerce websites. GrabIT simplifies the data collection process while conducting market research or managing a inventory of IT products.

Use Cases:
- Market Analysis: Collect comprehensive product data to gain insights into market trends and competitor offerings.
- Product Management: Automate data entry for product catalogs and inventory management.


Features:
- Easy to configure product webpage structure by specifying element css selectors for multiple websites in the `sites.yaml` file..
- Data extraction from individual product URLs or crawling using sitemap.xml.
- [React frontend](https://github.com/rnium/grabit_frontend) with interactive swagger api documentation.
- JWT authentication
- Docker ready

## How It Works
Under the hood, GrabIT is a web scraping tool that leverages several technologies to fetch, parse, validate, store, and serve data. Here’s a breakdown of its components:

- Requests: Used for fetching web pages.
- BeautifulSoup: Used for parsing data from HTML.
- Pydantic: Used for data validation.
- SQLAlchemy and PostgreSQL: Used for storing data.
- FastAPI: Serves the data as an API.

Appropriate CSS selectors are defined  in sites.yaml file which is used for parsing data from raw HTML. See Site Configuration below for more details.
## Run GrabIT

Clone the project

```bash
  git clone https://github.com/rnium/grabit.git
```

Go to the project directory

```bash
  cd grabit
```

Create your `sites.yaml` (see Site Configuration below to know how to configure sites.yaml) and Run the docker compose

```bash
  docker-compose up -d
```

Create an user

```bash
  docker exec -it grabit python manage.py createuser
```


## Site Configuration

To scrape data from a website using GrabIT, you need to configure each target website in the `sites.yaml` file. GrabIT focuses on extracting data from the product pages of websites. For example, consider **Ryans**, the leading IT product retailer in Bangladesh. Below is an illustration of the sections that GrabIT can scrape from a product page on Ryans:

![Ryans Product Page](https://i.ibb.co/9Z4mY8S/IMG-20240809-203209.jpg)
1. Product page container
2. Product title
3. Product regular/actual price
4. Product current/discounted price
5. Key features container
6. Key feature item
7. Product images container
8. Specification table
9. Specification container
10. Specification container heading
11. Specification item
12. Specification key
13. Specification value
14. Product description

### Configuration Example for Ryans:

```yaml
name: Ryans
urlpatterns:
  - http.*ryans.com
  - http.*ryanscomputers.com
product:
  main_selector: div[itemtype="http://schema.org/Product"]
  title_selector: .product_content h1[itemprop="name"]
  price_selector_actual: .rp-block .new-reg-text | .rp-block
  price_selector_current: .rp-block .new-sp-text | .rp-block
  description_selector: .spec-details .card .card-body
  key_feature:
    container_selector: .short-desc-attr ul.category-info
    item_selector: li
    attribute: null
    item_splitter: '-'
  spec_table:
    table_selector: "#add-spec-div | .specification-table"
    container_selector: .grid-container.for-last-hr
    item_selector: div.row[itemprop="description"]
    heading_selector: h6.fw-bold
    item_key_selector: .att-title
    item_value_selector: .att-value
    attribute: null
  images:
    container_selector: '#slideshow-items-container | .modal-product-img .side_view'
    item_selector: img
    attribute: src
```

### Root Directives:

- **`name`**: The name of the website.
- **`urlpatterns`**: A list of regex patterns for matching the website’s hostname.
- **`product`**: This section contains all the necessary selectors for scraping data from the product page. Refer to the *Selector Configuration* section for details.

The `sites.yaml` file is a [Multi-Document](https://gettaurus.org/docs/YAMLTutorial/#YAML-Multi-Documents) YAML file, allowing you to define configurations for multiple websites in the same file.

Note: After adding or altering a site configuration, restart the grabit container or Gunicorn server, go to the swagger api docs and then run a product link from the website to ensure it produces the expected result.

## Selector Configuration

To scrape data accurately, you need to specify appropriate and specific CSS selectors for each site. Below is a guide to configuring these selectors. Multiple selectors for a single item can be defined using a pipe (|) character. GrabIT will attempt to use each selector from left to right until it finds a matching element.

1. **Product Page Main Selector**:
   - **Directive**: `main_selector`
   - **Description**: The top-level wrapper that encloses all product information.

2. **Product Title**:
   - **Directive**: `title_selector`
   - **Expected Output**: String

3. **Product Actual Price**:
   - **Directive**: `price_selector_actual`
   - **Description**: The regular or listed price of the product.
   - **Expected Output**: Float
   - **Note**: The initial extraction is a string, which is then converted to a float using a price formatter. This function can be defined in the `/app/scraping/price_formatter.py` file and specified using the `price_formatter` directive. If not specified, a default formatter is used. If the default formatter is insufficient, you can define a custom one in `price_formatter.py`, add it to the `FORMATTER_MAPPING`, and reference it in the `price_formatter` directive.

4. **Product Current Price**:
   - **Directive**: `price_selector_current`
   - **Description**: The discounted price of the product.
   - **Expected Output**: Float

5. **Key Features**:
   - **Directive**: `key_feature`
   - **Description**: A list of key features, typically presented as an unordered list with 5-10 items.
   - **Configuration**:
     - **Container**: Specify the `container_selector` for the key features.
     - **Items**: Define the `item_selector` for list items.
     - **Splitter**: If the extracted string needs to be split into key-value pairs (e.g., `'Processor Name - Apple M3'` into `'Processor Name'` and `'Apple M3'`), specify the `item_splitter`. If not specified, GrabIT will treat the string as a single item.

6. **Images**:
   - **Directive**: `images`
   - **Description**: A list of images. In some cases, there are two different image containers: one for thumbnails and one for high-resolution display images. Be sure to look for and specify the container that holds the high-resolution images.
   - **Configuration**:
     - **Container**: Specify the `container_selector`.
     - **Items**: Define the `item_selector`.
     - **Attribute**: Specify the attribute (e.g., `src` for `<img>` tags) from which to extract the image URLs.

7. **Specification Table**:
   - **Directive**: `spec_table`
   - **Description**: Contains multiple containers with specifications on different aspects of the product.
   - **Configuration**:
     - **Table**: Specify the `table_selector`.
     - **Containers**: Define `container_selector` for each specification set (e.g., 'Processor', 'Memory').
     - **Heading**: Specify the `heading_selector` for container titles.
     - **Items**: Define the `item_selector` for selecting all items within a container.
     - **Key-Value Pairs**: Specify `item_key_selector` and `item_value_selector` to extract key-value pairs.

8. **Product Description**:
   - **Directive**: `description_selector`
