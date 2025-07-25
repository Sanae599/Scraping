import csv
import re
from scrapy.exceptions import DropItem
from decimal import Decimal
from gammvertscraper.items import CategoryItem, ProductItem

# Pipeline pour les catégories
class CleanCategoriesPipeline:
    """
    Nettoie les champs d'un CategoryItem.

    - Supprime les espaces inutiles.
    - Normalise le champ 'name' en minuscules et retire les guillemets ou apostrophes.
    """

    def process_item(self, item, spider):
        """
        Traite un item en nettoyant les champs texte.

        Args:
            item (Item): L'item à traiter.
            spider (Spider): Le spider Scrapy appelant.

        Returns:
            Item: L'item nettoyé.
        """
        if not isinstance(item, CategoryItem):
            return item
        for field, value in list(item.items()):
            if isinstance(value, list) and value:
                value = value[0]
            if isinstance(value, str):
                value = value.strip()
                if field == 'name':
                    value = value.lower()
                    value = re.sub(r"[\"'’‘]", "", value)
            item[field] = value
        return item


class ValidateCategoriesPipeline:
    """
    Valide que les champs obligatoires d'un CategoryItem sont présents.
    """

    def process_item(self, item, spider):
        """
        Vérifie la présence des champs requis dans un CategoryItem.

        Args:
            item (Item): L'item à valider.
            spider (Spider): Le spider Scrapy appelant.

        Raises:
            DropItem: Si un champ requis est manquant.

        Returns:
            Item: L'item validé.
        """
        if not isinstance(item, CategoryItem):
            return item
        required = ['name', 'url', 'category_id', 'is_pagelist']
        for field in required:
            if not item.get(field) and item.get(field) != 0:
                raise DropItem(f"Missing required field: {field}")
        return item


class DedupeCategoriesPipeline:
    """
    Élimine les doublons de CategoryItem basés sur 'category_id'.
    """

    def __init__(self):
        """
        Initialise un ensemble pour stocker les ID déjà vus.
        """
        self.seen = set()

    def process_item(self, item, spider):
        """
        Supprime les items ayant un 'category_id' déjà rencontré.

        Args:
            item (Item): L'item à vérifier.
            spider (Spider): Le spider Scrapy appelant.

        Raises:
            DropItem: Si l'item est un doublon.

        Returns:
            Item: L'item non dupliqué.
        """
        if item.__class__.__name__ != 'CategoryItem':
            return item
        cid = item['category_id']
        if cid in self.seen:
            raise DropItem(f"Duplicate {cid}")
        self.seen.add(cid)
        return item


class CsvCategoriesPipeline:
    """
    Exporte les CategoryItem valides dans un fichier CSV.
    """

    def open_spider(self, spider):
        """
        Ouvre le fichier CSV au démarrage du spider.
        """
        self.file = open('categories.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['name', 'url', 'category_id', 'parent_id', 'is_pagelist'])

    def process_item(self, item, spider):
        """
        Écrit un CategoryItem dans le fichier CSV.

        Args:
            item (Item): L'item à exporter.
            spider (Spider): Le spider Scrapy appelant.

        Returns:
            Item: L'item inchangé.
        """
        if isinstance(item, CategoryItem):
            self.writer.writerow([
                item['name'],
                item['url'],
                item['category_id'],
                item.get('parent_id', 'catégorie racine'),
                item['is_pagelist'],
            ])
        return item

    def close_spider(self, spider):
        """
        Ferme le fichier CSV à la fin du spider.
        """
        self.file.close()


# Pipeline pour les produits
class CleanProductsPipeline:
    """
    Nettoie les champs d'un ProductItem.

    - Supprime les espaces inutiles.
    - Normalise le champ 'name' en minuscules et retire les guillemets ou apostrophes.
    """

    def process_item(self, item, spider):
        """
        Traite un item produit en nettoyant les champs texte.

        Args:
            item (Item): L'item à traiter.
            spider (Spider): Le spider Scrapy appelant.

        Returns:
            Item: L'item nettoyé.
        """
        if not isinstance(item, ProductItem):
            return item
        for field, value in list(item.items()):
            if isinstance(value, list) and value:
                value = value[0]
            if isinstance(value, str):
                value = value.strip()
                if field == 'name':
                    value = value.lower()
                    value = re.sub(r"[\"'’‘]", "", value)
            item[field] = value
        return item


class ConvertPricePipeline:
    """
    Convertit le champ 'price' d'un ProductItem en objet Decimal.
    """

    def process_item(self, item, spider):
        """
        Extrait et convertit une chaîne de prix en Decimal.

        Args:
            item (Item): L'item à convertir.
            spider (Spider): Le spider Scrapy appelant.

        Returns:
            Item: L'item avec le champ 'price' converti.
        """
        if not isinstance(item, ProductItem):
            return item
        raw = item.get('price') or ''
        m = re.search(r'(\d+[\.,]\d+|\d+)', raw.replace('\u202f', '').replace(' ', ''))
        if m:
            val = m.group(1).replace(',', '.')
            try:
                item['price'] = Decimal(val)
            except:
                item['price'] = Decimal('0.0')
        else:
            item['price'] = Decimal('0.0')
        return item


class CsvProductsPipeline:
    """
    Exporte les ProductItem valides dans un fichier CSV.
    """

    def open_spider(self, spider):
        """
        Ouvre le fichier CSV au démarrage du spider.
        """
        self.file = open('products.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['url', 'page_number', 'name', 'price'])

    def process_item(self, item, spider):
        """
        Écrit un ProductItem dans le fichier CSV.

        Args:
            item (Item): L'item à exporter.
            spider (Spider): Le spider Scrapy appelant.

        Returns:
            Item: L'item inchangé.
        """
        if isinstance(item, ProductItem):
            self.writer.writerow([
                item['url'],
                item['page_number'],
                item['name'],
                item['price'],
            ])
        return item

    def close_spider(self, spider):
        """
        Ferme le fichier CSV à la fin du spider.
        """
        self.file.close()
