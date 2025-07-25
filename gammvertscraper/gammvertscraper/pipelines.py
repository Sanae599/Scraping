import csv
import re
from scrapy.exceptions import DropItem
from decimal import Decimal
from gammvertscraper.items import CategoryItem, ProductItem

# Pipeline pour les catégories
class CleanCategoriesPipeline:
    def process_item(self, item, spider):
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
    def process_item(self, item, spider):
        if not isinstance(item, CategoryItem):
            return item
        required = ['name', 'url', 'category_id', 'is_pagelist']
        for field in required:
            if not item.get(field) and item.get(field) != 0:
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
            raise DropItem(f"Duplicate {cid}")
        self.seen.add(cid)
        return item

class CsvCategoriesPipeline:
    def open_spider(self, spider):
        self.file = open('categories.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['name', 'url', 'category_id', 'parent_id', 'is_pagelist'])

    def process_item(self, item, spider):
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
        self.file.close()

# Pipeline pour les produits
class CleanProductsPipeline:
    def process_item(self, item, spider):
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
    def process_item(self, item, spider):
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
    def open_spider(self, spider):
        self.file = open('products.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['url', 'page_number', 'name', 'price'])

    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            self.writer.writerow([
                item['url'],
                item['page_number'],
                item['name'],
                item['price'],
            ])
        return item

    def close_spider(self, spider):
        self.file.close()