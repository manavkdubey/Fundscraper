import scrapy
from scrapy import signals
from fundscraper.items import PfizerItem
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data


# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = '~/.config/fundscraper/data/pfizer_data.csv'
columns=["Title","Release_Date","Review_Process","Grant_Type","Focus_Area","Country","Application_Due_Date","PDF_Link"]
load_previous_data(PREVIOUS_DATA_FILE,columns)
class PfizerSpider(scrapy.Spider):
    name = "pfizer"
    allowed_domains = ["www.pfizer.com"]
    start_urls = ["https://www.pfizer.com/about/programs-policies/grants/competitive-grants"]
    scraped_data=[]
    
    def parse(self, response):
        # Locate the table element using CSS selector
        table = response.css('table.cols-5')
        
        # Extract data from the table rows
        rows = table.css('tbody tr')
        for row in rows:
            item=PfizerItem()
            item['Title'] = row.css('td.views-field-title .compound-name::text').get()
            item['Release_Date'] = row.css('span.label:contains("Release Date:") + span.data time::attr(datetime)').get()
            item['Review_Process'] = row.css('span.label:contains("Review Process:") + span.data::text').get()
            item['Grant_Type'] = row.css('td.views-field-field-grant-type::text').get()
            item['Focus_Area'] = row.css('td.views-field-field-focus-area::text').get()
            item['Country'] = row.css('td.views-field-field-country::text').get()
            item['Application_Due_Date'] = row.css('td.views-field-field-rfp-loi-due-date time::attr(datetime)').get()
            item['PDF_Link'] = row.css('a.clinical-link::attr(href)').get()
            
            
            self.scraped_data.append({'Title':item['Title'], 
                                      'Release_Date':item['Release_Date'], 
                                      'Review_Process':item['Review_Process'],
                                       'Grant_Type':item['Grant_Type'],
                                        'Focus_Area':item['Focus_Area'], 
                                        'Country':item['Country'], 
                                        'Application_Due_Date':item['Application_Due_Date'],
                                        'PDF_Link':item['PDF_Link']})
            yield item
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PfizerSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data,columns,"Title",PREVIOUS_DATA_FILE,"Pfizer Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)
        