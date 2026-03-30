"""
FILE: azure_ai_search_clear_index_data.py
DESCRIPTION:
    This script demonstrates how to clear all documents from on Azure Search index using the Azure Search SDK for Python. It includes error handling and logging.
USAGE:
    1. Ensure you have the required environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-search-service-api-key>
    2. Run the script:
        python azure_ai_search_clear_index_data.py
    3. The script will delete all documents from the specified index in batches.
"""
import os, json, logging, sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    EntityRecognitionSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    SearchIndexerSkillset,
    SearchableField,
    IndexingParameters,
    SearchIndexerDataSourceConnection,
    IndexingParametersConfiguration,
    IndexingSchedule,
    CorsOptions,
    SearchIndexer,
    FieldMapping,
    ScoringProfile,
    ComplexField,
    ImageAnalysisSkill,
    OcrSkill,
    VisualFeature,
    TextWeights,
    SearchField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
)
from dotenv import load_dotenv
from typing import List
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
import time

# --------------------------------------------------------------------------
# Load environment variables from .env file
# --------------------------------------------------------------------------
load_dotenv()

# Configure logging
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

# Create handlers
console_handler = RichHandler()
console_handler.setLevel(logging.WARNING)

file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s -%(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

console = Console()

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "azure-ai-search-simple-index"

def _get_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            index = search_index_client.get_index(index_name)
            pprint(f"[green]Index '{index_name}' retrieved successfully.")
    except Exception as ex:
        pprint(f"[red]Error getting index: '{index_name}':{ex}")

def _get_index_document_count() -> int:
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            stats = search_index_client.get_index_statistics(index_name)
            doc_count = stats.get("document_count")
            pprint(f"[green]Index `{index_name}` document count: {doc_count}[/green]")

            return doc_count

    except Exception as ex:
        pprint(f"[red]Error getting document count for index '{index_name}':{ex}")
        logger.error(f"Error getting document count for index '{index_name}':{ex}")

def _clear_index_documents_with_wait(batch_size=1000) -> None:
    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:

            total_deleted = 0

            while True:
                results = list(search_client.search(
                    search_text="*",
                    select=["id"],
                    top=batch_size
                ))

                if not results:
                    break

                keys = [{"id":doc["id"]} for doc in results]

                search_client.delete_documents(documents=keys)

                total_deleted += len(keys)

                time.sleep(2)

            pprint(f"[green]All documents deleted from index '{index_name}' successfully. Total deleted: {total_deleted}")

    except Exception as ex:
        pprint(f"[red]Error clearing documents from index '{index_name}':{ex}")

if __name__ == "__main__":
    # _get_index()
    # _get_index_document_count()
    _clear_index_documents_with_wait()


