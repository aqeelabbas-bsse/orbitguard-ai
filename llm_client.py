"""
LLM client for watsonx.ai — used by the investigator and recommendation agents.

Loads credentials from a local .env file (never commit this file — it's
already covered in .gitignore). Handles the IBM Cloud IAM token exchange
and caches the short-lived access token so you're not re-authenticating on
every single agent call.
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

WATSONX_API_KEY = os.environ.get("WATSONX_API_KEY", "")
WATSONX_PROJECT_ID = os.environ.get("WATSONX_PROJECT_ID", "")
WATSONX_URL = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_MODEL_ID = os.environ.get("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

_cached_token = None
_cached_token_expiry = 0


def _get_access_token() -> str:
    """Exchange the IBM Cloud API key for a short-lived bearer token, cached
    until shortly before it expires."""
    global _cached_token, _cached_token_expiry

    if _cached_token and time.time() < _cached_token_expiry - 60:
        return _cached_token

    resp = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": WATSONX_API_KEY,
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    _cached_token = data["access_token"]
    _cached_token_expiry = time.time() + data.get("expires_in", 3600)
    return _cached_token


def call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        raise EnvironmentError(
            "WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in your "
            ".env file. See BUILD_GUIDE.md Phase 2 setup."
        )

    token = _get_access_token()

    max_retries = 5
    for attempt in range(1, max_retries + 1):
        resp = requests.post(
            f"{WATSONX_URL}/ml/v1/text/chat?version=2024-05-01",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "model_id": WATSONX_MODEL_ID,
                "project_id": WATSONX_PROJECT_ID,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": max_tokens,
            },
            timeout=60,
        )

        if resp.status_code == 429:
            # Free-tier rate limit hit. Honor Retry-After if the server
            # sends one, otherwise back off with increasing wait times.
            retry_after = resp.headers.get("Retry-After")
            wait_s = int(retry_after) if retry_after else min(10 * attempt, 60)
            print(f"[llm_client] Rate limited (429). Waiting {wait_s}s "
                  f"before retry {attempt}/{max_retries}...")
            time.sleep(wait_s)
            continue

        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    raise RuntimeError(
        f"Still rate-limited after {max_retries} retries. "
        "Wait a few minutes before re-running, or reduce "
        "MAX_EVENTS_TO_INVESTIGATE in main_phase2.py / main_phase4.py."
    )


if __name__ == "__main__":
    # Quick smoke test — confirms your .env credentials actually work
    # before you run the full Phase 2 pipeline on top of them.
    reply = call_llm(
        "You are a helpful assistant.",
        "Reply with exactly the word: OK",
    )
    print(f"[llm_client] Smoke test response: {reply}")