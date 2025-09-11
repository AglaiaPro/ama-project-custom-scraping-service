# A class for gathering companies in the sector
import time
from scraping.base_scraper import BaseScraper


class SectorScraper(BaseScraper):
    """
    Scraper for gathering all companies from a sector page.

    Responsibilities:
        - Open sector page and find all company links using a template.
        - Extract company names and URLs.
    """
    def __init__(self, driver, template):
        """
        Initialize the sector scraper.

        Args:
            driver: Selenium WebDriver instance.
            template (dict): Template for extracting companies from a sector page.
        """
        self.driver = driver
        self.template = template

    def get_companies(self, url):
        """
        Scrape all companies listed on the sector page.

        Args:
            url (str): URL of the sector page.

        Returns:
            list[dict]: List of companies with 'name' and 'url'.
        """
        companies = []

        self.driver.get(url)
        time.sleep(2) # Wait for page to load

        fields = self.template['page_companies_template']['fields']
        company_sel = self.template['page_companies_template']['company_selector']

        try:
            company_elements = self.driver.find_elements(
                self.get_by_type(company_sel['type']),
                company_sel['value']
            )

            for elem in company_elements:
                # company name
                name = self.extract_field(elem, fields['name'])
                # company URL
                url = self.extract_field(elem, fields['url'])

                if name and url:
                    companies.append({
                        "name": name,
                        "url": url
                    })
        except Exception as e:
            print(f"Error parsing company: {e}")

        return companies
