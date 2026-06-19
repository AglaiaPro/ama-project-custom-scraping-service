import asyncio

from pymongo.errors import PyMongoError

from app.exceptions import TemplateNotFound, SectorNotFound, ScrapingServiceError
from clients.driver_manager import setup_stealth_driver
from config.settings import COMPANY_SCRAPE_CONCURRENCY, TEST_COMPANY_LIMIT
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
    def __init__(self, gpt_client, html_fetcher, collections=None):
        """
        Initialize the scraping service.

        Args:
            gpt_client (GPTClient): GPT API client.
            html_fetcher (SeleniumFetcher): HTML fetcher for web pages.
        """
        self.gpt = gpt_client
        self.fetcher = html_fetcher
        collections = collections or get_collections()
        self.sectors_collection, self.templates_collection, _ = collections

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
            existing_sector = await asyncio.to_thread(self._find_sector_by_url, url)
            if existing_sector:
                print(f"The {url} sector already exists in the database")
                await asyncio.to_thread(self._add_user_to_sector, existing_sector["_id"], user_id)
                test_data = await self._scrape_existing_sector_test_data(url, existing_sector["_id"])
                return str(existing_sector["_id"]), test_data

            sector_html = await asyncio.to_thread(self.fetcher.get_html, url, True)
            if not sector_html:
                raise ValueError(f"Couldn't get the HTML sector from the link {url}")

            sector_template = await self.gpt.generate_template(html=sector_html, gpt_prompt=gpt_prompt_company_list)
            if not sector_template:
                raise TemplateNotFound("GPT did not return the sector template")

            companies_list = await asyncio.to_thread(self._validate_sector_template, url, sector_template)
            if not companies_list:
                raise ValueError(f"No list of companies found in the {url} sector")
            print('A suitable structure of sector, we continue to work')

            sector_name = await self.gpt.generate_sector_name(companies=companies_list, gpt_prompt=gpt_prompt_sector_name)
            if not sector_name:
                raise ValueError("GPT could not generate the sector name")

            company_links = self._extract_company_links(companies_list)
            if not company_links:
                raise ValueError("Couldn't extract links to companies")

            company_html = await asyncio.to_thread(self.fetcher.get_html, company_links[0], False)
            if not company_html:
                raise ValueError(f"Couldn't get the company's HTML {company_links[0]}")

            company_template = await self.gpt.generate_template(html=company_html, gpt_prompt=gpt_prompt_company_details)
            if not company_template:
                raise TemplateNotFound("GPT did not return the template to the company")

            company_scraper = CompanyScraper(
                company_template['company_template'],
                max_concurrency=COMPANY_SCRAPE_CONCURRENCY,
            )
            test_data = await company_scraper.scrape_companies(company_links)

            print(f'Получена информация о {len(test_data)} компаниях\n')
            for data in test_data:
                print(f'\n{data}\n')

            sector_id = await asyncio.to_thread(
                self._save_to_db,
                url,
                user_id,
                company_template,
                sector_template,
                sector_name,
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

            if len(companies) < TEST_COMPANY_LIMIT:
                raise ScrapingServiceError(
                    f"The link to the sector {url} does not contain a sufficient number of companies "
                    f"(found {len(companies)}, required {TEST_COMPANY_LIMIT})"
                )

            return companies
        except Exception as e:
            raise ScrapingServiceError(f"Error in validating the sector template {url}: {e}")
        finally:
            if driver:
                driver.quit()

    def _extract_company_links(self, companies):
        try:
            urls = [company['url'] for company in companies[:TEST_COMPANY_LIMIT]]
            if not urls:
                raise ScrapingServiceError("Couldn't extract links to companies from the template")
            return urls
        except Exception as e:
            raise ScrapingServiceError(f"Error when extracting links to companies: {e}")

    async def _scrape_existing_sector_test_data(self, url, sector_id):
        template = await asyncio.to_thread(self._find_template_by_sector_id, str(sector_id))
        if not template:
            raise TemplateNotFound(f"Sector {sector_id} exists, but its scraping template was not found")

        if "page_companies_template" not in template or "company_template" not in template:
            raise TemplateNotFound(f"Sector {sector_id} has an incomplete scraping template")

        companies_list = await asyncio.to_thread(self._validate_sector_template, url, template)
        company_links = self._extract_company_links(companies_list)
        company_scraper = CompanyScraper(
            template["company_template"],
            max_concurrency=COMPANY_SCRAPE_CONCURRENCY,
        )
        return await company_scraper.scrape_companies(company_links)

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

    def _find_template_by_sector_id(self, sector_id):
        return self.templates_collection.find_one({"website_id": str(sector_id)})

    def _add_user_to_sector(self, sector_id, user_id):
        try:
            self.sectors_collection.update_one(
                {'_id': sector_id},
                {'$addToSet': {'user_id': user_id}}
            )
        except PyMongoError as e:
            raise ScrapingServiceError(f"Sector Update error {sector_id}: {e}")

