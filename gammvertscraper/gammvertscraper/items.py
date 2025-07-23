# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GammvertscraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CategoryItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    category_id = scrapy.Field()
    parent_id = scrapy.Field()  # None si c’est une catégorie racine
    is_pager = scrapy.Field() # 1 ou 0 si page de produits ou non