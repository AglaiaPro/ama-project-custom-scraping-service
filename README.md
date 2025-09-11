# Custom Scraping Microservice

A microservice for dynamic scraping of custom websites using **FastAPI**, **Selenium**, and **OpenAI GPT**.  
It allows users to add new websites for scraping, confirm them, and delete them when necessary.  
Scraping templates are automatically generated with GPT and stored in MongoDB.

---

## Features

- Add a new custom website:
  - Fetch sector HTML.
  - GPT generates JSON template for company list.
  - Extract company links.
  - Generate template for company details.
  - Collect test data for 3 companies.
  - Save sector and templates to MongoDB.

- Confirm website:
  - Change sector status to `approved`.
  - Trigger main scraping process via another microservice.

- Delete website:
  - Delete sector and its templates from the database.
  - If multiple users are linked — only the current user’s access is removed.

---

## Project Structure

```
custom_scraping/
│── app/
│   │── exceptions.py        # Custom exceptions
│
│── api/
│   │── routers/
│       │── custom_website.py  # FastAPI endpoints
│
│── services/
│   │── custom_scraper_service.py
│   │── confirm_service.py
│   │── delete_service.py
│
│── scraping/
│   │── base_scraper.py
│   │── company_scraper.py
│   │── sector_scraper.py
│
│── clients/
│   │── driver_manager.py
│   │── fetch_html.py
│   │── gpt_client.py
│
│── database/
│   │── mongo_connection.py
│
│── prompts/
│   │── company_list_prompt.py
│   │── company_page_prompt.py
│   │── sector_name_prompt.py
│
│── config/
│   │── settings.py
│
│── main.py                  # FastAPI entry point
│── requirements.txt
```

---

## Installation & Run

### 1. Clone the repository
```bash
git clone https://github.com/your-repo/custom-scraping.git
cd custom-scraping
```

### 2. Install dependencies
Create a virtual environment and install packages:
```bash
pip install -r requirements.txt
```

### 3. Configure environment
In `config/settings.py` set the following:
- `MONGO_URI` — MongoDB connection string  
- `GPT_KEY` — OpenAI API key  
- `GPT_MODEL` — selected model (e.g., `gpt-4o`)  

### 4. Run service
```bash
uvicorn main:app --reload --port 8000
```

---

## API Endpoints

### 1. Create custom website (test scraping)
`POST /testcustomwebsite`

**Request:**
```json
{
  "url": "https://example.com/sector",
  "user_id": "12345"
}
```

**Response:**
```json
{
  "sector_id": "66e1f3d84b31b2...",
  "data": [
    {"name": "Company A", "url": "https://example.com/a"},
    {"name": "Company B", "url": "https://example.com/b"},
    {"name": "Company C", "url": "https://example.com/c"}
  ]
}
```

---

### 2. Confirm custom website
`POST /confirmcustomwebsite`

**Request:**
```json
{
  "sector_id": "66e1f3d84b31b2..."
}
```

**Response:**
```json
{
  "message": "Website confirmed and scraping started",
  "sector_id": "66e1f3d84b31b2...",
  "sector_url": "https://example.com/sector",
  "scraping_response": { "message": "Scraping started"}
}
```
~~~~
---
~~~~
### 3. Delete custom website
`DELETE /deletecustomwebsite`

**Request:**
```json
{
  "sector_id": "66e1f3d84b31b2...",
  "user_id": "12345"
}
```

**Response:**
```json
{
  "message": "Website 66e1f3d84b31b2... and related templates deleted for user 12345"
}
```

---

## Tech Stack

- **FastAPI** — REST API
- **Selenium + selenium-stealth** — scraping with anti-bot bypass
- **BeautifulSoup4** — HTML cleaning
- **OpenAI GPT** — JSON template generation
- **MongoDB (pymongo)** — storage for sectors, templates, and companies
- **httpx** — async HTTP requests

---

## Notes

- GPT may return invalid JSON — handled in code.  
- Selenium runs in headless mode with randomized User-Agent and environment.  
- MongoDB connection is tested via `ping` in `mongo_connection.py`.  

---
