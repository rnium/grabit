
# GrabIT: IT Product Data Scraper

GrabIT is a FastAPI based web application designed to scrape and store IT product data from various e-commerce websites. Whether you're conducting market research or managing a large inventory of IT products, Grabit simplifies the data collection process, saving you time and effort.

Use Cases:
- Market Analysis: Collect comprehensive product data to gain insights into market trends and competitor offerings.
- Product Management: Automate data entry for product catalogs and inventory management.


Key Features:
- Easy Configuration: Simplify the setup by easily configuring page structures and element selectors for multiple websites in the `sites.yaml` file.
- Versatile Scraping: Extract data from individual product URLs or from entire sitemap.
- Logging: Monitor the backend status in real-time during site crawling, providing insights and aiding in troubleshooting.
## Run Locally

Clone the project

```bash
  git clone https://github.com/rnium/grabit.git
```

Go to the project directory

```bash
  cd grabit
```

Create your `sites.yaml` and Run the docker compose

```bash
  docker-compose up -d
```

Go to `App` container shell and create an user

```bash
  python manage.py createuser
```


