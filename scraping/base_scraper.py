# Common classes and interfaces
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


class BaseScraper:
    """
    Base class providing common scraping utilities.

    Responsibilities:
        - Translate selector type strings to Selenium By types.
        - Extract data from web elements, supporting attributes, text, and multiple elements.
    """
    @staticmethod
    def get_by_type(selector_type):
        """
        Convert a selector type string to Selenium's By type.

        Args:
            selector_type (str): Type of selector ('css' or 'xpath').

        Returns:
            selenium.webdriver.common.by.By: Corresponding Selenium By type.

        Raises:
            ValueError: If the selector type is unsupported.
        """
        if selector_type == "css":
            return By.CSS_SELECTOR
        elif selector_type == "xpath":
            return By.XPATH
        else:
            raise ValueError(f"Unsupported selector type: {selector_type}")

    def extract_field(self, driver_or_elem, field):
        """
        Extract a value from a web element using the provided field template.

        Args:
            driver_or_elem: Selenium WebDriver or WebElement to search in.
            field (dict): Field template containing keys:
                - 'type': selector type ('css'/'xpath'/'table')
                - 'value': selector string
                - 'attribute': optional attribute to extract
                - 'multiple': optional boolean, whether to return a list

        Returns:
            str | list[str] | None: Extracted value(s), or None if not found.
        """
        value = field['value']
        attribute = field['attribute']
        multiple = field.get("multiple", False)

        if not value or not isinstance(value, str):
            print(f"[WARN] Invalid or empty selector: {field}")
            return None

        try:
            by = self.get_by_type(field.get('type'))

            if multiple:
                # Extract multiple elements
                elements = driver_or_elem.find_elements(by, value)
                if attribute is None:
                    return [elem.text.strip() for elem in elements]
                else:
                    return [elem.get_attribute(attribute).strip() for elem in elements if elem.get_attribute(attribute)]
            else:
                # Extract single element
                element = driver_or_elem.find_element(by, value)
                if attribute is None:
                    return element.text.strip()
                else:
                    return element.get_attribute(attribute).strip()

        except NoSuchElementException:
            # Element not found
            return None
        except Exception as e:
            print(f'Error extracting value for selector {field}: {e}')
            return None
