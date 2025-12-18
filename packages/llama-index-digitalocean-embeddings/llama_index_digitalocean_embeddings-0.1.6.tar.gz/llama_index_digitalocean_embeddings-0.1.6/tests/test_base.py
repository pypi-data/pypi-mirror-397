import asyncio
from llama_index.digitalocean.embeddings import DigitalOceanEmbeddings

embed = DigitalOceanEmbeddings(model="text-embedding-3-small", api_token="dummy-token")

# Sync
vec = embed.get_text_embedding("hello")
print("sync len:", len(vec), "head:", vec[:5])

# Async
async def main():
    avec = await embed._aget_text_embedding("hello async")
    print("async len:", len(avec), "head:", avec[:5])

asyncio.run(main())