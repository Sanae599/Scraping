# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CategoryItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    category_id = scrapy.Field()
    parent_id = scrapy.Field()  
    is_pagelist = scrapy.Field() 
    
class ProductItem(scrapy.Item):
    product_id      = scrapy.Field() 
    name            = scrapy.Field()
    url             = scrapy.Field()
    category_id     = scrapy.Field()  #FK vers CategoryItem
    price           = scrapy.Field()
    price_init      = scrapy.Field()
    price_reduc     = scrapy.Field()
    price_final     = scrapy.Field()
    categories      = scrapy.Field()
    currency        = scrapy.Field()
    availability    = scrapy.Field()  
    stock_qty       = scrapy.Field()
    pickup_available= scrapy.Field()
    shipping_cost   = scrapy.Field()
    shipping_volume = scrapy.Field()
    brand           = scrapy.Field()
    description     = scrapy.Field()
    rating          = scrapy.Field()  
    num_reviews     = scrapy.Field()  
    page_number     = scrapy.Field()  #debug
