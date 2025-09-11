from bson import ObjectId
from app.exceptions import SectorNotFound, TemplateNotFound
from database.mongo_connection import get_collections


class DeleteScraperService:
    """
    Service layer for deleting sectors, their templates, and associated companies.

    Responsibilities:
    - Delete a sector entirely if only one user is associated with it.
    - Remove a user's access to a sector if multiple users are associated.
    - Clean up related templates and companies in the database.

    Attributes:
        sectors_collection (Collection): MongoDB collection for sectors.
        templates_collection (Collection): MongoDB collection for templates.
        companies_collection (Collection): MongoDB collection for companies.
    """
    def __init__(self):
        """
        Initialize the service and get MongoDB collections.
        """
        self.sectors_collection, self.templates_collection, self.companies_collection = get_collections()

    def delete_sector(self, sector_id: str, user_id: str):
        """
        Delete a sector or remove a user's access to it.

        Steps:
            1. Fetch the sector by ID.
            2. Raise exception if the sector does not exist.
            3. If multiple users are associated:
                - Remove only the specified user_id from the sector.
            4. If only one user is associated:
                - Delete the sector.
                - Delete all associated templates.
                - Delete all associated companies.
            5. Log or raise exceptions if deletion fails.

        Args:
            sector_id (str): ID of the sector to delete.
            user_id (str): ID of the user requesting deletion.

        Raises:
            SectorNotFound: If the sector does not exist or the user is not part of it.
            TemplateNotFound: If no templates are found for the sector.
        """
        # Fetch the sector from the database
        sector = self.sectors_collection.find_one({'_id': ObjectId(sector_id)})
        if not sector:
            raise SectorNotFound(f"Sector {sector_id} not found")

        user_ids = sector.get('user_id', [])
        if len(user_ids) > 1:
            # If multiple users are associated, remove only this user from the sector
            update_result = self.sectors_collection.update_one(
                {'_id': ObjectId(sector_id)},
                {'$pull': {'user_id': user_id}}
            )
            if update_result.modified_count == 0:
                # User was not in the sector
                raise SectorNotFound(f"User {user_id} not found in sector {sector_id}")
        else:
            # If only one user, delete the sector entirely
            sector_result = self.sectors_collection.delete_one({'_id': ObjectId(sector_id)})
            if sector_result.deleted_count == 0:
                raise SectorNotFound(f"Sector {sector_id} not found")

            # Delete associated templates
            template_result = self.templates_collection.delete_one({'website_id': sector_id})
            if template_result.deleted_count == 0:
                raise TemplateNotFound(f"No templates found for sector {sector_id}")

            # Delete associated companies
            companies_result = self.companies_collection.delete_many({'sector_id': sector_id})
            if companies_result.deleted_count == 0:
                print(f"No companies found for sector {sector_id}")
