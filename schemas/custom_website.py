from pydantic import BaseModel


class CustomWebsiteRequest(BaseModel):
    """
    Request model for creating a custom website (sector) for scraping.

    Endpoint:
        POST /testcustomwebsite

    Attributes:
        url (str): URL of the sector page to be scraped.
        user_id (str): ID of the user requesting the creation.
    """
    url: str
    user_id: str

class ConfirmWebsiteRequest(BaseModel):
    """
    Request model for confirming an existing sector (approving it for scraping).

    Endpoint:
        POST /confirmcustomwebsite

    Attributes:
        sector_id (str): ID of the sector to confirm.
    """
    sector_id: str

class DeleteWebsiteRequest(BaseModel):
    """
    Request model for deleting a sector or removing a user's access.

    Endpoint:
        DELETE /deletecustomwebsite

    Attributes:
        sector_id (str): ID of the sector to delete.
        user_id (str): ID of the user requesting deletion.
    """
    sector_id: str
    user_id: str
