

# %%
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker


file = 'Files/markdown_files/10.1016@S0140-67362032340-0.pdf.md'

converter = DocumentConverter()
#%%
doc = converter.convert(file)
chunker = HybridChunker(
    tokenizer="BAAI/bge-small-en-v1.5",
    max_tokens=300)  # set tokenizer as needed
chunk_iter = chunker.chunk(doc.document)

# %%
print(list(chunk_iter)[1])
# %%
