import scrapy

class OnlinedstSpider(scrapy.Spider):
    name = "onlinedst"
    allowed_domains = ["onlinedst.gov.in"]
    start_urls = ["https://onlinedst.gov.in/Login.aspx"]

    def parse(self, response):
        # Extracting data from the first table
        first_table_rows = response.xpath('//div[@id="divprojectformat"]/table//tr')[1:]  # Skipping the header row

        for row in first_table_rows:
            item = {
                'S.No.': row.xpath('.//td[1]/text()').get(),
                'Programme or Scheme': row.xpath('.//td[2]/a/text()').get(),
                'Division': row.xpath('.//td[3]/span/text()').get(),
                'Start Date': row.xpath('.//td[4]/span/text()').get(),
                'End Date': row.xpath('.//td[5]/text()').get(),
            }
            yield item

        # Extracting data from the second table
        second_table_rows = response.xpath('//div[@id="divprojectformat1"]//table//tr')[1:]  # Skipping the header row

        for row in second_table_rows:
            item = {
                'S.No.': row.xpath('.//td[1]/text()').get(),
                'Programme or Scheme': row.xpath('.//td[2]/a/text()').get(),
                'Division': row.xpath('.//td[3]/span/text()').get(),
            }
            yield item
