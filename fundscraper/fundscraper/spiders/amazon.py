import scrapy
from fundscraper.items import AmazonItem
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from scrapy import signals

def send_email(data):
    # Email configuration
    sender_email = "dubeymanavkumar@gmail.com" # Replace with your email address
    sender_password = "yhcg wvpl yotu pngq" # Replace with your email password
    receiver_email = "dmanavkumar24@gmail.com" # Replace with the recipient's email address
    smtp_server = "smtp.gmail.com" # Use the appropriate SMTP server for your email provider
    smtp_port = 587 # Use the appropriate SMTP port for your email provider
    
    # Convert data to a DataFrame
    df = pd.DataFrame(data, columns=["Title","description","link"])
    
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



class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["www.amazon.science"]
    start_urls = ["https://www.amazon.science/research-awards/call-for-proposals"]
    scraped_data=[]

    def parse(self, response):
        items = response.css('ul.ListA-items > li.ListA-items-item')

        for item in items:
            amazon_item = AmazonItem()  # Create an instance of the AmazonItem class
            amazon_item['title'] = item.css('div.PromoA-title a::text').get()
            amazon_item['description'] = item.css('div.PromoA-description::text').get()
            amazon_item['link'] = item.css('div.PromoA-title a::attr(href)').get()

            self.scraped_data.append((amazon_item['title'],amazon_item['description'],amazon_item['link']))
            yield amazon_item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AmazonSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data)