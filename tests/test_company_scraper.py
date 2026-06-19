import asyncio
import threading

import scraping.company_scraper as company_scraper_module
from scraping.company_scraper import CompanyScraper


def _disable_human_delay(monkeypatch):
    monkeypatch.setattr(company_scraper_module.random, "uniform", lambda *_: 0)
    monkeypatch.setattr(company_scraper_module.time, "sleep", lambda _: None)


def test_scrape_companies_runs_company_pages_in_parallel(monkeypatch):
    state = {"active": 0, "max_active": 0, "quit_count": 0}
    lock = threading.Lock()

    class FakeDriver:
        def get(self, url):
            with lock:
                state["active"] += 1
                state["max_active"] = max(state["max_active"], state["active"])
            try:
                threading.Event().wait(0.05)
            finally:
                with lock:
                    state["active"] -= 1

        def quit(self):
            state["quit_count"] += 1

    monkeypatch.setattr(company_scraper_module, "setup_stealth_driver", lambda: FakeDriver())
    _disable_human_delay(monkeypatch)

    scraper = CompanyScraper({"fields": {}}, max_concurrency=3)
    results = asyncio.run(scraper.scrape_companies(["url-1", "url-2", "url-3"]))

    assert [result["url"] for result in results] == ["url-1", "url-2", "url-3"]
    assert state["max_active"] > 1
    assert state["quit_count"] == 3


def test_scrape_companies_respects_concurrency_limit(monkeypatch):
    state = {"active": 0, "max_active": 0}
    lock = threading.Lock()

    class FakeDriver:
        def get(self, url):
            with lock:
                state["active"] += 1
                state["max_active"] = max(state["max_active"], state["active"])
            try:
                threading.Event().wait(0.03)
            finally:
                with lock:
                    state["active"] -= 1

        def quit(self):
            pass

    monkeypatch.setattr(company_scraper_module, "setup_stealth_driver", lambda: FakeDriver())
    _disable_human_delay(monkeypatch)

    scraper = CompanyScraper({"fields": {}}, max_concurrency=2)
    results = asyncio.run(scraper.scrape_companies(["url-1", "url-2", "url-3", "url-4"]))

    assert len(results) == 4
    assert state["max_active"] == 2
