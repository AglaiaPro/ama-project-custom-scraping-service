from pymongo.errors import PyMongoError

from app.exceptions import TemplateNotFound, SectorNotFound, ScrapingServiceError
from clients.driver_manager import setup_stealth_driver
from database.mongo_connection import get_collections
from scraping.company_scraper import CompanyScraper
from scraping.sector_scraper import SectorScraper
from prompts.company_list_prompt import gpt_prompt_company_list
from prompts.company_page_prompt import gpt_prompt_company_details
from prompts.sector_name_prompt import gpt_prompt_sector_name


class CustomScraperService:
    """
        Service layer for scraping and registering custom websites (sectors).

        Responsibilities:
        - Validate sector templates and extract company links.
        - Use GPT to generate scraping templates and sector names.
        - Scrape test companies to ensure correctness of templates.
        - Save sector and templates to MongoDB.

        Attributes:
            gpt (GPTClient): Client for communicating with GPT model.
            fetcher (SeleniumFetcher): Utility for fetching HTML via Selenium.
            sectors_collection (Collection): MongoDB collection for sectors.
            templates_collection (Collection): MongoDB collection for templates.
        """
    def __init__(self, gpt_client, html_fetcher):
        """
        Initialize the scraping service.

        Args:
            gpt_client (GPTClient): GPT API client.
            html_fetcher (SeleniumFetcher): HTML fetcher for web pages.
        """
        self.gpt = gpt_client
        self.fetcher = html_fetcher
        self.sectors_collection, self.templates_collection, _ = get_collections()

    async def process_sector(self, url: str, user_id):
        """
        Main entry point for processing a new sector.

        Steps:
            1. Check if sector already exists.
            2. Fetch and validate sector HTML.
            3. Generate and validate sector/company templates.
            4. Extract and scrape test companies.
            5. Save sector and templates to MongoDB.

        Args:
            url (str): Sector page URL.
            user_id (str): ID of the user initiating scraping.

        Returns:
            tuple: (sector_id, test_data)
        """
        try:
            # 0. Checking if there is a sector in the database
            existing_sector = self._find_sector_by_url(url)
            if existing_sector:
                print(f"The {url} sector already exists in the database")
                # We add the user to the list if he is not there.
                self._add_user_to_sector(existing_sector["_id"], user_id)
                return str(existing_sector["_id"]), {}

            # 1. We get the html of the sector
            sector_html = self.fetcher.get_html(url, limit=True)
            if not sector_html:
                raise ValueError(f"Couldn't get the HTML sector from the link {url}")

            # 2. We send html to GPT and get a template for the list of companies.
            sector_template = await self.gpt.generate_template(html=sector_html, gpt_prompt=gpt_prompt_company_list)
            if not sector_template:
                raise TemplateNotFound("GPT did not return the sector template")

            # 3. Validating that the template is suitable (a list of companies has been found)
            companies_list = self._validate_sector_template(url, sector_template)
            if not companies_list:
                raise ValueError(f"No list of companies found in the {url} sector")
            print('A suitable structure of sector, we continue to work')

            # 4. We send html to GPT and get the sector name
            sector_name = await self.gpt.generate_sector_name(companies=companies_list, gpt_prompt=gpt_prompt_sector_name)
            if not sector_name:
                raise ValueError("GPT could not generate the sector name")

            # 5. We take 3 companies according to this template
            company_links = self._extract_company_links(companies_list)
            if not company_links:
                raise ValueError("Couldn't extract links to companies")

            # 6. We get the html of the first company
            company_html = self.fetcher.get_html(company_links[0], limit=False)
            if not company_html:
                raise ValueError(f"Couldn't get the company's HTML {company_links[0]}")

            # 7. We send html to GPT → generate a template for the company card
            company_template = await self.gpt.generate_template(html=company_html, gpt_prompt=gpt_prompt_company_details)
            if not company_template:
                raise TemplateNotFound("GPT did not return the template to the company")

            # 8. Scraping 3 companies for the test
            company_scraper = CompanyScraper(company_template['company_template'])
            test_data = company_scraper.scrape_companies(company_links)

            print('Получена информация о трех компаниях\n')
            for data in test_data:
                print(f'\n{data}\n')

            # 9. Saving the sector and templates in the database
            sector_id = self._save_to_db(
                url, user_id, company_template, sector_template, sector_name
            )

            return sector_id, test_data

        except PyMongoError as e:
            raise PyMongoError(f"Database error: {e}")
        except Exception as e:
            raise

    def _validate_sector_template(self, url, template):
        driver = None
        try:
            driver = setup_stealth_driver()
            sector_scraper = SectorScraper(driver, template)
            companies = sector_scraper.get_companies(url)

            print(f'Companies found {len(companies)}\n')
            for comp in companies:
                print('company', comp)

            if not companies:
                raise SectorNotFound(f"The {url} sector does not contain companies")

            if len(companies) <= 3:
                raise ScrapingServiceError(
                    f"The link to the sector {url} does not contain a sufficient number of companies (found {len(companies)})")

            return companies
        except Exception as e:
            raise ScrapingServiceError(f"Error in validating the sector template {url}: {e}")
        finally:
            if driver:
                driver.quit()

    def _extract_company_links(self, companies):
        try:
            urls = [company['url'] for company in companies[:3]]
            if not urls:
                raise ScrapingServiceError("Couldn't extract links to companies from the template")
            return urls
        except Exception as e:
            raise ScrapingServiceError(f"Error when extracting links to companies: {e}")

    def _save_to_db(self, url, user_id, comp_template, sector_template, sector_name):
        try:
            sector_doc = {
                'nimi': sector_name,
                'user_id': [user_id],
                'linkki': url,
                'status': 'pending'
            }
            sector_result = self.sectors_collection.insert_one(sector_doc)
            sector_id = sector_result.inserted_id

            template_doc = {
                'website_id': str(sector_id),
                **comp_template,
                **sector_template
            }
            self.templates_collection.insert_one(template_doc)
            print('\nThe new sector and its templates have been successfully added to the database\n')

            return str(sector_id)
        except PyMongoError as e:
            raise ScrapingServiceError(f"Error saving to the database: {e}")

    def _find_sector_by_url(self, url):
        sector = self.sectors_collection.find_one({"linkki": url})
        if not sector:
            return None
        return sector

    def _add_user_to_sector(self, sector_id, user_id):
        try:
            self.sectors_collection.update_one(
                {'_id': sector_id},
                {'$addToSet': {'user_id': user_id}}
            )
        except PyMongoError as e:
            raise ScrapingServiceError(f"Sector Update error {sector_id}: {e}")

