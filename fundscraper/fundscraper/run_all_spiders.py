import subprocess
import time

# List of your Scrapy spider names
spider_names = ['dstgov', 'dbtindia','amazon','birac','dbtindia','icmr','meity','ngobox','ngoboxgrants','onlinedst','pfizer']  # Add your spider names here

while True:
    for spider_name in spider_names:
        try:
            # Run the Scrapy spider using subprocess
            subprocess.run(['scrapy', 'crawl', spider_name])
        except Exception as e:
            print(f"Error running {spider_name}: {e}")

    # Wait for 5 minutes before running again
    time.sleep(300)  # 300 seconds = 5 minutes