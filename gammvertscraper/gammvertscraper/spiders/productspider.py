import scrapy
from ..items import ProductItem
import math
import re
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse


class ProductSpider(scrapy.Spider):
    name = "ProductlistSpider"
    allowed_domains = ["gammvert.fr"]
    start_urls = ["https://www.gammvert.fr/c/plante-d-exterieur"]

    custom_settings ={
        'DEFAULT_REQUEST_HEADERS':{
            'authority': 'www.gammvert.fr',
            'accept': 'text/html,application/xhtml+xml',
            'user-agent': 'Mozilla/5.0 (...)',
            'cookie': '__cf_bm=xyz; other_cookie=abc',
            }}

    def parse(self, response):
        #Extraction du nombre total d'articles
        total_text = response.css('div.ens-product-list-template__products-counter span::text').get()

        if total_text:
            #Extraction des chiffres
            match = re.search(r'(\d+)\s+produits?\s+sur\s+(\d+)', total_text)
            if match:
                current_products = int(match.group(1))
                total_products = int(match.group(2))

            #Calcul du nombre de pages
            total_pages = math.ceil(total_products / 50)

            #Génération d'url pour toutes les pages
            for page_num in range(1, total_pages+1):
                page_url = self.build_page_url(response.url, page_num)
                yield scrapy.Request(
                    url = page_url,
                    callback = self.parse_products,
                    meta={'page': page_num, 'total_pages': total_pages},
                    headers= self.custom_settings['DEFAULT_REQUEST_HEADERS']
                )

        else:
            yield from self.parse_products(response)

    def build_page_url(self, base_url, page_number):
        """Construit l'URL avec le paramètre p=X """
        parsed = urlparse(base_url)
        query_params = parse_qs(parsed.query)
        
        # Ajouter ou modifier le paramètre 'p'
        query_params['p'] = [str(page_number)]
        
        # Reconstruire l'URL proprement
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
            
        return new_url

    def parse_products(self, response):
        """Extrait les produits d'une page spécifique"""
        page_num = response.meta.get('page', 1)
        total_pages = response.meta.get('total_pages', '?')

        product_links = response.css('a.ens-product-list__link')
        products_count = 0

        for link in product_links:
            # Extrayez l'URL de l'élément <a>
            url = link.attrib.get('href', '')

            if url:
                full_url = urljoin(response.url, url)
                # Extraction des données de l'article présente sur la page liste
                product = link.css('article.ds-ens-product-card')
                basic_name = product.css('h2.ds-ens-product-card__name::text').get()
                basic_price = product.css('span.ds-ens-pricing__price-amount--l::text').get()
                
                # Lancer une requête vers la page détail du produit
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_product_details,
                    meta={
                        'page_number': page_num,
                        'basic_name': basic_name.strip() if basic_name else None,
                        'basic_price': basic_price.strip() if basic_price else None,
                        'product_url': full_url
                    },
                    headers=self.custom_settings['DEFAULT_REQUEST_HEADERS']
                )
                products_count += 1


    def parse_product_details(self, response):
        page_number = response.meta.get('page_number')
        basic_name = response.meta.get('basic_name')
        basic_price = response.meta.get('basic_price')
        product_url = response.meta.get('product_url')
        categories = self.extract_categories(response)

        product_data = {
            'name': self.extract_name(response) or basic_name,
            'url': product_url,
            'page_number': page_number,
            'price_init' : response.css('span.ds-ens-pricing__discount-text--crossed::text').get(),
            'price_reduc' : response.css('span.ds-ens-pricing__discount-amount::text').get(),
            'price_final' : response.css('span.ds-ens-pricing__price-amount--xxxl::text').get() or basic_price,
            'categories' : categories

            }
        yield product_data

    def extract_name(self, response):
        """Extrait le nom du produit depuis la page détail"""
        return (
            response.css('h1.product-title::text').get() or
            response.css('.product-name::text').get() or
            response.css('h1::text').get()
        )
    
    def extract_categories(self, response):
        """Extrait toutes les catégories depuis le fil d'ariane de la page détail produit"""
        categories = []

        breadcrumb_items = response.css('ul.idf-breadcrumb__items li.idf-breadcrumb__item')

        for item in breadcrumb_items:
            # Vérifier si c'est un lien (pas l'accueil ni le produit actuel)
            link = item.css('a.idf-breadcrumb__entry')
            if link:
                # Extraire le texte du label
                label = item.css('span.idf-breadcrumb__entry-label::text').get()
                if label and label.strip():
                    categories.append(label.strip())
        
        return categories



