# connecting to mongo db and getting collections
from pymongo.mongo_client import MongoClient
from config.settings import MONGO_URI


def get_mongo_client():
    return MongoClient(MONGO_URI)


def get_collections():
    try:
        cluster = get_mongo_client()
        db = cluster.automated_market_analysis

        cluster.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return db.business_sectors, db.scraping_templates, db.companies
    except Exception as e:
        print(e)
        return None
