import scrapy
from scrapy import signals
from fundscraper.items import ICMRItem
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data

# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = '~/.config/fundscraper/data/icmr_data.csv'
columns=["Sr_No","Title","Last_Date","Link_to_apply","Document"]
load_previous_data(PREVIOUS_DATA_FILE,columns)
class IcmrSpider(scrapy.Spider):
    name = "icmr"
    allowed_domains = ["main.icmr.nic.in"]
    start_urls = ["https://main.icmr.nic.in/call%20for%20proposals"]
    scraped_data=[]

    def parse(self, response):
        rows = response.css('.view-content .views-table tbody tr')
        for row in rows:
            item = ICMRItem()
            item['Sr_No'] = row.css('.views-field-counter::text').get().strip()
            item['Title'] = row.css('.views-field-title::text').get().strip()
            item['Last_Date'] = row.css('.views-field-field-seminar-date span.date-display-single::text').get()
            item['Link_to_apply'] = row.css('.views-field-field-link-to-apply::text').get().strip()
            item['Document'] = row.css('.views-field-field-seminar-upload-file a::attr(href)').get()
            
            # Add the item data to the dictionary
            self.scraped_data.append({
                'Sr_No': item['Sr_No'],
                'Title': item['Title'],
                'Last_Date': item['Last_Date'],
                'Link_to_apply': item['Link_to_apply'],
                'Document': item['Document'],
            })
            
            yield item
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(IcmrSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data,columns,"Title",PREVIOUS_DATA_FILE,"ICMR Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)