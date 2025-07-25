import scrapy
from scrapy.loader import ItemLoader
from gammvertscraper.items import CategoryItem

EXCLUDE = {"/c/destockage"}

class RecursiveCategoriesSpider(scrapy.Spider):
    """
    Spider Scrapy pour explorer récursivement les catégories du site gammvert.fr.

    Ce spider commence par le menu principal, extrait les catégories, et suit les liens
    vers les sous-catégories jusqu’à atteindre les pages produits (feuilles).
    Il évite de revisiter les catégories déjà traitées et peut ignorer certaines URLs.
    """

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
        """
        Initialise le spider avec des ensembles pour suivre les catégories visitées
        et les catégories racines.
        """
        super().__init__(*args, **kwargs)
        self.visited_ids = set()
        self.root_categories_ids = set()

    def parse(self, response):
        """
        Point d’entrée du spider. Analyse la page d’accueil pour extraire les catégories principales.

        Args:
            response (scrapy.http.Response): La réponse HTTP de la page d’accueil.

        Yields:
            scrapy.Request: Requête vers une sous-catégorie.
            CategoryItem: Objet contenant les données de la catégorie principale.
        """
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
        """
        Analyse une page de catégorie pour extraire les sous-catégories ou identifier une page produit.

        Args:
            response (scrapy.http.Response): La réponse HTTP de la page de catégorie.

        Yields:
            scrapy.Request: Requête vers une sous-catégorie.
            CategoryItem: Objet contenant les données de la sous-catégorie.
        """
        parent_id = response.meta['parent_id']

        title = response.css('h1::text').get(default='').strip()
        url = response.url.rstrip('/')
        cat_id = self.generate_id(title or "unknown", url)

        if cat_id in self.visited_ids:
            return
        self.visited_ids.add(cat_id)

        nodes = response.css('section.ens-category-list a.ens-category-list__item')
        if not nodes:
            nodes = response.css('div.ens-product-list-categories__list a.ens-product-list-categories__item')

        is_pagelist = 0 if nodes else 1

        if cat_id not in self.root_categories_ids:
            loader = ItemLoader(item=CategoryItem())
            loader.add_value("name", title)
            loader.add_value("url", url)
            loader.add_value("category_id", cat_id)
            loader.add_value("parent_id", parent_id)
            loader.add_value("is_pagelist", is_pagelist)
            item = loader.load_item()

            yield item

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
        """
        Génère un identifiant unique basé sur le nom et l’URL de la catégorie.

        Args:
            name (str): Le nom de la catégorie.
            url (str): L’URL complète de la catégorie.

        Returns:
            str: Un identifiant unique formaté.
        """
        name_part = name.lower().replace(" ", "_")
        url_part = url.lower().replace("://", "_").replace("/", "_").strip("_")
        return f"{name_part}_{url_part}"
