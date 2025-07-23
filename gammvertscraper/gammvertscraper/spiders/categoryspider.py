import scrapy
from gammvertscraper.items import CategoryItem

EXCLUDE = {"/c/destockage"}

class TopCategoriesSpider(scrapy.Spider):
    name = "top_categories"
    allowed_domains = ["gammvert.fr"]
    start_urls = ["https://www.gammvert.fr"] 

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        },
    }

    def parse(self, response):
        navbar = response.css('nav')
        for cat in navbar:
            cat_item = CategoryItem()
            cat_item['name'] = cat.css('.ens-main-navigation-items__link-label::text').getall()            
            cat_relative_url = cat.css("a[href^='/c/']::attr(href)").getall()
            cat_item['url'] = 'https://www.gammvert.fr/' + cat_relative_url

            #cat_item['category_id'] = self.generate_id(cat_item['name'],cat_item['url'])
            cat_item['category_id'] = "singe"
            cat_item['parent_id'] = None
            cat_item['is_pager'] = 0

            #yield response.follow(cat_item['url'],callback=self.parse_subcat)
            yield cat_item
    def parse_subcat(self,resonse):
        pass

    def generate_id(name,url):
        new_id = name.strip().lower().replace(" ","_") + "_" + url.strip().lower().replace("/","_").strip("_")
        return new_id