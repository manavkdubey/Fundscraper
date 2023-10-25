import scrapy
from scrapy import signals
from fundscraper.items import BiracItem
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data



# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = 'fundscraper/data/birac_data.csv'
columns=["call_for_proposal", "URL","call_status","start_date","last_submission_date"]
load_previous_data(PREVIOUS_DATA_FILE,columns)

class BiracSpider(scrapy.Spider):
    name = "birac"
    allowed_domains = ["www.birac.nic.in"]
    start_urls = ["https://www.birac.nic.in/cfp.php"]
    scraped_data=[]

    def parse(self, response):
        # Use response.css to locate the table
        table = response.css('table#current')

        # Extract data from the table rows
        rows = table.css('tbody tr')
        for row in rows:
            birac_item = BiracItem()
            birac_item['sno'] = row.css('td.sorting_1::text').get()
            birac_item['call_for_proposal'] = row.css('td a::text').get().strip()
            birac_item['URL']='https://www.birac.nic.in/'+row.css('td a::attr(href)').get()
            birac_item['call_status'] = row.css('td small.text-red::text').get()
            birac_item['start_date'] = row.css('td small.text-green::text').get()
            birac_item['last_submission_date'] = row.css('td small.text-red.pull-right::text')
            self.scraped_data.append({
                    "call_for_proposal":  birac_item['call_for_proposal'], 
                    "URL": birac_item['URL'],
                    "call_status":  birac_item['call_status'],
                    "start_date": birac_item['start_date'],
                    "last_submission_date": birac_item['last_submission_date']
                })
            yield birac_item
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BiracSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data,columns,"URL",PREVIOUS_DATA_FILE,"Birac Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)
