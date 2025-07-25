import csv
import re
from scrapy.exceptions import DropItem
from decimal import Decimal
from gammvertscraper.items import CategoryItem, ProductItem

#Pipeline catégories
class CleanCategoriesPipeline:
    def process_item(self, item, spider):
        if not isinstance(item, CategoryItem):
            return item

        for field, value in list(item.items()):
            # 1) Déballer les listes à un seul élément
            if isinstance(value, list) and value:
                value = value[0]
            # 2) Si c’est une chaîne, la nettoyer
            if isinstance(value, str):
                value = value.strip()
                # 3) Spécifique au champ "name" :
                if field == 'name':
                    # passer tout en minuscules
                    value = value.lower()
                    # supprimer guillemets simples ou doubles
                    value = re.sub(r"[\"’‘']", "", value)
            item[field] = value

        return item


class ValidateCategoriesPipeline:
    def process_item(self, item, spider):
        if not isinstance(item, CategoryItem):
            return item

        required = ['name', 'url', 'category_id', 'is_pagelist']
        for field in required:
            if not item.get(field) and item.get(field) != 0:
                # on autorise la valeur 0 pour page_list
                raise DropItem(f"Missing required field: {field}")
        return item

class DedupeCategoriesPipeline:
    def __init__(self):
        self.seen = set()

    def process_item(self, item, spider):
        if item.__class__.__name__ != 'CategoryItem':
            return item

        cid = item['category_id']
        if cid in self.seen:
            raise DropItem(f"Duplicate {cid}") # benjamin : raise ou return a vide ? / return item
        self.seen.add(cid)
        return item


class CsvCategoriesPipeline:
    def open_spider(self, spider):
        self.file = open('categories.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['name', 'url', 'category_id', 'parent_id', 'is_pagelist'])

    def process_item(self, item, spider):
        # On ne traite que les CategoryItem
        if isinstance(item, CategoryItem):
            self.writer.writerow([
                item['name'],
                item['url'],
                item['category_id'],
                item.get('parent_id', 'catégorie racine'),
                item['is_pagelist'],
            ])
        return item  # on retourne l'item dans tous les cas

    def close_spider(self, spider):
        self.file.close()


#Pipeline products

class ConvertPricePipeline:
    # Transforme basic_price "715,54 €" en Decimal('715.54')
    def process_item(self, item, spider):
        if not isinstance(item, ProductItem):
            return item

        raw = item.get('basic_price') or ''
        # extraire le nombre, remplacer la virgule par un point
        m = re.search(r'(\d+[\.,]\d+|\d+)', raw.replace('\u202f', '').replace(' ', ''))
        if m:
            val = m.group(1).replace(',', '.')
            try:
                item['basic_price'] = Decimal(val)
            except:
                item['basic_price'] = Decimal('0.0')
        else:
            item['basic_price'] = Decimal('0.0')
        return item
    
class CsvProductsPipeline:
    #Écrit les ProductItem dans products.csv
    def open_spider(self, spider):
        self.file = open('products.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        # en-tête selon votre JSON d'exemple
        self.writer.writerow(['url', 'page_number', 'basic_name', 'basic_price'])

    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            # écriture de la ligne CSV
            self.writer.writerow([
                item['url'],
                item['page_number'],
                item['basic_name'],
                item['basic_price'],
            ])
        return item

    def close_spider(self, spider):
        # fermeture du fichier à la fin du crawl
        self.file.close()