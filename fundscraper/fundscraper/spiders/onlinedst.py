import scrapy
from scrapy import signals
from fundscraper.items import OnlinedstfirstItem, onlinedstsecondItem
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data


# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE1 = 'data/onlinedst_data1.csv'
PREVIOUS_DATA_FILE2 = 'data/onlinedst_data2.csv'
columns1=["serial_number","programme_or_scheme","division","start_date","end_date"]
columns2=["serial_number","programme_or_scheme","division"]
load_previous_data(PREVIOUS_DATA_FILE1,columns1)
load_previous_data(PREVIOUS_DATA_FILE2,columns2)
class OnlinedstSpider(scrapy.Spider):
    name = "onlinedst"
    allowed_domains = ["onlinedst.gov.in"]
    start_urls = ["https://onlinedst.gov.in/Login.aspx"]
    first_scraped_data=[]
    second_scraped_data=[]
    def parse(self, response):
        # Extracting data from the first table
        first_table_rows = response.xpath('//div[@id="divprojectformat"]/table//tr')[1:]  # Skipping the header row

        for row in first_table_rows:
            item = OnlinedstfirstItem()  # Create an instance of the OnlinedstfirstItem
            item['serial_number'] = row.xpath('.//td[1]/text()').get()
            item['programme_or_scheme'] = row.xpath('.//td[2]/a/text()').get()
            item['division'] = row.xpath('.//td[3]/span/text()').get()
            item['start_date'] = row.xpath('.//td[4]/span/text()').get()
            item['end_date'] = row.xpath('.//td[5]/text()').get()
            self.first_scraped_data.append({
                'serial_number': item['serial_number'],
                'programme_or_scheme': item['programme_or_scheme'],
                'division': item['division'],
                'start_date': item['start_date'],
                'end_date': item['end_date']
            })
            yield item

        # Extracting data from the second table
        second_table_rows = response.xpath('//div[@id="divprojectformat1"]//table//tr')[1:]  # Skipping the header row

        for row in second_table_rows:
            item = onlinedstsecondItem()
            item['serial_number']= row.xpath('.//td[1]/text()').get()
            item['programme_or_scheme']= row.xpath('.//td[2]/a/text()').get()
            item['division']= row.xpath('.//td[3]/text()').get()
            self.second_scraped_data.append({
                'serial_number': item['serial_number'],
                'programme_or_scheme': item['programme_or_scheme'],
                'division': item['division'],
            })
            yield item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(OnlinedstSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.first_scraped_data,columns1,"programme_or_scheme",PREVIOUS_DATA_FILE1,"Onlinedst Updates")
            send_email(self.second_scraped_data,columns2,"programme_or_scheme",PREVIOUS_DATA_FILE2,"Onlinedst Updates")
            save_current_data(self.first_scraped_data,PREVIOUS_DATA_FILE1,columns1)
            save_current_data(self.second_scraped_data,PREVIOUS_DATA_FILE2,columns2)
