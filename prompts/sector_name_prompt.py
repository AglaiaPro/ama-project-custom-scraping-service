# a prompt for the GPT API
# we send a list of companies based on which we get the name of the sector
from config.settings import GPT_MODEL

gpt_prompt_sector_name = {
  "model": GPT_MODEL,
  "messages": [
    {
      "role": "system",
      "content": (
        "You are an expert in company classification. "
        "Your ONLY task is to output a sector name that best describes the provided companies. "
        "Do not include explanations, comments, markdown, or any extra text. "
        "The response must contain ONLY the sector name."
      )
    },
    {
      "role": "user",
      "content": (
        "Here is the list of companies:\n\n[COMPANY_LIST]\n\n"
        "Generate ONLY the sector name they belong to. Nothing else."
      )
    }
  ],
  "temperature": 0.0
}