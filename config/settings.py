import os

GPT_KEY = os.getenv("OPENAI_KEY")
MONGO_URI = os.getenv("MONGO_URI")
GPT_MODEL = "gpt-4o"

SCRAPING_SERVICE_URL = os.getenv("SCRAPING_SERVICE_URL", "http://scraping-service:8001")