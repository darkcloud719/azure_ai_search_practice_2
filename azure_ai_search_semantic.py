"""
FILE: azure_ai_search_semantic.py
DESCRIPTION:
    This script demonstrates how to create a simple Azure Search index, upload documents,
    and perform a semantic search query using the Azure Search SDK for Python. It includes error handling.
USAGE:
    1. Ensure you have the required environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-search-service-api-key>
    2. Run the script:
        python azure_ai_search_semantic.py
    3. The script will create an index, upload documents from 'text-sample.json', and perform a semantic search query.
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
from pathlib import Path
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

# Create formatters and add them to handlers
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
    table.add_column("Category", style="green")
    table.add_column("Content", style="white")

    for r in results:
        table.add_row(
            str(r.get("id", "")),
            r.get("title", ""),
            r.get("category", ""),
            r.get("content", "")[:100] + "..." if r.get("content", "") else ""
        )

    console.print(table)

def _delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.delete_index(index_name)
            pprint(f"[green]Index `{index_name}` deleted successfully.[/green]")
    except Exception as e:
        pprint(f"[red]Error deleting index: {e}[/red]")
        logger.error(f"Error deleting index: {e}")

def _create_index():
    try:
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String)
        ]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                keywords_fields=[SemanticField(field_name="category")],
                content_fields=[SemanticField(field_name="content")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(
            name="MyProfile",
            text_weights=TextWeights(weights={"content":1.5})
        )
        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{"name":"sg","source_fields":["title","content"]}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            semantic_search=semantic_search
        )

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.create_index(index)
            pprint(f"[green]Index {index_name} created successfully.[/green]")
    except Exception as ex:
        pprint(f"[red]Error creating index: {index_name}:{ex}[/red]")
        logging.error(f"Error creating index: {index_name}:{ex}")

def _upload_index():
    try:
        path = Path.cwd() / "text-sample.json"
        with open(path, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            result = search_client.upload_documents(documents=input_data)
            # pprint(f"[green]Documents uploaded successfully: {result}[/green]")

    except Exception as e:
        pprint(f"[red]Error uploading documents: {e}[/red]")
        logger.error(f"Error uploading documents: {e}")


def search_index_by_queryType_semantic():
    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SEMANTIC,
                search_text="gateway",
                include_total_count=True,
                semantic_configuration_name="my-semantic-config"
            )

            all_records = list(results)
            logger.info(f"Results: {all_records}")
            print_search_results(all_records)

    except Exception as e:
        pprint(f"[red]Error performing search: {e}[/red]")
        logger.error(f"Error performing search: {e}")

if __name__ == "__main__":
    # _delete_index()
    # _create_index()
    # _upload_index()
    search_index_by_queryType_semantic()
            


