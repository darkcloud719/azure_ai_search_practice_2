"""
FILE: azure_ai_search_skillset_indexer.py
DESCRIPTION:
    This sample demonstrates how to create an Azure AI Search index with a skillset and indexer, and how to clear documents
    from the index with a wait mechanism to ensure all documents are deleted.
USAGE:
    1. Ensure you have the necessary environment variables set in a .env file:
        AZURE_SEARCH_SERVICE_ENDPOINT=<your-search-service-endpoint>
        AZURE_SEARCH_API_KEY=<your-search-service-api-key>
        AZURE_STORAGE_CONNECTION_STRING=<your-azure-storage-connection-string>
    2. Run the script to create the index, data source connection, skillset, and indexer:
        python azure_ai_search_skillset_indexer.py
    3. To clear documents from the index, uncomment the _clear_index_documents_with_wait() call in the main block and run the script again.
"""
import os, json, logging, sys, openai, time
from openai import AzureOpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient, SearchIndexingBufferedSender
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
    VectorEncodingFormat,
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

# -----------------------------------------------------------------------------
# Load environment variables from .env file
# -----------------------------------------------------------------------------
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
index_name = "hotels-vector-index"
indexer_name = "hotels-vector-indexer"
storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")


def _delete_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            if search_index_client.get_index(index_name):
                pprint(f"[yellow]Deleting existing index: {index_name}[/yellow]")
                search_index_client.delete_index(index_name)
    except Exception as ex:
        pprint(f"[red]Error deleting index: {ex}[/red]")
        logger.error(f"Error deleting index: {ex}")


def _get_index():
    try:
        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            if search_index_client.get_index(index_name):
                pprint(f"[yellow]Index already exists: {index_name}[/yellow]")
    except Exception as ex:
        pprint(f"[red]Error retrieving index: {ex}[/red]")
        logger.error(f"Error retrieving index: {ex}")

def _create_index():
    try:
        fields = [
            SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True),
            SimpleField(name="hotelName", type=SearchFieldDataType.String, sortable=True),
            SearchableField(name="description", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
            SearchableField(name="description_fr", type=SearchFieldDataType.String, analyzer_name="fr.lucene"),
            SearchableField(name="category", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
            SearchableField(name="tags", type=SearchFieldDataType.String, facetable=True, filterable=True, collection=True),
            SimpleField(name="parkingIncluded", type=SearchFieldDataType.Boolean, filterable=True, sortable=True),
            SimpleField(name="smokingAllowed", type=SearchFieldDataType.Boolean, filterable=True, sortable=True),
            SimpleField(name="lastRenovationDate", type=SearchFieldDataType.DateTimeOffset, facetable=True, filterable=True, sortable=True),
            SimpleField(name="rating", type=SearchFieldDataType.Double, facetable=True, filterable=True, sortable=True),
            SimpleField(name="location", type=SearchFieldDataType.GeographyPoint, filterable=True, sortable=True),
            ComplexField(name="address", fields=[
               SearchableField(name="streetAddress", type=SearchFieldDataType.String),
               SearchableField(name="city", type=SearchFieldDataType.String, facetable=True, sortable=True),
               SearchableField(name="stateProvince", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
               SearchableField(name="postalCode", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True),
               SearchableField(name="country", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=True)
            ]),
            SimpleField(name="url", type=SearchFieldDataType.String),
            SimpleField(name="file_name", type=SearchFieldDataType.String),
            SearchableField(name="emails", type=SearchFieldDataType.String, collection=True),
            SimpleField(name="mysentiment", type=SearchFieldDataType.String),
            ComplexField(
                name="namedEntities",
                fields=[
                    SimpleField(name="text", type=SearchFieldDataType.String),
                    SimpleField(name="category", type=SearchFieldDataType.String),
                    SimpleField(name="subcategory", type=SearchFieldDataType.String),
                    SimpleField(name="length", type=SearchFieldDataType.Int32),
                    SimpleField(name="offset", type=SearchFieldDataType.Int32),
                    SimpleField(name="confidenceScore", type=SearchFieldDataType.Double)
                ],
                collection=True
            )
        ]

        semantic_config = SemanticConfiguration(
            name="my-semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="hotelName"),
                keywords_fields=[SemanticField(field_name="category"), SemanticField(field_name="tags")],
                content_fields=[SemanticField(field_name="description"), SemanticField(field_name="description_fr")]
            )
        )

        semantic_search = SemanticSearch(configurations=[semantic_config])

        scoring_profiles:List[ScoringProfile] = []
        scoring_profile = ScoringProfile(
            name="my-scoring-profile",
            text_weights=TextWeights(weights={"description": 1.0})
        )

        scoring_profiles.append(scoring_profile)
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)

        suggesters = [{"name":"sg","source_fields":["tags","address/city","address/country"]}]

        index = SearchIndex(
            name=index_name,
            fields=fields,
            scoring_profiles=scoring_profiles,
            cors_options=cors_options,
            suggesters=suggesters,
            semantic_search=semantic_search
        )

        with SearchIndexClient(service_endpoint, AzureKeyCredential(key)) as search_index_client:
            search_index_client.create_index(index)
            pprint(f"[green]Index created successfully: {index_name}[/green]")
    except Exception as ex:
        pprint(f"[red]Error creating index: {ex}[/red]")
        logger.error(f"Error creating index: {ex}")

