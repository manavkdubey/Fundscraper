import scrapy

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

from scrapy import signals

from fundscraper.items import BiracItem



def send_email(data):
    # Email configuration
    sender_email = "dubeymanavkumar@gmail.com"  # Replace with your email address
    sender_password = "yhcg wvpl yotu pngq"  # Replace with your email password
    receiver_email = "dmanavkumar24@gmail.com"  # Replace with the recipient's email address
    smtp_server = "smtp.gmail.com"  # Use the appropriate SMTP server for your email provider
    smtp_port = 587  # Use the appropriate SMTP port for your email provider

    # Convert data to a DataFrame
    df = pd.DataFrame(data, columns=["sno", "call_for_proposal","url","call_status","start_date","last_submission_date"])

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
            birac_item['url']='https://www.birac.nic.in/'+row.css('td a::attr(href)').get()
            birac_item['call_status'] = row.css('td small.text-red::text').get()
            birac_item['start_date'] = row.css('td small.text-green::text').get()
            birac_item['last_submission_date'] = row.css('td small.text-red.pull-right::text')
            self.scraped_data.append((birac_item['sno'], birac_item['call_for_proposal'], birac_item['url'], birac_item['call_status'], birac_item['start_date'], birac_item['last_submission_date']))

            yield birac_item
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BiracSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data)