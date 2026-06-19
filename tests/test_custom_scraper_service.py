import asyncio

import services.custom_scraper_service as custom_service_module
from services.custom_scraper_service import CustomScraperService


class FakeCollection:
    def __init__(self, found_document=None, documents=None):
        self.found_document = found_document
        self.documents = documents or {}
        self.updated = []

    def find_one(self, query):
        if "website_id" in query:
            return self.documents.get(query["website_id"])
        return self.found_document

    def update_one(self, query, update):
        self.updated.append((query, update))


def test_process_sector_rescrapes_existing_sector_with_saved_template(monkeypatch):
    sectors_collection = FakeCollection({"_id": "sector-1", "linkki": "https://example.com"})
    templates_collection = FakeCollection(
        documents={
            "sector-1": {
                "website_id": "sector-1",
                "page_companies_template": {"fields": {}, "company_selector": {}},
                "company_template": {"fields": {}},
            }
        }
    )

    class FakeCompanyScraper:
        def __init__(self, template, max_concurrency):
            self.template = template
            self.max_concurrency = max_concurrency

        async def scrape_companies(self, links):
            return [{"url": link, "name": f"Company {index}"} for index, link in enumerate(links, start=1)]

    monkeypatch.setattr(custom_service_module, "CompanyScraper", FakeCompanyScraper)

    service = CustomScraperService(
        gpt_client=object(),
        html_fetcher=object(),
        collections=(sectors_collection, templates_collection, object()),
    )
    monkeypatch.setattr(
        service,
        "_validate_sector_template",
        lambda url, template: [
            {"url": "https://example.com/1"},
            {"url": "https://example.com/2"},
            {"url": "https://example.com/3"},
        ],
    )

    sector_id, test_data = asyncio.run(service.process_sector("https://example.com", "user-1"))

    assert sector_id == "sector-1"
    assert test_data == [
        {"url": "https://example.com/1", "name": "Company 1"},
        {"url": "https://example.com/2", "name": "Company 2"},
        {"url": "https://example.com/3", "name": "Company 3"},
    ]
    assert sectors_collection.updated == [
        ({"_id": "sector-1"}, {"$addToSet": {"user_id": "user-1"}})
    ]


def test_extract_company_links_uses_configured_test_limit(monkeypatch):
    monkeypatch.setattr(custom_service_module, "TEST_COMPANY_LIMIT", 2)
    service = CustomScraperService(
        gpt_client=object(),
        html_fetcher=object(),
        collections=(object(), object(), object()),
    )

    links = service._extract_company_links(
        [
            {"url": "https://example.com/1"},
            {"url": "https://example.com/2"},
            {"url": "https://example.com/3"},
        ]
    )

    assert links == ["https://example.com/1", "https://example.com/2"]
