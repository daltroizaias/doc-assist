# %%
from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, field_validator
from settings import settings

from tqdm import tqdm
# %%
# Modelos de dados
class Noticia(BaseModel):
    published: datetime
    title: str
    noticia: str

    @field_validator("published", mode="before")
    def parse_rfc2822(cls, value):
        if isinstance(value, str):
            return parsedate_to_datetime(value)
        return value

class Noticias(BaseModel):
    noticias: list[Noticia]


# %%
# URL do feed RSS

def get_feed(url: str) -> feedparser.util.FeedParserDict:
    feed = feedparser.parse(url)
    return feed


# Converte feed para o modelo

def transform_data(feed: feedparser.util.FeedParserDict) -> Noticias:
    dados_noticia = [
        Noticia(
            published=info["published"],
            title=info["title"],
            noticia=info.get("summary", "")
        )
        for info in feed["entries"]
    ]

    dados_noticia = Noticias(noticias=dados_noticia)

    return dados_noticia




# %%

def gen_prompt(noticia: Noticia):

    # Template de prompt
    template = """
    Você é um gerente de relações públicas e deve estar atualizado:
    Você receberá uma lista de notícias e deve resumir elas em formato de bullet point para simplificar a leitura.
    Classificar o tipo de noticia em: [Economia, Politica, Gerais]

    <noticias>
    {noticias}
    </noticias>

    Retorne em formato markdown com a seguinte estrutura:
    ## Tema: Economia

    ## Titulo:
    - item 1
    - item 2

    Sem texto adicional
    """

    prompt_template = PromptTemplate(
        input_variables=["noticias"],
        template=template
    )

    # Formata as notícias para o prompt
    noticias_texto = f"""
    Data: {noticia.published}\n
    Titulo: {noticia.title}\n
    noticia: {noticia.noticia}\n
    """

    final_prompt = prompt_template.format(noticias=noticias_texto)

    return final_prompt


# %%

def gen_response(noticia, llm):
    final_prompt = gen_prompt(noticia=noticia)
    response = llm.invoke(final_prompt)

    return response.content

# %%
URL = 'https://g1.globo.com/rss/g1/politica'
feed = get_feed(url=URL)

noticias = transform_data(feed=feed)
print(f'num noticias:{len(feed)}')


# Inicializa o LLM
llm = ChatGroq(
    model='deepseek-r1-distill-llama-70b',
    api_key=settings.GROQ_API_KEY,
)
#%%
lista_resposta = []


for noticia in tqdm(noticias.noticias):
    try:
        texto = gen_response(noticia=noticia, llm=llm)
        lista_resposta.append(texto)
    except Exception as e:
        print(f'ERRO: {e}')

data_atual = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
file_name = f'Noticias_{data_atual}'
with open(f'{file_name}.md', 'w', encoding='utf-8') as file:
    separador = '-'*30
    file.write(separador.join(lista_resposta,))


# %%
lista_resposta
# %%
