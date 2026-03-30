import os, json, logging, sys
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.models import QueryType, QueryCaptionResult, QueryAnswerResult, VectorizedQuery, VectorizableTextQuery, VectorFilterMode
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
    AzureOpenAIVectorizerParameters,
    SynonymMap
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
index_name = "hotels-index"

def create_synonym_map():
    try:
        synonyms = [
            "USA, United States, United States of America, US",
            "Washington, Wash => WA"
        ]

        synonym_map = SynonymMap(name="test-syn-map", synonyms=synonyms)
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.create_synonym_map(synonym_map)
            pprint(f"[green]Synonym map created successfully: {result.name}[/green]")
    except Exception as ex:
        pprint(f"[red]Error creating synonym map: {ex}[/red]")

def create_synonym_map_from_file():
    try:
        synonym_file_path = Path.cwd() / "synonym_map.json"
        with open(synonym_file_path, "r", encoding="utf-8") as f:
            synonyms = json.load(f)
            synonym_map = SynonymMap(name="test-syn-map-file", synonyms=synonyms)
            with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
                result = search_index_client.create_synonym_map(synonym_map)
                pprint(f"[green]Synonym map `{result.name}` created successfully from file.")
    except Exception as ex:
        pprint(f"[red]Error creating synonym map from file: {ex}[/red]")
        logger.error(f"Error creating synonym map from file: {ex}")

def get_synonym_map():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.get_synonym_map("test-syn-map")
            pprint(f"[green]Retrieved Synonym Map: {result.name}, Synonyms: {result.synonyms}[/green]")
    except Exception as ex:
        pprint(f"[red]Error retrieving synonym map: {ex}[/red]")
        logger.error(f"Error retrieving synonym map: {ex}")

def get_synonym_maps():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            synonym_maps = search_index_client.get_synonym_maps()
            table = Table(title="Synonym Maps")
            table.add_column("Name", style="cyan", no_wrap=True)
            table.add_column("Synonyms", style="magenta")
            for syn_map in synonym_maps:
                table.add_row(syn_map.name, ", ".join(syn_map.synonyms))
            console.print(table)
    except Exception as ex:
        pprint(f"[red]Error retrieving synonym maps: {ex}[/red]")
        logger.error(f"Error retrieving synonym maps: {ex}")

def delete_synonym_map():
    try:
        with SearchIndexClient(endpoint=service_endpoint, credential=AzureKeyCredential(key)) as search_index_client:
            result = search_index_client.delete_synonym_map("test-syn-map")
            pprint(f"[green]Synonym map deleted successfully.[/green]")
    except Exception as ex:
        pprint(f"[red]Error deleting synonym map: {ex}[/red]")

if __name__ == "__main__":
    # create_synonym_map()
    # get_synonym_map()
    # get_synonym_maps()
    delete_synonym_map()








