# prompt for gpt template request for subsequent scraping of the list of companies
from config.settings import GPT_MODEL

gpt_prompt_company_list = {
  "model": GPT_MODEL,
  "messages": [
    {
      "role": "system",
      "content": (
        "You are an expert in HTML parsing and web data extraction. "
        "Your ONLY task is to output a valid JSON object for scraping. "
        "Do not include explanations, comments, markdown code blocks, or any extra text. "
        "The response must be a pure JSON object."
      )
    },
    {
      "role": "user",
      "content": (
        "Here is the HTML of the page with the list of companies:\n\n[INSERT HTML HERE]\n\n"
        "Generate a JSON template that strictly follows this schema:\n\n"
        "{\n"
        "  \"page_companies_template\": {\n"
        "    \"type\": \"companies_list\",\n"
        "    \"fields\": {\n"
        "      \"name\": {\n"
        "        \"type\": \"css\" or \"xpath\",\n"
        "        \"value\": \"selector string\",\n"
        "        \"attribute\": \"attribute name (e.g., href) or null\"\n"
        "      },\n"
        "      \"url\": {\n"
        "        \"type\": \"css\" or \"xpath\",\n"
        "        \"value\": \"selector string or null\",\n"
        "        \"attribute\": \"attribute name (e.g., href) or null\"\n"
        "      },\n"
        "      \"next_page_selector\": {\n"
        "        \"type\": \"css\" or \"xpath\",\n"
        "        \"value\": \"selector string\",\n"
        "        \"attribute\": \"attribute name (e.g., href) or null\"\n"
        "      }\n"
        "    },\n"
        "    \"company_selector\": {\n"
        "      \"type\": \"css\" or \"xpath\",\n"
        "      \"value\": \"selector string for one company block\"\n"
        "    }\n"
        "  }\n"
        "}\n\n"
        "⚠️ RULES:\n"
        "1. Output ONLY valid JSON (no markdown, no ```json, no text outside braces).\n"
        "2. Do not add comments.\n"
        "3. Do not change field names.\n"
        "4. If unsure about a selector, guess the most likely one but still return valid JSON."
      )
    }
  ],
  "temperature": 1
}
