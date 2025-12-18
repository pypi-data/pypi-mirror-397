import asyncio
import time
from typing import Any, List, Optional

import requests

from llama_index.core.embeddings import BaseEmbedding


class DigitalOceanEmbeddings(BaseEmbedding):
    """LlamaIndex embedding model backed by DigitalOcean GenAI embeddings REST API."""

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_token: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        
        # Users must explicitly provide a token; this library does not read
        if not api_token:
            raise ValueError(
                "An API token is required. Pass api_token explicitly; "
                "environment variables are not read by this library."
            )

        # Use private attributes to avoid Pydantic validation issues
        self._model = model
        self._api_token = api_token
        self._base_url = "https://api.digitalocean.com/v2/gen-ai/embeddings"
        self._headers = {
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = self._fetch_embeddings([query])
        return embeddings[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = self._fetch_embeddings([text])
        return embeddings[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._fetch_embeddings(texts)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return await asyncio.to_thread(self._get_query_embedding, query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return await asyncio.to_thread(self._get_text_embedding, text)

    def _fetch_embeddings(self, inputs: List[str]) -> List[List[float]]:
        """Fetch embeddings from DigitalOcean API with retry logic."""
        payload = {
            "model": self._model,
            "input": inputs,
        }

        retries = 0
        while True:
            try:
                resp = requests.post(
                    self._base_url,
                    headers=self._headers,
                    json=payload,
                    timeout=30.0,
                )

                # Retry on transient HTTP errors
                if (
                    resp.status_code in {429, 500, 502, 503, 504}
                    and retries < 3
                ):
                    retries += 1
                    time.sleep(1.0 * retries)
                    continue

                resp.raise_for_status()
                data = resp.json()
                return [item["embedding"] for item in data.get("data", [])]
            except requests.RequestException:
                if retries < 3:
                    retries += 1
                    time.sleep(1.0 * retries)
                    continue
                raise


