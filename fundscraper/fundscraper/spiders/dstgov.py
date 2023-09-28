import scrapy
from fundscraper.items import DstItem
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import json

from scrapy import signals


JSON_FILE_PATH = "/Users/manavkumardubey/Desktop/projects/Fundscraper/fundscraper/data/dst_data.json"
def check_send_email():
    print("Email sent successfully")
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


# Load previously scraped data from the JSON file, if it exists
if os.path.exists(JSON_FILE_PATH):
    with open(JSON_FILE_PATH, 'r') as json_file:
        previous_data = json.load(json_file)
else:
    previous_data = []
print("PREV---PREV---PREV---PREV---PREV---PREV---PREV---PREV---PREV---PREV---PREV---PREV---PREV---")
print(previous_data)
# Create a global list to store all scraped data
combined_data = []

class DstgovSpider(scrapy.Spider):
    name = "dstgov"
    allowed_domains = ["dst.gov.in"]
    start_urls = ["https://dst.gov.in/whatsnew"]
    scraped_data = []  # To store scraped data

    def parse(self, response):
        entries = response.css('div.item-list ul li')

        for entry in entries:
            dst_item = DstItem()
            dst_item['name'] = entry.css('div span a::text').get()
            url = entry.css('div span a::attr(href)').get()
            
            if dst_item['name'] is not None and url is not None:
                dst_item['url'] = 'https://dst.gov.in' + url
                self.scraped_data.append((dst_item['name'], dst_item['url']))
                yield dst_item

        next_page = response.css('li.pager-next a::attr(href)').get()
        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DstgovSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            # Check for new entries
            new_entries = [entry for entry in self.scraped_data if entry not in previous_data]
            print("NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---NEW---")
            print(new_entries)
            print("COMP----COMP----COMP----COMP----COMP----COMP----COMP----COMP----COMP----COMP----COMP----") 
            # Check for new entries
            new_entries = [entry for entry in self.scraped_data if entry not in previous_data]

            # Check for removed entries (entries that were in previous_data but not in scraped_data)
            removed_entries = [entry for entry in previous_data if entry not in self.scraped_data]

            # Update the combined_data list with the latest scraped data
            combined_data = self.scraped_data

            # Save the combined data to the JSON file
            with open(JSON_FILE_PATH, 'w') as json_file:
                json.dump(combined_data, json_file)

            # Print or perform any action you want based on the differences
            if new_entries:
                print("New entries detected:", new_entries)
            if removed_entries:
                print("Removed entries detected:", removed_entries)

            if len(new_entries):
                combined_data.extend(new_entries)
                # Save the combined data to the JSON file
                with open(JSON_FILE_PATH, 'w') as json_file:
                    json.dump(combined_data, json_file)
                check_send_email()
