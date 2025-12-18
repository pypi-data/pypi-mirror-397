DigitalOcean Embeddings for LlamaIndex
======================================

This package provides a `DigitalOceanEmbeddings` implementation for LlamaIndex that calls DigitalOcean AI embeddings endpoints.

Quickstart
----------

1. Install:

   ```
   pip install llama-index-digitalocean-embeddings
   ```

2. Set environment variable:

   - `DIGITALOCEAN_TOKEN`: DigitalOcean Personal Access Token with AI access.

   -  ### Getting a DigitalOcean token

      Your `DIGITALOCEAN_TOKEN` is a Personal Access Token you create in the DigitalOcean Control Panel:

      a. Log in to `https://cloud.digitalocean.com`.
      b. Go to **Settings → API → Personal Access Tokens**.
      c. Click **Generate New Token**, choose the scopes you need (for embeddings, typically **CRUD** for GenAI and read for project), give the token a name, and click **Generate**.
      d. Copy the token and set it in your shell:

        ```bash
        export DIGITALOCEAN_TOKEN=your_token_here
        ```

      For more detailed, step‑by‑step guidance, see the [official DigitalOcean documentation](https://docs.digitalocean.com/reference/api/create-personal-access-token/).

3. Use:

   ```python
   from llama_index.digitalocean.embeddings import DigitalOceanEmbeddings
   from llama_index.core import VectorStoreIndex, Document

   embed_model = DigitalOceanEmbeddings(model="text-embedding-3-small")
   docs = [Document(text="Hello from DigitalOcean")]
   index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
   print(index.as_query_engine().query("What was the greeting?"))
   ```

Configuration
-------------

- `model`: Embedding model name (e.g., `text-embedding-3-small`, `text-embedding-3-large`).
- `api_token`: `DIGITALOCEAN_TOKEN`.

License
-------

Apache-2.0.

