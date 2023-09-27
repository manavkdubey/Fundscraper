import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.async_api import async_playwright

class SerbSpider(scrapy.Spider):
    name = "serb"
    allowed_domains = ["www.serbonline.in"]
    start_urls = ["https://www.serbonline.in/SERB/HomePage"]
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }


    async def parse(self, response):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(response.url)

            # Define the selector for the button
            button_selector = 'div.col-md-4 a[data-target="#modal3"]'

            # Scroll down the page using JavaScript
            await page.evaluate("window.scrollBy(0, 1000);")  # Adjust the scroll amount as needed

            # Wait for a short period of time for the button to become visible (you can adjust the delay)
            await page.wait_for_selector(button_selector)

            # Click the button
            await page.click(button_selector)

            # Wait for the modal to load (customize the wait condition as needed)
            await page.wait_for_selector('//table[@id="schemeTable"]//tr[position() > 1]')

            # Extract data from the modal
            scheme_elements = await page.query_selector_all('//table[@id="schemeTable"]//tr[position() > 1]')

            for scheme_element in scheme_elements:
                scheme_name = await scheme_element.inner_text()
                scheme_url = await scheme_element.query_selector('a').get_attribute('href')

                yield {
                    'Scheme Name': scheme_name,
                    'Scheme URL': scheme_url,
                }

            await browser.close()

    def closed(self, reason):
        pass