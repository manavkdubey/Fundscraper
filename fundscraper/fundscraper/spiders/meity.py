import scrapy

from fundscraper.items import MeityItem
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

from scrapy import signals


# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = 'data/meity_data.csv'

def load_previous_data():
    try:
        return pd.read_csv(PREVIOUS_DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "URL"])

def save_current_data(data):
    df = pd.DataFrame(data, columns=["Name", "URL"])
    df.to_csv(PREVIOUS_DATA_FILE, index=False)

def send_email(data):
    # Load previously scraped data
    previous_data = load_previous_data()

    # Create a set of unique URLs from previous data
    previous_urls = set(previous_data["URL"])

    # Find new entries by comparing with previous data
    new_entries = [entry for entry in data if entry["URL"] not in previous_urls]

    if not new_entries:
        print("No new entries found. Email not sent.")
        return

    # Email configuration (same as before)
    sender_email = "dubeymanavkumar@gmail.com"
    sender_password = "yhcg wvpl yotu pngq"
    receiver_email = "dmanavkumar24@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the HTML content of the email (same as before)
    html_content = f"""
    <html>
    <body>
        <h2>New Scraped Data</h2>
        {pd.DataFrame(new_entries, columns=["Name", "URL"]).to_html(index=False, escape=False)}
    </body>
    </html>
    """

    # Create the MIMEText object with HTML content (same as before)
    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "New Scraped Data"
    message.attach(MIMEText(html_content, "html"))

    # Connect to the SMTP server and send the email (same as before)
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
            self.scraped_data.append({
                                "Name": meity_item['name'],
                                "URL": meity_item['url'],
                                
                            })                 
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
            save_current_data(self.scraped_data)
