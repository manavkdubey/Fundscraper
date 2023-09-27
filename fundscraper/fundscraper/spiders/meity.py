import scrapy

from fundscraper.items import MeityItem
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

from scrapy import signals



def send_email(data):
    # Email configuration
    sender_email = "dubeymanavkumar@gmail.com"  # Replace with your email address
    sender_password = "yhcg wvpl yotu pngq"  # Replace with your email password
    receiver_email = "dmanavkumar24@gmail.com"  # Replace with the recipient's email address
    smtp_server = "smtp.gmail.com"  # Use the appropriate SMTP server for your email provider
    smtp_port = 587  # Use the appropriate SMTP port for your email provider

    # Convert data to a DataFrame
    df = pd.DataFrame(data, columns=["Name", "URL"])

    # Create the HTML content of the email
    html_content = f"""
    <html>
    <body>
        <h2>Scraped Data</h2>
        {df.to_html(index=False, escape=False)}
    </body>
    </html>
    """

    # Create the MIMEText object with HTML content
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Scraped Data"
    message.attach(MIMEText(html_content, "html"))

    # Connect to the SMTP server and send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Error sending email:", str(e))




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
                meity_item['url'] = 'www.meity.gov.in' + url
                self.scraped_data.append((meity_item['name'], meity_item['url']))
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
            send_email(self.scraped_data)
