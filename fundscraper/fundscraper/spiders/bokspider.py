import scrapy


class BokspiderSpider(scrapy.Spider):
    name = "bokspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        pass
