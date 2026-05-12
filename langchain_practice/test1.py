from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import BaseCallbackHandler

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_OPENAI_API_DEPLOYMENT_4O = os.getenv("AZURE_OPENAI_API_DEPLOYMENT_4O")


class PrintCallback(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print("\n[LLM Start]")

    def on_llm_end(self, response, **kwargs):
        print("\n[LLM End]")

    def on_llm_new_token(self, token, **kwargs):
        print(token, end="", flush=True)

llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
    deployment_name=AZURE_OPENAI_API_DEPLOYMENT_4O,
    openai_api_version=AZURE_OPENAI_API_VERSION,
    openai_api_key=AZURE_OPENAI_API_KEY,
    temperature=0.3,
    max_tokens=2048,
    max_retries=3,
    request_timeout=60,
    streaming=True
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "{input}")
])

# result = llm.invoke({"input":"What is the capital of France?"}, callbacks=[PrintCallback()])

chain = prompt | llm | StrOutputParser()

result = chain.invoke({"input":"What is the capital of France?"}, config={"callbacks":[PrintCallback()]})