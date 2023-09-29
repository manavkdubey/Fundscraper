import scrapy
from fundscraper.items import AmazonItem
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from scrapy import signals

# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = 'data/amazon_data.csv'

def load_previous_data():
    try:
        return pd.read_csv(PREVIOUS_DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Description", "URL"])

def save_current_data(data):
    df = pd.DataFrame(data, columns=["Name", "Description", "URL"])
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
    receiver_email = "shiv.05102@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the HTML content of the email (same as before)
    html_content = f"""
    <html>
    <body>
        <h2>New Scraped Data</h2>
        {pd.DataFrame(new_entries, columns=["Name", "Description", "URL"]).to_html(index=False, escape=False)}
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
            self.scraped_data.append({
                    "Name": amazon_item['title'],
                    "Description": amazon_item['description'],
                    "URL": amazon_item['link']
                })
            yield amazon_item

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(AmazonSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_closed(self, reason):
        if reason == 'finished':
            
            send_email(self.scraped_data)
            save_current_data(self.scraped_data)