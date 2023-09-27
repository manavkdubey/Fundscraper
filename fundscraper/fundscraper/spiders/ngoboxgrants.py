import scrapy
from fundscraper.items import ngoItem
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
    df = pd.DataFrame(data, columns=["Title","organization","deadline","link"])
    
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
            item['url'] = 'https://ngobox.org/'+entry.css('div div div div p a ::attr(href)').get()

            self.scraped_data.append((item['title'],item['organization'],item['deadline'],item['url']))

            yield item
        
        

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(NgoboxgrantsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data)
