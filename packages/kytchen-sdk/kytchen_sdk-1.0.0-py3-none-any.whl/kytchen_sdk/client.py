"""Kytchen client for Python."""

from __future__ import annotations

from typing import Any, AsyncIterator

import httpx

from .datasets import Datasets
from .keys import Keys
from .errors import AuthenticationError, KytchenError, NotFoundError, RateLimitError
from .types import Budget, Evidence, QueryResult, RunEvent


class KytchenClient:
    """Async client for the Kytchen API.

    Example:
        ```python
        import asyncio
        from kytchen_sdk import KytchenClient

        async def main():
            client = KytchenClient(api_key="kyt_sk_...")

            # Upload a dataset
            dataset = await client.datasets.create("my-data", "data.txt")

            # Query the dataset
            result = await client.query(
                query="What is the main topic?",
                dataset_ids=[dataset.id],
            )
            print(result.answer)

        asyncio.run(main())
        ```
    """

    DEFAULT_BASE_URL = "https://api.kytchen.dev"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize the Kytchen client.

        Args:
            api_key: Your Kytchen API key (starts with kyt_sk_)
            base_url: Optional custom API base URL
            timeout: Request timeout in seconds (default: 60)
        """
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "kytchen-python/0.1.0",
            },
        )

        self.datasets = Datasets(self)
        self.keys = Keys(self)

    async def __aenter__(self) -> KytchenClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

    async def query(
        self,
        query: str,
        dataset_ids: list[str],
        *,
        budget: Budget | None = None,
        provider: str | None = None,
        model: str | None = None,
        provider_api_key: str | None = None,
    ) -> QueryResult:
        """Execute a query against one or more datasets.

        Args:
            query: The question to ask
            dataset_ids: List of dataset IDs to query
            budget: Optional resource budget constraints
            provider: LLM provider (anthropic, openai)
            model: Model name
            provider_api_key: API key for the LLM provider (BYOLLM)

        Returns:
            Query result with answer and evidence
        """
        payload: dict[str, Any] = {
            "query": query,
            "dataset_ids": dataset_ids,
        }

        if budget:
            payload["budget"] = budget.to_dict()
        if provider:
            payload["provider"] = provider
        if model:
            payload["model"] = model
        if provider_api_key:
            payload["provider_api_key"] = provider_api_key

        data = await self._request("POST", "/v1/query", json=payload)
        return self._parse_query_result(data)

    async def query_stream(
        self,
        query: str,
        dataset_ids: list[str],
        *,
        budget: Budget | None = None,
        provider: str | None = None,
        model: str | None = None,
        provider_api_key: str | None = None,
    ) -> AsyncIterator[RunEvent]:
        """Execute a query with streaming events.

        Args:
            query: The question to ask
            dataset_ids: List of dataset IDs to query
            budget: Optional resource budget constraints
            provider: LLM provider (anthropic, openai)
            model: Model name
            provider_api_key: API key for the LLM provider (BYOLLM)

        Yields:
            RunEvent objects as the query progresses
        """
        payload: dict[str, Any] = {
            "query": query,
            "dataset_ids": dataset_ids,
        }

        if budget:
            payload["budget"] = budget.to_dict()
        if provider:
            payload["provider"] = provider
        if model:
            payload["model"] = model
        if provider_api_key:
            payload["provider_api_key"] = provider_api_key

        async with self._http.stream(
            "POST",
            "/v1/query/stream",
            json=payload,
            headers={"Accept": "text/event-stream"},
        ) as response:
            if response.status_code != 200:
                await response.aread()
                raise self._handle_error(response)

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json
                    try:
                        data = json.loads(line[6:])
                        yield RunEvent(
                            type=data.get("type", "unknown"),
                            data=data.get("data", {}),
                            timestamp=data.get("timestamp", 0),
                        )
                    except json.JSONDecodeError:
                        pass

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: dict[str, tuple[str, bytes, str]] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API."""
        kwargs: dict[str, Any] = {}
        if params:
            kwargs["params"] = params
        if json:
            kwargs["json"] = json
        if files:
            # Convert to httpx format
            kwargs["files"] = files

        response = await self._http.request(method, path, **kwargs)

        if response.status_code == 204:
            return {}

        if not response.is_success:
            raise self._handle_error(response)

        return response.json()

    def _handle_error(self, response: httpx.Response) -> KytchenError:
        """Convert HTTP error response to exception."""
        message = response.reason_phrase or "Unknown error"
        try:
            data = response.json()
            if "detail" in data:
                if isinstance(data["detail"], str):
                    message = data["detail"]
                elif isinstance(data["detail"], list) and data["detail"]:
                    message = str(data["detail"][0])
            elif "message" in data:
                message = data["message"]
        except Exception:
            pass

        status = response.status_code
        if status == 401:
            return AuthenticationError(message)
        if status == 404:
            return NotFoundError(message)
        if status == 429:
            return RateLimitError(message)
        return KytchenError(message, status)

    def _parse_query_result(self, data: dict) -> QueryResult:
        """Parse API response into QueryResult object."""
        evidence = [
            Evidence(
                tool_name=e.get("tool_name", ""),
                snippet=e.get("snippet", ""),
                params=e.get("params", {}),
                line_start=e.get("line_start"),
                line_end=e.get("line_end"),
                note=e.get("note"),
            )
            for e in data.get("evidence", [])
        ]

        return QueryResult(
            run_id=data.get("run_id", ""),
            answer=data.get("answer"),
            success=data.get("success", False),
            error=data.get("error"),
            evidence=evidence,
            metrics=data.get("metrics", {}),
        )
