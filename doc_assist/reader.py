# %%
from docling.document_converter import DocumentConverter
from settings import settings
import os
from tqdm import tqdm


ROOT_MD = settings.OUTPUT_FILE
ROOT_PDF = settings.INPUT_FILE


# %%
def load_save_file(file: str) -> str:
    """
    Carrega os dados PDF e os tranforma em Markdown e os salva na pasta
    """
    print("convertendo")
    converter = DocumentConverter()
    result = converter.convert(file)

    file_name_orig = os.path.basename(file)
    file_name_cor = os.path.join(ROOT_MD, file_name_orig + ".md")

    print("salvando")
    with open(os.path.join(file_name_cor), "w", encoding="utf-8") as file:
        file.write(result.document.export_to_markdown())

    return result


def verificador(pasta_pdf: str, pasta_markdown: str):
    """
    Verifica quais os arquivos já foram processados e mantem somente
    aqueles que ainda não foram processados
    """

    files_markdown = os.listdir(pasta_markdown)
    files_markdown = [file.replace(".md", "") for file in files_markdown]

    files_pdf = os.listdir(pasta_pdf)
    file_unique = []
    for file in files_pdf:
        if file not in files_markdown:
            file_unique.append(file)

    return file_unique


def run():
    files = verificador(ROOT_PDF, ROOT_MD)
    progress_bar = tqdm(files)
    for file in progress_bar:
        progress_bar.set_description(f"Processando arquivo {file.split('/')[-1]}")

        load_save_file(file=os.path.join(ROOT_PDF, file))


if __name__ == "__main__":
    run()
