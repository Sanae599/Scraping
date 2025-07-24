import scrapy
import math
import re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

class ProductListSpider(scrapy.Spider):
    name = "ProductListSpidertest"
    allowed_domains = ["gammvert.fr"]
    start_urls = ["https://www.gammvert.fr/c/agrumes"]

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'authority': 'www.gammvert.fr',
            'accept': 'text/html,application/xhtml+xml',
            'user-agent': 'Mozilla/5.0 (...)',
            'cookie': '__cf_bm=xyz; other_cookie=abc',
        }
    }

    def parse(self, response):
        total_text = response.css('div.ens-product-list-template__products-counter span::text').get()
        if total_text:
            match = re.search(r'(\d+)\s+produits?\s+sur\s+(\d+)', total_text)
            if match:
                total_products = int(match.group(2))
                total_pages = math.ceil(total_products / 50)

                for page_num in range(1, total_pages + 1):
                    page_url = self.build_page_url(response.url, page_num)
                    yield scrapy.Request(
                        url=page_url,
                        callback=self.parse_products,
                        meta={'page': page_num, 'total_pages': total_pages},
                        headers=self.custom_settings['DEFAULT_REQUEST_HEADERS']
                    )
        else:
            yield from self.parse_products(response)

    def build_page_url(self, base_url, page_number):
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        query_params['p'] = [str(page_number)]
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
        return new_url

    def parse_products(self, response):
        page_num = response.meta.get('page', 1)
        product_links = response.css('a.ens-product-list__link')

        for link in product_links:
            url = link.attrib.get('href', '')
            if url:
                full_url = urljoin(response.url, url)
                product = link.css('article.ds-ens-product-card')
                basic_name = product.css('h2.ds-ens-product-card__name::text').get()
                basic_price = product.css('span.ds-ens-pricing__price-amount--l::text').get()

                yield {
                    'url': full_url,
                    'page_number': page_num,
                    'basic_name': basic_name.strip() if basic_name else None,
                    'basic_price': basic_price.strip() if basic_price else None,
                }