def _create_data_source_connection():
    try:
        container = SearchIndexerDataContainer(name="hotels-container")

        data_source_connection = SearchIndexerDataSourceConnection(
            name="hotels-blob-datasource",
            type="azureblob",
            connection_string=storage_connection_string,
            container=container
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.create_data_source_connection(data_source_connection)
            pprint(f"[green]Data source connection created successfully: hotels-blob-datasource[/green]")
    except Exception as ex:
        pprint(f"Error creating data source connection: {ex}[/red]")

def _create_skillset():

    try:
        inp = InputFieldMappingEntry(name="text", source="/document/description")

        sentiment_output = OutputFieldMappingEntry(name="sentiment", target_name="mysentiment")
        email_output = OutputFieldMappingEntry(name="emails", target_name="emails")
        name_output = OutputFieldMappingEntry(name="namedEntities", target_name="namedEntities")

        sentimentSkill = SentimentSkill(name="my-sentiment-skill", inputs=[inp], outputs=[sentiment_output])
        entityRecognitionSkill = EntityRecognitionSkill(
            name="my-entity-recognition-skill",
            inputs=[inp],
            outputs=[email_output, name_output]
        )

        skillset = SearchIndexerSkillset(
            name="hotels-skillset",
            skills=[sentimentSkill, entityRecognitionSkill],
            description="Extract sentiment and named entities from hotel descriptions"
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.create_skillset(skillset)
            pprint(f"[green]Skillset created successfully: hotels-skillset[/green]")
    except Exception as ex:
        pprint(f"[red]Error creating skillset: {ex}[/red]")
        logger.error(f"Error creating skillset: {ex}")

def _create_indexer():
    try:
        
        configuraation = IndexingParametersConfiguration(
            parsing_mode="jsonArray",
            query_timeout=None
        )

        parameters = IndexingParameters(configuration=configuraation)

        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name="hotels-blob-datasource",
            target_index_name=index_name,
            skillset_name="hotels-skillset",
            parameters=parameters,
            field_mappings=[
                FieldMapping(source_field_name="metadata_storage_path", target_field_name="url"),
                FieldMapping(source_field_name="metadata_storage_name", target_field_name="file_name")
            ],
            output_field_mappings=[
                FieldMapping(source_field_name="/document/mysentiment", target_field_name="mysentiment"),
                FieldMapping(source_field_name="/document/emails", target_field_name="emails"),
                FieldMapping(source_field_name="document/namedEntities", target_field_name="namedEntities")
            ]
        )

        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            search_indexer_client.create_indexer(indexer)
            pprint(f"[green]Indexer created successfully: {indexer_name}[/green]")

    except Exception as ex:
        pprint(f"[red]Error creating indexer: {ex}[/red]")
        logger.error(f"Error creating indexer: {ex}")

def _delete_indexer():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            if search_indexer_client.get_indexer(indexer_name):
                pprint(f"[yellow]Deleting existing indexer: {indexer_name}[/yellow]")
                search_indexer_client.delete_indexer(indexer_name)
    except Exception as ex:
        pprint(f"[red]Error deleting indexer: {ex}[/red]")
        logger.error(f"Error deleting indexer: {ex}")

def _delete_data_source_connection():
    try:
        with SearchIndexerClient(service_endpoint, AzureKeyCredential(key)) as search_indexer_client:
            if search_indexer_client.get_data_source_connection("hotels-blob-datasource"):
                pprint(f"[yellow]Deleting existing data source connectinon: hotels-blob-datasource[/yellow]")
                search_indexer_client.delete_data_source_connection("hotels-blob-datasource")
    except Exception as ex:
        pprint(f"[red]Error deleting data source connection: {ex}][/red]")
        logger.error(f"Error deleting data source connection: {ex}")

def _clear_index_documents_with_wait(batch_size=1000):
    try:
        with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            total_deleted = 0
            while True:
                results = search_client.search(
                    search_text="*",
                    top=batch_size,
                    select="hotelId"
                )

                docs = list(results)

                if not docs:
                    break

                print(docs)

                keys = [{"hotelId": doc["hotelId"]} for doc in docs]

                search_client.delete_documents(documents=keys)

                total_deleted += len(keys)

                time.sleep(2)

            # pprint(f"[yellow]Deleted {len(keys)} documents. Total deleted: {total_deleted}[/yellow]")
            pprint(f"[yellow]Deleted {total_deleted} documents from index: {index_name}[/yellow]")

    except Exception as ex:
        pprint(f"[red]Error clearing index documents: {ex}[/red]")
        logger.error(f"Error clearing index documents: {ex}")


if __name__ == "__main__":
    # _delete_index()
    # _delete_indexer()
    # _delete_data_source_connection()
    # _create_index()
    # _create_data_source_connection()
    # _create_skillset()
    # _create_indexer()
    _clear_index_documents_with_wait()
    
    








