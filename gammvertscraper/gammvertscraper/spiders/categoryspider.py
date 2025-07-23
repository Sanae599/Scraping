import scrapy


class CategoryspiderSpider(scrapy.Spider):
    name = "categoryspider"
    allowed_domains = ["gammvert.fr"]
    start_urls = ["https://gammvert.fr"]

    def parse(self, response):
        categories = response.css('nav .ens-main-navigation-items__link-label::text').getall()
        links = response.css('nav .ens-main-navigation-items__link::attr(href)').getall()

        

        response.css('nav ens-main-navigation-items__link ds-ens-anchor ds-ens-anchor--link ens-main-navigation-items__link').getall()