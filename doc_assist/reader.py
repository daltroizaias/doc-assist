# %%
from docling.document_converter import DocumentConverter



# %%
ROOT = 'papers/'
FILE = '168675-Texto do Artigo-413103-2-10-20200930.pdf'
source = ROOT + FILE  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"
# %%
