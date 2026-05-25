"""OpenAI API utilities"""
import os
import time
import logging
from typing import Optional
import openai
import httpx
from json import JSONDecodeError

logger = logging.getLogger(__name__)

# Error messages that indicate a transient failure worth retrying
_TRANSIENT_PATTERNS = [
    "Expecting value",          # JSONDecodeError from malformed response
    "Server Error",             # 5xx errors
    "Service Unavailable",
    "Too Many Requests",        # 429 rate limit
    "Connection error",
    "Read timed out",
    "Remote end closed connection",
    "Internal Server Error",
    "Bad Gateway",
    "Gateway Timeout",
    "upstream error",
]

_MAX_RETRIES = 3
_BASE_DELAY = 2  # seconds


def _is_transient_error(error: Exception) -> bool:
    """Check if an error is transient and worth retrying."""
    error_str = str(error)
    for pattern in _TRANSIENT_PATTERNS:
        if pattern.lower() in error_str.lower():
            return True
    if isinstance(error, (httpx.HTTPStatusError, httpx.ConnectError,
                           httpx.ReadTimeout, httpx.RemoteProtocolError,
                           JSONDecodeError)):
        return True
    return False


def openai_completion(
    prompt: str,
    args: 'OpenAIDecodingArguments',
    model_name: str = "deepseek/deepseek-v4-pro",
    provider: str = "openai",
    system_prompt: Optional[str] = None
) -> str:
    """Get completion from OpenAI API with retry logic for transient errors."""
    if provider == "openai":
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    elif provider == "groq":
        client = openai.OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
    elif provider == "openrouter":
        client = openai.OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Build kwargs once (same for all retries)
    completion_kwargs = {k: v for k, v in vars(args).items() if v is not None}

    if provider == "openai":
        if "max_tokens" in completion_kwargs:
            completion_kwargs["max_completion_tokens"] = completion_kwargs.pop("max_tokens")
    else:
        if "max_completion_tokens" in completion_kwargs and "max_tokens" not in completion_kwargs:
            completion_kwargs["max_tokens"] = completion_kwargs.pop("max_completion_tokens")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    last_error = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                **completion_kwargs
            )
            content = response.choices[0].message.content

            # Debug logging
            logger.debug(f"API Response - Model: {response.model}")
            logger.debug(f"API Response - Finish reason: {response.choices[0].finish_reason}")
            logger.debug(f"API Response - Content length: {len(content) if content else 0}")
            logger.debug(f"API Response - Content preview: {repr(content[:200]) if content else 'None'}")
            if hasattr(response, 'usage'):
                logger.debug(f"API Response - Token usage: {response.usage}")

            return content

        except Exception as e:
            last_error = e
            if attempt < _MAX_RETRIES and _is_transient_error(e):
                delay = _BASE_DELAY * (2 ** attempt)
                logger.warning(
                    f"Transient error on attempt {attempt + 1}/{_MAX_RETRIES + 1} "
                    f"(model={model_name}): {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"Error in OpenAI completion (attempt {attempt + 1}): {e}")
                raise
