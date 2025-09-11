# template for requesting the GPT API to create a scraping template for one company (company_template)
from config.settings import GPT_MODEL

gpt_prompt_company_details = {
  "model": 'gpt-5-mini',
  "temperature": 1,
  "messages": [
    {
      "role": "system",
      "content": (
        "You are an expert in HTML parsing and web data extraction. "
        "Your ONLY task is to output a valid JSON object with CSS or XPath selectors for scraping. "
        "The output must be directly usable in Selenium WebDriver with Python. "
        "⚠️ Forbidden syntax: ':contains', ':has', ':nth-child', jQuery-like pseudo-selectors, or any non-standard CSS. "
        "If you need to filter by text → use XPath with contains(text(), ...). "
        "Always ensure the selectors are unique and valid for Selenium. "
        "Do not include explanations, comments, markdown code blocks, or any extra text. "
        "The response must be a pure JSON object."
      )
    },
    {
      "role": "user",
      "content": (
        "Here is the HTML of the company page:\n\n[INSERT HTML HERE]\n\n"
        "Generate a JSON scraping template following these strict rules:\n\n"
        "{\n"
        "  \"company_template\": {\n"
        "    \"type\": \"company_details\",\n"
        "    \"fields\": {\n"
        "      \"<field_name>\": {\n"
        "        \"type\": \"css\" | \"xpath\" | \"table\",\n"
        "        \"value\": \"unique selector string or null\",\n"
        "        \"attribute\": \"attribute name or null\",\n"
        "        \"multiple\": true/false\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n\n"
        "⚠️ STRICT RULES:\n"
        "1. Output ONLY valid JSON.\n"
        "2. Each field must have keys: \"type\", \"value\", \"attribute\", \"multiple\".\n"
        "3. Each field must use a UNIQUE selector (combination of type + value + attribute).\n"
        "4. NEVER use ':contains' or any non-standard CSS selector. INVALID: div:contains(\"text\").\n"
        "5. If you must match text, use XPath. VALID: //div[contains(text(), \"text\")].\n"
        "6. Use CSS only for id, class, attributes, or structural selectors supported by Selenium.\n"
        "7. If the field is a table, use {\"type\": \"table\", \"fields\": {...}} with unique selectors for columns.\n"
        "8. Use 'multiple': true only for lists or repeating elements.\n"
        "9. Do not include fields not present in the HTML.\n"
        "10. Do not return empty or null-only fields.\n"
        "11. Field names must reflect semantic meaning (e.g., name, phone_number, address, website, year_founded, company_type, about_company, financials).\n"
        "12. Ensure all selectors are directly usable in Selenium without modification.\n"
      )
    }
  ]
}
