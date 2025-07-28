# %% 
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from settings import settings
from vetorizador import VectorConfig

vector_config = VectorConfig(
    chunker_tokenizer='BAAI/bge-base-en-v1.5',
    max_tokens=512,
    collection_name='teste_collection',
)

# %%
query_raw = 'sleep quality relationship to chronic pain'
dense_model = TextEmbedding(model_name=vector_config.chunker_tokenizer)

query_emb = list(dense_model.passage_embed([query_raw]))[0].tolist()


client = QdrantClient(url=settings.VECTOR_HOST)

#%%
result = client.query_points(
    collection_name=vector_config.collection_name,
    query=query_emb,
    limit=3
)
# %%
for r in result:

    _ , payload = r

    print('tamanho da lista ', len(payload))

    for resp in payload:
        print(resp.payload)
        

# %%
