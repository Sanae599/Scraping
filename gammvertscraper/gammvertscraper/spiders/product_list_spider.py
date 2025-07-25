import scrapy
import math
import re
import csv
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from gammvertscraper.items import ProductItem

class ProductListSpider(scrapy.Spider):
    """
    Spider pour extraire les listes de produits depuis le site Gamm Vert.
    Ce spider commence par les URLs de catégories et extrait les produits listés.
    """
    name = "ProductListSpider"
    allowed_domains = ["gammvert.fr"]

    # Configuration personnalisée pour les en-têtes de requête HTTP
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'authority': 'www.gammvert.fr',
            'accept': 'text/html,application/xhtml+xml',
            'user-agent': 'Mozilla/5.0 (...)',
            'cookie': '__cf_bm=xyz; other_cookie=abc',
        }
    }

    def __init__(self, *args, **kwargs):
        """
        Initialise le spider en chargeant les catégories depuis un fichier CSV.
        Définit les URLs de départ pour les catégories où `is_pagelist` est vrai.
        """
        super(ProductListSpider, self).__init__(*args, **kwargs)

        # Charger les catégories depuis le fichier CSV généré par le categoryspider
        self.categories = []
        try:
            with open('categories.csv', mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.categories = list(reader)
        except FileNotFoundError:
            self.logger.error("Fichier categories.csv non trouvé.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture du fichier CSV: {e}")

        # Définir les URLs de départ (seulement celles où is_pagelist est 1)
        self.start_urls = [
            category['url'] for category in self.categories
            if int(category['is_pagelist']) == 1  # Convertir en entier si nécessaire
        ]

        # Créer un mapping pour récupérer les infos de catégories
        self.category_mapping = {cat['url']: cat for cat in self.categories}
        self.logger.info(f"Chargé {len(self.categories)} catégories depuis categories.csv")
        self.logger.info(f"URLs de départ: {len(self.start_urls)} URLs de catégories")

    def parse(self, response):
        """
        Parse la réponse pour extraire le nombre total de produits et génère des requêtes
        pour chaque page de résultats.

        Args:
            response (scrapy.http.Response): La réponse HTTP à parser.
        """
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
        """
        Construit l'URL pour une page spécifique de résultats.

        Args:
            base_url (str): L'URL de base à modifier.
            page_number (int): Le numéro de la page.

        Returns:
            str: L'URL complète pour la page spécifiée.
        """
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
        """
        Parse la réponse pour extraire les informations sur les produits listés.

        Args:
            response (scrapy.http.Response): La réponse HTTP à parser.

        Yields:
            ProductItem: Un objet contenant les informations du produit extraites.
        """
        page_num = response.meta.get('page', 1)
        product_links = response.css('a.ens-product-list__link')
        for link in product_links:
            url = link.attrib.get('href', '')
            if url:
                full_url = urljoin(response.url, url)
                product = link.css('article.ds-ens-product-card')
                basic_name = product.css('h2.ds-ens-product-card__name::text').get()
                basic_price = product.css('span.ds-ens-pricing__price-amount--l::text').get()
                item = ProductItem(
                    url=full_url,
                    page_number=page_num,
                    name=basic_name.strip() if basic_name else None,
                    price=basic_price.strip() if basic_price else None,
                )
                self.logger.info(f"Product item created: {item}")
                yield item
