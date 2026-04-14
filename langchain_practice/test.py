from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal
from rich import print 
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
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
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
    openai_api_key=AZURE_OPENAI_API_KEY,
    openai_api_version=AZURE_OPENAI_API_VERSION
)

class llm_schema(BaseModel):
    movie_summary_flag: Literal["positive", "negative"]

llm_structured_output = llm_openai.with_structured_output(llm_schema)

# TASK - 1 [Prompt]
prompt_template = ChatPromptTemplate.from_messages([
    ("system","You are a movie review evaluator"),
    ("human", "Please categorize the movie review as positive or negative: {input}")
])

# TASK - 2 [LLM]
llm_structured_output = llm_openai.with_structured_output(llm_schema)

# TASK - 3 [Custom Runnable]
def pydantic_json(input: llm_schema) -> str:
    return input.model_dump()['movie_summary_flag']

pydantic_json_lambda = RunnableLambda(pydantic_json)

# Conditional Chain 1
# TASK - 1 [Prompt]
linkedin_prompt = ChatPromptTemplate.from_messages([
    ("system","You are a LinkedIn post generator"),
    ("human", "Create a post for the following text for LinkedIn: {text}")
])

# TASK - 2 [LLM]

# TASK - 3 [Str Parser]

str_parser = StrOutputParser()

chain_linkedin = linkedin_prompt | llm_openai | str_parser

