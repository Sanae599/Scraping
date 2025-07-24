import scrapy
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

    def parse(self, response):
        #Top-catégories dans le menu principal
        for a in response.css('li.ens-main-navigation-items__item a[href^="/c/"]'):
            href = a.attrib["href"]
            if href in EXCLUDE:
                continue
            url = response.urljoin(href)
            name = a.css('.ens-main-navigation-items__link-label::text').get().strip()
            cat_id = self.generate_id(name, url)

            yield CategoryItem(
                name=name,
                url=url,
                category_id=cat_id,
                parent_id=None,
                is_pager=0
            )
            yield response.follow(
                url,
                callback=self.parse_category,
                meta={'parent_id': cat_id}
            )

    def parse_category(self, response):
        parent_id = response.meta['parent_id']

        #1)recherche de sous-catégories classiques
        nodes = response.css('section.ens-category-list a.ens-category-list__item')
        #2) si aucune, on regarde dans le bandeau sous-catégories" des pages produits
        if not nodes:
            nodes = response.css('div.ens-product-list-categories__list a.ens-product-list-categories__item')

        #Si on trouve des sous-catégories → on poursuit la récursion
        if nodes:
            for node in nodes:
                name = node.css('h3.ds-ens-card__title::text, ::text').get().strip()
                href = node.attrib.get('href')
                if not href:
                    continue
                url = response.urljoin(href)
                cat_id = self.generate_id(name, url)

                yield CategoryItem(
                    name=name,
                    url=url,
                    category_id=cat_id,
                    parent_id=parent_id,
                    is_pager=0
                )
                yield response.follow(
                    url,
                    callback=self.parse_category,
                    meta={'parent_id': cat_id}
                )
            return

        #Sinon → page finale (liste de produits)
        #On crée un item pour marquer ce niveau comme page de produits
        title = response.css('h1::text').get(default='').strip()
        url   = response.url
        cat_id = self.generate_id(title or "unknown", url)

        yield CategoryItem(
            name=title,
            url=url,
            category_id=cat_id,
            parent_id=parent_id,
            is_pager=1
        )

    def generate_id(self, name, url):
        name_part = name.lower().replace(" ", "_")
        url_part  = url.lower().replace("://", "_").replace("/", "_").strip("_")
        return f"{name_part}_{url_part}"
