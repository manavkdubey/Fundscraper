import scrapy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from scrapy import signals
from fundscraper.items import BiracItem



# Store previously scraped data in a file (you can use a database as well)
PREVIOUS_DATA_FILE = 'data/birac_data.csv'

def load_previous_data():
    try:
        return pd.read_csv(PREVIOUS_DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["call_for_proposal", "URL","call_status","start_date","last_submission_date"])

def save_current_data(data):
    df = pd.DataFrame(data, columns=["call_for_proposal", "URL","call_status","start_date","last_submission_date"])
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
        {pd.DataFrame(data, columns=["call_for_proposal", "URL","call_status","start_date","last_submission_date"]).to_html(index=False, escape=False)}
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
            self.scraped_data.append({
                    "call_for_proposal":  birac_item['call_for_proposal'], 
                    "URL": birac_item['url'],
                    "call_status":  birac_item['call_status'],
                    "start_date": birac_item['start_date'],
                    "last_submission_date": birac_item['last_submission_date']
                })
            yield birac_item
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BiracSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            send_email(self.scraped_data)
            save_current_data(self.scraped_data)
