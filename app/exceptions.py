"""
Here we create custom exceptions to catch errors.
"""


class SectorNotFound(Exception):
    pass


class TemplateNotFound(Exception):
    pass


class ScrapingServiceError(Exception):
    pass
