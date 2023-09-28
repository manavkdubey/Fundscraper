import scrapy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import json
from scrapy import signals
from fundscraper.items import DbtItem


JSON_FILE_PATH = "/Users/manavkumardubey/Desktop/projects/Fundscraper/fundscraper/data/dbt_data.json"

def send_email(data):
    # Email configuration
    sender_email = "dubeymanavkumar@gmail.com"  # Replace with your email address
    sender_password = "yhcg wvpl yotu pngq"  # Replace with your email password
    receiver_email = "dmanavkumar24@gmail.com"  # Replace with the recipient's email address
    smtp_server = "smtp.gmail.com"  # Use the appropriate SMTP server for your email provider
    smtp_port = 587  # Use the appropriate SMTP port for your email provider

    # Convert data to a DataFrame
    df = pd.DataFrame(data, columns=["Name", "URL","End Date"])

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

# Load previously scraped data from the JSON file, if it exists
if os.path.exists(JSON_FILE_PATH):
    with open(JSON_FILE_PATH, 'r') as json_file:
        previous_data = json.load(json_file)
else:
    previous_data = [] 

# Create a global list to store all scraped data
combined_data = []       

class DbtindiaSpider(scrapy.Spider):
    name = "dbtindia"
    allowed_domains = ["dbtindia.gov.in"]
    start_urls = ["https://dbtindia.gov.in/latest-announcement"]
    scraped_data=[]

    def parse(self, response):
        
        entries = response.css('table.cols-4 tbody tr')
        

        for entry in entries:
            dbt_item = DbtItem()
            dbt_item['name'] = entry.css('td.views-field-title ::text').get()
            url = entry.css('td.views-field-php a ::attr(href)').get()
            dbt_item['end_date'] = entry.css('td.views-field-field-start-date span ::text').get()

            
            
            if dbt_item['name'] is not None and url is not None and dbt_item['end_date'] is not None:
                dbt_item['url'] = 'https://dbtindia.gov.in/latest-announcement' + url
                self.scraped_data.append((dbt_item['name'], dbt_item['url'],dbt_item['end_date']))

                yield dbt_item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DbtindiaSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            # Check for new entries
            new_entries = [entry for entry in self.scraped_data if entry not in previous_data]
            if new_entries:
                combined_data.extend(new_entries)
                # Save the combined data to the JSON file
                with open(JSON_FILE_PATH, 'w') as json_file:
                    json.dump(combined_data, json_file)
                send_email(new_entries)

