import scrapy
from fundscraper.items import ngoItem
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from scrapy import signals
from fundscraper.spiders.send_email import send_email,load_previous_data,save_current_data


# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = 'data/ngoboxgrants_data.csv'
columns=["Title","organization","deadline","URL"]
load_previous_data(PREVIOUS_DATA_FILE,columns)


class NgoboxgrantsSpider(scrapy.Spider):
    name = "ngoboxgrants"
    allowed_domains = ["ngobox.org"]
    start_urls = ["https://ngobox.org/grant_announcement_listing.php"]
    scraped_data=[]

    def parse(self, response):
        
        entries = response.css('div.fadeInLeft')

        for entry in entries:
        
            item = ngoItem()  # Initialize your item
            item['title'] = entry.css('div div div div p a ::text').get()
            item['organization'] = entry.css('p.p_balck::text').get().strip()
            item['deadline'] = entry.css('div.list_bottumsec::text').get().strip()
            item['URL'] = 'https://ngobox.org/'+entry.css('div div div div p a ::attr(href)').get()

            self.scraped_data.append({'title':item['title'],
                                                'organization':item['organization'],
                                                'deadline':item['deadline'],
                                                'URL':item['URL']})
            yield item
        
        

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NgoboxgrantsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data,columns,"URL",PREVIOUS_DATA_FILE,"NGOBOXGRANTS Updates")
            save_current_data(self.scraped_data,PREVIOUS_DATA_FILE,columns)
