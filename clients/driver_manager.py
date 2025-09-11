"""
Stealth Selenium WebDriver setup module.

This module provides utility functions to create and configure a Selenium
Chrome WebDriver instance with anti-detection features for web scraping.

Features:
- Generates random User-Agent, language, platform, and screen resolution.
- Configures Chrome options for headless mode and automation evasion.
- Uses selenium-stealth to further mask automation characteristics.
- Ready-to-use function: `setup_stealth_driver()` returns a stealth-configured WebDriver.

Typical usage:
    from clients.driver_manager import setup_stealth_driver

    driver = setup_stealth_driver()
    driver.get("https://example.com")
"""

import random
from selenium import webdriver
from selenium_stealth import stealth
from fake_useragent import UserAgent


def get_random_user_agent():
    ua = UserAgent()
    return ua.random


def get_random_languages():
    languages = ["en-US", "en", "ru", "fr", "de", "es", "zh", "ja"]
    return random.sample(languages, k=random.randint(1, 3))


def get_random_platform():
    platforms = ["Win32", "MacIntel", "Linux x86_64"]
    return random.choice(platforms)


def get_random_resolution():
    resolutions = ["1920x1080", "1366x768", "1440x900", "1600x900", "1280x720"]
    return random.choice(resolutions)


def setup_stealth_driver():
    options = webdriver.ChromeOptions()

    user_agent = get_random_user_agent()
    options.add_argument(f"user-agent={user_agent}")

    width, height = get_random_resolution().split("x")
    options.add_argument(f"--window-size={width},{height}")

    options.add_argument("--headless=new")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)

    stealth(driver,
            languages=get_random_languages(),
            vendor="Google Inc.",
            platform=get_random_platform(),
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGl Engine",
            fix_hairline=True,
            )
    return driver
