import time
from clients.driver_manager import setup_stealth_driver
from bs4 import BeautifulSoup


class SeleniumFetcher:
    """
    HTML fetching and cleaning utilities using Selenium.

    This module provides the `SeleniumFetcher` class for:
    - Loading web pages using a stealth-configured Selenium WebDriver.
    - Cleaning HTML by removing scripts, styles, iframes, and other unnecessary tags.
    - Optionally truncating long HTML content for efficient processing.

    Typical usage:
        from clients.selenium_fetcher import SeleniumFetcher

        fetcher = SeleniumFetcher()
        cleaned_html = fetcher.get_html("https://example.com", limit=True)
    """
    def __init__(self):
        self.driver = setup_stealth_driver()

    def get_html(self, url: str, limit: bool):
        self.driver.get(url)
        time.sleep(2)
        cleaned_html = self.clean_html_generic(self.driver.page_source, limit)
        return cleaned_html

    def clean_html_generic(self, html: str, limit: bool, max_length: int = 30000) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.body if soup.body else soup
        for tag in body(["script", "style", "noscript", "iframe"]):
            tag.decompose()

        raw_html = str(body)
        if limit:
            if len(raw_html) > max_length:
                start_index = len(raw_html) // 2 - max_length // 2
                raw_html = "\n<!-- truncated start -->" + raw_html[start_index:]
        soup2 = BeautifulSoup(raw_html, 'html.parser')
        cleaned_html = soup2.prettify()
        return cleaned_html
