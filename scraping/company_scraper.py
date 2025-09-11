# A class for detailed data collection about a company
import random
import time
from scraping.base_scraper import BaseScraper
from clients.driver_manager import setup_stealth_driver


class CompanyScraper(BaseScraper):
    """
    Scraper for gathering detailed information about a single company.

    Responsibilities:
        - Open company page and parse fields according to template.
        - Handle table-like fields.
        - Return structured dictionary with company details.
    """
    def __init__(self, template):
        """
        Initialize the company scraper with a field template.

        Args:
            template (dict): Template describing which fields to scrape.
        """
        self.template = template

    def scrape_company(self, company_url):
        """
        Scrape data from a single company page.

        Args:
            company_url (str): URL of the company page.

        Returns:
            dict | None: Parsed company details or None if failed.
        """
        driver = None
        try:
            driver = setup_stealth_driver()
            driver.get(company_url)
            # Randomized sleep to mimic human behavior
            time.sleep(random.uniform(1, 5))

            fields = self.template.get('fields', {})
            details = self.parse_fields(driver, fields)

            details['url'] = company_url

            print(f"[OK] {details['url']}")

            return details

        except Exception as e:
            print(f"[ERROR] Failed to scrape company {company_url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def scrape_companies(self, links):
        """
        Scrape multiple companies sequentially.

        Args:
            links (list[str]): List of company URLs.

        Returns:
            list[dict]: List of parsed company details.
        """
        results = []
        for url in links:
            if url:
                details = self.scrape_company(url)
                if details:
                    results.append(details)
        return results

    def parse_fields(self, driver, fields):
        """
        Parse fields for a company page recursively.

        Args:
            driver: Selenium WebDriver instance.
            fields (dict): Dictionary of field templates.

        Returns:
            dict: Parsed field values.
        """
        result = {}
        for key, field in fields.items():
            if isinstance(field, dict):
                if field.get('type') == 'table':
                    result[key] = self.parse_table(driver, field)

                elif all(k in field for k in ("type", "value", "attribute")):
                    result[key] = self.extract_field(driver, field)

                else:
                    result[key] = self.parse_fields(driver, field)
            else:
                print(f"Unknown field structure for key: {key}")
                continue
        return result

    def parse_table(self, driver, field):
        """
        Parse table-like fields into a list of row dictionaries.

        Args:
            driver: Selenium WebDriver instance.
            field (dict): Table field template.

        Returns:
            list[dict]: List of rows extracted from the table.
        """
        subfields = field.get('fields', {})

        # collecting data for each column
        columns = {
            name: self.extract_field(driver, fdata)
            for name, fdata in subfields.items()
        }
        # Let's determine the maximum number of rows by the length of the longest column.
        max_len = max((len(col) for col in columns.values() if isinstance(col, list)), default=0)

        rows = []
        for i in range(max_len):
            row = {
                col_name: col_values[i] if isinstance(col_values, list) and i < len(col_values) else None
                for col_name, col_values in columns.items()
            }
            rows.append(row)
        return rows
