# %%
from docling.document_converter import DocumentConverter
from settings import settings
import os
from tqdm import tqdm
# %%
ROOT_PDF = settings.INPUT_FILE
ROOT_MD = settings.OUTPUT_FILE


def load_save_file(file: str) -> str:

    print('convertendo')
    converter = DocumentConverter()
    result = converter.convert(file)

    file_name_orig = os.path.basename(file)
    file_name_cor= os.path.join(ROOT_MD, file_name_orig + '.md')

    print('salvando')
    with open(os.path.join(file_name_cor), 'w', encoding='utf-8') as file:
        file.write(result.document.export_to_markdown())

    return result


# %% 

files = os.listdir(ROOT_PDF)
progress_bar = tqdm(files)
for file in progress_bar:
    progress_bar.set_description(f'Processando arquivo {file.split('/')[-1]}')

    load_save_file(file=os.path.join(ROOT_PDF, file))
# %%
