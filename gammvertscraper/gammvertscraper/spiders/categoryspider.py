import scrapy


class CategoryspiderSpider(scrapy.Spider):
    name = "categoryspider"
    allowed_domains = ["gammvert.fr"]
    start_urls = ["https://gammvert.fr"]

    def parse(self, response):
        pass
