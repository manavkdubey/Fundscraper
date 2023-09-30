# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FundscraperItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass
class DstItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

class DbtItem(scrapy.Item):
    name=scrapy.Field()
    url=scrapy.Field()
    end_date=scrapy.Field()

class SERB(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

class MeityItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()

class BiracItem(scrapy.Item):
    sno = scrapy.Field()
    call_for_proposal = scrapy.Field()
    call_status = scrapy.Field()
    start_date = scrapy.Field()
    last_submission_date = scrapy.Field()
    url = scrapy.Field()

class PfizerItem(scrapy.Item):
    Title = scrapy.Field()
    Release_Date = scrapy.Field()
    Review_Process = scrapy.Field()
    Grant_Type = scrapy.Field()
    Focus_Area = scrapy.Field()
    Country = scrapy.Field()
    Application_Due_Date = scrapy.Field()
    PDF_Link = scrapy.Field()

class FirstTableItem(scrapy.Item):
    s_no = scrapy.Field()
    programme_or_scheme = scrapy.Field()
    division = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()

class SecondTableItem(scrapy.Item):
    s_no = scrapy.Field()
    programme_or_scheme = scrapy.Field()
    division = scrapy.Field()

class AmazonItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    link = scrapy.Field()
    image_url = scrapy.Field()

class ffn_Item(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    description = scrapy.Field()

class ngoItem(scrapy.Item):
    title = scrapy.Field()
    organization = scrapy.Field()
    deadline = scrapy.Field()
    URL = scrapy.Field()

class ICMRItem(scrapy.Item):
    Sr_No = scrapy.Field()
    Title = scrapy.Field()
    Last_Date = scrapy.Field()
    Link_to_apply = scrapy.Field()
    Document = scrapy.Field()
class OnlinedstfirstItem(scrapy.Item):
    serial_number = scrapy.Field()
    programme_or_scheme = scrapy.Field()
    division = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()

class onlinedstsecondItem(scrapy.Item):
    serial_number = scrapy.Field()
    programme_or_scheme = scrapy.Field()
    division = scrapy.Field()
    

