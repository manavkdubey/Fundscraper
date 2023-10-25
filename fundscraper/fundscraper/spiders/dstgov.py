import scrapy
from scrapy import signals
from fundscraper.items import DstItem
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data





# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = 'fundscraper/data/dstgov_data.csv'
columns=["Name", "URL"]
load_previous_data(PREVIOUS_DATA_FILE,columns)


class DstgovSpider(scrapy.Spider):
    name = "dstgov"
    allowed_domains = ["dst.gov.in"]
    start_urls = ["https://dst.gov.in/whatsnew"]
    scraped_data = []  # To store scraped data

    def parse(self, response):
        entries = response.css('div.item-list ul li')

        for entry in entries:
            dst_item = DstItem()
            dst_item['name'] = entry.css('div span a::text').get()
            url = entry.css('div span a::attr(href)').get()
            
            if dst_item['name'] is not None and url is not None:
                dst_item['URL'] = 'https://dst.gov.in' + url
            self.scraped_data.append({
                                "Name": dst_item['name'],
                                "URL": dst_item['URL'],
                                
                            })                
            yield dst_item

        next_page = response.css('li.pager-next a::attr(href)').get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DstgovSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            
            send_email(self.scraped_data,columns,"URL",PREVIOUS_DATA_FILE,"DstGov Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)