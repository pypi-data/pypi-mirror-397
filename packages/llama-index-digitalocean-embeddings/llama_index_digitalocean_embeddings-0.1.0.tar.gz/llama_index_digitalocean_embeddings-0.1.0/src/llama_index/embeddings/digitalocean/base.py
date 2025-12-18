import asyncio
import os
import time
from typing import Iterable, List, Optional

import requests

try:  # pragma: no cover - used when llama-index-core is available
    from llama_index.core.embeddings.base import BaseEmbedding
except ImportError:  # pragma: no cover - lightweight stub for environments without llama-index-core
    class BaseEmbedding:
        def get_text_embedding(self, text: str):
            return self._get_text_embedding(text)

        def get_query_embedding(self, query: str):
            return self._get_query_embedding(query)

        def get_text_embeddings(self, texts: List[str]):
            return self._get_text_embeddings(texts)

        def get_query_embeddings(self, queries: List[str]):
            return self._get_query_embeddings(queries)


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
        # Prefer the Gradient/DigitalOcean model access key; fall back to legacy token for compatibility.
        self.api_token = (
            model_access_key
            or os.getenv("GRADIENT_MODEL_ACCESS_KEY")
            or api_token
            or os.getenv("DIGITALOCEAN_TOKEN")
        )
        if not self.api_token:
            raise ValueError(
                "Gradient model access key is required. Set GRADIENT_MODEL_ACCESS_KEY "
                "or pass model_access_key/api_token."
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

