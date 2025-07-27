# %%
import os
import uuid
from datetime import datetime
from typing import Iterator

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker import BaseChunk
from fastembed import TextEmbedding
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from settings import settings
from tqdm import tqdm


# %%
class VectorConfig(BaseModel):
    collection_name: str
    max_tokens: int
    chunker_tokenizer: str


class Ingestor:
    def __init__(self, vector_config: VectorConfig, root_files: str):
        self.vector_config = vector_config
        self.qdrant = QdrantClient(
            url=settings.VECTOR_HOST,
            check_compatibility=False,
        )
        self.root_files = root_files

    def create_collection(self):
        try:
            self.qdrant.create_collection(
                collection_name=self.vector_config.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_config.max_tokens,
                    distance=Distance.COSINE,
                ),
                timeout=5000,
            )

        except Exception as err:
            if 'already exists' not in str(err):
                print(f'Erro ao criar coleção: {err}')
                raise
            print(f'Coleção {self.vector_config.collection_name} já existe')

        return print(
            f'Coleção {self.vector_config.collection_name} pronta para uso'
        )

    def chunker_data(self, file: str) -> Iterator[BaseChunk]:
        # Leitura do Documento
        converter = DocumentConverter()
        doc = converter.convert(file)

        # Transformação em chunk
        chunker = HybridChunker(
            tokenizer=self.vector_config.chunker_tokenizer,
            max_tokens=self.vector_config.max_tokens,
            merge_peers=True,
        )
        return chunker.chunk(doc.document)

    def embedding_processor(self, file: str) -> list[PointStruct]:
        chunk_iter = self.chunker_data(file)
        # Embedding dos chunks
        dense_model = TextEmbedding(
            model_name=self.vector_config.chunker_tokenizer
        )

        points: list[PointStruct] = []
        for i in chunk_iter:
            # Embbedding do chunk
            dense_embedding = list(dense_model.passage_embed([i.text]))[
                0
            ].tolist()

            payload = {
                'text': i.text,
                'model_embedding': self.vector_config.chunker_tokenizer,
                'source_file': os.path.basename(file),
                'ingestion_date': datetime.now().isoformat(),
                'data_collection_date': file,
            }

            # Organiza no formato do vector database
            point = PointStruct(
                id=str(uuid.uuid4()), vector=dense_embedding, payload=payload
            )

            points.append(point)
        return points

    def run(self):
        # Cria a tabela
        self.create_collection()

        # Verifica os arquivos da pasta
        files = os.listdir(self.root_files)

        if files:
            # Barra de progressão
            progress_bar = tqdm(files)
            for file in progress_bar:
                progress_bar.set_description(
                    f'Processando arquivo {os.path.basename(file)}'
                )

                # Cria os chunks e retorna o embedding dos dados
                file_path = os.path.join(self.root_files, file)
                points = self.embedding_processor(file_path)

                self.qdrant.upsert(
                    collection_name=self.vector_config.collection_name,
                    points=points,
                    wait=True,
                )
            return print(
                f'Processo concluído, adicionado {len(files)} ao banco de dados'  # noqa: E501
            )


# %%
vector_config = VectorConfig(
    chunker_tokenizer='BAAI/bge-base-en-v1.5',
    max_tokens=512,
    collection_name='teste_collection',
)
file_path = settings.OUTPUT_FILE
ingestor = Ingestor(vector_config=vector_config, root_files=file_path)

ingestor.run()
# %%
