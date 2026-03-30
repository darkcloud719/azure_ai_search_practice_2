"""
FILE: azure_ai_search_full.py
DESCRIPTION:
    This script demonstrates how to create a simple Azure Search index, upload documents,
    and perform a search query using the Azure Search SDK for Python. It includes error handling.
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

# Create formatter and add it to handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

console = Console()

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "azure-ai-search-simple-index"

def print_search_results(results):

    table = Table(title="Search Results")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Content", style="magenta")
    table.add_column("Score", style="green")
    table.add_column("Content", style="white")

    for r in results:
        table.add_row(
            str(r.get("id", "")),
            r.get("title", ""),
            r.get("category", ""),
            # r.get("content","")[:100]
            r.get("content", "")[:100] + "..." if r.get("content", "") else ""
        )

    console.print(table)

def search_index_by_queryType_full():
    try:
        with SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            query = "What is Azure AI?"
            results = search_client.search(
                query_type=QueryType.FULL,
                search_text=query,
                include_total_count=True,
                top=2
            )

            all_records = list(results)
            logger.info(f"Results: {all_records}")
            print_search_results(all_records)


    except Exception as e:
        pprint(f"[red]Error performing search: {e}[/red]")
        logger.error(f"Error performing search: {e}")


if __name__ == "__main__":
    search_index_by_queryType_full()






