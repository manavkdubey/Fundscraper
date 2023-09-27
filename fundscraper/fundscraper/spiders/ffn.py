import scrapy
from fundscraper.items import ffn_Item
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import random
import time
from scrapy import signals

class FfnSpider(scrapy.Spider):
    name = "ffn"
    allowed_domains = ["fundsforngos.org"]
    start_urls = ["https://www.fundsforngos.org"]
    scraped_data = []

    # List of HTTP status codes to handle
    handle_httpstatus_list = [403]  # Add other status codes if needed

    def generate_user_agent(self):
        # List of user agents to choose from (you can add more if needed)
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
            # Add more user agents here
        ]
        return random.choice(user_agents)

    def start_requests(self):
        for url in self.start_urls:
            headers = {'User-Agent': self.generate_user_agent()}
            yield scrapy.Request(url, headers=headers, callback=self.parse, errback=self.error_handler)

    def parse(self, response):
        if response.status == 403:
            self.logger.error(f"Received 403 Forbidden response from {response.url}")
            return

        items = response.css('div.RssGrid-item')

        for item in items:
            ffn_item = ffn_Item()
            ffn_item['title'] = item.css('div.rssapp-card-title a::text').get()
            ffn_item['link'] = item.css('div.rssapp-card-title a::attr(href)').get()
            ffn_item['description'] = item.css('div.rssapp-card-description::text').get()

            self.scraped_data.append((ffn_item['title'], ffn_item['link'], ffn_item['description']))

            yield ffn_item

            # Add a delay of a few seconds between requests
            time.sleep(random.uniform(3, 5))  # Adjust the delay as needed


    def error_handler(self, failure):
        self.logger.error(f"Request failed: {failure.value.response.status} {failure.value.response.url}")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FfnSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, reason):
        if reason == 'finished':
            self.send_email(self.scraped_data)

    def send_email(self, data):
        # Email configuration
        sender_email = "dubeymanavkumar@gmail.com"  # Replace with your email address
        sender_password = "your-email-password"  # Replace with your email password
        receiver_email = "dmanavkumar24@gmail.com"  # Replace with the recipient's email address
        smtp_server = "smtp.gmail.com"  # Use the appropriate SMTP server for your email provider
        smtp_port = 587  # Use the appropriate SMTP port for your email provider

        # Convert data to a DataFrame
        df = pd.DataFrame(data, columns=["Title", "Link", "Description"])

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
            self.logger.info("Email sent successfully.")
        except Exception as e:
            self.logger.error("Error sending email: %s", str(e))
