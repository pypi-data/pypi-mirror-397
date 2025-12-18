import asyncio
import time
from typing import Iterable, List, Optional

import requests
from llama_index.core.embeddings.base import BaseEmbedding


class DigitalOceanEmbeddings(BaseEmbedding):
    """LlamaIndex embedding model backed by DigitalOcean GenAI embeddings REST API."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_token: Optional[str] = None,
        model_access_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> None:
        # Users must explicitly provide a token; this library does not read
        # environment variables to avoid hidden configuration.
        self.api_token = model_access_key or api_token
        if not self.api_token:
            raise ValueError(
                "An API token is required. Pass api_token or model_access_key explicitly; "
                "environment variables are not read by this library."
            )

        self.model = model
        self.base_url = "https://api.digitalocean.com/v2/gen-ai/embeddings"
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    # --- BaseEmbedding interface ---
    def _get_query_embedding(self, query: str) -> List[float]:
        return self._fetch_embeddings([query])[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._fetch_embeddings([text])[0]

    def _get_query_embeddings(self, queries: List[str]) -> List[List[float]]:
        return self._fetch_embeddings(list(queries))

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._fetch_embeddings(list(texts))

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return (await self._afetch_embeddings([query]))[0]

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return (await self._afetch_embeddings([text]))[0]

    async def _aget_query_embeddings(self, queries: List[str]) -> List[List[float]]:
        return await self._afetch_embeddings(list(queries))

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return await self._afetch_embeddings(list(texts))

    # --- public batch helpers for newer LlamaIndex cores ---
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch text embedding API expected by newer LlamaIndex versions."""
        return self._get_text_embeddings(texts)

    def get_query_embedding_batch(self, queries: List[str]) -> List[List[float]]:
        """Batch query embedding API expected by newer LlamaIndex versions."""
        return self._get_query_embeddings(queries)

    async def aget_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        """Async batch text embedding API expected by newer LlamaIndex versions."""
        return await self._aget_text_embeddings(texts)

    async def aget_query_embedding_batch(self, queries: List[str]) -> List[List[float]]:
        """Async batch query embedding API expected by newer LlamaIndex versions."""
        return await self._aget_query_embeddings(queries)

    # --- helpers ---
    def _fetch_embeddings(self, inputs: Iterable[str]) -> List[List[float]]:
        payload = {
            "model": self.model,
            "input": list(inputs),
        }

        retries = 0
        while True:
            try:
                resp = requests.post(
                    self.base_url,
                    headers=self._headers,
                    json=payload,
                    timeout=self.timeout,
                )

                # Retry on transient HTTP errors
                if (
                    resp.status_code in {429, 500, 502, 503, 504}
                    and retries < self.max_retries
                ):
                    retries += 1
                    time.sleep(self.backoff_factor * retries)
                    continue

                resp.raise_for_status()
                data = resp.json()
                return [item["embedding"] for item in data.get("data", [])]
            except requests.RequestException:
                if retries < self.max_retries:
                    retries += 1
                    time.sleep(self.backoff_factor * retries)
                    continue
                raise

    async def _afetch_embeddings(self, inputs: Iterable[str]) -> List[List[float]]:
        # Use a thread to reuse the sync HTTP implementation without adding
        # an additional async HTTP dependency.
        return await asyncio.to_thread(self._fetch_embeddings, list(inputs))


