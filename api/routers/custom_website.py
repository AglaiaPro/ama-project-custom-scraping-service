from fastapi import HTTPException, APIRouter
from openai import OpenAIError, RateLimitError
from pymongo.errors import PyMongoError

from app.exceptions import SectorNotFound, TemplateNotFound, ScrapingServiceError
from schemas.custom_website import CustomWebsiteRequest, ConfirmWebsiteRequest, DeleteWebsiteRequest

from services.confirm_service import ConfirmScraperService
from services.delete_service import DeleteScraperService
from services.custom_scraper_service import CustomScraperService

from config.settings import GPT_KEY
from clients.gpt_client import GPTClient
from clients.fetch_html import SeleniumFetcher


router = APIRouter()


@router.post('/testcustomwebsite')
async def create_custom_website_test(data: CustomWebsiteRequest):
    """
    Creates a new custom website with the 'pending' status,
    generates a parsing template and returns test data (3 companies).

    Args:
    data (CustomWebsiteRequest): Request payload with URL and user_id.
    gpt_client (GPTClient): Dependency-injected GPT client.

    Returns:
        dict: {"sector_id": str, "data": list} containing test company data.
    """
    try:
        gpt_client = GPTClient(GPT_KEY)
        selenium_fetcher = SeleniumFetcher()
        try:
            custom_scraper = CustomScraperService(gpt_client, selenium_fetcher)
            sector_id, test_data = await custom_scraper.process_sector(data.url, data.user_id)
        finally:
            selenium_fetcher.close()

        return {
            "sector_id": sector_id,
            "data": test_data,
        }
    except SectorNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TemplateNotFound as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ScrapingServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=f"OpenAI quota or rate limit error: {e}")
    except OpenAIError as e:
        raise HTTPException(status_code=502, detail=f"OpenAI API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.post('/confirmcustomwebsite')
async def confirm_website(data: ConfirmWebsiteRequest):
    """
    Confirms the custom site:
    Changes the status in business_sectors to 'confirmed'
    Gets the website link
    Starts scraping through another microservice, the scraping service

    Args:
        data (ConfirmWebsiteRequest): Payload with sector_id.

    Returns:
        dict: Confirmation message, sector_id, sector_url, and scraping_response.
    """
    try:
        service = ConfirmScraperService()
        url = service.confirm_sector(data.sector_id)
        print('link found {} and status changed'.format(url))
        scraping_response = await service.start_scraping(url=url)

        return {
            'message': 'Website confirmed and scraping started',
            'sector_id': data.sector_id,
            'sector_url': url,
            'scraping_response': scraping_response
        }
    except SectorNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ScrapingServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unexpected error: {e}')


@router.delete('/deletecustomwebsite')
async def delete_website(data: DeleteWebsiteRequest):
    """
    Deletes a custom site:
    Deletes a sector in business_sectors by sector_id
    and the templates associated with it, where its id is listed.
    If there were several users, then we delete only the user's ID from this sector.

    Args:
        data (DeleteWebsiteRequest): Payload with sector_id and user_id.

    Returns:
        dict: Confirmation message.
    """
    try:
        service = DeleteScraperService()
        service.delete_sector(data.sector_id, data.user_id)

        return {
            'message': f'Website {data.sector_id} and related templates deleted for user {data.user_id}'
        }
    except SectorNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TemplateNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unexpected error: {e}')
