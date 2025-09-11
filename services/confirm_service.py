import httpx
from bson import ObjectId
from pymongo.errors import PyMongoError
from app.exceptions import SectorNotFound, ScrapingServiceError
from config.settings import SCRAPING_SERVICE_URL
from database.mongo_connection import get_collections


class ConfirmScraperService:
    """
    Service layer for confirming sectors and triggering scraping.

    Responsibilities:
    - Confirm a sector in the database by setting its status to 'approved'.
    - Trigger the first scraping process via an external scraping service.

    Attributes:
        sectors_collection (Collection): MongoDB collection for sectors.
    """
    def __init__(self):
        """
        Initialize the service and get MongoDB collections.
        """
        self.sectors_collection, _, _ = get_collections()

    def confirm_sector(self, sector_id: str):
        """
        Confirm a sector by updating its status to 'approved'.

        Steps:
            1. Fetch the sector from the database.
            2. Raise exception if the sector is not found.
            3. Update the sector's status in MongoDB.

        Args:
            sector_id (str): ID of the sector to confirm.

        Returns:
            str: The link of the confirmed sector.

        Raises:
            PyMongoError: If there is a database error.
            SectorNotFound: If the sector does not exist.
        """
        try:
            # Try to fetch the sector by its ObjectId
            sector = self.sectors_collection.find_one({'_id': ObjectId(sector_id)})
        except PyMongoError as e:
            raise PyMongoError(f"Database error: {e}")
        if not sector:
            # Raise custom exception if sector does not exist
            raise SectorNotFound(f"Sector with id {sector_id} not found")

        # Update the status to 'approved'
        self.sectors_collection.update_one(
            {'_id': ObjectId(sector_id)},
            {'$set': {'status': 'approved'}}
        )
        # Return the sector link for further processing
        return sector.get('linkki')

    async def start_scraping(self, url: str):
        """
        Trigger scraping process via external scraping service.

        Steps:
            1. Send a POST request to the scraping-service.
            2. Raise custom exceptions on connection or HTTP errors.

        Args:
            url (str): URL of the sector to scrape.

        Returns:
            dict: JSON response from the scraping service.

        Raises:
            ScrapingServiceError: If the service is unreachable or returns an error.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SCRAPING_SERVICE_URL}/firstcustomscraping",
                    json={'link': url}
                )
                # Raise error if HTTP response code indicates failure
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            # Raised when connection to the scraping service fails
            raise ScrapingServiceError(f"Could not connect to scraping-service: {e}")
        except httpx.HTTPStatusError as e:
            raise ScrapingServiceError(f"Scraping-service returned error: {e.response.text}")
