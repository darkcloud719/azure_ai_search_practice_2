"""
FILE: azure_ai_search_datasource.py
DESCRIPTION:
    This script demonstrates how to create, list, get, and delete an Azure Search data source connection
    using the Azure Search SDK for Python. It includes error handling and logging.
USAGE:
    1. Ensure you have the required environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-search-service-api-key>
        AZURE_STORAGE_CONNECTION_STRING=<your-azure-storage-connection-string>
    2. Run the script:
        python azure_ai_search_datasource.py
    3. The script will create a data source connection to an Azure Blob Storage container, list existing data source connections,
        get details of the created data source connection, and then delete it.
"""

import os, json, logging, sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionType, QueryAnswerType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery, VectorizableTextQuery, VectorFilterMode
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
from dotenv import load_dotenv
from rich import print as pprint
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
import time

# --------------------------------------------------------------------------
# Load environment variables from .env file
# --------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__file__)
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
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def create_data_source_connection():
    try:
        container = SearchIndexerDataContainer(name="my-container")
        data_source_connection = SearchIndexerDataSourceConnection(
            name="my-datasource",
            type="azureblob",
            connection_string=connection_string,
            container=container
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as indexer_client:
            result = indexer_client.create_data_source_connection(data_source_connection)
            pprint(f"[green]Data source connection created successfully: {result.name}[/green]")
    except Exception as ex:
        pprint(f"[red]Error creating data source connection: {ex}[/red]")
        logger.error(f"Error creating data source connection: {ex}")

def list_data_source_connections():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as indexer_client:
            result = indexer_client.get_data_source_connections()
            names = [ds.name for ds in result]
            pprint(f"[green]Data source connections: {', '.join(names)}[/green]")
    except Exception as ex:
        pprint(f"[red]Error listing data source connections: {ex}[/red]")
        logger.error(f"Error listing data source connections: {ex}")

def get_data_source_connection():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as indexer_client:
            result = indexer_client.get_data_source_connection("my-datasource")
            pprint(f"[green]Data source connection details: {result.name}[/green]")
    except Exception as ex:
        pprint(f"[red]Error getting data source connection: {ex}[/red]")
        logger.error(f"Error getting data source connection: {ex}")

def delete_data_source_connection():
    try:
        with SearchIndexerClient(service_endpoint, credential=AzureKeyCredential(key)) as indexer_client:
            result = indexer_client.delete_data_source_connection("my-datasource")
            pprint(f"[green]Data source connection deleted successfully.[/green]")
    except Exception as ex:
        pprint(f"[red]Error deleting data source connection: {ex}[/red]")
        logger.error(f"Error deleting data source connection: {ex}")

if __name__ == "__main__":
    # create_data_source_connection()
    # list_data_source_connections()
    # get_data_source_connection()
    delete_data_source_connection()






