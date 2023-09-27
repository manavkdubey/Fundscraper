import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, task

# Get the Scrapy project settings
settings = get_project_settings()

# Create a CrawlerProcess with the project settings
process = CrawlerProcess(settings)

# Add all spider names to a list
spider_list = ['dstgov', 'dbtindia']  # Replace with your spider names

# Function to run the spiders
def run_spiders():
    for spider_name in spider_list:
        process.crawl(spider_name)
    process.start()

# Run the spiders periodically every 5 minutes
task_loop = task.LoopingCall(run_spiders)
task_loop.start(300)  # 300 seconds = 5 minutes

# Start the Twisted reactor to run the periodic task
reactor.run()
