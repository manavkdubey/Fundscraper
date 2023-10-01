import scrapy
from scrapy import signals
from fundscraper.items import DbtItem
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data

# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = '~/.config/fundscraper/data/previous_data.csv'
columns=["Name", "URL", "End Date"]
load_previous_data(PREVIOUS_DATA_FILE,columns)
class DbtindiaSpider(scrapy.Spider):
    name = "dbtindia"
    allowed_domains = ["dbtindia.gov.in"]
    start_urls = ["https://dbtindia.gov.in/latest-announcement"]
    scraped_data = []

    def parse(self, response):
        entries = response.css('table.cols-4 tbody tr')

        for entry in entries:
            dbt_item = DbtItem()
            dbt_item['name'] = entry.css('td.views-field-title ::text').get()
            url = entry.css('td.views-field-php a ::attr(href)').get()
            dbt_item['end_date'] = entry.css('td.views-field-field-start-date span ::text').get()

            if dbt_item['name'] is not None and url is not None and dbt_item['end_date'] is not None:
                dbt_item['URL'] = 'https://dbtindia.gov.in/latest-announcement' + url
                self.scraped_data.append({
                    "Name": dbt_item['name'],
                    "URL": dbt_item['URL'],
                    "End Date": dbt_item['end_date']
                })
                yield dbt_item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DbtindiaSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data,columns,"URL",PREVIOUS_DATA_FILE,"DBTINDIA Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)


