import asyncio
import copy
import json
from openai import OpenAI


class GPTClient:
    """
    OpenAI GPT client utilities for template and sector name generation.

    This module provides the `GPTClient` class for:
    - Generating scraping templates from HTML using GPT chat completions.
    - Generating sector names from a list of companies.
    - Handling JSON parsing and validating GPT responses.
    - Running GPT requests asynchronously in a thread-safe manner.

    Typical usage:
        from clients.gpt_client import GPTClient

        gpt_client = GPTClient(api_key="YOUR_API_KEY")
        template = await gpt_client.generate_template(html, gpt_prompt)
        sector_name = await gpt_client.generate_sector_name(companies, gpt_prompt)
    """
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    async def generate_template(self, html, gpt_prompt):
        prompt = copy.deepcopy(gpt_prompt)
        prompt["messages"][1]["content"] = prompt["messages"][1]["content"].replace(
            "[INSERT HTML HERE]", html
        )
        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=prompt["model"],
                messages=prompt["messages"],
                temperature=prompt.get("temperature"),
            )
        )
        raw_template = response.choices[0].message.content
        try:
            template = json.loads(raw_template)
        except json.JSONDecodeError as e:
            raise ValueError(f"GPT returned invalid JSON: {e}\nGPT response: {raw_template}")

        return template

    async def generate_sector_name(self, companies, gpt_prompt) -> str:
        prompt = copy.deepcopy(gpt_prompt)

        companies_str = json.dumps(companies, ensure_ascii=False, indent=2)

        prompt["messages"][1]["content"] = prompt["messages"][1]["content"].replace(
            "[COMPANY_LIST]", companies_str
        )
        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=prompt["model"],
                messages=prompt["messages"],
                temperature=prompt.get("temperature", 0.0),
            )
        )
        raw_name = response.choices[0].message.content
        sector_name = raw_name.strip().replace("\n", "").replace('"', "")
        if not sector_name:
            raise ValueError(f"GPT returned empty sector name. Full response: {response}")

        return sector_name
