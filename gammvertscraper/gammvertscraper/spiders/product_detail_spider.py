import scrapy
from ..items import ProductItem
import json
import os

class ProductDetailSpider(scrapy.Spider):
    name = "ProductDetailSpider"
    allowed_domains = ["gammvert.fr"]

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'authority': 'www.gammvert.fr',
            'accept': 'text/html,application/xhtml+xml',
            'user-agent': 'Mozilla/5.0 (...)',
            'cookie': '__cf_bm=xyz; other_cookie=abc',
        }
    }

    def start_requests(self):
        # Vous pouvez soit lire les URLs depuis un fichier ou une base de données,
        # soit les passer directement ici pour le test.
        json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'productli.json')
        with open(json_file_path, 'r', encoding='utf-8') as file:
            products = json.load(file)

        for product in products:
            yield scrapy.Request(
                url=product['url'],
                callback=self.parse_product_details,
                meta={
                    'page_number': product['page_number'],
                    'basic_name': product['basic_name'],
                    'basic_price': product['basic_price'],
                    'product_url': product['url']
                }
            )

    def parse_product_details(self, response):
        basic_name = response.meta.get('basic_name')
        basic_price = response.meta.get('basic_price')
        product_url = response.url
        categories = self.extract_categories(response)

        product_data = ProductItem(
            name=self.extract_name(response) or basic_name,
            url=product_url,
            page_number=response.meta.get('page_number'),
            price_init=response.css('span.ds-ens-pricing__discount-text--crossed::text').get(),
            price_reduc=response.css('span.ds-ens-pricing__discount-amount::text').get(),
            price_final=response.css('span.ds-ens-pricing__price-amount--xxxl::text').get() or basic_price,
            categories=categories
        )
        yield product_data

    def extract_name(self, response):
        return (
            response.css('h1.product-title::text').get() or
            response.css('.product-name::text').get() or
            response.css('h1::text').get()
        )

    def extract_categories(self, response):
        categories = []
        breadcrumb_items = response.css('ul.idf-breadcrumb__items li.idf-breadcrumb__item')

        for item in breadcrumb_items:
            link = item.css('a.idf-breadcrumb__entry')
            if link:
                label = item.css('span.idf-breadcrumb__entry-label::text').get()
                if label and label.strip():
                    categories.append(label.strip())

        categorized = {}
        if len(categories) >= 1:
            categorized['cat'] = categories[0]
        if len(categories) >= 2:
            categorized['subcat'] = categories[1]
        if len(categories) >= 3:
            categorized['subsubcat'] = categories[2]
        if len(categories) >= 4:
            categorized['subsubsubcat'] = categories[3]
        if len(categories) >= 5:
            categorized['subsubsubsubcat'] = categories[4]

        return categorized
