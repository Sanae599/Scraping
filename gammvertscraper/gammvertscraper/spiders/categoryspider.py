import scrapy
from scrapy.loader import ItemLoader
from gammvertscraper.items import CategoryItem

EXCLUDE = {"/c/destockage"}

class RecursiveCategoriesSpider(scrapy.Spider):
    name = "recursive_categories"
    allowed_domains = ["gammvert.fr"]
    start_urls = ["https://www.gammvert.fr"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visited_ids = set()
        self.root_categories_ids = set()

    def parse(self, response):
        # Top-catégories dans le menu principal
        for a in response.css('li.ens-main-navigation-items__item a[href^="/c/"]'):
            href = a.attrib["href"]
            if href in EXCLUDE:
                continue
            url = response.urljoin(href)
            name = a.css('.ens-main-navigation-items__link-label::text').get().strip()
            cat_id = self.generate_id(name, url)

            self.root_categories_ids.add(cat_id)

            loader = ItemLoader(item=CategoryItem())
            loader.add_value("name", name)
            loader.add_value("url", url)
            loader.add_value("category_id", cat_id)
            loader.add_value("parent_id", None)
            loader.add_value("is_pagelist", 0)
            item = loader.load_item()

            yield item

            yield response.follow(
                url,
                callback=self.parse_category,
                meta={'parent_id': cat_id}
            )

    def parse_category(self, response):
        parent_id = response.meta['parent_id']

        # Chargement de l’item pour la catégorie courante
        title = response.css('h1::text').get(default='').strip()
        url = response.url.rstrip('/')
        cat_id = self.generate_id(title or "unknown", url)

        # Si on a déjà vu cette catégorie, on ignore
        if cat_id in self.visited_ids:
            return
        self.visited_ids.add(cat_id)

        # On cherche les sous-catégories
        nodes = response.css('section.ens-category-list a.ens-category-list__item')
        if not nodes:
            nodes = response.css('div.ens-product-list-categories__list a.ens-product-list-categories__item')

        is_pagelist = 0 if nodes else 1
        
        # Si c’est une racine, on ne re-yield pas (on l’a déjà yield dans parse)
        if cat_id not in self.root_categories_ids:
            loader = ItemLoader(item=CategoryItem())
            loader.add_value("name", title)
            loader.add_value("url", url)
            loader.add_value("category_id", cat_id)
            loader.add_value("parent_id", parent_id)
            loader.add_value("is_pagelist", is_pagelist)
            item = loader.load_item()

            yield item

        # Puis on suit les sous-catégories
        for node in nodes:
            name = node.css('h3.ds-ens-card__title::text, ::text').get()
            if not name:
                continue
            name = name.strip()
            href = node.attrib.get('href')
            if not href:
                continue
            sub_url = response.urljoin(href).rstrip('/')
            sub_cat_id = self.generate_id(name, sub_url)

            if sub_cat_id in self.visited_ids:
                continue

            yield response.follow(
                sub_url,
                callback=self.parse_category,
                meta={'parent_id': cat_id}
            )

    def generate_id(self, name, url):
        name_part = name.lower().replace(" ", "_")
        url_part = url.lower().replace("://", "_").replace("/", "_").strip("_")
        return f"{name_part}_{url_part}"
