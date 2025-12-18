#  RubigramClient - Rubika API library for python
#  Copyright (C) 2025-present Javad <https://github.com/DevJavad>
#  Github - https://github.com/DevJavad/rubigram


from typing import Optional
import asyncio
import logging
import rubigram


logger = logging.getLogger(__name__)


class Request:
    """
    HTTP request handler with retry logic for Rubika API calls.

    This class provides a robust method for making HTTP requests to the
    Rubika Bot API with configurable retry behavior, exponential backoff,
    and error handling. It validates API responses and raises appropriate
    exceptions for failed requests.

    Note:
        This class is typically used as a mixin or extension to the
        Client class via monkey-patching or inheritance.

    Example:
    .. code-block:: python
        # Monkey-patch the client with request method
        client = Client(token="YOUR_BOT_TOKEN")
        client.request = Request.request.__get__(client, Client)

        # Use the request method
        response = await client.request(
            endpoint="sendMessage",
            payload={"chat_id": "b0123456789", "text": "Hello"}
        )
    """

    async def request(
        self: "rubigram.Client",
        endpoint: str,
        payload: dict,
        *,
        headers: Optional[dict] = None,
        proxy: Optional[str] = None,
        retries: Optional[int] = None,
        delay: Optional[float] = None,
        backoff: Optional[float] = None,
    ) -> dict:
        """
        Make an HTTP request to the Rubika API with retry logic.

        Parameters:
            endpoint (str):
                API endpoint name (e.g., "sendMessage", "getChats").
            payload (dict):
                Request payload to send as JSON.
            headers (Optional[dict], optional):
                Custom HTTP headers. If None, uses default headers.
                Defaults to None.
            proxy (Optional[str], optional):
                Proxy URL for this request. If None, uses client's proxy.
                Defaults to None.
            retries (Optional[int], optional):
                Number of retry attempts. If None, uses client's retries.
                Defaults to None.
            delay (Optional[float], optional):
                Initial delay between retries in seconds. If None, uses
                client's delay. Defaults to None.
            backoff (Optional[float], optional):
                Exponential backoff multiplier. If None, uses client's
                backoff. Defaults to None.

        Returns:
            dict: The "data" field from the API response if status is "OK".

        Raises:
            rubigram.errors.InvalidInput:
                When API returns status other than "OK" or missing data field.
            Exception:
                The last exception encountered after all retry attempts fail.

        Note:
            - Retries use exponential backoff: delay *= backoff each attempt
            - Only retries on HTTP errors or invalid API responses
            - Logs each attempt with debug level
            - Validates response structure: {"status": "OK", "data": {...}}

        Example:
        .. code-block:: python
            # Basic request
            response = await client.request(
                endpoint="getChats",
                payload={"sort": "Date"}
            )

            # Request with custom retry settings
            response = await client.request(
                endpoint="sendMessage",
                payload={"chat_id": "b0123456789", "text": "Hello"},
                retries=5,
                delay=2.0,
                backoff=1.5
            )

            # Request with proxy
            response = await client.request(
                endpoint="getUserInfo",
                payload={"user_id": "b0123456789"},
                proxy="http://proxy:8080"
            )
        """
        actual_proxy = proxy or self.proxy
        actual_retries = retries or self.retries
        actual_delay = delay or self.delay
        actual_backoff = backoff or self.backoff
        exception = None

        for attempt in range(1, actual_retries + 1):
            try:
                logger.debug(
                    "HTTP request, endpoint=%s, payload=%s, attempt=%s", endpoint, payload, attempt
                )
                url = self.api + endpoint
                async with self.http.session.post(
                    url, json=payload, headers=headers, proxy=actual_proxy
                ) as response:
                    response.raise_for_status()

                    data: dict = await response.json()
                    if data.get("status") == "OK" and data.get("data"):
                        return data["data"]
                    else:
                        raise rubigram.errors.InvalidInput(data)

            except Exception as error:
                exception = error
                logger.warning(
                    "HTTP Error, attempt=%s, error=%s", attempt, error
                )

        if attempt < actual_retries:
            await asyncio.sleep(actual_delay)
            actual_delay *= actual_backoff

        raise exception