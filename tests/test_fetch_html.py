import clients.fetch_html as fetch_html_module
from clients.fetch_html import SeleniumFetcher


def test_selenium_fetcher_creates_driver_lazily_and_closes_it(monkeypatch):
    created_drivers = []

    class FakeDriver:
        page_source = """
        <html>
          <body>
            <script>window.bad = true</script>
            <p>Hello company</p>
          </body>
        </html>
        """

        def __init__(self):
            self.visited_url = None
            self.quit_called = False

        def get(self, url):
            self.visited_url = url

        def quit(self):
            self.quit_called = True

    def driver_factory():
        driver = FakeDriver()
        created_drivers.append(driver)
        return driver

    monkeypatch.setattr(fetch_html_module.time, "sleep", lambda _: None)

    fetcher = SeleniumFetcher(driver_factory=driver_factory)

    assert created_drivers == []

    html = fetcher.get_html("https://example.com", limit=False)

    assert len(created_drivers) == 1
    assert created_drivers[0].visited_url == "https://example.com"
    assert "Hello company" in html
    assert "window.bad" not in html

    fetcher.close()

    assert created_drivers[0].quit_called is True
    assert fetcher.driver is None
