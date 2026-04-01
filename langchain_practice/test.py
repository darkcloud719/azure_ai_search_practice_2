from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from rich import print
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
import time
import os
import logging
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = RichHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
) 

file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

console = Console()

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_OPENAI_API_DEPLOYMENT_4O = os.getenv("AZURE_OPENAI_API_DEPLOYMENT_4O")

llm_openai = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
    deployment_name=AZURE_OPENAI_API_DEPLOYMENT_4O,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    openai_api_key=AZURE_OPENAI_API_KEY
)

# Prompt

prompt = ChatPromptTemplate.from_messages([
    ("system","You are a professional translator. Translate Mandarin to English."),
    ("human","{input}")
])

# Parser 
parser = StrOutputParser()

# Chain 
chain = prompt | llm_openai | parser

# Invoke

msg = "教授跟我說:如果學東西要別人教你，你才開始學，那你就太弱了"
result = chain.invoke({"input": msg})

table = Table(title="Translated Text")
table.add_column("Input", style="cyan")
table.add_column("Output", style="magenta")
table.add_row(msg, result)
console.print(table)


