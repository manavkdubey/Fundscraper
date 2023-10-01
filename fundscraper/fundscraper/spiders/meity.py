import scrapy
from fundscraper.items import MeityItem
from scrapy import signals
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data


# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = '~/.config/fundscraper/data/meity_data.csv'
columns=["Name", "URL"]
load_previous_data(PREVIOUS_DATA_FILE,columns)


class MeitySpider(scrapy.Spider):
    name = "meity"
    allowed_domains = ["www.meity.gov.in"]
    start_urls = ["https://www.meity.gov.in/whatsnew"]
    scraped_data=[]

    def parse(self, response):
        entries = response.css('div.view-content table.views-table tbody tr')

        for entry in entries:
            meity_item = MeityItem()
            meity_item['name'] = entry.css('td.views-field-title a::text').get()
            url = entry.css('td.views-field-title a::attr(href)').get()
            
            if meity_item['name'] is not None and url is not None:
                meity_item['URL'] = 'www.meity.gov.in' + url
            self.scraped_data.append({
                                "Name": meity_item['name'],
                                "URL": meity_item['URL'],
                                
                            })                 
            yield meity_item


        next_page = response.css('li.pager-next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MeitySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data,columns,"URL",PREVIOUS_DATA_FILE,"MEITY Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)
