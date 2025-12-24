import time
import os

import requests
import logging
import asyncio

DEFAULT_RETRY_STATUS = {429, 500, 502, 503, 504}

# ------------------ LOGGER ------------------
def _get_logger(log_file=None):
    if os.getenv("PYQUICKTOOLS_LOG", "1") != "1":
        logger = logging.getLogger("pyquicktools.http")
        logger.addHandler(logging.NullHandler())
        return logger

    logger = logging.getLogger("pyquicktools.http")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = (
        logging.FileHandler(log_file)
        if log_file
        else logging.StreamHandler()
    )

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger



# ------------------ SYNC GET ------------------
def get(
    url,
    *,
    retries=3,
    timeout=5,
    backoff_factor=1,
    retry_statuses=DEFAULT_RETRY_STATUS,
    log_file=None,
    **kwargs,
):
    session = requests.Session()
    logger = _get_logger(log_file)
    last_exception = None

    for attempt in range(retries + 1):
        try:
            logger.info(f"GET attempt {attempt + 1} → {url}")
            response = session.get(url, timeout=timeout, **kwargs)

            if response.status_code in retry_statuses:
                raise requests.HTTPError(
                    f"Retryable status {response.status_code}",
                    response=response,
                )
            return response

        except requests.RequestException as e:
            last_exception = e
            logger.warning(f"GET failed: {e}")

            if attempt == retries:
                break
            time.sleep(backoff_factor * (2 ** attempt))

    raise last_exception


# ------------------ SYNC POST ------------------
def post(
    url,
    *,
    retries=3,
    timeout=5,
    backoff_factor=1,
    retry_statuses=DEFAULT_RETRY_STATUS,
    idempotency_key=None,
    log_file=None,
    **kwargs,
):
    session = requests.Session()
    logger = _get_logger(log_file)
    last_exception = None

    headers = kwargs.pop("headers", {})
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    else:
        retries = 0  #  unsafe POST → no retry

    for attempt in range(retries + 1):
        try:
            logger.info(f"POST attempt {attempt + 1} → {url}")
            response = session.post(
                url, timeout=timeout, headers=headers, **kwargs
            )

            if response.status_code in retry_statuses:
                raise requests.HTTPError(
                    f"Retryable status {response.status_code}",
                    response=response,
                )
            return response

        except requests.RequestException as e:
            last_exception = e
            logger.warning(f"POST failed: {e}")

            if attempt == retries:
                break
            time.sleep(backoff_factor * (2 ** attempt))

    raise last_exception


# ------------------ ASYNC GET ------------------
async def async_get(
    url,
    *,
    retries=3,
    timeout=5,
    backoff_factor=1,
    retry_statuses=DEFAULT_RETRY_STATUS,
    **kwargs,
):
    import aiohttp  # lazy import

    timeout_cfg = aiohttp.ClientTimeout(total=timeout)

    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
                async with session.get(url, **kwargs) as response:
                    if response.status in retry_statuses:
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                        )
                    return await response.json()

        except Exception:
            if attempt == retries:
                raise
            await asyncio.sleep(backoff_factor * (2 ** attempt))


# ------------------ ASYNC POST ------------------
async def async_post(
    url,
    *,
    retries=3,
    timeout=5,
    backoff_factor=1,
    retry_statuses=DEFAULT_RETRY_STATUS,
    idempotency_key=None,
    **kwargs,
):
    import aiohttp  # lazy import

    if not idempotency_key:
        retries = 0  #  unsafe async POST

    headers = kwargs.pop("headers", {})
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    timeout_cfg = aiohttp.ClientTimeout(total=timeout)

    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=timeout_cfg) as session:
                async with session.post(url, headers=headers, **kwargs) as response:
                    if response.status in retry_statuses:
                        raise aiohttp.ClientResponseError(
                            response.request_info,
                            response.history,
                            status=response.status,
                        )
                    return await response.json()

        except Exception:
            if attempt == retries:
                raise
            await asyncio.sleep(backoff_factor * (2 ** attempt))

