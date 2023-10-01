
import time
from scrapy.crawler import CrawlerProcess
from fundscraper.spiders.amazon import AmazonSpider
from fundscraper.spiders.birac import BiracSpider
from fundscraper.spiders.dbtindia import DbtindiaSpider
from fundscraper.spiders.dstgov import DstgovSpider
from fundscraper.spiders.icmr import IcmrSpider
from fundscraper.spiders.meity import MeitySpider
from fundscraper.spiders.ngobox import NgoboxSpider
from fundscraper.spiders.ngoboxgrants import NgoboxgrantsSpider
from fundscraper.spiders.onlinedst import OnlinedstSpider
from fundscraper.spiders.pfizer import PfizerSpider
from fundscraper import settings

def run_spiders():
    process = CrawlerProcess()
    process.crawl(AmazonSpider)
    process.crawl(BiracSpider)
    process.crawl(DbtindiaSpider)
    process.crawl(DstgovSpider)
    process.crawl(IcmrSpider)
    process.crawl(MeitySpider)
    process.crawl(NgoboxSpider)
    process.crawl(NgoboxgrantsSpider)
    process.crawl(OnlinedstSpider)
    process.crawl(PfizerSpider)
    process.start()

def main():
    while True:
        try:
            run_spiders()
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        # Sleep for 5 minutes (300 seconds) before the next iteration
        time.sleep(300)

if __name__ == "__main__":
    main()
