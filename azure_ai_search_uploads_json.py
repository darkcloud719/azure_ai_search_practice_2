"""
FILE: azure_ai_search_uploads_json.py
DESCRIPTION:
    This script demonstrates how to create a simple Azure Search index, upload documents from a JSON file,
    and perform a search query using the Azure Search SDK for Python. It includes error handling.
USAGE:
    1. Ensure you have the required environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-search-service-api-key>
    2. Run the script:
        python azure_ai_search_uploads_json.py
    3. The script will create an index, upload documents from 'hotels-small.json', and perform a search query.
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
from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------
# Load environment variables from .env file
# -----------------------------------------------------------------
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

def _delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            if search_index_client.get_index(index_name):
                search_index_client.delete_index(index_name)
                pprint(f"[green] Deleted existing index: {index_name}[/green]")
            else:
                pprint(f"[yellow] No existing index found: {index_name}[/yellow]")
                logger.info(f"No existing index found: {index_name}")
    except Exception as e:
        pprint(f"[red] Error deleting index: {e}[/red]")
        logger.error(f"Error deleting index: {e}")

def _create_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            fields = [
                SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
                SearchableField(name="hotelName", type=SearchFieldDataType.String, sortable=True),
                SearchableField(name="description", type=SearchFieldDataType.String),
                SearchableField(name="descriptionFr", type=SearchFieldDataType.String),
                SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True),
                SimpleField(name="parkingIncluded", type=SearchFieldDataType.Boolean, filterable=True, facetable=True),
                SimpleField(name="smokingAllowed", type=SearchFieldDataType.Boolean, filterable=True),
                SimpleField(name="lastRenovationDate", type=SearchFieldDataType.DateTimeOffset, filterable=True),
                SimpleField(name="rating", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
                SimpleField(name="location", type=SearchFieldDataType.GeographyPoint, filterable=True),
                ComplexField(
                    name="address",
                    fields=[
                        SearchableField(name="streetAddress", type=SearchFieldDataType.String, filterable=True),
                        SearchableField(name="city", type=SearchFieldDataType.String, filterable=True),
                        SimpleField(name="stateProvince", type=SearchFieldDataType.String, filterable=True),
                        SimpleField(name="country", type=SearchFieldDataType.String, filterable=True),
                        SimpleField(name="postalCode", type=SearchFieldDataType.String, filterable=True)
                    ]
                ),
                ComplexField(
                    name="rooms",
                    collection=True,
                    fields=[
                        SearchableField(name="description", type=SearchFieldDataType.String),
                        SearchableField(name="descriptionFr", type=SearchFieldDataType.String),
                        SimpleField(name="type", type=SearchFieldDataType.String, filterable=True),
                        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
                        SimpleField(name="bedOptions", type=SearchFieldDataType.String),
                        SimpleField(name="sleepsCount", type=SearchFieldDataType.Int32),
                        SimpleField(name="smokingAllowed", type=SearchFieldDataType.Boolean),
                        SearchableField(name="tags", type=SearchFieldDataType.String, collection=True)
                    ]
                )
            ]

            # semantic_config = SemanticConfiguration(
            #     name="my-semantic-config",
            #     prioritized_fields=SemanticPrioritizedFields(
            #         title_field=SemanticField(field_name="hotelName"),
            #         keywords_fields=SemanticField(field_name="category"),
            #         content_fields=[
            #             SemanticField(field_name="description"),
            #             SemanticField(field_name="description_fr"),
            #             SemanticField(field_name="address/streetAddress"),
            #             SemanticField(field_name="address/city"),
            #             SemanticField(field_name="address/stateProvince"),
            #             SemanticField(field_name="address/country"),
            #             SemanticField(field_name="address/postalCode")
            #         ]
            #     )
            # )

            semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="hotelName"),
                keywords_fields=[SemanticField(field_name="category")],
                content_fields=[
                    SemanticField(field_name="description"),
                    SemanticField(field_name="descriptionFr"),
                    SemanticField(field_name="address/streetAddress"),
                    SemanticField(field_name="address/city"),
                    SemanticField(field_name="address/stateProvince"),
                    SemanticField(field_name="address/country"),
                    SemanticField(field_name="address/postalCode")            
                ]
                )
            )

            semantic_search = SemanticSearch(configurations=[semantic_config])

            scoring_profiles:List[ScoringProfile] = []
            scoring_profile = ScoringProfile(
                name="my-scoring-profile",
                text_weights=TextWeights(weights={"description": 1.5, "descriptionFr": 1.5})
            )
            scoring_profiles.append(scoring_profile)

            cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
            suggesters = [{"name": "sg", "source_fields":["hotelName", "description", "descriptionFr"]}]

            index = SearchIndex(
                name=index_name,
                fields=fields,
                semantic_search=semantic_search,
                scoring_profiles=scoring_profiles,
                cors_options=cors_options,
                suggesters=suggesters
                
            )

            result = search_index_client.create_index(index)
            pprint(f"[green] Index created successfully: {index_name}[/green]")

    except Exception as e:
        pprint(f"[red] Error creating index: {e}[/red]")
        logger.error(f"Error creating index: {e}")

def _upload_documents():
    try:
        path = Path.cwd() / "hotels-small.json"

        with open(path, "r", encoding="utf-8") as f:
            input_data = json.load(f)
            with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
                result = search_client.upload_documents(documents=input_data)
                if result[0].succeeded:
                    pprint(f"[green] Documents uploaded successfully.[/green]")
                else:
                    pprint(f"[red] Error uploading documents: {result[0].error_message}[/red]")
    except Exception as e:
        pprint(f"[red] Error uploading documnents: {e}[/red]")
        logger.error(f"Error uploading documents: {e}")

if __name__ == "__main__":
    _delete_index()
    _create_index()
    _upload_documents()



            





