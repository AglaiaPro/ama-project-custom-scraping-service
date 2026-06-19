import os

GPT_KEY = os.getenv("OPENAI_KEY") or os.getenv("GPT_KEY")
MONGO_URI = os.getenv("MONGO_URI")
GPT_MODEL = "gpt-4o"

SCRAPING_SERVICE_URL = os.getenv("SCRAPING_SERVICE_URL", "http://scraping-service:8001")


def _get_positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        return default

    return value if value > 0 else default


TEST_COMPANY_LIMIT = _get_positive_int_env("TEST_COMPANY_LIMIT", 3)
COMPANY_SCRAPE_CONCURRENCY = _get_positive_int_env(
    "COMPANY_SCRAPE_CONCURRENCY",
    TEST_COMPANY_LIMIT,
)
