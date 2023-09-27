import scrapy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from scrapy import signals
from fundscraper.items import PfizerItem

def send_email(data):
    # Email configuration
    sender_email = "dubeymanavkumar@gmail.com" # Replace with your email address
    sender_password = "yhcg wvpl yotu pngq" # Replace with your email password
    receiver_email = "dmanavkumar24@gmail.com" # Replace with the recipient's email address
    smtp_server = "smtp.gmail.com" # Use the appropriate SMTP server for your email provider
    smtp_port = 587 # Use the appropriate SMTP port for your email provider
    
    # Convert data to a DataFrame
    df = pd.DataFrame(data, columns=["Title", "Release_Date","Review_Process","Grant_Type","Focus_Area","Country","Application_Due_Date","PDF_Link"])
    
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
            
            
            self.scraped_data.append((item['Title'], item['Release_Date'], item['Review_Process'], item['Grant_Type'], item['Focus_Area'], item['Country'], item['Application_Due_Date'], item['PDF_Link']))
            yield item
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(PfizerSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data)
        