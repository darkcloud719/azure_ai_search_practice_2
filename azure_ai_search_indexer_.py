"""
FILE: azure_ai_search_indexer.py
DESCRIPTION:
    This script demonstrates how to create an Azure Search indexer, data source connection,
    and index using the Azure Search SDK for Python. It includes error handling and logging.
USAGE:
    1. Ensure you have the required environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-search-service-api-key>
        AZURE_STORAGE_CONNECTION_STRING=<your-azure-storage-connection-string>
    2. Run the script:
        python azure_ai_search_indexer.py
    3. The script will create an index, data source connection, and indexer for Azure Search.
"""
import os, json, logging, sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType, QueryCaptionResult, QueryAnswerResult, QueryCaptionResult, QueryAnswerResult, VectorizedQuery, VectorizableTextQuery, VectorFilterMode
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    EntityRecognitionSkill,
    SentimentSkill,
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
    SemanticSearch,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters
)
from typing import List
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# Load environment variables from .env file
# --------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__file__)
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

service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "azure-ai-service-index"
indexer_name = "azure-ai-service-indexer"
data_source_name = "azure-ai-service-data-source"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def _delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            search_index_client.delete_index(index_name)
            pprint(f"[yellow]Deleted index: {index_name}[/yellow]")
    except Exception as ex:
        pprint(f"[red]Error deleting index: {ex}[/red]")
        logger.error(f"Error deleting index: {ex}")

def _create_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
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
                    keywords_fields=[SemanticField(field_name="category")],
                    content_fields=[SemanticField(field_name="content")]
                )
            )

            semantic_search = SemanticSearch(configurations=[semantic_config])

            scoring_profiles:List[ScoringProfile] = []
            scoring_profile = ScoringProfile(
                name="my-scoring-profile",
                text_weights=TextWeights(weights={"title": 3, "category": 2, "content": 1})
            )

            scoring_profiles.append(scoring_profile)
            cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
            suggester = [{"name":"sg","source_fields":["title","content"]}]

            index = SearchIndex(
                name=index_name,
                fields=fields,
                cors_options=cors_options,
                scoring_profiles=scoring_profiles
            )

            result=  search_index_client.create_index(index)
            pprint(f"[green]Index created successfully: {result.name}[/green]")

    except Exception as ex:
        pprint(f"[red]Error creating index: {ex}[/red]")
        logger.error(f"Error creating index: {ex}")

def _create_data_source_connection():
    try:
        container = SearchIndexerDataContainer(name="my-container")
        
        data_source_connection = SearchIndexerDataSourceConnection(
            name=data_source_name,
            type="azureblob",
            connection_string=connection_string,
            container=container
        )

        with SearchIndexerClient(endpoint=service_endpoint, credential=AzureKeyCredential(key)) as search_indexer_client:
            result = search_indexer_client.create_data_source_connection(data_source_connection)
            pprint(f"[green]Data source connection {data_source_name} created successfully.")
    except Exception as ex:
        pprint(f"Error creating data source connection: {ex}")
        logger.error(f"Error creating data source connection: {ex}")

