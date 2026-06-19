from pymongo.mongo_client import MongoClient
from pymongo.errors import PyMongoError

from config.settings import MONGO_URI


def get_mongo_client():
    if not MONGO_URI:
        raise PyMongoError("MONGO_URI environment variable is not configured")

    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def get_collections():
    try:
        cluster = get_mongo_client()
        db = cluster.automated_market_analysis

        cluster.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return db.business_sectors, db.scraping_templates, db.companies
    except Exception as e:
        raise PyMongoError(f"Could not connect to MongoDB: {e}") from e
