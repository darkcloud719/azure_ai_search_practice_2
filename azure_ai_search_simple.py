"""
FILE: azure_ai_search_simple.py
DESCRIPTION:
    This script demonstrates how to create a simple Azure Search index, upload documents,
    and perform a search query using the Azure Search SDK for Python. It includes error handling.
USAGE:
    1. Ensure you have the required environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-search-service-api-key>
    2. Run the script:
        python azure_ai_search_simple.py
    3. The script will create an index, upload documents from 'text-sample.json', and perform a search query.
"""

import os
import json
import logging
from pathlib import Path
from typing import List
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
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console

# --------------------------------------------------------------------------
# Load environment variables from .env file
# --------------------------------------------------------------------------
load_dotenv()

# logging.basicConfig(
#     level=logging.WARNING,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     handlers=[RichHandler()]
# )

# 
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = RichHandler()
console_handler.setLevel(logging.WARNING)

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

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "azure-ai-search-simple-index"


# --------------------------------------------------------------------------
# Helper function to create a search index
# --------------------------------------------------------------------------
def _delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as index_client:
            index_client.delete_index(index_name)
            pprint(F"[green]Index '{index_name}' deleted successfully.[/green]")
    except Exception as e:
        pprint(f"[red]Error deleting index: {e}[/red]")
        logger.error(f"Error deleting index: {e}")

def _create_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as index_client:
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="category", type=SearchFieldDataType.String, filterable=True),
                SearchableField(name="content", type=SearchFieldDataType.String)
            ]

            semantic_config = SemanticConfiguration(
                name="my-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    keywords_field=SemanticField(field_name="category"),
                    content_fields=[SemanticField(field_name="content")]
                )
            )

            scoring_profiles:List[ScoringProfile] = []
            scoring_profile = ScoringProfile(
                name="MyProfile",
                text_weights=TextWeights(weights={"content":2.0})
            )
            scoring_profiles.append(scoring_profile)

            cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
            suggester = [{"name":"sg","source_fields":["title","content"]}]

            index = SearchIndex(
                name=index_name,
                fields=fields,
                scoring_profiles=scoring_profiles,
                cors_options=cors_options
            )

            with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
                result = search_index_client.create_index(index)
                pprint(f"[green]Index '{index_name}' created successfully.[/green]")

    except Exception as e:
        pprint(f"[red]Error creating index: {e}[/red]")
        logger.error(f"Error creating index: {e}")

def _upload_documents():
    try:
        # path = Path.cwd() / "text-sample.json"
        path = Path.cwd().joinpath("text-sample.json")
        with open(path, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            result = search_client.upload_documents(documents=input_data)
            pprint(f"[green]Documents uploaded successfully: {result}.[/green]")

    except Exception as e:
        pprint(f"[red]Error uploading documents: {e}][/red]")
        logger.error(f"Error uploading documents: {e}")


def print_search_results(results):
    table = Table(title="Azure Search Results")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Content", style="white")

    for r in results:
        table.add_row(
            str(r.get("id","")),
            r.get("title",""),
            r.get("category",""),
            r.get("content","")[:100]
        )

    console.print(table)

def search_index_by_querytype_simple():
    try:
        # logger.info("TEST")
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SIMPLE,
                search_text="gateway",
                scoring_profile="MyProfile",
                include_total_count=True
            )

            all_records = [r for r in results]
            if not all_records:
                pprint("[yellow]No results found.[/yellow]")
            else:
                print_search_results(all_records)

    except Exception as e:
        pprint(f"[red]Error searching index: {e}[/red]")



if __name__ == "__main__":

    # _delete_index()
    # _create_index()
    # _upload_documents()
    search_index_by_querytype_simple()