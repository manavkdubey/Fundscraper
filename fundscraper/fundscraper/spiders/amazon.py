import scrapy
from fundscraper.items import AmazonItem
from scrapy import signals
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data


# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = '~/.config/fundscraper/data/amazon_data.csv'
columns=["Name", "Description", "URL"]
load_previous_data(PREVIOUS_DATA_FILE,columns)
class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["www.amazon.science"]
    start_urls = ["https://www.amazon.science/research-awards/call-for-proposals"]
    scraped_data=[]

    def parse(self, response):
        items = response.css('ul.ListA-items > li.ListA-items-item')

        for item in items:
            amazon_item = AmazonItem()  # Create an instance of the AmazonItem class
            amazon_item['title'] = item.css('div.PromoA-title a::text').get()
            amazon_item['description'] = item.css('div.PromoA-description::text').get()
            amazon_item['link'] = item.css('div.PromoA-title a::attr(href)').get()
            self.scraped_data.append({
                    "Name": amazon_item['title'],
                    "Description": amazon_item['description'],
                    "URL": amazon_item['link']
                })
            yield amazon_item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AmazonSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            
            send_email(self.scraped_data,columns,"URL",PREVIOUS_DATA_FILE,"Amazon Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)