import time
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def run_spiders():
    process = CrawlerProcess(get_project_settings())
    
    # List your spiders here
    spiders = [
        'amazon', 'birac', 'dbtindia', 'dstgov', 'icmr', 'meity', 
        'ngobox', 'ngoboxgrants', 'onlinedst', 'pfizer'  # Add more spiders if needed
    ]

    for spider_name in spiders:
        process.crawl(spider_name)

    process.start()

if __name__ == "__main__":
    while True:
        p = Process(target=run_spiders)
        p.start()
        p.join()
        
        # Wait for 25 seconds before starting the next round
        time.sleep(25)
