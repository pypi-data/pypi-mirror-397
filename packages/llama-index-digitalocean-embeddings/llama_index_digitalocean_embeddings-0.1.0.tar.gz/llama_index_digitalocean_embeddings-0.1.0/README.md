DigitalOcean Embeddings for LlamaIndex
======================================

This package provides a `DigitalOceanEmbeddings` implementation for LlamaIndex that calls DigitalOcean AI embeddings endpoints.

Quickstart
----------

1. Install:

   ```
   pip install -e .
   ```

2. Set environment variable:

   - `DIGITALOCEAN_TOKEN`: DigitalOcean Personal Access Token with AI access.

3. Use:

   ```python
   from llama_index.embeddings.digitalocean import DigitalOceanEmbeddings
   from llama_index.core import VectorStoreIndex, Document

   embed_model = DigitalOceanEmbeddings(model="text-embedding-3-small")
   docs = [Document(text="Hello from DigitalOcean")]
   index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
   print(index.as_query_engine().query("What was the greeting?"))
   ```

Configuration
-------------

- `model`: Embedding model name (e.g., `text-embedding-3-small`, `text-embedding-3-large`).
- `api_token`: Overrides `GRADIENT_MODEL_ACCESS_KEY` / `DIGITALOCEAN_TOKEN`.
- `model_access_key`: Preferred parameter name; same behavior as `api_token`.

Authentication resolution order:

1. `model_access_key` argument
2. `GRADIENT_MODEL_ACCESS_KEY` environment variable
3. `api_token` argument
4. `DIGITALOCEAN_TOKEN` environment variable

How it works (GenAI Embeddings REST API)
----------------------------------------

`DigitalOceanEmbeddings` does **not** use the Gradient SDK for embeddings. Instead, it calls the
DigitalOcean GenAI embeddings REST endpoint directly:

`POST https://api.digitalocean.com/v2/gen-ai/embeddings`

with a JSON body of the form:

```json
{
  "model": "text-embedding-3-small",
  "input": [
    "Hello, world!",
    "What is AI?"
  ]
}
```

The Python implementation in this package mirrors the official guidance from DigitalOcean: it uses a
bearer token, posts to `/v2/gen-ai/embeddings`, and reads the vectors from `data[*].embedding` in
the response.

Example: direct `curl` call
---------------------------

If you want to experiment with the raw API outside of LlamaIndex:

```bash
curl -X POST "https://api.digitalocean.com/v2/gen-ai/embeddings" \
  -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "text-embedding-3-small",
        "input": [
          "Hello, world!",
          "What is AI?"
        ]
      }'
```

You can then store the returned vectors in a vector-capable database (e.g., PostgreSQL + pgvector,
Milvus, etc.), or just let LlamaIndex manage that via its vector stores as shown in the Quickstart.

Notes
-----

- Handles auth via bearer token.
- Includes simple retries/backoff for transient HTTP errors (e.g., 429/5xx).
- See `tests/` for mocked examples.

License
-------

Apache-2.0.

