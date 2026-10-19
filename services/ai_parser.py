import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Working models on this Groq account (in priority order)
MODELS_TO_TRY = [
    'openai/gpt-oss-20b',
    'openai/gpt-oss-120b',
    'qwen/qwen3.8-27b',
]

SYSTEM_PROMPT = """You are an expert financial transaction parser for Indian users.
Extract transaction details from the given text (SMS, quick note, or OCR text).
Respond with ONLY a valid JSON object — no extra text, no markdown, no backticks.

JSON must have exactly these keys:
- "description": short merchant/item name (e.g., "Zomato", "Uber", "Rent")
- "amount": number (e.g., 250.50)
- "category": one of [Food & Dining, Transport, Rent, Utilities, Entertainment, Health, Shopping, Education, Subscriptions, Groceries, Personal Care, Miscellaneous]
- "type": "expense" or "income"
"""


def parse_transaction_with_ai(text: str) -> dict:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in the environment.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    last_error = None
    for model in MODELS_TO_TRY:
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text[:4000]}
                ],
                "temperature": 0.1,
                "max_tokens": 200
            }

            response = requests.post(url, headers=headers, json=payload, timeout=20)

            if response.status_code != 200:
                last_error = f"Model {model}: {response.text[:200]}"
                print(f"[ai_parser] {last_error}")
                continue

            raw = response.json()['choices'][0]['message']['content'].strip()

            # Extract JSON even if model wrapped it in markdown
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                raw = json_match.group(0)

            return json.loads(raw)

        except json.JSONDecodeError as e:
            last_error = f"Model {model} returned invalid JSON: {e}"
            print(f"[ai_parser] {last_error}")
        except Exception as e:
            last_error = str(e)
            print(f"[ai_parser] Error with {model}: {last_error}")

    raise ValueError(f"All AI models failed. Last error: {last_error}")