def _delete_data_source_connection():
    try:
        with SearchIndexerClient(endpoint=service_endpoint, credential=AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.delete_data_source_connection(data_source_name)
            pprint(f"[yellow]Data source connection {data_source_name} deleted successfully.[/yellow]")
    except Exception as ex:
        pprint(f"[red]Error deleting data source connection: {ex}[/red]")
        logger.error("Error deleting data source connection: {ex}")


def _create_indexer():
    try:
        configuration = IndexingParametersConfiguration(
            parsing_mode="jsonArray",
            query_timeout=None
        )

        parameters = IndexingParameters(configuration=configuration)

        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name=data_source_name,
            target_index_name=index_name,
            parameters=parameters
        )

        with SearchIndexerClient(endpoint=service_endpoint, credential=AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.create_indexer(indexer)
            pprint(f"Indexer {indexer_name} created successfully.")
    except Exception as ex:
        pprint(f"[red]Error creating indexer {indexer_name}: {ex}[/red]")
        logger.error(f"Error creating indexer {indexer_name}: {ex}")

def _delete_indexer():
    try:
        with SearchIndexerClient(endpoint=service_endpoint, credential=AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.delete_indexer(indexer_name)
            pprint(f"[yellow]Indexer {indexer_name} deleted successfully.[/yellow]")
    except Exception as ex:
        pprint(f"[red]Error deleting indexer {indexer_name}: {ex}[/red]")
        logger.error(f"Error deleting indexer {indexer_name}: {ex}")

def print_search_results(results):
    table = Table(title="Azure Search Results")
    table.add_column("Id", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Content", style="white")

    for r in results:
        table.add_row(
            str(r.get("id", "")),
            r.get("title", ""),
            r.get("category", ""),
            r.get("content", "")[:100] + "..." if r.get("content") else ""
        )

    console.print(table)


def _simple_query_search():
    try:
        with SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SIMPLE,
                search_fields=["title"],
                search_text="Azure",
                include_total_count=True,
                scoring_profile="my-scoring-profile",
                top=5
            )

            all_results = list(results)
            if not all_results:
                pprint("[yellow]No results found.[/yellow]")
            else:
                print_search_results(all_results)

    except Exception as ex:
        pprint(f"[red]Error performing simple query search: {ex}[/red]")
        logger.error("Error performing simple query search: {ex}")

def _full_query_search():
    try:
        with SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.FULL,
                search_text="title:'Azure' AND category:'Management'",
                include_total_count=True
            )

            pprint(f"Total results: {results.get_count()}")

            all_results = list(results)
            if not all_results:
                pprint(["yellow]No results found.[/yellow]"])
            else:
                print_search_results(all_results)

    except Exception as ex:
        pprint(f"[red]Error performing full query search: {ex}[/red]")
        logger.error(f"Error performing full query search: {ex}")

def _update_index():
    try:
        semantic_config = SemanticConfiguration(
            name="my-semantic-config2",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                keywords_fields=[SemanticField(field_name="category")],
                content_fields=[SemanticField(field_name="content")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(
            name="my-scoring-profile",
            text_weights=TextWeights(weights={"title": 5, "category": 3, "content": 1})
        )

        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        suggester = [{"name":"sg","source_fields":["title","content"]}]

        with SearchIndexClient(endpoint=service_endpoint, credential=AzureKeyCredential(key)) as search_index_client:
            index = search_index_client.get_index(index_name)
            index.semantic_search = semantic_search
            index.cors_options = cors_options
            index.scoring_profiles = scoring_profiles

            result = search_index_client.create_or_update_index(index)

            pprint(f"[green]Index updated successfully: {result.name}[/green]")

    except Exception as ex:
        pprint(f"[red]Error updating index: {ex}[/red]")
        logger.error(f"Error updating index: {ex}")

def _semantic_query_search():

    try:
        with SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(key)) as search_client:
            results = search_client.search(
                query_type=QueryType.SEMANTIC,
                search_text="What is Azure Services ?",
                include_total_count=True,
                semantic_configuration_name="my-semantic-config2",
                query_caption=QueryCaptionType.EXTRACTIVE,
                query_answer=QueryAnswerType.EXTRACTIVE,
                top=2
            )

            all_results = list(results)
            if not all_results:
                pprint("[yellow]No results found.[/yellow]")
            else:
                print_search_results(all_results)

    except Exception as ex:
        pprint(f"[red]Error searching with semantic query: {ex}[/red]")
        logger.error(f"Error searching with semantic query: {ex}")



if __name__ == "__main__":
    # _delete_index()
    # _delete_data_source_connection()
    # _delete_indexer()
    # _create_index()
    # _create_data_source_connection()
    # _create_indexer()
    # _simple_query_search()
    # _full_query_search()
    # _update_index()
    _semantic_query_search()

        


