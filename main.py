"""
Main entry point for the FastAPI application.
Here we initialize the app and include all API routers.
"""
from fastapi import FastAPI
from api.routers import custom_website

app = FastAPI()
# Connect a router with endpoints to work with custom sites
app.include_router(custom_website.router)
